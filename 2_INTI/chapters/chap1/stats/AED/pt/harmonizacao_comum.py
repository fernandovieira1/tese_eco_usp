"""Leitura, calendário e exportação dos derivados; as fontes são somente leitura."""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
from pathlib import Path

import numpy as np
import pandas as pd

from aed_support import aplicar_referencia_141, ler_csv, limpar_base


PARAMETROS = {
    'periodo_painel': [2001, 2024],
    'territorio': 'IBGE_2023_141',
    'janela_precos': 'ano civil anterior (t-1)',
    'janela_pam': [1991, 2000],
    'minimo_anos_pam': 7,
    'referencia_chuva_principal': [1981, 2000],
    'referencias_chuva_alternativas': [[1981, 2010], [1991, 2020]],
    'interpretacao': 'variaveis candidatas; nao implica identificacao causal',
}


def hash_arquivo(caminho):
    h = hashlib.sha256()
    with Path(caminho).open('rb') as fonte:
        for bloco in iter(lambda: fonte.read(8 * 1024 * 1024), b''):
            h.update(bloco)
    return h.hexdigest()


def cadastro_municipios(raiz):
    p = Path(raiz) / '2_INTI/xdata/chap1/processed/territorio_141/municipios_referencia.json'
    cadastro = pd.DataFrame(json.loads(p.read_text(encoding='utf-8')))
    cadastro['codigo_ibge'] = cadastro['codigo_ibge'].astype('string')
    if cadastro['codigo_ibge'].duplicated().any() or len(cadastro) != 141:
        raise ValueError('A referencia deve conter 141 codigos distintos.')
    return cadastro


def grade_painel(raiz):
    codigos = cadastro_municipios(raiz)['codigo_ibge']
    return pd.MultiIndex.from_product([codigos, range(2001, 2025)],
                                     names=['codigo_ibge', 'ano']).to_frame(index=False)


def carregar_fontes(nome, raiz):
    """Lê os caminhos do TXT e aplica o mesmo tratamento territorial da fase 2."""
    from gerar_notebooks import extrair_blocos
    raiz = Path(raiz)
    txt = raiz / '2_INTI/chapters/chap1/stats/HIPOTESES TESE - CHAP1.txt'
    blocos, _ = extrair_blocos(txt)
    bloco = next(b for b in blocos if b['nome'] == nome)
    # Os diagnósticos completos já aparecem nas fases 1–3 dos notebooks.
    with contextlib.redirect_stdout(io.StringIO()):
        brutas = []
        for caminho in bloco['caminhos']:
            ids = set(brutas[0]['SEQ_TAD'].dropna()) if brutas and 'coordenadas' in caminho else None
            brutas.append(ler_csv(raiz / caminho.replace('\\', '/'), ids_embargo=ids))
        limpas = [limpar_base(b) for b in brutas]
        bases, _ = aplicar_referencia_141(limpas, bloco['caminhos'], raiz)
    return bases


def recortar(base):
    return base.loc[base['ano'].between(2001, 2024)].copy() if 'ano' in base else base.copy()


def defasar_ano(base, colunas, grupos=('codigo_ibge',), defasagem=1):
    """Liga o ano exato: uma lacuna nunca faz t-2 passar por t-1."""
    chaves = list(grupos) + ['ano']
    if base[chaves].isna().any().any() or base.duplicated(chaves).any():
        raise ValueError(f'Chaves ausentes ou repetidas: {chaves}')
    anterior = base[chaves + list(colunas)].copy()
    anterior['ano'] = anterior['ano'] + defasagem
    anterior = anterior.rename(columns={c: f'{c}_lag{defasagem}' for c in colunas})
    return base.merge(anterior, on=chaves, how='left', validate='one_to_one')


def validar_tabela(base, chaves):
    if base[chaves].isna().any().any() or base.duplicated(chaves).any():
        raise ValueError(f'Tabela nao unica nas chaves: {chaves}')
    numeros = base.select_dtypes(include='number')
    if np.isinf(numeros.to_numpy(dtype=float, na_value=np.nan)).any():
        raise ValueError('Infinito encontrado; verificar denominadores e logaritmos.')


def resumo_cobertura(tabelas):
    linhas = []
    for nome, base in tabelas.items():
        for coluna in base.columns:
            linhas.append({'tabela': nome, 'coluna': coluna, 'linhas': len(base),
                           'valores_presentes': int(base[coluna].notna().sum()),
                           'ausentes': int(base[coluna].isna().sum()),
                           'tipo': str(base[coluna].dtype)})
    return pd.DataFrame(linhas)


def exportar_resultado(resultado, raiz):
    """Cada notebook escreve apenas em sua pasta de derivados, nunca na origem."""
    pasta = Path(raiz) / '2_INTI/xdata/chap1/processed/harmonizacao' / resultado['nome']
    pasta.mkdir(parents=True, exist_ok=True)
    arquivos = {}
    for nome, tabela in resultado['tabelas'].items():
        caminho = pasta / f'{nome}.csv'
        tabela.to_csv(caminho, index=False, encoding='utf-8', na_rep='')
        arquivos[nome] = {'arquivo': str(caminho.relative_to(raiz)),
                         'sha256': hash_arquivo(caminho), 'linhas': len(tabela),
                         'colunas': list(tabela.columns),
                         'metadados': tabela.attrs.get('metadados', tabela.attrs)}
    cobertura = resumo_cobertura(resultado['tabelas'])
    cobertura.to_csv(pasta / 'cobertura.csv', index=False, encoding='utf-8')
    dicionario = pd.DataFrame(resultado['dicionario'])
    dicionario.to_csv(pasta / 'dicionario.csv', index=False, encoding='utf-8')
    manifesto = {k: v for k, v in resultado.items() if k != 'tabelas'}
    manifesto['arquivos'] = arquivos
    manifesto['parametros_comuns'] = PARAMETROS
    # Sem substituir falhas por zero; cada estado possui uma descrição explícita.
    (pasta / 'manifesto.json').write_text(json.dumps(manifesto, ensure_ascii=False, indent=2,
                                                   default=str, allow_nan=False), encoding='utf-8')
    return pasta
