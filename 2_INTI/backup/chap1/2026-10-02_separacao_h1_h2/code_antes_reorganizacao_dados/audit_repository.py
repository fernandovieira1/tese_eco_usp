"""Read-only audit of original repository content; writes evidence under data/catalog.

Run from any directory: python 2_INTI/code/audit_repository.py
No downloads, checkout, commits, or changes to pre-existing files are performed.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
from datetime import datetime, timezone
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "2_INTI/data/catalog"
SOURCE_PATTERN = re.compile(
    r"mapbiomas|chirps|era5|rammt|gaez|boa esperan|earth engine|crosswalk", re.I
)
TEXT_EXTENSIONS = {".tex", ".md", ".txt", ".py", ".r", ".js", ".ipynb", ".json", ".yaml", ".yml", ".bib"}
DATA_EXTENSIONS = {".csv", ".xlsx", ".xls", ".parquet", ".tif", ".tiff", ".nc", ".shp", ".gpkg", ".geojson", ".dta", ".rds"}


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=ROOT)


def textgit(*args: str) -> str:
    return git(*args).decode("utf-8", errors="replace").strip()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_csv(name: str, rows: list[dict]) -> None:
    with (OUT / name).open("w", encoding="utf-8-sig", newline="") as f:
        if rows:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)


def tree_entries(ref: str) -> list[tuple[str, str]]:
    result = []
    for line in git("ls-tree", "-r", "-z", ref).split(b"\0"):
        if not line:
            continue
        info, name = line.split(b"\t", 1)
        mode, kind, oid = info.decode().split()
        if kind == "blob":
            result.append((oid, name.decode("utf-8")))
    return result


def contents(data: bytes, suffix: str) -> str:
    if suffix == ".ipynb":
        n = json.loads(data)
        return "\n".join("".join(c.get("source", [])) for c in n["cells"])
    if suffix in {".zip", ".docx"}:
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            return "\n".join(
                z.read(i).decode("utf-8", errors="replace")
                for i in z.namelist()
                if Path(i).suffix.lower() in TEXT_EXTENSIONS or i == "word/document.xml"
            )
    return data.decode("utf-8", errors="replace")


def audit_workbook() -> dict:
    p = ROOT / "1_SUYANA/data/carbon_emissions.xlsx"
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with zipfile.ZipFile(p) as z:
        ss = ["".join(x.itertext()) for x in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", ns)]
        rows = []
        for row in ET.fromstring(z.read("xl/worksheets/sheet1.xml")).findall(".//m:row", ns):
            values = []
            for c in row.findall("m:c", ns):
                v = c.find("m:v", ns)
                val = v.text if v is not None else ""
                values.append(ss[int(val)] if c.get("t") == "s" and val else val)
            rows.append(values)
    data = rows[1:]
    years = [int(re.sub(r"[^0-9]", "", str(r[0]))) for r in data]
    values = [float(r[1]) for r in data]
    return {"path": p.relative_to(ROOT).as_posix(), "columns": rows[0], "observations": len(data),
            "year_min": min(years), "year_max": max(years), "duplicate_years": len(years) - len(set(years)),
            "missing_cells": sum(v == "" for r in data for v in r), "min": min(values), "max": max(values),
            "unit_as_recorded": rows[0][1], "year_marker": data[0][0],
            "source_identified_in_workbook": False,
            "decision": "Preservar como contexto; nao aproveitar no painel municipal H1/H2."}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    branch = textgit("branch", "--show-current")
    if branch != "main":
        raise RuntimeError("Audit output requires the main branch; no checkout performed.")
    head = textgit("rev-parse", "HEAD")
    baseline = []
    inventory = []
    zip_rows = []
    notebooks = []
    for oid, name in tree_entries(head):
        p = ROOT / name
        data = p.read_bytes()
        baseline.append({"arquivo": name, "bytes": len(data), "sha256": sha256(data), "git_blob_head": oid, "commit_base": head})
        inventory.append({"arquivo": name, "extensao": p.suffix.lower(), "bytes": len(data), "sha256": sha256(data),
                          "origem": "HEAD original", "hits_fontes": ";".join(sorted(set(SOURCE_PATTERN.findall(contents(data, p.suffix.lower()))))) if p.suffix.lower() in TEXT_EXTENSIONS | {".zip", ".docx"} else ""})
        if p.suffix.lower() == ".zip":
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                for member in z.infolist():
                    if member.is_dir():
                        continue
                    payload = z.read(member)
                    zip_rows.append({"arquivo_zip": name, "membro": member.filename, "bytes": len(payload),
                                     "sha256": sha256(payload), "extensao": Path(member.filename).suffix.lower()})
        if p.suffix.lower() == ".ipynb":
            n = json.loads(data)
            notebooks.append({"path": name, "cells": len(n["cells"]), "code_cells": sum(c.get("cell_type") == "code" for c in n["cells"]),
                              "source_code": contents(data, ".ipynb"), "matches": sorted(set(SOURCE_PATTERN.findall(contents(data, ".ipynb"))))})
    baseline_path = OUT / "baseline_repositorio_sha256.csv"
    if baseline_path.exists():
        with baseline_path.open(encoding="utf-8-sig", newline="") as f:
            old = list(csv.DictReader(f))
        if [(r["arquivo"], r["sha256"]) for r in old] != [(r["arquivo"], r["sha256"]) for r in baseline]:
            raise RuntimeError("Original file hashes changed; preserved baseline was not overwritten.")
    else:
        write_csv("baseline_repositorio_sha256.csv", baseline)
    write_csv("inventario_repositorio_original.csv", inventory)
    write_csv("inventario_zip_membros.csv", zip_rows)

    all_objects = {}
    for line in textgit("rev-list", "--objects", "--all").splitlines():
        if " " in line:
            oid, name = line.split(" ", 1)
            all_objects[oid] = name
    fsck = textgit("fsck", "--full", "--no-reflogs")
    dangling_trees = re.findall(r"dangling tree ([a-f0-9]{40})", fsck)
    dangling_inventory = []
    for ref in dangling_trees:
        entries = tree_entries(ref)
        dangling_inventory.append({"tree": ref, "entries": len(entries), "data_or_code_paths": [p for _, p in entries if Path(p).suffix.lower() in DATA_EXTENSIONS | {".ipynb", ".py", ".r", ".js"}]})
        all_objects.update({oid: name for oid, name in entries})
    scans, archive_count, notebook_count = 0, 0, 0
    matches = []
    data_blobs = []
    for oid, name in all_objects.items():
        ext = Path(name).suffix.lower()
        if ext in DATA_EXTENSIONS:
            data_blobs.append({"blob": oid, "path": name})
        if ext not in TEXT_EXTENSIONS | {".zip", ".docx"}:
            continue
        data = git("cat-file", "blob", oid)
        source = contents(data, ext)
        scans += 1
        archive_count += ext == ".zip"
        notebook_count += ext == ".ipynb"
        hits = sorted(set(SOURCE_PATTERN.findall(source)))
        if hits:
            matches.append({"blob": oid, "path": name, "matches": hits})
    audit = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(), "branch": branch, "head": head,
        "refs": textgit("show-ref").splitlines(), "commit_count_main": int(textgit("rev-list", "--count", "main")),
        "commit_count_all_refs": int(textgit("rev-list", "--count", "--all")),
        "commits": textgit("log", "--all", "--format=%H %ad %s", "--date=iso-strict").splitlines(),
        "deleted_files_history": textgit("log", "--all", "--diff-filter=D", "--summary"),
        "fsck": fsck, "dangling_trees": dangling_inventory,
        "tracked_files": len(baseline), "zip_files": len({r["arquivo_zip"] for r in zip_rows}), "zip_members": len(zip_rows),
        "historical_text_code_zip_docx_blobs_scanned": scans, "historical_zip_blobs": archive_count,
        "historical_notebook_blobs": notebook_count, "historical_keyword_matches": matches,
        "historical_data_blobs": data_blobs, "notebooks": notebooks, "existing_workbook": audit_workbook(),
        "scope": "Local refs, original tracked files, reachable historical blobs and dangling trees; no remote fetch or unrelated directories.",
    }
    (OUT / "auditoria_historico_git.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    report = f"""# Auditoria do histórico e dos arquivos originais

## Escopo e resultado

- Branch: `main`; HEAD original: `{head}`.
- {len(baseline)} arquivos originais com SHA-256 preservado em `baseline_repositorio_sha256.csv`.
- {audit['commit_count_all_refs']} commits alcançáveis em todos os refs locais; origem do histórico: fevereiro de 2025.
- {scans} blobs históricos de texto, código, DOCX e ZIP examinados pelo conteúdo, incluindo {archive_count} versões de ZIP e {notebook_count} versões de notebooks.
- {audit['zip_files']} ZIPs atuais e {len(zip_rows)} membros inventariados e lidos; nenhum dataset ou pipeline H1/H2 dentro desses arquivos.
- Duas árvores sem referência de commit examinadas por `git fsck --full --no-reflogs`; contêm versões do mesmo projeto documental, sem dados municipais adicionais.
- Não foi identificado pipeline removido de MapBiomas, CHIRPS, ERA5, PAM/PPM, RAMMT, GAEZ ou harmonização municipal nos objetos locais examinados.
- Nenhum checkout, merge, recuperação destrutiva, download ou modificação de arquivo original foi feito por esta auditoria.

## Evidências aproveitáveis

`2_INTI/chapters/chap1/0_introduction.tex` contém as definições e fontes candidatas de H1/H2. As menções identificadas são documentação metodológica, sem aquisição ou processamento implementado. Preservar integralmente esse texto como referência conceitual.

`1_SUYANA/chapters/qualificacao/qualificacao_fernando.tex` menciona MapBiomas. A imagem `assets/mapa_biomas_mt.png` é uma ilustração; não contém geometrias ou crosswalk que permitam recuperar classificação territorial validada.

Os seis notebooks atuais tratam de emissões globais, gráficos conceituais, simulações e uma comparação de modelos. Nenhum contém chamadas às fontes H1/H2 procuradas. Devem ser preservados, mas não reaproveitados como pipeline empírico municipal. O notebook de emissões usa `pd.read_excel('carbon_emissions.xlsx')`, caminho relativo que não aponta para a pasta `data` quando executado a partir de `code`.

## Única planilha de dados original

`1_SUYANA/data/carbon_emissions.xlsx`: uma aba, 86 observações anuais, 1940–2025, colunas `Characteristic` e `Emissions in billion metric tons`. Não há anos duplicados nem células vazias nos registros. Valor mínimo 4,85 e máximo 38,11 bilhões de toneladas métricas. O ano 2025 contém marcador de nota; sua condição observada/projetada não está documentada na planilha. A fonte original não foi autenticada pelo arquivo. Preservar como dado contextual; não integrar ao painel H1/H2.

## História relevante

- `c73c0fe` (2025-12-11): entrada da planilha e do gráfico de emissões.
- `0c1ab8d` (2026-09-04): separação SUYANA/INTI.
- `b0617bc` (2026-09-21): reorganização de seções e remoção de dois arquivos LaTeX; não removeu dados empíricos.
- `4ee8080` (2026-09-25): reconstrução de H1 no texto.
- `bf2d9cf` (2026-09-26): ajustes após reunião e detalhamento de H1/H2.

## Limites e recuperação

A auditoria cobre o repositório local, seus refs, objetos históricos e ZIPs, inclusive arquivos ocultos no inventário inicial. Ela não confirma a inexistência de trabalho em outros computadores, contas, pastas externas ou branches remotos ainda não conhecidos localmente. Não há componente empírico identificado que exija restauração a partir do histórico. Se surgir um caminho/commit externo adicional, a recuperação deverá ser aditiva e precedida de validação, sem substituir o conteúdo de `main`.

Os resultados detalhados, inclusive código-fonte dos notebooks, listas de blobs, refs, arquivos removidos e planilha, estão em `auditoria_historico_git.json`. Para verificar preservação dos originais, executar novamente `python 2_INTI/code/audit_repository.py`; o script recusa substituir o baseline quando seus hashes mudam.
"""
    (OUT / "auditoria_historico_repositorio.md").write_text(report, encoding="utf-8")
    print(json.dumps({k: audit[k] for k in ["branch", "head", "tracked_files", "zip_files", "zip_members", "historical_text_code_zip_docx_blobs_scanned", "historical_zip_blobs", "historical_notebook_blobs"]}))
    print(json.dumps(audit["existing_workbook"]))


if __name__ == "__main__":
    main()
