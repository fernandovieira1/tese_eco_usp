"""Public-source acquisition with immutable raw files and a JSONL audit trail."""
from pathlib import Path
import hashlib
import json
from datetime import datetime, timezone
import requests

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / '2_INTI' / 'data'

def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def fetch(url, relative, source, version='', manifest='acquisition_core.jsonl', timeout=90):
    """Never overwrite an existing raw file. Save failures as evidence, not data."""
    dest = DATA / relative
    if not dest.resolve().is_relative_to(DATA.resolve()):
        raise ValueError('Destination outside 2_INTI/data')
    log = DATA / 'catalog' / manifest
    log.parent.mkdir(parents=True, exist_ok=True)
    record = dict(url=url, arquivo_local=dest.relative_to(ROOT).as_posix(), fonte=source,
                  versao=version, data_acesso=datetime.now(timezone.utc).isoformat())
    if dest.exists():
        entries = [json.loads(x) for x in log.read_text(encoding='utf-8').splitlines()] if log.exists() else []
        previous = [x for x in entries if x.get('arquivo_local') == record['arquivo_local'] and x.get('sha256')]
        digest = sha256(dest)
        if not previous or previous[-1]['sha256'] != digest or previous[-1]['url'] != url:
            raise ValueError(f'Existing file without matching provenance: {dest}')
        return dest
    try:
        response = requests.get(url, timeout=timeout, stream=True,
                                headers={'User-Agent': 'INTI-research-data-audit/1.0'})
        record.update(http_status=response.status_code, url_final=response.url,
                      content_type=response.headers.get('Content-Type', ''),
                      last_modified=response.headers.get('Last-Modified', ''))
        response.raise_for_status()
        dest.parent.mkdir(parents=True, exist_ok=True)
        part = dest.with_name(dest.name + '.part')
        with part.open('xb') as f:
            for chunk in response.iter_content(1024 * 1024):
                f.write(chunk)
        part.rename(dest)
        record.update(status='BAIXADO', bytes=dest.stat().st_size, sha256=sha256(dest))
    except Exception as exc:
        record.update(status='FALHA', erro=str(exc))
        raise
    finally:
        with log.open('a', encoding='utf-8') as f:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    return dest

def write_json(relative, value):
    p = DATA / relative
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    return p
