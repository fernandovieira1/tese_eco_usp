"""Reconstrói derivados espaciais na referência fixa IBGE 2023 (141 municípios)."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import urllib.request

from aed_support import encontrar_raiz

FONTES = [
    'h1__suitability_yield__gaez_v4_6190__candidatos.csv',
    'h2__biome_share__ibge2019_malha2024__candidato.csv',
    'topography__copdem90__municipio_candidato.csv',
    'h2__precip_mm__chirps_v2__mensal_candidato.csv',
    'h2__precip_anomaly__chirps_v2__ano_civil_candidatos.csv',
    'h1__autos_ibama__geocodificacao_candidata.csv',
    'h1__autos_ibama__espacial_municipio_anual_candidato.csv',
]
URL_MALHA = 'https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2023/UFs/MT/MT_Municipios_2023.zip'


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def registrar_manifesto(raiz):
    dados = raiz / '2_INTI/xdata/chap1'
    destino = dados / 'processed/territorio_141'
    malha = dados / 'raw/vector/ibge/MT_Municipios_2023.zip'
    saidas = {}
    for nome in FONTES:
        origem, derivado = dados / 'processed/tabular' / nome, destino / nome
        if not derivado.exists():
            raise FileNotFoundError(derivado)
        saidas[nome] = {'origem_sha256': sha(origem), 'derivado_sha256': sha(derivado)}
    manifesto = {'referencia': 'IBGE_2023_141', 'n_municipios': 141,
        'malha_url': URL_MALHA, 'malha_sha256': sha(malha),
        'metodo': 'Reextração de rasters e reclassificação de pontos na malha 2023 completa; não soma índices nem faz rateio uniforme.',
        'limite': 'Referência fixa 2023 também incorpora diferenças de limites além de Boa Esperança. Não certifica toda a harmonização histórica de séries administrativas.',
        'origem_boa_esperanca': 'Sorriso e Nova Ubiratã na criação legal; a sobreposição cartográfica com 2023 também inclui parcelas de Vera e Paranatinga.',
        'fonte_ibge': 'https://educa.ibge.gov.br/criancas/voce-sabia/22741-novo-municipio.html',
        'arquivos': saidas}
    (destino / 'manifesto141.json').write_text(json.dumps(manifesto, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Manifesto territorial validado:', destino / 'manifesto141.json')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--somente-manifesto', action='store_true', help='Conferir saídas já reconstruídas, sem recalcular.')
    args = p.parse_args()
    raiz = encontrar_raiz()
    malha = raiz / '2_INTI/xdata/chap1/raw/vector/ibge/MT_Municipios_2023.zip'
    if not malha.exists():
        malha.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(URL_MALHA, timeout=120) as r, malha.open('xb') as f:
            while b := r.read(1024 * 1024):
                f.write(b)
    if not args.somente_manifesto:
        pasta = Path(__file__).resolve().parent
        for script in ['reconstruir_141_estaticas.py', 'reconstruir_141_chuva.py', 'reconstruir_141_ibama.py']:
            subprocess.run([sys.executable, str(pasta / script)], check=True)
    registrar_manifesto(raiz)


if __name__ == '__main__':
    main()
