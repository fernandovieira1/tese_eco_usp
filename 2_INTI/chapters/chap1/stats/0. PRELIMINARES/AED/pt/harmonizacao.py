"""Executa os passos 1 e 2 por candidato; exportação permanece uma ação explícita."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from harmonizacao_comum import (PARAMETROS, cadastro_municipios, carregar_fontes, hash_arquivo,
                               defasar_ano, grade_painel, recortar, validar_tabela)
from harmonizacao_economia import (anualizar_chuva, anualizar_precos, carregar_deflator,
                                  criar_interacoes, preparar_gaez, produtividade_historica)
from harmonizacao_instituicoes import construir_instituicoes, diagnosticar_pendencias
from harmonizacao_notebooks import EXPLICACOES


class Contexto:
    """Cache apenas desta execução: uma nova execução volta a ler os arquivos."""
    def __init__(self, raiz, nome=None, bases=None):
        self.raiz = Path(raiz)
        self.cache = {nome: bases} if bases is not None else {}
        self.fontes_usadas = set()
        self.derivados = {}

    def fonte(self, nome):
        self.fontes_usadas.add(nome)
        if nome not in self.cache:
            self.cache[nome] = carregar_fontes(nome, self.raiz)
        return self.cache[nome]

    def deflator(self, tipo):
        arquivo = {'cpi': 'bls_fred_CPIAUCNS_1960_2024.csv',
                   'ipca': 'ibge_sidra_1737_ipca_2266_1994_2024.json'}[tipo]
        caminho = self.raiz / '2_INTI/xdata/chap1/raw/tabular/deflatores_harmonizacao_20261014' / arquivo
        # Ausência do índice não é interpretada como inflação zero.
        if not caminho.is_file():
            return None
        return carregar_deflator(caminho, fonte=tipo)

    def precos(self):
        if 'precos' not in self.derivados:
            self.derivados['precos'] = anualizar_precos(self.fonte('x1_psoja-pmilho')[0], self.deflator('cpi'))
        return self.derivados['precos']

    def capacidade(self, tipo):
        if tipo not in self.derivados:
            self.derivados[tipo] = (produtividade_historica(self.fonte('x2a_hprodsoj-hprodmil')[0])
                                   if tipo == 'pam' else preparar_gaez(self.fonte('x2b_yield-sojamilho')[0]))
        return self.derivados[tipo]

    def interacoes(self):
        return criar_interacoes(self.precos(), pam=self.capacidade('pam'), gaez=self.capacidade('gaez'))

    def usos(self):
        from harmonizacao_terra import construir_usos
        if 'usos' not in self.derivados:
            self.derivados['usos'] = construir_usos(self.fonte('x5a_cobertura_terra')[0],
                                                  cadastro_municipios(self.raiz))
        return self.derivados['usos']

    def instituicoes(self):
        if 'instituicoes' not in self.derivados:
            self.derivados['instituicoes'] = construir_instituicoes(
                self.fonte('x3b_infracoes')[0], self.fonte('x3c_infracoes')[0],
                cadastro_municipios(self.raiz), ipca=self.deflator('ipca'))
        return self.derivados['instituicoes']


def _unidade(coluna, nome):
    c = coluna.lower()
    if c == 'ano': return 'ano civil'
    if 'codigo' in c: return 'identificador municipal'
    if c.startswith(('flag_', 'tem_', 'elegivel', 'grade_', 'completude_')) or c.endswith('_validada'): return 'booleano'
    if c.startswith(('n_', 'meses_', 'anos_', 'count')): return 'contagem'
    if 'interacao' in c: return 'produto das escalas descritas na fórmula'
    if any(x in c for x in ('zscore', 'capacidade_z', 'ln_', 'dln_')): return 'adimensional'
    if 'pct' in c: return '%'
    if any(x in c for x in ('share', 'fracao', 'taxa_', 'aptidao_0_1')): return 'proporção (0–1)'
    if 'lotacao' in c: return 'cabeças/ha'
    if 'kg_ha' in c: return 'kg/ha; conferir matéria seca nos cenários GAEZ'
    if 'preco' in c: return 'USD/t para grãos; USD/kg para carne; real: poder de compra médio de 2024'
    if 'multas' in c or 'multa' in c: return 'R$; reais: dezembro de 2024'
    if 'efetivo_bovino' in c or 'rebanho' in c: return 'cabeças'
    if c.endswith('_ha') or '_ha_' in c: return 'ha'
    if 'precip' in c: return 'mm, salvo escores adimensionais explicitamente nomeados'
    if 'elevation' in c: return 'm'
    if c in ('aptidao', 'valor_medio', 'capacidade_valor'): return 'conforme unidade/cenário da linha'
    return 'metadado, categoria ou unidade indicada na fonte'


def _dicionario(nome, tabelas):
    _, processo, formula, limite = EXPLICACOES[nome]
    return [{'tabela': tabela, 'coluna': coluna, 'unidade': _unidade(coluna, nome),
             'regra_da_construcao': formula, 'processo': processo,
             'limite_interpretacao': limite}
            for tabela, base in tabelas.items() for coluna in base.columns]


def _saida_y(ctx):
    """Só aceita insumos com contrato de máscara; nunca usa diferença de estoques."""
    from harmonizacao_terra import construir_transicoes, construir_taxas
    pasta = ctx.raiz / '2_INTI/xdata/chap1/processed/harmonizacao'
    transicoes = pasta / 'transicoes_reais_10_1_141.csv'
    cobertura = pasta / 'cobertura_transicoes_10_1_141.csv'
    if transicoes.is_file() and cobertura.is_file():
        tipos = {'codigo_ibge': 'string', 'colecao': 'string', 'malha': 'string', 'mascara_id': 'string'}
        tr = pd.read_csv(transicoes, dtype=tipos)
        co = pd.read_csv(cobertura, dtype=tipos)
        validar_insumos_y(tr, co, grade_painel(ctx.raiz))
        conversao = construir_transicoes(tr, co)
        conversao.attrs['fontes_transicoes'] = {p.name: hash_arquivo(p) for p in (transicoes, cobertura)}
        conversao.attrs['periodo_intervalo'] = 'ano t representa a transição do mapa t-1 ao mapa t'
        conversao.attrs['cobertura'] = 'Área inválida medida diretamente; qualquer lacuna real mantém Y ausente.'
        conversao.attrs['n_pares_incompletos'] = int((~co.cobertura_completa).sum())
        return {'conversao': conversao, 'taxas': construir_taxas(conversao), 'cobertura_transicoes': co}, []
    pendencia = ('Transições compatíveis da Coleção 10.1 ainda indisponíveis. O download público verificado '
                 'é 10.0; o asset 10.1 exige acesso Earth Engine. Não misturar coleções. '
                 'Use obter_transicoes_mapbiomas.py para obter o insumo compatível.')
    base = grade_painel(ctx.raiz)
    for col in ['conv_agricultura_ha', 'conv_pastagem_ha', 'nativa_inicial_ha',
                'taxa_conv_agricultura', 'taxa_conv_pastagem']:
        base[col] = np.nan
    base['flag_medida_nao_construida'] = True
    base['motivo_ausencia'] = 'transicoes_col10_1_indisponiveis'
    return {'situacao_conversao': base}, [pendencia]


def validar_insumos_y(transicoes, cobertura, grade):
    """Igualdade entre fontes não basta: ambas devem cumprir o contrato do projeto."""
    for tabela in (transicoes, cobertura):
        for coluna, esperado in [('colecao', '10.1'), ('malha', 'IBGE_MT_2023_141')]:
            if coluna not in tabela or not tabela[coluna].astype('string').eq(esperado).all():
                raise ValueError(f'Y requer {coluna}={esperado}; não misturar referências.')
        if tabela[['codigo_ibge', 'ano']].isna().any().any():
            raise ValueError('Chaves de transição ausentes.')
        pares = set(map(tuple, tabela[['codigo_ibge', 'ano']].to_numpy()))
        esperados = set(map(tuple, grade[['codigo_ibge', 'ano']].to_numpy()))
        if not pares <= esperados:
            raise ValueError('Transições fora dos municípios/anos do painel.')
    validar_tabela(cobertura, ['codigo_ibge', 'ano'])
    if set(map(tuple, cobertura[['codigo_ibge', 'ano']].to_numpy())) != esperados:
        raise ValueError('Cobertura da grade incompleta; resultados parciais não substituem o insumo completo.')


def construir_variavel(nome, raiz, bases=None, contexto=None):
    """Retorna tabelas, regras e pendências; nenhuma ausência é preenchida por zero."""
    if nome not in EXPLICACOES:
        raise ValueError(f'Candidato sem regra: {nome}')
    ctx = contexto or Contexto(raiz, nome, bases)
    base = ctx.fonte(nome)[0]
    pendencias = []
    status = 'construida_com_ressalvas'
    parametros = dict(PARAMETROS)

    if nome.startswith('Y_'):
        tabelas, pendencias = _saida_y(ctx)
        status = 'pendente_insumo' if pendencias else 'construida_com_ressalvas'
    elif nome.startswith(('x1_', 'x1a_')):
        culturas = ['carne_bovina'] if nome.startswith('x1a_') else ['soja', 'milho']
        precos = ctx.precos()
        tabelas = {'precos_anuais': precos.loc[precos.produto.isin(culturas)].copy()}
        if nome.startswith('x1_'):
            tabelas['exposicoes_alternativas'] = ctx.interacoes()
        if ctx.deflator('cpi') is None:
            pendencias.append('CPI ausente: preços reais continuam NA; execute a aquisição explícita dos deflatores.')
        pendencias.append('Janela t−1 e exposições fixas não garantem exogeneidade nem medem lucro esperado.')
    elif nome == 'x2_prodsoja-prodmilho':
        cols = ['codigo_ibge', 'ano', 'produto', 'producao_t', 'area_colhida_ha', 'rendimento_medio_kg_ha']
        pam = base[cols].copy()
        validar_tabela(pam, ['codigo_ibge', 'ano', 'produto'])
        pam['rendimento_recalculado_kg_ha'] = 1000 * pam.producao_t / pam.area_colhida_ha.where(pam.area_colhida_ha > 0)
        pam['diferenca_rendimento_kg_ha'] = pam.rendimento_recalculado_kg_ha - pam.rendimento_medio_kg_ha
        pam['flag_area_colhida_nula'] = pam.area_colhida_ha.eq(0)
        pam['flag_rendimento_ausente'] = pam.rendimento_medio_kg_ha.isna()
        pam = defasar_ano(pam, ['rendimento_medio_kg_ha'], grupos=('codigo_ibge', 'produto'))
        tabelas = {'rendimento_observado': recortar(pam)}
        pendencias.append('Rendimento observado pode responder aos incentivos; correspondência territorial histórica pendente.')
    elif nome.startswith(('x2a_', 'x2b_', 'x2c_')):
        historica = nome.startswith('x2a_')
        cap = ctx.capacidade('pam' if historica else 'gaez')
        if not historica:
            prefixo = 'yx' if nome.startswith('x2b_') else 'sx'
            cap = cap.loc[cap.variavel_raster.str.startswith(prefixo)].copy()
        inter = criar_interacoes(ctx.precos(), pam=cap if historica else None,
                                 gaez=None if historica else cap)
        tabelas = {'capacidade_fixa': cap, 'exposicoes_alternativas': inter}
        pendencias.append('Geografia histórica PAM e seleção de produtores permanecem sinalizadas.' if historica else
                          'Temporalidade da base GAEZ de 2010 não validada; sem conversão arbitrária de umidade.')
    elif nome in ('x3_infracoes', 'x3a_infracoes', 'x3b_infracoes', 'x3c_infracoes', 'x3d_infracoes'):
        todos = ctx.instituicoes()
        if nome == 'x3c_infracoes':
            chaves = ['qualidade_geocodificacao', 'perfil_temas']
        elif nome == 'x3a_infracoes':
            chaves = ['instituicoes_espacial', 'qualidade_geocodificacao']
        elif nome == 'x3b_infracoes':
            chaves = ['instituicoes_informada', 'instituicoes_espacial', 'perfil_temas']
        else:
            chaves = ['instituicoes_informada', 'perfil_temas']
        tabelas = {k: todos[k] for k in chaves}
        if nome in ('x3_infracoes', 'x3a_infracoes', 'x3d_infracoes'):
            colunas = ['codigo_ibge', 'ano'] + [c for c in base if c.startswith(('n_autos_', 'valor_multas_', 'n_valores_'))]
            tabelas['agregado_original_conferencia'] = recortar(base[colunas])
        pendencias.append('Contagens observadas podem ser parciais e responder à conversão; não medem eficácia causal.')
        parametros['selecoes'] = 'Flora; Desmatamento/Desmatamento e Queimada (alternativas, sem soma)'
        parametros['data_evento'] = 'lavratura; status atual não reconstrói situação histórica'
        parametros['moeda_multas'] = 'R$ de dezembro de 2024; IPCA mensal antes da soma'
    elif nome == 'x3e_infracoes' or nome.startswith('x7_custo-'):
        status = 'adiada_conforme_plano'
        if nome == 'x3e_infracoes':
            dados = ctx.fonte(nome)
            diagnostico = diagnosticar_pendencias(dados[0], dados[1])
            tabelas = {'pendencias': diagnostico.loc[diagnostico.candidato.eq(nome)].copy()}
            pendencias.append('Embargos: reconstruir identidade, emissão, situação e unidade antes de criar fluxo/estoque.')
        else:
            cobertura = base.groupby(['arquivo_origem', 'aba'], observed=True).size().rename('n_celulas').reset_index()
            tabelas = {'cobertura_celulas': cobertura,
                       'pendencias': pd.DataFrame({'campo_necessario': ['localidade', 'tecnologia', 'safra', 'ano',
                             'categoria_custo', 'unidade', 'moeda', 'metodologia', 'valor_custo_validado']})}
            pendencias.append('CONAB: células ainda sem mapa de significado comparável; excluída do painel principal.')
    elif nome == 'x4_pecuaria':
        rebanho = base[['codigo_ibge', 'ano', 'efetivo_bovino']].copy()
        validar_tabela(rebanho, ['codigo_ibge', 'ano'])
        tabelas = {'rebanho': recortar(defasar_ano(rebanho, ['efetivo_bovino']))}
        pendencias.append('Estoque bovino não mede produtividade; limites históricos e momento da medição requerem atenção.')
    elif nome == 'x4a_pecuaria':
        from harmonizacao_terra import construir_lotacao
        tabelas = {'lotacao': construir_lotacao(base, ctx.usos())}
        pendencias.append('Lotação é aparente: referências temporais PPM/MapBiomas e limites históricos ainda importam.')
    elif nome == 'x5_cobertura_terra':
        cols = ['codigo_ibge', 'ano', 'native_veg_ha_lag1', 'native_veg_share_lag1']
        nativa = recortar(base[cols])
        validar_tabela(nativa, ['codigo_ibge', 'ano'])
        nativa['flag_denominador_nulo'] = nativa.native_veg_ha_lag1.eq(0)
        nativa['flag_denominador_ausente'] = nativa.native_veg_ha_lag1.isna()
        tabelas = {'vegetacao_inicial_candidata': nativa}
        pendencias.append('Denominador preservado da fonte; validar máscara contra as transições antes de formar Y.')
    elif nome == 'x5a_cobertura_terra':
        tabelas = {'usos_instalados': ctx.usos()}
        pendencias.append('Áreas instaladas não representam conversão bruta; classes residuais e cobertura ficam sinalizadas.')
    elif nome == 'x6_biomas':
        cols = ['codigo_ibge', 'biome_amazonia_share_i', 'biome_cerrado_share_i', 'biome_pantanal_share_i']
        biomas = base[cols].copy()
        validar_tabela(biomas, ['codigo_ibge'])
        biomas['soma_fracoes'] = biomas[cols[1:]].sum(axis=1, min_count=3)
        inter = ctx.interacoes().merge(biomas, on='codigo_ibge', how='left', validate='many_to_one')
        z = 'interacao_ln_preco_real_usd2024_media_anual_lag1_capacidade_z'
        for bioma in ['cerrado', 'pantanal']:
            inter[f'exposicao_real_x_{bioma}'] = inter[z] * inter[f'biome_{bioma}_share_i']
        tabelas = {'fracoes_biomas': biomas, 'heterogeneidade_biomas': inter}
        pendencias.append('Amazônia é referência das interações. Frações não são normalizadas para esconder lacunas cartográficas.')
    elif nome in ('x8_chuva', 'x8_chuvaa'):
        chuva = anualizar_chuva(ctx.fonte('x8_chuva')[0])
        tabelas = {'chuva_historico_e_referencias': chuva, 'chuva_painel': recortar(chuva)}
        parametros['cobertura_minima_pixels'] = 0.95
        pendencias.append('1981–2000 é referência de 20 anos; referências de 30 anos são alternativas retrospectivas.')
    elif nome == 'x9_relevo':
        cols = ['codigo_ibge', 'elevation_mean_m', 'elevation_min_m', 'elevation_max_m']
        relevo = base[cols].copy()
        validar_tabela(relevo, ['codigo_ibge'])
        relevo['flag_ordem_invalida'] = ((relevo.elevation_min_m > relevo.elevation_mean_m)
                                        | (relevo.elevation_mean_m > relevo.elevation_max_m))
        if relevo.flag_ordem_invalida.any():
            raise ValueError('Resumos de elevação fora de ordem.')
        tabelas = {'elevacao_estatica': relevo}
        pendencias.append('DSM inclui superfície; não foram inventadas declividade, rugosidade ou variação anual.')
    else:
        raise ValueError(nome)

    # Os metadados de cada função acompanham a tabela e seu manifesto.
    from gerar_notebooks import extrair_blocos
    blocos, _ = extrair_blocos(ctx.raiz / '2_INTI/chapters/chap1/stats/HIPOTESES TESE - CHAP1.txt')
    # Dependências da variável, sem herdar fontes de outros notebooks no cache.
    dependencias = {nome}
    if nome in ('x1_psoja-pmilho', 'x6_biomas'):
        dependencias.update(['x1_psoja-pmilho', 'x2a_hprodsoj-hprodmil', 'x2b_yield-sojamilho'])
    if nome.startswith(('x2a_', 'x2b_', 'x2c_')):
        dependencias.add('x1_psoja-pmilho')
        dependencias.add('x2a_hprodsoj-hprodmil' if nome.startswith('x2a_') else 'x2b_yield-sojamilho')
    if nome.startswith('x1a_'):
        dependencias.add('x1_psoja-pmilho')
    if nome in ('x3_infracoes', 'x3a_infracoes', 'x3b_infracoes', 'x3c_infracoes', 'x3d_infracoes'):
        dependencias.update(['x3b_infracoes', 'x3c_infracoes'])
    if nome == 'x4a_pecuaria':
        dependencias.add('x5a_cobertura_terra')
    if nome == 'x8_chuvaa':
        dependencias.add('x8_chuva')
    fontes = {b['nome']: b['caminhos'] for b in blocos if b['nome'] in dependencias}
    principal = 'taxas' if nome == 'Y_tx-conv' and 'taxas' in tabelas else next(iter(tabelas))
    return {'nome': nome, 'status': status, 'principal': principal, 'tabelas': tabelas,
            'parametros': parametros, 'pendencias': pendencias, 'fontes_txt': fontes,
            'fontes_territoriais': 'processed/territorio_141/manifesto141.json',
            'fontes_deflatores': 'raw/tabular/deflatores_harmonizacao_20261014/manifesto_deflatores.json',
            'dicionario': _dicionario(nome, tabelas)}
