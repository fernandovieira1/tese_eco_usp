"""Funções incorporadas nas células dos notebooks pelo gerador."""
from pathlib import Path
import csv
import hashlib
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import display

# Aumente para ver mais grupos; as tabelas descritivas sempre incluem todos.
MAX_GRUPOS_GRAFICOS = 6


def encontrar_raiz(inicio=None):
    """Funciona com o kernel aberto na raiz ou na pasta do notebook."""
    inicio = Path(inicio or Path.cwd()).resolve()
    for pasta in [inicio, *inicio.parents]:
        if (pasta / '2_INTI/RESEARCH_PROTOCOL.md').is_file():
            return pasta
    raise FileNotFoundError('Abra o VS Code na pasta tese_eco_usp.')


def ler_csv(caminho, ids_embargo=None):
    # Ler como texto preserva códigos, zeros e símbolos de ausência da fonte.
    bruto_ibama = caminho.name.startswith('termo_')
    opcoes = dict(sep=';' if bruto_ibama else ',', encoding='utf-8-sig',
                  dtype='string', keep_default_na=False)
    if caminho.name == 'termo_embargo_historico.csv':
        # Texto descritivo e geometrias grandes não são necessários nesta AED.
        colunas = ['SEQ_TAD', 'SEQ_HIST_TAD', 'DT_ALTERACAO',
                   'DES_STATUS_FORMULARIO', 'SIT_CANCELADO', 'DAT_EMBARGO',
                   'COD_MUNICIPIO', 'MUNICIPIO', 'UF', 'NUM_LONGITUDE_TAD',
                   'NUM_LATITUDE_TAD', 'QTD_AREA_EMBARGADA', 'TIPO_AREA',
                   'SIT_DESEMBARGO', 'DAT_DESEMBARGO', 'SEQ_AUTO_INFRACAO']
        partes = []
        total = 0
        for parte in pd.read_csv(caminho, usecols=colunas, chunksize=50000, **opcoes):
            total += len(parte)
            # A união permite identificar códigos e UFs discordantes depois.
            mt = parte['UF'].str.strip().eq('MT') | parte['COD_MUNICIPIO'].str.startswith('51')
            partes.append(parte.loc[mt].copy())
        resultado = pd.concat(partes, ignore_index=True)
        print(f'Histórico: {total:,} linhas lidas; {len(resultado):,} candidatas a MT.')
        return resultado
    if caminho.name == 'termo_de_embargo_coordenadas.csv':
        partes = []
        for parte in pd.read_csv(caminho, chunksize=50000, **opcoes):
            if ids_embargo is not None:
                parte = parte.loc[parte['SEQ_TAD'].isin(ids_embargo)]
            partes.append(parte.copy())
        return pd.concat(partes, ignore_index=True)
    return pd.read_csv(caminho, **opcoes)


def limpar_base(original):
    base = original.copy()
    for col in base:
        base[col] = base[col].str.strip().replace('', pd.NA)
    # Só cópias idênticas são retiradas. Eventos sem ID não podem ser deduplicados.
    repetidas = base.duplicated()
    if 'SEQ_AUTO_INFRACAO' in base and 'SEQ_TAD' not in base:
        repetidas &= base['SEQ_AUTO_INFRACAO'].notna()
    if 'SEQ_TAD' in base:
        repetidas &= base['SEQ_TAD'].notna()
    print('Linhas inteiramente repetidas retiradas:', int(repetidas.sum()))
    base = base.loc[~repetidas].copy()
    numeros = {
        'ano', 'mes', 'class_id', 'area_ha', 'area_mapeada_ha',
        'native_veg_ha_it', 'native_veg_share_it', 'native_veg_ha_lag1',
        'native_veg_share_lag1', 'valor_original', 'preco_nominal',
        'ln_price', 'dln_price', 'area_colhida_ha', 'area_plantada_ha',
        'producao_t', 'rendimento_medio_kg_ha', 'yield_calculado_kg_ha',
        'valor_medio', 'n_pixels_validos', 'n_autos_ibama_it',
        'n_autos_ibama_espacial', 'n_valores_ausentes', 'valor_multas_ibama_it',
        'valor_multas_ibama_espacial', 'valor_multa_nominal', 'efetivo_bovino',
        'biome_amazonia_share_i', 'biome_cerrado_share_i', 'biome_pantanal_share_i',
        'soma_fracoes', 'precip_mm', 'fracao_pixels_validos', 'precip_mm_anual',
        'count', 'sum', 'elevation_mean_m', 'elevation_min_m', 'elevation_max_m',
        'n_pixels', 'linha_excel', 'coluna_excel',
    }
    numeros.update(c for c in base if c.startswith(('precip_anomaly_', 'precip_zscore_',
                    'precip_deficit_', 'precip_excess_', 'mean_', 'std_', 'count_')))
    brasileiros = {'QTD_AREA_EMBARGADA', 'NUM_LONGITUDE_TAD', 'NUM_LATITUDE_TAD',
                    'LONGITUDE', 'LATITUDE', 'AREA_POLIGONO'}
    for col in base.columns.intersection(list(numeros | brasileiros)):
        texto = base[col]
        if col in brasileiros:
            # Nestes campos, vírgula é separador decimal; não inventar milhares.
            texto = texto.str.replace(',', '.', regex=False)
        convertido = pd.to_numeric(texto, errors='coerce')
        invalidos = texto.notna() & convertido.isna()
        if invalidos.any():
            print(col, ': valores não numéricos preservados em bases_brutas:',
                  texto.loc[invalidos].value_counts().head().to_dict())
        base[col] = convertido.replace([np.inf, -np.inf], np.nan)
    datas = ['data', 'DAT_HORA_AUTO_INFRACAO', 'DT_FATO_INFRACIONAL',
             'DAT_EMBARGO', 'DT_ALTERACAO', 'DAT_DESEMBARGO']
    for col in base.columns.intersection(datas):
        texto = base[col]
        base[col] = pd.to_datetime(texto, errors='coerce', format='mixed')
        print(col, ': datas inválidas =', int((texto.notna() & base[col].isna()).sum()))
    if 'data' in base:
        base['ano'] = base['data'].dt.year.astype('Int64')
        base['mes'] = base['data'].dt.month.astype('Int64')
    if 'COD_MUNICIPIO' in base and 'codigo_ibge' not in base:
        base['codigo_ibge'] = base['COD_MUNICIPIO'].copy()
    if 'DT_ALTERACAO' in base:
        # Ano de alteração do registro: não é uma contagem de embargos novos.
        base['ano'] = base['DT_ALTERACAO'].dt.year.astype('Int64')
    for col in base.columns.intersection(['codigo_ibge', 'codigo_ibge_espacial']):
        base[col] = base[col].astype('string').str.replace(r'\.0$', '', regex=True)
        base[f'{col}_valido'] = base[col].str.fullmatch(r'\d{7}', na=False)
        print(col, ': códigos ausentes/inválidos =', int((~base[f'{col}_valido']).sum()))
    if {'UF', 'codigo_ibge'}.issubset(base):
        base['flag_uf_codigo_divergente'] = base['UF'].eq('MT') != base['codigo_ibge'].str.startswith('51')
        print('Divergências UF/código para MT:', int(base['flag_uf_codigo_divergente'].sum()))
    for col in base.columns.intersection(['ano', 'mes', 'class_id']):
        fracionario = base[col].notna() & base[col].mod(1).ne(0)
        if fracionario.any():
            raise ValueError(f'{col} tem valores fracionários; confira a fonte.')
        base[col] = base[col].astype('Int64')
    for col in base.columns.intersection(['produto', 'variavel', 'biome', 'nivel_insumo',
                                          'regime', 'unidade', 'TIPO_INFRACAO', 'SIT_CANCELADO']):
        base[col] = base[col].astype('category')
    return base


def aplicar_referencia_141(bases, caminhos, raiz):
    """Usa derivados espaciais recalculados; nunca soma médias municipais."""
    pasta = raiz / '2_INTI/xdata/chap1/processed/territorio_141'
    manifesto_path = pasta / 'manifesto141.json'
    if not manifesto_path.is_file():
        raise FileNotFoundError('Execute reconstruir_territorio141.py antes da AED de 141 municípios.')
    manifesto = json.loads(manifesto_path.read_text(encoding='utf-8'))
    cadastro = pd.DataFrame(json.loads((pasta / 'municipios_referencia.json').read_text(encoding='utf-8')))
    codigos = set(cadastro['codigo_ibge'].astype(str))
    if len(codigos) != 141 or '5101837' in codigos:
        raise ValueError('Cadastro territorial incompatível com a referência de 141 municípios.')
    resultado = []
    for base, relativo in zip(bases, caminhos):
        original = raiz / relativo.replace('\\', '/')
        nome = original.name
        if nome in manifesto['arquivos']:
            registro = manifesto['arquivos'][nome]
            derivado = pasta / nome
            for arquivo, esperado in [(original, registro['origem_sha256']), (derivado, registro['derivado_sha256'])]:
                if hashlib.sha256(arquivo.read_bytes()).hexdigest() != esperado:
                    raise ValueError(f'{arquivo.name} mudou. Reconstrua e valide os derivados territoriais.')
            base = limpar_base(ler_csv(derivado))
            print('Referência IBGE 2023 aplicada por reextração espacial:', nome)
        else:
            base = base.copy()
        if 'codigo_ibge' in base:
            novo = base['codigo_ibge'].eq('5101837').fillna(False)
            if novo.any():
                # PAM só registra produção do novo município em 2025, fora do painel.
                if 'pam_soja_milho' not in nome:
                    raise ValueError('Há observações do novo município sem desagregação territorial validada.')
                medidas = ['area_colhida_ha', 'area_plantada_ha', 'producao_t', 'rendimento_medio_kg_ha']
                no_periodo = novo & base['ano'].le(2024)
                if base.loc[no_periodo, medidas].notna().any().any():
                    raise ValueError('PAM tem medidas novas antes de 2025; revisar território antes de redistribuir.')
                print('PAM: retiradas do recorte de 141 apenas linhas vazias de Boa Esperança até 2024 e registros pós-painel.')
                print('Todas as linhas de origem permanecem em bases_fontes_limpas e bases_brutas.')
                base = base.loc[~novo].copy()
            print('Municípios presentes:', base['codigo_ibge'].nunique(), '/ referência de 141')
            fora = base['codigo_ibge'].notna() & ~base['codigo_ibge'].isin(codigos)
            if fora.any():
                print('Códigos fora do cadastro, preservados para conferência:', sorted(base.loc[fora, 'codigo_ibge'].unique()))
        resultado.append(base)
    return resultado, cadastro


def assert_unique(base, chaves):
    if base[chaves].isna().any().any():
        raise ValueError(f'Chave ausente: {chaves}')
    if base.duplicated(chaves).any():
        raise ValueError(f'Chave repetida: {chaves}. Não agregar conflitos automaticamente.')


def harmonizar_codigos(base, correspondencia, chaves):
    """Esqueleto para mapa 1:1 por ano já validado pelo pesquisador."""
    # Não resolve desmembramentos: áreas e totais exigem pesos territoriais próprios.
    assert_unique(correspondencia, ['codigo_ibge', 'ano'])
    out = base.merge(correspondencia[['codigo_ibge', 'ano', 'codigo_harmonizado']],
                     on=['codigo_ibge', 'ano'], how='left', validate='many_to_one')
    if out['codigo_harmonizado'].isna().any():
        raise ValueError('Falta correspondência territorial; não manter código silenciosamente.')
    out['codigo_ibge_original'] = out['codigo_ibge']
    out['codigo_ibge'] = out.pop('codigo_harmonizado').astype('string')
    assert_unique(out, chaves)
    return out


def recortar(base):
    if 'ano' in base:
        print('Linhas sem ano:', int(base['ano'].isna().sum()))
        return base.loc[base['ano'].between(2001, 2024).fillna(False)].copy()
    print('Fonte sem ano validado: sem replicação artificial em 2001–2024.')
    return base.copy()


def diagnosticar(base, valores, chaves):
    if chaves:
        conflitos = base.loc[base.duplicated(chaves, keep=False)]
        print('Linhas com chave repetida:', len(conflitos))
        if len(conflitos):
            display(conflitos.head(10))
    linhas = []
    for col in valores:
        s = base[col]
        linhas.append({'medida': col, 'linhas': len(s), 'ausente_na_linha': int(s.isna().sum()),
                       'zero_registrado': int(s.eq(0).sum()), 'nao_zero': int((s.notna() & s.ne(0)).sum())})
    display(pd.DataFrame(linhas))
    print('Zero registrado não prova zero verdadeiro: conferir a regra da fonte.')
    print('Ausência de cultivo e medida não construída exigem informação própria.')


def lacunas_painel(base, grupos):
    # O universo abaixo contém só municípios presentes na fonte, não todos os de MT.
    if {'data', 'variavel'}.issubset(base):
        grade = pd.DataFrame({'data': pd.date_range('2001-01-01', '2024-12-01', freq='MS')})
        grade = grade.merge(base[['variavel']].dropna().drop_duplicates(), how='cross')
        presentes = base[['data', 'variavel']].drop_duplicates().assign(registro_presente=True)
        cobertura = grade.merge(presentes, on=['data', 'variavel'], how='left', validate='one_to_one')
        faltam = cobertura['registro_presente'].isna()
        print('Meses sem registro de preço em 2001–2024:', int(faltam.sum()))
        display(cobertura.loc[faltam].head(10))
        return
    if not {'codigo_ibge', 'ano'}.issubset(base):
        return
    unidades = ['codigo_ibge'] + grupos
    existentes = base[unidades].dropna().drop_duplicates()
    anos = pd.DataFrame({'ano': pd.Series(range(2001, 2025), dtype='Int64')})
    grade = existentes.merge(anos, how='cross')
    if 'mes' in base:
        grade = grade.merge(pd.DataFrame({'mes': range(1, 13)}), how='cross')
    chave = list(grade.columns)
    presentes = base[chave].drop_duplicates().assign(registro_presente=True)
    cobertura = grade.merge(presentes, on=chave, how='left', validate='one_to_one')
    faltam = cobertura['registro_presente'].isna()
    print('Combinações sem linha no universo observado:', int(faltam.sum()))
    print('Grade diagnóstica; não preenche os dados nem comprova existência histórica do município.')
    display(cobertura.loc[faltam].head(10))


def rotular_grupos(base, grupos):
    out = base.copy()
    if grupos:
        out['_grupo'] = out[grupos].astype('string').fillna('(ausente)').agg(' | '.join, axis=1)
    else:
        out['_grupo'] = 'Todas as observações'
    return out


def grupos_para_grafico(base):
    grupos = sorted(base['_grupo'].dropna().unique())
    if len(grupos) > MAX_GRUPOS_GRAFICOS:
        print(f'Gráficos limitados aos primeiros {MAX_GRUPOS_GRAFICOS} de {len(grupos)} grupos, em ordem.')
        print('Aumente MAX_GRUPOS_GRAFICOS na fase 1 para mostrar todos.')
    return grupos[:MAX_GRUPOS_GRAFICOS]


def graficos_univariados(base, valores, grupos, unidades):
    plot = rotular_grupos(base, grupos)
    labels = grupos_para_grafico(plot)
    # Painéis separados evitam misturar culturas, classes e cenários.
    for col in valores:
        for label in labels:
            sub = plot.loc[plot['_grupo'].eq(label)]
            s = sub[col].dropna().astype(float)
            if s.empty:
                print('Sem valores para plotar:', col, label)
                continue
            fig, axes = plt.subplots(1, 2, figsize=(11, 3))
            sns.histplot(x=s, bins=30, ax=axes[0])
            sns.boxplot(x=s, ax=axes[1])
            for ax in axes:
                ax.set_xlabel(f'{col} ({unidades.get(col, "ver dicionário")})')
            fig.suptitle(f'{col} — {label}')
            fig.tight_layout()
            plt.show()
            plt.close(fig)
    print('Extremos são sinalizados pelo boxplot; nenhum foi removido ou winsorizado.')


def graficos_tempo(base, valores, grupos, unidades):
    if 'ano' not in base:
        print('Sem dimensão temporal validada nesta fonte.')
        return
    plot = rotular_grupos(base, grupos)
    selecionados = grupos_para_grafico(plot)
    plot = plot.loc[plot['_grupo'].isin(selecionados)]
    for col in valores:
        fig, ax = plt.subplots(figsize=(11, 4))
        for label, sub in plot.groupby('_grupo', observed=True):
            serie = sub.groupby('ano', observed=True)[col].median().reindex(range(2001, 2025))
            ax.plot(serie.index, serie.to_numpy(dtype=float, na_value=np.nan), label=label)
        ax.set(xlabel='Ano', ylabel=f'Mediana de {col} ({unidades.get(col, "ver dicionário")})',
               title='Evolução descritiva: observações disponíveis em cada ano', xlim=(2001, 2024))
        ax.legend(fontsize=7, loc='upper left', bbox_to_anchor=(1, 1))
        fig.tight_layout()
        plt.show()
        plt.close(fig)
    print('Medianas descritivas; composição da amostra pode variar. Não são agregações finais.')
    cobertura = base.groupby('ano', observed=True).size().rename('n_linhas').reindex(range(2001, 2025))
    display(cobertura.to_frame())


def graficos_bivariados(base, valores, grupos, unidades):
    if not valores or base.empty:
        print('Sem medida pronta para comparação bivariada.')
        return
    plot = rotular_grupos(base, grupos)
    selecionados = grupos_para_grafico(plot)
    plot = plot.loc[plot['_grupo'].isin(selecionados)]
    if {'codigo_ibge', 'ano'}.issubset(base):
        # Até 20 códigos em ordem: exemplo legível, sem pretensão de representatividade.
        for label, sub in plot.groupby('_grupo', observed=True):
            codigos = sorted(sub['codigo_ibge'].dropna().unique())[:20]
            for col in valores:
                matriz = sub.loc[sub['codigo_ibge'].isin(codigos)].pivot_table(
                    index='codigo_ibge', columns='ano', values=col, aggfunc='median', observed=True)
                matriz = matriz.reindex(index=codigos, columns=range(2001, 2025))
                if matriz.empty or not matriz.notna().any().any():
                    continue
                fig, ax = plt.subplots(figsize=(12, 6))
                sns.heatmap(matriz.astype(float), mask=matriz.isna(), cmap='viridis', ax=ax,
                            cbar_kws={'label': unidades.get(col, col)})
                ax.set_title(f'{col} por município e ano — {label}\nMediana; branco = ausente')
                fig.tight_layout()
                plt.show()
                plt.close(fig)
    elif 'codigo_ibge' in base:
        for label, sub in plot.groupby('_grupo', observed=True):
            for col in valores:
                pequeno = sub.sort_values('codigo_ibge').head(20)
                fig, ax = plt.subplots(figsize=(10, 4))
                sns.barplot(data=pequeno, x='codigo_ibge', y=col, errorbar=None, ax=ax)
                ax.tick_params(axis='x', rotation=90)
                ax.set_title(f'{col} — {label}; primeiros 20 códigos (estático)')
                ax.set_ylabel(unidades.get(col, col))
                fig.tight_layout()
                plt.show()
                plt.close(fig)
    elif {'data', 'variavel', 'preco_nominal'}.issubset(base):
        assert_unique(base, ['data', 'variavel'])
        largo = base.pivot(index='data', columns='variavel', values='preco_nominal')
        if largo.shape[1] == 2:
            fig, ax = plt.subplots(figsize=(5, 4))
            sns.scatterplot(data=largo, x=largo.columns[0], y=largo.columns[1], ax=ax)
            ax.set_title('Preços mensais: associação descritiva, USD/t')
            plt.show()
            plt.close(fig)
        else:
            sazonal = base.assign(mes=base['data'].dt.month)
            fig, ax = plt.subplots(figsize=(8, 4))
            sns.boxplot(data=sazonal, x='mes', y='preco_nominal', ax=ax)
            ax.set_title('Preço mensal por mês do calendário; USD/kg')
            plt.show()
            plt.close(fig)
    elif 'aba' in base:
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(data=base.head(20), y='aba', x=valores[0], errorbar=None, ax=ax)
        ax.set_title('Cobertura de até 20 abas; ainda não é uma comparação de custos')
        fig.tight_layout()
        plt.show()
        plt.close(fig)
