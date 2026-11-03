"""Aquisição reproduzível das transições REAIS da Coleção 10.1.

Exemplo (PowerShell, dentro de AED/pt):
    python obter_transicoes_mapbiomas.py --executar-gee --projeto ID_DO_PROJETO

Requer earthengine-api autenticada e projeto GEE habilitado. Não autentica nem
publica arquivos remotamente por conta própria. Consulta o asset público e salva
os resultados locais por município/ano; uma interrupção permite retomar.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from urllib.request import Request, urlopen

import pandas as pd
import numpy as np

from harmonizacao_terra import FOLHAS, NATIVAS, construir_transicoes


ROOT = Path(__file__).resolve().parents[6]
ASSET = "projects/mapbiomas-public/assets/brazil/lulc/collection10_1/mapbiomas_brazil_collection10_1_coverage_v1"
MALHA = ROOT / "2_INTI/xdata/chap1/raw/vector/ibge/MT_Municipios_2023.zip"
CACHE = ROOT / "2_INTI/xdata/chap1/raw/tabular/mapbiomas/transicoes_col10_1_141/v2_cobertura_explicita"
SAIDA = ROOT / "2_INTI/xdata/chap1/processed/harmonizacao"
AUDIT = ROOT / "2_INTI/audit/aed_chap1_20261013/harmonizacao"


def _sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def diagnosticar_fontes():
    """Consulta catálogos pequenos; não baixa rasters de outra coleção."""
    AUDIT.mkdir(parents=True, exist_ok=True)
    urls = {
        "catalogo_gcs_10": "https://storage.googleapis.com/storage/v1/b/mapbiomas-public/o?maxResults=1000&prefix=initiatives/brasil/collection_10/lulc/coverage/",
        "catalogo_gcs_brasil": "https://storage.googleapis.com/storage/v1/b/mapbiomas-public/o?maxResults=1000&delimiter=/&prefix=initiatives/brasil/",
        "catalogo_temas_plataforma": "https://prd.plataforma.mapbiomas.org/api/v1/brazil/themes",
        "catalogo_territorios_plataforma": "https://prd.plataforma.mapbiomas.org/api/v1/brazil/territories/categories",
    }
    report = {"asset_necessario": ASSET, "fontes": {}}
    for name, url in urls.items():
        try:
            with urlopen(Request(url, headers={"tenant-id": "mapbiomas"}), timeout=30) as response:
                data = response.read()
            target = AUDIT / f"{name}.json"
            target.write_bytes(data)
            report["fontes"][name] = {"url": url, "bytes": len(data), "sha256": _sha(target), "arquivo": str(target)}
        except Exception as exc:
            report["fontes"][name] = {"url": url, "erro": str(exc)}
    report["decisao"] = "Usar somente coleção10.1 e malha2023; metadados de10/11 não autorizam substituição."
    (AUDIT / "diagnostico_fontes_transicoes.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def tabelas_do_resultado(resultado):
    """Traduz a matriz devolvida pelo GEE sem converter cobertura ausente em zero."""
    request = resultado["requisicao"]
    properties = resultado["resultado"]
    required = ["area_total_ha", "area_valida_par_ha", "area_nao_valida_par_ha", "nativa_inicial_ha", "groups"]
    if any(k not in properties or properties[k] is None for k in required):
        raise ValueError("Resposta GEE sem cobertura ou sem matriz completa.")
    common = {"codigo_ibge": str(request["codigo_ibge"]), "ano": int(request["ano"]), "colecao": "10.1",
              "malha": "IBGE_MT_2023_141", "mascara_id": request["mascara_id"]}
    rows = []
    for group in properties["groups"]:
        code = int(group["transition"])
        rows.append({**common, "classe_origem": code // 100, "classe_destino": code % 100, "area_ha": group["sum"]})
    coverage = {**common, **{k: properties[k] for k in required if k != "groups"}}
    for key in required[:-1]:
        if not np.isfinite(coverage[key]) or coverage[key] < 0:
            raise ValueError(f"Área inválida na resposta: {key}.")
    if coverage["area_total_ha"] <= 0:
        raise ValueError("A área municipal deve ser positiva.")
    # Medimos a área inválida diretamente. Subtrair duas somas grandes pode
    # produzir alguns m² de erro numérico mesmo sem qualquer pixel ausente.
    if not np.isclose(coverage["area_valida_par_ha"] + coverage["area_nao_valida_par_ha"],
                      coverage["area_total_ha"], rtol=1e-8, atol=1e-4):
        raise ValueError("Áreas válida/inválida não recompõem a área municipal.")
    coverage["cobertura_completa"] = coverage["area_nao_valida_par_ha"] == 0
    coverage["fracao_area_valida_par"] = coverage["area_valida_par_ha"] / coverage["area_total_ha"]
    return pd.DataFrame(rows, columns=list(common) + ["classe_origem", "classe_destino", "area_ha"]), pd.DataFrame([coverage])


def _inicializar_worker(projeto, geometrias, polygon_sha):
    """Cada processo possui seu próprio cliente HTTP, sem compartilhar tokens por IPC."""
    import ee
    global _IMAGE, _GEOMETRIAS, _POLYGON_SHA, _GRAFOS
    ee.Initialize(project=projeto)
    _IMAGE = ee.Image(ASSET)
    _GEOMETRIAS, _POLYGON_SHA, _GRAFOS = geometrias, polygon_sha, {}


def _coletar_par(tarefa):
    import ee
    codigo, ano, projection = tarefa
    valid_ids = sorted(FOLHAS - {27})
    mask_id = hashlib.sha256(f"{ASSET}|{_POLYGON_SHA}|{codigo}|{ano - 1}|{ano}|folhas_validas|v2".encode()).hexdigest()
    req = {"asset": ASSET, "codigo_ibge": codigo, "ano": ano, "malha_sha256": _POLYGON_SHA,
           "mascara_id": mask_id, "grade": projection, "classes_validas": valid_ids,
           "protocolo": "v2_cobertura_explicita"}
    target = CACHE / f"{codigo}_{ano}.json"
    if target.exists():
        result = json.loads(target.read_text(encoding="utf-8"))
        if result["requisicao"] != req:
            raise ValueError(f"Cache incompatível; preservar arquivo e escolher novo destino: {target}")
        return result
    if ano not in _GRAFOS:
        previous, current = _IMAGE.select(f"classification_{ano - 1}"), _IMAGE.select(f"classification_{ano}")
        valid = previous.remap(valid_ids, [1] * len(valid_ids), 0).eq(1).And(
            current.remap(valid_ids, [1] * len(valid_ids), 0).eq(1))
        code = previous.multiply(100).add(current).rename("transition").updateMask(valid).toInt16()
        area = ee.Image.pixelArea().divide(10000)
        native = previous.remap(sorted(NATIVAS), [1] * len(NATIVAS), 0).eq(1)
        measures = area.rename("area_total_ha").addBands(area.updateMask(valid).rename("area_valida_par_ha"))
        measures = measures.addBands(area.updateMask(valid).multiply(native).rename("nativa_inicial_ha"))
        # A área sem classe nos dois anos é calculada, não inferida por subtração.
        invalid = valid.unmask(0, sameFootprint=False).Not()
        measures = measures.addBands(area.multiply(invalid).rename("area_nao_valida_par_ha"))
        _GRAFOS[ano] = (area.updateMask(valid).addBands(code), measures)
    transition_image, measures = _GRAFOS[ano]
    geometry = ee.Geometry(_GEOMETRIAS[codigo], proj="EPSG:4326", geodesic=False)
    params = {"geometry": geometry, "crs": projection["crs"], "crsTransform": projection["transform"],
              "maxPixels": 10_000_000_000, "tileScale": 4}
    matrix = transition_image.reduceRegion(reducer=ee.Reducer.sum().group(groupField=1, groupName="transition"), **params)
    totals = measures.reduceRegion(reducer=ee.Reducer.sum(), **params)
    query = ee.Dictionary(totals).combine(matrix)
    for tentativa in range(3):
        try:
            properties = query.getInfo()
            break
        except ee.EEException as exc:
            transient = any(t in str(exc).lower() for t in ["timed out", "internal error", "temporarily", "concurrent aggregations", "429", "503"])
            if not transient or tentativa == 2:
                raise
            time.sleep(5 * 2 ** tentativa)
    result = {"requisicao": req, "resultado": properties}
    # Cache novo por protocolo e par: nenhum bruto anterior é sobrescrito.
    with target.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
    return result


def coletar_gee(projeto, anos=range(2001, 2025), codigos=None, workers=1):
    """Calcula pares t-1/t na grade nativa do raster e nos 141 polígonos originais.

    Não usa bestEffort nem escala mais grossa. As áreas vêm de pixelArea, porque
    30 m nominais não autorizam supor 900 m² em uma grade de latitude/longitude.
    """
    try:
        import ee
    except ImportError as exc:
        raise RuntimeError("Instale earthengine-api no ambiente do projeto; esta etapa precisa de autenticação GEE.") from exc
    import geopandas as gpd
    from shapely.geometry import mapping

    anos = list(anos)
    if not isinstance(workers, int) or not 1 <= workers <= 8:
        raise ValueError("Usar de 1 a 8 processos; reduzir em caso de limites do serviço.")
    ee.Initialize(project=projeto)
    image = ee.Image(ASSET)
    asset_metadata = ee.data.getAsset(ASSET)
    municipalities = gpd.read_file(f"zip://{MALHA}").to_crs(4326)
    municipalities["codigo_ibge"] = municipalities["CD_MUN"].astype(str)
    if len(municipalities) != 141 or municipalities.codigo_ibge.nunique() != 141:
        raise ValueError("A malha de origem deve conter exatamente os 141 municípios de 2023.")
    if codigos:
        municipalities = municipalities.loc[municipalities.codigo_ibge.isin([str(x) for x in codigos])]
        if len(municipalities) != len(set(codigos)):
            raise ValueError("Código solicitado não encontrado na malha de referência.")
    CACHE.mkdir(parents=True, exist_ok=True)
    AUDIT.mkdir(parents=True, exist_ok=True)
    metadata_path = AUDIT / "asset_mapbiomas_10_1.json"
    metadata_path.write_text(json.dumps(asset_metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    polygon_sha = _sha(MALHA)
    geometrias = {row.codigo_ibge: mapping(row.geometry) for row in municipalities.itertuples()}
    transitions, coverage = [], []
    tarefas = []
    projections = ee.Dictionary({str(a): image.select(f"classification_{a}").projection()
                                 for a in sorted(set(anos) | {a - 1 for a in anos})}).getInfo()
    for ano in anos:
        projection = projections[str(ano - 1)]
        if projection != projections[str(ano)]:
            raise ValueError("As duas bandas não possuem a mesma grade de pixels.")
        tarefas.extend((codigo, ano, projection) for codigo in municipalities.codigo_ibge)

    def acumular(result):
            pair, cov = tabelas_do_resultado(result)
            construir_transicoes(pair, cov)  # Valida conservação antes de acumular.
            transitions.append(pair)
            coverage.append(cov)
            req = result["requisicao"]
            print(f"{len(coverage)}/{len(tarefas)} {req['codigo_ibge']} {req['ano'] - 1}->{req['ano']}: validado", flush=True)

    if workers == 1:
        _inicializar_worker(projeto, geometrias, polygon_sha)
        for tarefa in tarefas:
            acumular(_coletar_par(tarefa))
    else:
        executor = ProcessPoolExecutor(max_workers=workers, initializer=_inicializar_worker,
                                       initargs=(projeto, geometrias, polygon_sha))
        try:
            futures = [executor.submit(_coletar_par, tarefa) for tarefa in tarefas]
            for future in as_completed(futures):
                acumular(future.result())
        finally:
            executor.shutdown(wait=True, cancel_futures=True)
    matrix = pd.concat(transitions, ignore_index=True).sort_values(["codigo_ibge", "ano", "classe_origem", "classe_destino"])
    cov = pd.concat(coverage, ignore_index=True).sort_values(["codigo_ibge", "ano"])
    result = construir_transicoes(matrix, cov)
    SAIDA.mkdir(parents=True, exist_ok=True)
    suffix = "" if codigos is None and list(anos) == list(range(2001, 2025)) else "_parcial"
    matrix.to_csv(SAIDA / f"transicoes_reais_10_1_141{suffix}.csv", index=False)
    cov.to_csv(SAIDA / f"cobertura_transicoes_10_1_141{suffix}.csv", index=False)
    result.to_csv(SAIDA / f"conversao_taxas_10_1_141{suffix}.csv", index=False)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executar-gee", action="store_true")
    parser.add_argument("--projeto", help="ID de projeto GEE habilitado; nenhuma credencial é gravada pelo script.")
    parser.add_argument("--ano-inicio", type=int, default=2001)
    parser.add_argument("--ano-fim", type=int, default=2024)
    parser.add_argument("--codigo", action="append", help="Opcional: execução parcial de verificação.")
    parser.add_argument("--workers", type=int, default=1, help="Processos independentes, de 1 a 8; padrão sequencial.")
    args = parser.parse_args()
    if args.executar_gee:
        if not args.projeto:
            parser.error("--executar-gee exige --projeto, além da autenticação prévia.")
        if not 2001 <= args.ano_inicio <= args.ano_fim <= 2024:
            parser.error("O painel autorizado é 2001–2024.")
        coletar_gee(args.projeto, range(args.ano_inicio, args.ano_fim + 1), args.codigo, args.workers)
    else:
        print(json.dumps(diagnosticar_fontes(), ensure_ascii=False, indent=2))
