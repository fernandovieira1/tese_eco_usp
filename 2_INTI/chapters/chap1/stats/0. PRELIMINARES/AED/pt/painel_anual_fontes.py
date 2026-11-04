"""Reúne os derivados anuais já existentes, sem alterar fontes ou recalculá-las.

O manifesto de cada candidato define seus arquivos e hashes. Fontes equivalentes
são conferidas e entram uma única vez; fontes adiadas ficam apenas no inventário.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from construir_painel import abrir_colunas, juntar, preparar_y_painel
from harmonizacao_comum import hash_arquivo, recortar, validar_tabela


PASTA_DERIVADOS = Path('2_INTI/xdata/chap1/processed/harmonizacao')
NOMES = (
    'Y_conv', 'Y_tx-conv', 'x1_psoja-pmilho', 'x1a_pcarne',
    'x2_prodsoja-prodmilho', 'x2a_hprodsoj-hprodmil',
    'x2b_yield-sojamilho', 'x2c_aptid-sojamilho',
    'x3_infracoes', 'x3a_infracoes', 'x3b_infracoes', 'x3c_infracoes',
    'x3d_infracoes', 'x3e_infracoes', 'x4_pecuaria', 'x4a_pecuaria',
    'x5_cobertura_terra', 'x5a_cobertura_terra', 'x6_biomas',
    'x7_custo-soja', 'x7_custo-milho-s1', 'x7_custo-milho-s2',
    'x8_chuva', 'x8_chuvaa', 'x9_relevo',
)
ADIADAS = {'x3e_infracoes', 'x7_custo-soja', 'x7_custo-milho-s1', 'x7_custo-milho-s2'}
SOBREPOSICOES = {
    'Y_conv': 'Mesmas transições de Y_tx-conv; área e taxa entram juntas uma vez.',
    'Y_tx-conv': 'Taxa e denominador compartilhados com Y_conv; sem duplicar destinos.',
    'x1_psoja-pmilho': 'Exposições repetidas nos candidatos de capacidade; conservar uma cópia.',
    'x2a_hprodsoj-hprodmil': 'Capacidade PAM e exposições também presentes em x1.',
    'x2b_yield-sojamilho': 'Cenários GAEZ yx; exposições também presentes em x1.',
    'x2c_aptid-sojamilho': 'Cenários GAEZ sx; exposições também presentes em x1.',
    'x3_infracoes': 'Tabela informada igual à reconstrução em x3b e x3d.',
    'x3a_infracoes': 'Tabela espacial igual à reconstrução em x3b.',
    'x3b_infracoes': 'Origem usada para as duas associações territoriais do IBAMA.',
    'x3c_infracoes': 'Perfil de temas e qualidade de geocodificação; diagnóstico, sem regressor próprio.',
    'x3d_infracoes': 'Tabela informada igual à reconstrução em x3 e x3b.',
    'x4a_pecuaria': 'Somente lotação e seus indicadores; rebanho/área já entram pelos outros candidatos.',
    'x6_biomas': 'Frações fixas e interações; exposições de origem já entram por x1.',
    'x8_chuva': 'Mesmo total/anomalias de x8_chuvaa; entram uma única vez.',
    'x8_chuvaa': 'Mesmo total/anomalias de x8_chuva; sem duplicação de colunas.',
}


def carregar_fontes(raiz):
    """Lê os 25 manifestos e todos os CSV declarados, verificando integridade."""
    raiz = Path(raiz).resolve()
    pasta = (raiz / PASTA_DERIVADOS).resolve()
    fontes, linhas = {}, []
    for nome in NOMES:
        local = pasta / nome
        caminho_manifesto = local / 'manifesto.json'
        manifesto = json.loads(caminho_manifesto.read_text(encoding='utf-8'))
        if manifesto.get('nome') != nome:
            raise ValueError(f'Nome incompatível no manifesto: {nome}')
        esperado = 'adiada_conforme_plano' if nome in ADIADAS else 'construida_com_ressalvas'
        if manifesto.get('status') != esperado:
            raise ValueError(f'Situação mudou em {nome}; rever inclusão no painel.')
        tabelas = {}
        for chave, meta in manifesto['arquivos'].items():
            # O caminho fica limitado à pasta de derivados deste candidato.
            caminho = (raiz / Path(meta['arquivo'].replace('\\', '/'))).resolve()
            if caminho.parent != local.resolve() or caminho.suffix.lower() != '.csv':
                raise ValueError(f'Caminho fora da pasta esperada: {nome}/{chave}')
            if hash_arquivo(caminho) != meta['sha256']:
                raise ValueError(f'SHA256 divergente: {nome}/{chave}')
            tipos = {c: 'string' for c in ('codigo_ibge', 'colecao', 'malha', 'mascara_id')
                     if c in meta['colunas']}
            base = pd.read_csv(caminho, dtype=tipos, float_precision='round_trip', low_memory=False)
            if len(base) != meta['linhas'] or list(base.columns) != meta['colunas']:
                raise ValueError(f'Esquema/contagem divergente: {nome}/{chave}')
            if 'codigo_ibge' in base:
                if not base.codigo_ibge.str.fullmatch(r'51\d{5}').all():
                    raise ValueError(f'Código municipal inválido: {nome}/{chave}')
            if 'ano' in base:
                ano = pd.to_numeric(base.ano, errors='raise')
                if ano.isna().any() or (ano % 1 != 0).any():
                    raise ValueError(f'Ano inválido: {nome}/{chave}')
                base['ano'] = ano.astype('int64')
            base.attrs['metadados'] = meta.get('metadados', {})
            tabelas[chave] = base
        fontes[nome] = {'manifesto': manifesto, 'tabelas': tabelas,
                        'manifesto_sha256': hash_arquivo(caminho_manifesto)}
        participacao = ('adiada: sem coluna analítica' if nome in ADIADAS else
                        'diagnóstico: fora da matriz' if nome == 'x3c_infracoes' else
                        'incluída: equivalências reunidas sem duplicação')
        linhas.append({'notebook': nome + '.ipynb', 'nome': nome, 'status': manifesto['status'],
                       'papel_painel': participacao, 'n_tabelas': len(tabelas),
                       'tabelas': '; '.join(tabelas),
                       'sobreposicao': SOBREPOSICOES.get(nome, 'Sem duplicação adicional.'),
                       'pendencias': ' | '.join(manifesto.get('pendencias', [])),
                       'hashes_validados': True})
    return fontes, pd.DataFrame(linhas)


def _tabela(fontes, nome, tabela):
    return fontes[nome]['tabelas'][tabela].copy()


def _iguais(a, b, chaves, contexto):
    """Redundância só é eliminada depois de confirmar valores e chaves."""
    validar_tabela(a, chaves)
    validar_tabela(b, chaves)
    if set(a.columns) != set(b.columns):
        raise ValueError(f'Colunas divergentes entre fontes equivalentes: {contexto}')
    try:
        pd.testing.assert_frame_equal(
            a.sort_values(chaves).reset_index(drop=True),
            b[a.columns].sort_values(chaves).reset_index(drop=True),
            check_dtype=False, check_exact=True, check_categorical=False,
        )
    except AssertionError as erro:
        raise ValueError(f'Valores divergentes entre fontes equivalentes: {contexto}') from erro


def construir_grade(fontes):
    """141 territórios de referência × 24 anos; não preenche medidas ausentes."""
    codigos = _tabela(fontes, 'x6_biomas', 'fracoes_biomas')[['codigo_ibge']]
    validar_tabela(codigos, ['codigo_ibge'])
    if len(codigos) != 141 or not codigos.codigo_ibge.str.fullmatch(r'51\d{5}').all():
        raise ValueError('A referência territorial deve conter 141 municípios de MT.')
    return pd.MultiIndex.from_product([codigos.codigo_ibge.sort_values(), range(2001, 2025)],
                                     names=['codigo_ibge', 'ano']).to_frame(index=False)


def preparar_blocos(fontes):
    """Prepara 16 junções; mantém a seleção de colunas do construtor vigente."""
    blocos = []
    grade = construir_grade(fontes)
    codigos = set(grade.codigo_ibge)

    def adicionar(nome, tabela, chaves, origens, fontes_colunas=None):
        validar_tabela(tabela, chaves)
        if 'codigo_ibge' in chaves and not set(tabela.codigo_ibge) <= codigos:
            raise ValueError(f'Município fora da referência: {nome}')
        if 'ano' in chaves and not tabela.ano.between(2001, 2024).all():
            raise ValueError(f'Ano fora do painel: {nome}')
        blocos.append({'nome': nome, 'tabela': tabela, 'chaves': list(chaves),
                       'origens': list(origens), 'fontes_colunas': fontes_colunas or {}})

    chaves = ['codigo_ibge', 'ano']
    y = _tabela(fontes, 'Y_conv', 'taxas')
    for tabela in ('conversao', 'taxas', 'cobertura_transicoes'):
        _iguais(_tabela(fontes, 'Y_conv', tabela), _tabela(fontes, 'Y_tx-conv', tabela),
                chaves + (['destino'] if tabela != 'cobertura_transicoes' else []), tabela)
    adicionar('conversao', preparar_y_painel(y), chaves,
              [('Y_conv', 'taxas'), ('Y_tx-conv', 'taxas')])

    precos = recortar(pd.concat([_tabela(fontes, n, 'precos_anuais')
                                for n in ('x1_psoja-pmilho', 'x1a_pcarne')], ignore_index=True))
    valores = [c for c in precos if c.startswith(('preco_', 'ln_', 'dln_', 'flag_'))]
    adicionar('precos', abrir_colunas(precos, ['ano'], ['produto'], valores), ['ano'],
              [('x1_psoja-pmilho', 'precos_anuais'), ('x1a_pcarne', 'precos_anuais')])

    for tipo, nomes in [('pam', ['x2a_hprodsoj-hprodmil']),
                         ('gaez', ['x2c_aptid-sojamilho', 'x2b_yield-sojamilho'])]:
        cap = pd.concat([_tabela(fontes, n, 'capacidade_fixa') for n in nomes], ignore_index=True)
        valores = ['capacidade_valor', 'capacidade_z'] + [c for c in cap if c.startswith('flag_')]
        adicionar('capacidade_' + tipo,
                  abrir_colunas(cap, ['codigo_ibge'], ['produto', 'cenario_capacidade'], valores),
                  ['codigo_ibge'], [(n, 'capacidade_fixa') for n in nomes])

    inter = _tabela(fontes, 'x1_psoja-pmilho', 'exposicoes_alternativas')
    origem_inter = [('x1_psoja-pmilho', 'exposicoes_alternativas')]
    for nome in ['x2a_hprodsoj-hprodmil', 'x2b_yield-sojamilho', 'x2c_aptid-sojamilho']:
        alternativa = _tabela(fontes, nome, 'exposicoes_alternativas')
        selecionado = inter.loc[inter.cenario_capacidade.isin(alternativa.cenario_capacidade)]
        comuns = list(alternativa.columns)
        _iguais(selecionado[comuns], alternativa, chaves + ['produto', 'cenario_capacidade'], nome)
        origem_inter.append((nome, 'exposicoes_alternativas'))
    col = 'interacao_ln_preco_real_usd2024_media_anual_lag1_capacidade_z'
    adicionar('exposicoes', abrir_colunas(inter, chaves, ['produto', 'cenario_capacidade'], [col]),
              chaves, origem_inter)

    pam = _tabela(fontes, 'x2_prodsoja-prodmilho', 'rendimento_observado')
    adicionar('rendimento_pam', abrir_colunas(pam, chaves, ['produto'],
              ['rendimento_medio_kg_ha', 'rendimento_recalculado_kg_ha',
               'rendimento_medio_kg_ha_lag1', 'flag_rendimento_ausente']),
              chaves, [('x2_prodsoja-prodmilho', 'rendimento_observado')])
    for bloco, nome, tabela in [('rebanho', 'x4_pecuaria', 'rebanho'),
                                ('usos_instalados', 'x5a_cobertura_terra', 'usos_instalados')]:
        adicionar(bloco, _tabela(fontes, nome, tabela), chaves, [(nome, tabela)])
    cols = chaves + ['lotacao_cabecas_ha', 'flag_pastagem_zero', 'flag_rebanho_ausente',
                    'flag_pastagem_ausente', 'flag_bovinos_sem_pastagem',
                    'compatibilidade_datas_estoques_validada']
    adicionar('lotacao', _tabela(fontes, 'x4a_pecuaria', 'lotacao')[cols], chaves,
              [('x4a_pecuaria', 'lotacao')])
    adicionar('vegetacao_inicial', _tabela(fontes, 'x5_cobertura_terra', 'vegetacao_inicial_candidata'),
              chaves, [('x5_cobertura_terra', 'vegetacao_inicial_candidata')])

    for associacao, outros in [('informada', ['x3_infracoes', 'x3d_infracoes']),
                               ('espacial', ['x3a_infracoes'])]:
        tabela = 'instituicoes_' + associacao
        inst = _tabela(fontes, 'x3b_infracoes', tabela)
        for nome in outros:
            _iguais(inst, _tabela(fontes, nome, tabela), chaves, nome)
        renomear = {c: c + '__ibama_' + associacao for c in inst if c not in chaves}
        adicionar('ibama_' + associacao, inst.rename(columns=renomear), chaves,
                  [(n, tabela) for n in ['x3b_infracoes'] + outros])

    for tabela in ['chuva_historico_e_referencias', 'chuva_painel']:
        _iguais(_tabela(fontes, 'x8_chuva', tabela), _tabela(fontes, 'x8_chuvaa', tabela), chaves, tabela)
    adicionar('chuva', _tabela(fontes, 'x8_chuva', 'chuva_painel'), chaves,
              [('x8_chuva', 'chuva_painel'), ('x8_chuvaa', 'chuva_painel')])
    adicionar('biomas', _tabela(fontes, 'x6_biomas', 'fracoes_biomas'), ['codigo_ibge'],
              [('x6_biomas', 'fracoes_biomas')])
    adicionar('relevo', _tabela(fontes, 'x9_relevo', 'elevacao_estatica'), ['codigo_ibge'],
              [('x9_relevo', 'elevacao_estatica')])
    bio = _tabela(fontes, 'x6_biomas', 'heterogeneidade_biomas')
    adicionar('exposicoes_biomas', abrir_colunas(bio, chaves, ['produto', 'cenario_capacidade'],
              ['exposicao_real_x_cerrado', 'exposicao_real_x_pantanal']), chaves,
              [('x6_biomas', 'heterogeneidade_biomas')])
    return blocos


def _origens_coluna(bloco, coluna, fontes):
    """Restringe cenários/produtos à fonte que realmente contém a coluna."""
    partes = coluna.split('__')
    original = partes[0]
    if original.startswith('y_'):
        original = original[2:]
    origens = []
    for nome, tabela in bloco['origens']:
        base = fontes[nome]['tabelas'][tabela]
        if original not in base:
            continue
        categorias = partes[1:]
        if categorias and not categorias[0].startswith('ibama_'):
            if 'produto' in base and categorias[0] not in set(base.produto):
                continue
            if 'cenario_capacidade' in base and len(categorias) > 1:
                if categorias[1] not in set(base.cenario_capacidade):
                    continue
        origens.append((nome, tabela, original))
    return origens


def rastrear_colunas(fontes, blocos):
    """Dicionário por coluna final, com origem, unidade, regra e ressalvas."""
    registros = [
        {'coluna_painel': 'codigo_ibge', 'bloco': 'grade', 'notebooks': 'x6_biomas.ipynb',
         'tabelas_origem': 'fracoes_biomas', 'coluna_origem': 'codigo_ibge',
         'unidade': 'código IBGE', 'regra': '141 códigos da referência territorial fixa',
         'limite_interpretacao': 'Unidades territoriais constantes; não são 142 municípios atuais.'},
        {'coluna_painel': 'ano', 'bloco': 'grade', 'notebooks': 'grade do painel',
         'tabelas_origem': 'calendário 2001–2024', 'coluna_origem': 'ano',
         'unidade': 'ano civil', 'regra': '24 anos para cada território',
         'limite_interpretacao': 'Grade completa não implica observações completas.'},
    ]
    for bloco in blocos:
        for coluna in bloco['tabela']:
            if coluna in bloco['chaves']:
                continue
            origens = _origens_coluna(bloco, coluna, fontes)
            if not origens:
                raise ValueError(f'Coluna sem rastreabilidade: {coluna}')
            itens = [item for nome, tabela, original in origens
                     for item in fontes[nome]['manifesto']['dicionario']
                     if item['tabela'] == tabela and item['coluna'] == original]
            def unico(campo):
                return ' | '.join(dict.fromkeys(str(x.get(campo, '')) for x in itens))
            unidade = unico('unidade')
            if coluna.startswith(('capacidade_z', 'ln_', 'ln1p_', 'dln_', 'interacao_ln_',
                                   'exposicao_real_x_')):
                unidade = 'adimensional'
            elif coluna == 'y_cobertura_completa':
                unidade = 'booleano'
            elif coluna.startswith('preco_'):
                unidade = ('US$/kg' if '__carne_bovina' in coluna else 'US$/t')
                if 'real_' in coluna:
                    unidade += ' a preços médios de 2024'
            elif coluna.startswith('capacidade_valor'):
                unidade = ('índice GAEZ (0–10.000)' if '__gaez_sx' in coluna else
                           'kg de matéria seca/ha' if '__gaez_yx' in coluna else 'kg/ha')
            registros.append({'coluna_painel': coluna, 'bloco': bloco['nome'],
                'notebooks': '; '.join(dict.fromkeys(n + '.ipynb' for n, _, _ in origens)),
                'tabelas_origem': '; '.join(dict.fromkeys(n + '/' + t for n, t, _ in origens)),
                'coluna_origem': '; '.join(dict.fromkeys(c for _, _, c in origens)),
                'unidade': unidade, 'regra': unico('regra_da_construcao'),
                'limite_interpretacao': unico('limite_interpretacao')})
    resultado = pd.DataFrame(registros)
    if resultado.coluna_painel.duplicated().any():
        raise ValueError('Coluna final duplicada no dicionário de rastreabilidade.')
    return resultado


def construir_desde_fontes(fontes):
    """Conveniência para testes; o notebook mostra cada junção separadamente."""
    blocos = preparar_blocos(fontes)
    painel = construir_grade(fontes)
    for bloco in blocos:
        painel = juntar(painel, bloco['tabela'], bloco['chaves'])
    validar_tabela(painel, ['codigo_ibge', 'ano'])
    if painel.shape != (3384, 296):
        raise ValueError(f'Estrutura mudou: {painel.shape}; revisar inventário antes de continuar.')
    return painel, blocos, rastrear_colunas(fontes, blocos)
