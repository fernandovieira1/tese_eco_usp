"""Reextrai CHIRPS nos 141 municípios da malha IBGE 2023, sem alterar fontes.

Usa os GeoTIFFs locais e a mesma regra da linhagem original: centros de pixel,
pesos cos(latitude), valores finitos não negativos e exclusão de NoData.
O ano civil continua candidato exploratório, sem escolher janela de safra.
"""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
import sys

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.features import rasterize


MENSAL = "h2__precip_mm__chirps_v2__mensal_candidato.csv"
ANUAL = "h2__precip_anomaly__chirps_v2__ano_civil_candidatos.csv"


def encontrar_raiz():
    for pasta in Path(__file__).resolve().parents:
        if (pasta / "2_INTI/RESEARCH_PROTOCOL.md").is_file():
            return pasta
    raise FileNotFoundError("Não foi encontrada a raiz do repositório.")


def hash_arquivo(caminho):
    digest = sha256()
    with Path(caminho).open("rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(1024 * 1024), b""):
            digest.update(bloco)
    return digest.hexdigest()


def construir_anual(mensal):
    """Exige 12 meses por total e 30 anos por climatologia; desvio usa ddof=1."""
    chave = ["codigo_ibge", "ano", "mes"]
    if mensal[chave].isna().any().any() or mensal.duplicated(chave).any():
        raise ValueError("Chave mensal ausente ou repetida.")
    if not mensal["mes"].between(1, 12).all():
        raise ValueError("Mês fora de 1 a 12.")
    anual = (mensal.groupby(["codigo_ibge", "ano"], observed=True)["precip_mm"]
             .agg(sum=lambda serie: serie.sum(min_count=1), count="count").reset_index())
    # `sum` registra a soma disponível; total anual exige os doze meses válidos.
    anual["precip_mm_anual"] = anual["sum"].where(anual["count"].eq(12))
    for inicio, fim in ((1981, 2010), (1991, 2020)):
        sufixo = f"{inicio}_{fim}"
        referencia = (anual.loc[anual["ano"].between(inicio, fim)]
                      .groupby("codigo_ibge", observed=True)["precip_mm_anual"]
                      .agg(mean="mean", std=lambda serie: serie.std(ddof=1), count="count"))
        # Preserva a contagem para diagnóstico e impede uma normal climática incompleta.
        referencia.loc[referencia["count"].ne(30), ["mean", "std"]] = np.nan
        anual = anual.join(referencia.add_suffix(f"_{sufixo}"), on="codigo_ibge", validate="many_to_one")
        anomalia = f"precip_anomaly_{sufixo}"
        anual[anomalia] = (anual["precip_mm_anual"] - anual[f"mean_{sufixo}"]).where(
            anual[f"count_{sufixo}"].eq(30)
        )
        anual[f"precip_zscore_{sufixo}"] = anual[anomalia] / anual[f"std_{sufixo}"].where(
            anual[f"std_{sufixo}"] > 0
        )
        anual[f"precip_deficit_{sufixo}"] = (-anual[anomalia]).clip(lower=0)
        anual[f"precip_excess_{sufixo}"] = anual[anomalia].clip(lower=0)
    return anual


def extrair_mensal(municipios, arquivos, raiz):
    """Rasteriza uma vez e usa bincount em todas as imagens da mesma grade."""
    rotulos = pesos = total_pesos = None
    assinatura_grade = None
    linhas = []
    fontes = []
    n_municipios = len(municipios)
    for ordem, caminho in enumerate(arquivos, start=1):
        ano, mes = map(int, re.fullmatch(r"chirps-v2\.0\.(\d{4})\.(\d{2})\.tif", caminho.name).groups())
        with rasterio.open(caminho) as raster:
            assinatura = (raster.crs.to_string(), tuple(raster.transform), raster.height, raster.width, raster.count)
            if assinatura_grade is None:
                if raster.crs.to_epsg() != 4326 or raster.count != 1:
                    raise ValueError("A regra cos(latitude) exige raster geográfico EPSG:4326 com uma banda.")
                if raster.transform.b != 0 or raster.transform.d != 0 or raster.transform.e >= 0:
                    raise ValueError("Grade rotacionada ou orientação inesperada.")
                xmin, ymin, xmax, ymax = municipios.total_bounds
                if not (raster.bounds.left <= xmin and raster.bounds.bottom <= ymin
                        and raster.bounds.right >= xmax and raster.bounds.top >= ymax):
                    raise ValueError("O recorte CHIRPS não cobre integralmente a malha.")
                assinatura_grade = assinatura
                # all_touched=False reproduz a atribuição pelo centro do pixel.
                rotulos = rasterize(
                    [(geometria, i + 1) for i, geometria in enumerate(municipios.geometry)],
                    out_shape=raster.shape, transform=raster.transform, fill=0,
                    all_touched=False, dtype="int16",
                )
                latitudes = raster.transform.f + (np.arange(raster.height) + 0.5) * raster.transform.e
                pesos = np.broadcast_to(np.cos(np.deg2rad(latitudes))[:, None], raster.shape)
                total_pesos = np.bincount(rotulos.ravel(), weights=pesos.ravel(), minlength=n_municipios + 1)
                if (total_pesos[1:] <= 0).any():
                    raise ValueError("Há município sem centro de pixel; não produzir uma média fictícia.")
            elif assinatura != assinatura_grade:
                raise ValueError(f"Grade diferente da máscara reutilizada: {caminho.name}")
            valores = raster.read(1)
            validos = np.isfinite(valores) & (valores >= 0) & (rotulos > 0)
            if raster.nodata is not None:
                validos &= valores != raster.nodata
            numerador = np.bincount(
                rotulos[validos], weights=(valores * pesos)[validos], minlength=n_municipios + 1,
            )
            denominador = np.bincount(rotulos[validos], weights=pesos[validos], minlength=n_municipios + 1)
            medias = np.divide(numerador, denominador, out=np.full(n_municipios + 1, np.nan), where=denominador > 0)
            linhas.append(pd.DataFrame({
                "codigo_ibge": municipios["CD_MUN"].to_numpy(),
                "municipio": municipios["NM_MUN"].to_numpy(),
                "ano": ano, "mes": mes, "precip_mm": medias[1:],
                "fracao_pixels_validos": denominador[1:] / total_pesos[1:],
            }))
            fontes.append({
                "arquivo": caminho.relative_to(raiz).as_posix(), "sha256": hash_arquivo(caminho),
                "ano": ano, "mes": mes, "nodata": raster.nodata,
                "centros_validos_MT": int(validos.sum()),
                "min_mm": float(valores[validos].min()) if validos.any() else None,
                "max_mm": float(valores[validos].max()) if validos.any() else None,
            })
        if ordem % 60 == 0 or ordem == len(arquivos):
            print(f"CHIRPS: {ordem}/{len(arquivos)} meses reextraídos", flush=True)
    grade = {
        "crs": assinatura_grade[0], "transform": list(assinatura_grade[1]),
        "height": assinatura_grade[2], "width": assinatura_grade[3],
        "mascara_rasterizada_vezes": 1,
        "mascara_sha256": sha256(rotulos.tobytes()).hexdigest(),
        "centros_por_municipio": dict(zip(
            municipios["CD_MUN"].tolist(),
            np.bincount(rotulos.ravel(), minlength=n_municipios + 1)[1:].astype(int).tolist(),
        )),
    }
    return pd.concat(linhas, ignore_index=True), fontes, grade


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    raiz = encontrar_raiz()
    dados = raiz / "2_INTI/xdata/chap1"
    malha = dados / "raw/vector/ibge/MT_Municipios_2023.zip"
    pasta_rasters = dados / "interim/raster/chirps_v2_mt_fullbounds"
    destino = dados / "processed/territorio_141"
    auditoria = raiz / "2_INTI/audit/aed_chap1_20261013/territorio141_chuva.json"
    originais = [dados / "processed/tabular" / nome for nome in (MENSAL, ANUAL)]
    fontes_protegidas = [malha, *originais]
    hashes_antes = {str(c.relative_to(raiz)): hash_arquivo(c) for c in fontes_protegidas}
    municipios = gpd.read_file("zip://" + malha.resolve().as_posix()).to_crs(4326)
    municipios["CD_MUN"] = municipios["CD_MUN"].astype("string")
    municipios = municipios.sort_values("CD_MUN").reset_index(drop=True)
    if len(municipios) != 141 or municipios["CD_MUN"].nunique() != 141:
        raise ValueError("A malha precisa conter 141 códigos únicos.")
    if "5101837" in set(municipios["CD_MUN"]):
        raise ValueError("Boa Esperança do Norte ainda está presente como município separado.")
    if not municipios.geometry.is_valid.all() or municipios.geometry.is_empty.any():
        raise ValueError("Malha contém geometrias inválidas/vazias; não reparar em silêncio.")
    arquivos = sorted(pasta_rasters.glob("chirps-v2.0.*.tif"))
    esperado = {f"chirps-v2.0.{ano}.{mes:02d}.tif" for ano in range(1981, 2026) for mes in range(1, 13)}
    if {c.name for c in arquivos} != esperado:
        raise ValueError("É necessário exatamente um raster por mês entre 1981 e 2025.")
    mensal, fontes, grade = extrair_mensal(municipios, arquivos, raiz)
    mensal = mensal.sort_values(["codigo_ibge", "ano", "mes"]).reset_index(drop=True)
    anual = construir_anual(mensal)
    esquemas = [pd.read_csv(c, nrows=0).columns.tolist() for c in originais]
    if mensal.columns.tolist() != esquemas[0] or anual.columns.tolist() != esquemas[1]:
        raise AssertionError("O esquema das tabelas derivadas difere do original.")
    if len(mensal) != 141 * 45 * 12 or len(anual) != 141 * 45:
        raise AssertionError("Número inesperado de observações.")
    if mensal.duplicated(["codigo_ibge", "ano", "mes"]).any() or anual.duplicated(["codigo_ibge", "ano"]).any():
        raise AssertionError("Chave duplicada no resultado.")
    if not mensal["fracao_pixels_validos"].between(0, 1 + 1e-12).all():
        raise AssertionError("Fração de pixels válidos fora de 0–1.")
    if (mensal["precip_mm"].dropna() < 0).any():
        raise AssertionError("Precipitação negativa.")
    for coluna in ("count_1981_2010", "count_1991_2020"):
        if not anual[coluna].eq(30).all():
            raise AssertionError("Há normal com menos de 30 anos completos; conferir o relatório mensal.")
    if not anual["count"].eq(12).all():
        raise AssertionError("Há ano com menos de 12 meses válidos.")
    original_mensal = pd.read_csv(originais[0], dtype={"codigo_ibge": "string"})
    comparacao = mensal.merge(
        original_mensal[["codigo_ibge", "ano", "mes", "precip_mm"]],
        on=["codigo_ibge", "ano", "mes"], how="left", suffixes=("_2023", "_2024"), validate="one_to_one",
    )
    comparacao["diferenca_absoluta_mm"] = (comparacao["precip_mm_2023"] - comparacao["precip_mm_2024"]).abs()
    diferencas = comparacao.groupby("codigo_ibge")["diferenca_absoluta_mm"].max().sort_values(ascending=False)
    destino.mkdir(parents=True, exist_ok=True)
    for tabela, nome in ((mensal, MENSAL), (anual, ANUAL)):
        temporario = destino / (nome + ".tmp")
        tabela.to_csv(temporario, index=False, encoding="utf-8")
        temporario.replace(destino / nome)
    hashes_depois = {str(c.relative_to(raiz)): hash_arquivo(c) for c in fontes_protegidas}
    if hashes_depois != hashes_antes:
        raise AssertionError("Uma fonte protegida mudou durante a execução.")
    relatorio = {
        "gerado_utc": datetime.now(timezone.utc).isoformat(),
        "script": Path(__file__).relative_to(raiz).as_posix(),
        "script_sha256": hash_arquivo(__file__),
        "malha": malha.relative_to(raiz).as_posix(), "malha_sha256": hash_arquivo(malha),
        "municipios": 141, "periodo_completo_preservado": [1981, 2025],
        "recorte_candidato_modelo": [2001, 2024],
        "regra": {
            "geografia": "Extração espacial integral na malha IBGE 2023; não atribui BEN a um único município-pai.",
            "media_municipal": "Centro do pixel (all_touched=False), peso cos(latitude), mesmo método da linhagem original.",
            "nodata": "Exclui NoData, negativos e valores não finitos; ausência permanece ausente.",
            "anual": "Ano civil; soma exige 12 meses válidos distintos.",
            "climatologias": "1981–2010 e 1991–2020 exigem 30 anos completos; std(ddof=1); z-score exige std>0.",
        },
        "linhagem_codigo": "2_INTI/xlegado/code/prepare_chirps.py (consultado, não alterado)",
        "grade_reutilizada": grade,
        "checagens": {
            "linhas_mensais": len(mensal), "linhas_anuais": len(anual), "rasters": len(arquivos),
            "municipios_mensais": int(mensal["codigo_ibge"].nunique()),
            "municipios_anuais": int(anual["codigo_ibge"].nunique()),
            "chaves_unicas": True, "schema_identico_original": True,
            "totais_anuais_com_12_meses": bool(anual["count"].eq(12).all()),
            "normais_com_30_anos": bool(anual[["count_1981_2010", "count_1991_2020"]].eq(30).all().all()),
            "precip_mensal_ausente": int(mensal["precip_mm"].isna().sum()),
            "fracao_pixels_validos_minima": float(mensal["fracao_pixels_validos"].min()),
            "originais_preservados_sha256_antes_depois": hashes_antes,
        },
        "comparacao_malha_2024": {
            "nota": "Diferenças resultam da reextração sobre a malha de 2023; não representam mudanças climáticas.",
            "municipios_diferenca_maior_1e_9mm": int(diferencas.gt(1e-9).sum()),
            "maiores_diferencas_maximas_mm": {str(c): float(v) for c, v in diferencas.head(15).items()},
        },
        "outputs": [{"arquivo": (destino / nome).relative_to(raiz).as_posix(), "sha256": hash_arquivo(destino / nome)}
                    for nome in (MENSAL, ANUAL)],
        "fontes_raster": fontes,
        "ambiente": {"python": sys.version, "pandas": pd.__version__, "numpy": np.__version__,
                     "geopandas": gpd.__version__, "rasterio": rasterio.__version__},
    }
    auditoria.parent.mkdir(parents=True, exist_ok=True)
    auditoria.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": "OK", "mensal": len(mensal), "anual": len(anual), "municipios": 141,
                      "relatorio": auditoria.relative_to(raiz).as_posix()}, ensure_ascii=False))


if __name__ == "__main__":
    main()
