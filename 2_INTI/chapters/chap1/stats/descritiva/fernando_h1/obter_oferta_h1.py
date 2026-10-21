"""Adquire abate estadual e exportacoes por domicilio fiscal para a descritiva H1.

Executar da raiz: python 2_INTI/chapters/chap1/stats/descritiva/obter_oferta_h1.py
Respostas existentes sao reutilizadas; os dados brutos nunca sao sobrescritos.
"""

import csv
import gzip
import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[5]
DATA = ROOT / "2_INTI/xdata/chap1"
RAW = DATA / "raw/tabular/oferta_descritiva_20261020"
OUT = DATA / "processed/harmonizacao/oferta_descritiva"
CATALOG = ROOT / "2_INTI/xdata/catalog/aquisicao_oferta_descritiva_20261020.json"
COMEX = "https://api-comexstat.mdic.gov.br/cities"
YEARS = range(2000, 2025)
PRODUCTS = {"1201": "soja", "1005": "milho", "0201": "carne_bovina", "0202": "carne_bovina"}


def acquire(name, url, payload=None):
    path = RAW / name
    if path.exists():
        content = path.read_bytes()
        meta = json.loads(path.with_suffix(".proveniencia.json").read_text(encoding="utf-8"))
        if meta["url"] != url or meta["consulta"] != payload:
            raise ValueError(f"Consulta difere do arquivo preservado: {path}")
        if hashlib.sha256(content).hexdigest() != meta["sha256"]:
            raise ValueError(f"Hash do arquivo bruto diverge: {path}")
    else:
        request = Request(url, data=json.dumps(payload).encode() if payload else None,
                          headers={"Content-Type": "application/json", "User-Agent": "Tese-H1/1.0"})
        with urlopen(request, timeout=60) as response:
            content = response.read()
            if content[:2] == b"\x1f\x8b":
                content = gzip.decompress(content)
            json.loads(content)
            meta = {"url": url, "consulta": payload, "http_status": response.status,
                    "acesso_utc": datetime.now(timezone.utc).isoformat(),
                    "sha256": hashlib.sha256(content).hexdigest()}
        path.write_bytes(content)
        path.with_suffix(".proveniencia.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return json.loads(content), meta


def write_csv(name, rows):
    with (OUT / name).open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def comex_list(response):
    if response.get("success") is not True:
        raise ValueError(f"Consulta Comex sem sucesso: {response.get('message')}")
    rows = response["data"]["list"]
    if not rows or len(rows) >= 150000:
        raise ValueError("Consulta Comex vazia ou potencialmente truncada.")
    return rows


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    sources = []
    ibge = "https://servicodados.ibge.gov.br/api/v3/agregados/1092"
    metadata, meta = acquire("ibge_abate_metadados.json", ibge + "/metadados")
    sources.append(meta)
    if set(metadata["nivelTerritorial"]["Administrativo"]) != {"N1", "N3"}:
        raise ValueError("Rever os niveis territoriais do abate.")
    url = (ibge + "/periodos/200001-202404/variaveis/284|285?localidades=N3[51]"
           "&classificacao=12716[115236]|18[992]|12529[118225]")
    slaughter, meta = acquire("ibge_abate_mt_2000_2024.json", url)
    sources.append(meta)
    by_variable = {item["id"]: item for item in slaughter}
    expected_quarters = {f"{year}{quarter:02}" for year in YEARS for quarter in range(1, 5)}
    annual = {year: {"ano": year} for year in YEARS}
    for variable, name, unit in [("284", "abate_bovinos_cabecas_mt", "Cabeças"),
                                 ("285", "peso_carcacas_bovinas_kg_mt", "Quilogramas")]:
        item = by_variable[variable]
        assert item["unidade"] == unit
        assert len(item["resultados"]) == 1
        result = item["resultados"][0]
        assert {c["id"]: set(c["categoria"]) for c in result["classificacoes"]} == {
            "12716": {"115236"}, "18": {"992"}, "12529": {"118225"}}
        assert len(result["series"]) == 1
        series = result["series"][0]
        assert series["localidade"]["id"] == "51"
        assert series["localidade"]["nivel"]["id"] == "N3"
        assert set(series["serie"]) == expected_quarters
        for year in YEARS:
            values = [int(series["serie"][f"{year}{quarter:02}"]) for quarter in range(1, 5)]
            assert all(value >= 0 for value in values)
            annual[year][name] = sum(values)

    states, meta = acquire("comex_ufs.json", COMEX + "/filters/state?language=pt")
    sources.append(meta)
    # Comex usa codigo 52 para MT neste filtro; o codigo IBGE da UF e 51.
    assert next(item for item in states["data"][0] if item["text"] == "Mato Grosso")["id"] == "52"
    cities, meta = acquire("comex_municipios.json", COMEX + "/filters/city?language=pt")
    sources.append(meta)
    city_codes = {item["text"]: str(item["id"]) for item in cities["data"][0]}
    headings, meta = acquire("comex_sh4.json", COMEX + "/filters/heading?language=pt")
    sources.append(meta)
    assert set(PRODUCTS).issubset({item["id"] for item in headings["data"][0]})
    payload = {"flow": "export", "monthDetail": False,
               "period": {"from": "2000-01", "to": "2024-12"},
               "filters": [{"filter": "state", "values": [52]},
                           {"filter": "heading", "values": list(PRODUCTS)}],
               "details": ["city", "heading"], "metrics": ["metricFOB", "metricKG"]}
    response, meta = acquire("comex_exportacoes_mt_municipio_sh4_2000_2024.json",
                             COMEX + "?language=pt", payload)
    sources.append(meta)
    export_rows = comex_list(response)
    totals_query = dict(payload, details=["heading"])
    totals, meta = acquire("comex_exportacoes_mt_totais_sh4_2000_2024.json",
                           COMEX + "?language=pt", totals_query)
    sources.append(meta)
    reference = {(int(row["year"]), row["headingCode"]):
                 (int(row["metricFOB"]), int(row["metricKG"])) for row in comex_list(totals)}
    summed = defaultdict(lambda: [0, 0])
    exports = defaultdict(lambda: [0, 0])
    seen = set()
    cadastro = json.loads((DATA / "processed/territorio_141/municipios_referencia.json").read_text(encoding="utf-8"))
    valid_codes = {str(row["codigo_ibge"]) for row in cadastro}
    for row in export_rows:
        year, heading = int(row["year"]), row["headingCode"]
        code = city_codes[row["noMunMinsgUf"]]
        key = (code, year, heading)
        assert year in YEARS and heading in PRODUCTS and code in valid_codes
        assert key not in seen
        seen.add(key)
        fob, kg = int(row["metricFOB"]), int(row["metricKG"])
        assert fob >= 0 and kg >= 0
        summed[(year, heading)][0] += fob
        summed[(year, heading)][1] += kg
        exports[(code, year, PRODUCTS[heading])][0] += fob
        exports[(code, year, PRODUCTS[heading])][1] += kg
    assert {key: tuple(value) for key, value in summed.items()} == reference
    assert {year for _, year, _ in exports} == set(YEARS)
    processed = [{"codigo_ibge": code, "ano": year, "produto": product,
                  "exportacao_fob_usd_nominal_domicilio": value[0],
                  "exportacao_kg_liquido_domicilio": value[1]}
                 for (code, year, product), value in sorted(exports.items())]
    write_csv("abate_mt_anual.csv", list(annual.values()))
    write_csv("exportacoes_municipais_anual.csv", processed)
    manifest = {"fontes": sources, "periodo": [2000, 2024], "sh4": PRODUCTS,
                "validacoes": {"trimestres_por_variavel": len(expected_quarters),
                                "linhas_comex": len(export_rows), "totais_sh4_conferidos": len(reference),
                                "linhas_exportacao_processadas": len(processed)},
                "limites": ["Abate: estabelecimentos sob inspecao, UF MT; nao representa origem municipal dos animais.",
                            "Peso de carcacas nao e peso de carne desossada nem oferta total de carne.",
                            "Exportacao: domicilio fiscal do exportador; nao e producao ou origem municipal.",
                            "FOB em dolares correntes, sem deflacao; SH4 1201, 1005 e 0201+0202.",
                            "Ausencia de registro Comex sera mantida como NA, sem imputar zero."]}
    (OUT / "manifesto.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    CATALOG.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest["validacoes"], ensure_ascii=False))


if __name__ == "__main__":
    main()
