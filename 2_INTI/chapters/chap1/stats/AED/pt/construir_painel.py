"""Executa as derivações e reúne as candidatas em uma grade municipal anual.

Uso: python construir_painel.py
O arquivo é candidato: ter uma coluna não autoriza usá-la como controle causal.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from aed_support import encontrar_raiz
from gerar_notebooks import DICIONARIO, extrair_blocos
from harmonizacao import Contexto, construir_variavel
from harmonizacao_comum import exportar_resultado, grade_painel, hash_arquivo, recortar, validar_tabela


def abrir_colunas(base, indice, categorias, valores):
    """Pivô sem média: duplicatas são erros, nunca novas observações."""
    validar_tabela(base, indice + categorias)
    largo = base.pivot(index=indice, columns=categorias, values=valores)
    largo.columns = ['__'.join(str(x) for x in c) if isinstance(c, tuple) else str(c) for c in largo.columns]
    return largo.reset_index()


def juntar(painel, tabela, chaves):
    validar_tabela(tabela, chaves)
    comuns = (set(painel.columns) & set(tabela.columns)) - set(chaves)
    if comuns:
        raise ValueError(f'Colunas já presentes; resolver significado antes de juntar: {sorted(comuns)}')
    anterior = len(painel)
    unido = painel.merge(tabela, on=chaves, how='left', validate='many_to_one')
    if len(unido) != anterior:
        raise AssertionError('Junção multiplicou observações.')
    return unido


def preparar_y_painel(taxas):
    """Carrega os dois destinos junto com o denominador e a cobertura de cada par."""
    chaves = ['codigo_ibge', 'ano']
    largo = abrir_colunas(taxas, chaves, ['destino'], ['conversao_ha', 'taxa_conversao'])
    campos = ['colecao', 'malha', 'mascara_id', 'area_total_ha', 'area_valida_par_ha',
              'area_nao_valida_par_ha', 'nativa_inicial_ha', 'cobertura_completa',
              'fracao_area_valida_par', 'flag_denominador_zero', 'flag_denominador_ausente']
    cobertura = taxas[chaves + campos].drop_duplicates()
    validar_tabela(cobertura, chaves)  # Os dois destinos devem usar a mesma cobertura.
    cobertura = cobertura.rename(columns={c: 'y_' + c for c in campos})
    return juntar(largo, cobertura, chaves)


def executar(raiz):
    raiz = Path(raiz)
    ctx = Contexto(raiz)
    resultados = {}
    for bloco in extrair_blocos(DICIONARIO)[0]:
        nome = bloco['nome']
        resultado = construir_variavel(nome, raiz, contexto=ctx)
        exportar_resultado(resultado, raiz)
        resultados[nome] = resultado
        print(nome, resultado['status'], flush=True)

    painel = grade_painel(raiz)
    origens = []

    def adicionar(tabela, chaves, origem):
        nonlocal painel
        painel = juntar(painel, tabela, chaves)
        origens.extend({'coluna_painel': c, 'origem': origem} for c in tabela if c not in chaves)

    def tabela(nome, chave):
        return resultados[nome]['tabelas'][chave]

    y = resultados['Y_conv']
    if y['status'] == 'pendente_insumo':
        adicionar(y['tabelas']['situacao_conversao'], ['codigo_ibge', 'ano'], 'Y_conv: situação e pendência')
    else:
        largo = preparar_y_painel(y['tabelas']['taxas'])
        adicionar(largo, ['codigo_ibge', 'ano'], 'Y_conv/Y_tx-conv: mesma máscara inicial')

    # Séries globais são comuns aos municípios; sua repetição não cria novos choques.
    precos = recortar(ctx.precos())
    valores = [c for c in precos if c.startswith(('preco_', 'ln_', 'dln_', 'flag_'))]
    adicionar(abrir_colunas(precos, ['ano'], ['produto'], valores), ['ano'], 'Banco Mundial + CPI-U')

    # Cenários de capacidade continuam separados; não se escolhe um modelo aqui.
    for tipo in ['pam', 'gaez']:
        cap = ctx.capacidade(tipo)
        valores = ['capacidade_valor', 'capacidade_z'] + [c for c in cap if c.startswith('flag_')]
        adicionar(abrir_colunas(cap, ['codigo_ibge'], ['produto', 'cenario_capacidade'], valores),
                  ['codigo_ibge'], f'capacidade fixa: {tipo}')
    inter = ctx.interacoes()
    col = 'interacao_ln_preco_real_usd2024_media_anual_lag1_capacidade_z'
    adicionar(abrir_colunas(inter, ['codigo_ibge', 'ano'], ['produto', 'cenario_capacidade'], [col]),
              ['codigo_ibge', 'ano'], 'preço real anterior × capacidade fixa padronizada')

    pam = tabela('x2_prodsoja-prodmilho', 'rendimento_observado')
    adicionar(abrir_colunas(pam, ['codigo_ibge', 'ano'], ['produto'],
                            ['rendimento_medio_kg_ha', 'rendimento_recalculado_kg_ha',
                             'rendimento_medio_kg_ha_lag1', 'flag_rendimento_ausente']),
              ['codigo_ibge', 'ano'], 'PAM observada: não capacidade predeterminada')

    adicionar(tabela('x4_pecuaria', 'rebanho'), ['codigo_ibge', 'ano'], 'PPM')
    adicionar(tabela('x5a_cobertura_terra', 'usos_instalados'), ['codigo_ibge', 'ano'], 'MapBiomas: estoques')
    lotacao = tabela('x4a_pecuaria', 'lotacao')
    cols = ['codigo_ibge', 'ano', 'lotacao_cabecas_ha', 'flag_pastagem_zero',
            'flag_rebanho_ausente', 'flag_pastagem_ausente', 'flag_bovinos_sem_pastagem',
            'compatibilidade_datas_estoques_validada']
    adicionar(lotacao[cols], ['codigo_ibge', 'ano'], 'PPM/MapBiomas: lotação aparente')
    adicionar(tabela('x5_cobertura_terra', 'vegetacao_inicial_candidata'),
              ['codigo_ibge', 'ano'], 'MapBiomas: denominador candidato já defasado')

    for associacao in ['informada', 'espacial']:
        instituicoes = ctx.instituicoes()[f'instituicoes_{associacao}'].copy()
        instituicoes = instituicoes.rename(columns={c: f'{c}__ibama_{associacao}'
                                                    for c in instituicoes if c not in ['codigo_ibge', 'ano']})
        adicionar(instituicoes, ['codigo_ibge', 'ano'], f'IBAMA: {associacao}; observar cobertura/flags')

    adicionar(tabela('x8_chuva', 'chuva_painel'), ['codigo_ibge', 'ano'], 'CHIRPS: total e referências alternativas')
    adicionar(tabela('x6_biomas', 'fracoes_biomas'), ['codigo_ibge'], 'IBGE: biomas/território2023')
    adicionar(tabela('x9_relevo', 'elevacao_estatica'), ['codigo_ibge'], 'Copernicus: DSM')
    # As interações com biomas são alternativas, não regressoras obrigatórias.
    bio = tabela('x6_biomas', 'heterogeneidade_biomas')
    adicionar(abrir_colunas(bio, ['codigo_ibge', 'ano'], ['produto', 'cenario_capacidade'],
                            ['exposicao_real_x_cerrado', 'exposicao_real_x_pantanal']),
              ['codigo_ibge', 'ano'], 'exposição econômica × fração de bioma; Amazônia referência')

    validar_tabela(painel, ['codigo_ibge', 'ano'])
    if len(painel) != 3384 or painel.codigo_ibge.nunique() != 141:
        raise AssertionError('A grade final deve conter 141 × 24 chaves, sem impor completude das medidas.')
    saida = raiz / '2_INTI/xdata/chap1/processed/harmonizacao'
    caminho = saida / 'painel_candidato_2001_2024_141.csv'
    painel.to_csv(caminho, index=False, encoding='utf-8', na_rep='')
    pd.DataFrame(origens).to_csv(saida / 'origens_colunas_painel.csv', index=False, encoding='utf-8')
    pd.DataFrame({'coluna': painel.columns, 'presentes': painel.notna().sum().to_numpy(),
                  'ausentes': painel.isna().sum().to_numpy()}).to_csv(saida / 'cobertura_painel.csv', index=False)
    resumo = {'linhas': len(painel), 'municipios': 141, 'anos': [2001, 2024], 'colunas': len(painel.columns),
              'sha256': hash_arquivo(caminho), 'y_construido': y['status'] != 'pendente_insumo',
              'pronto_para_inferencia_causal': False,
              'observacao': 'Grade candidata com alternativas e indicadores de qualidade. Não define controles nem identificação.',
              'situacao_por_notebook': {k: {'status': v['status'], 'pendencias': v['pendencias']}
                                        for k, v in resultados.items()},
              'fontes_preservadas': 'conferidas separadamente na auditoria; não usar esta anotação como teste'}
    (saida / 'manifesto_painel.json').write_text(json.dumps(resumo, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in resumo.items() if k != 'situacao_por_notebook'}, ensure_ascii=True))
    return painel, resumo


if __name__ == '__main__':
    executar(encontrar_raiz())
