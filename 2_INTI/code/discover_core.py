"""Fetch official metadata before parameterizing empirical data requests."""
import json
from data_common import fetch

TASKS = [
 ('https://servicodados.ibge.gov.br/api/v3/agregados/1612/metadados', 'raw/tabular/ibge/pam1612_metadata.json', 'IBGE/PAM', 'API v3'),
 ('https://servicodados.ibge.gov.br/api/v3/agregados/3939/metadados', 'raw/tabular/ibge/ppm3939_metadata.json', 'IBGE/PPM', 'API v3'),
 ('https://servicodados.ibge.gov.br/api/v1/localidades/estados/51/municipios', 'raw/tabular/ibge/municipios_mt_consulta20260928.json', 'IBGE', 'API v1; cadastro corrente'),
 ('https://data.mapbiomas.org/api/datasets/:persistentId/?persistentId=doi:10.58053/MapBiomas/SJZOLT', 'raw/tabular/mapbiomas/collection10_1_metadata.json', 'MapBiomas Brasil', '10.1; Dataverse V1'),
 ('https://brasil.mapbiomas.org/downloads/estatisticas/', 'raw/tabular/mapbiomas/statistics_page_20260928.html', 'MapBiomas Brasil', 'Página consultada 2026-09-28'),
 ('https://geoftp.ibge.gov.br/informacoes_ambientais/estudos_ambientais/biomas/vetores/', 'raw/vector/ibge/biomes_directory.html', 'IBGE', 'Diretório'),
 ('https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2024/UFs/MT/MT_Municipios_2024.zip', 'raw/vector/ibge/MT_Municipios_2024.zip', 'IBGE', 'Malha 2024; alternativa territorial'),
]

if __name__ == '__main__':
    for task in TASKS:
        try:
            p = fetch(*task)
            print(p.name, p.stat().st_size, flush=True)
        except Exception as exc:
            print(task[1], type(exc).__name__, str(exc)[:250], flush=True)
