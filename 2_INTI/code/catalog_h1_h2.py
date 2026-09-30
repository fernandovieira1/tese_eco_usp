"""Build file/variable catalogues, validation evidence and requirement matrix.

Run after acquisitions and processing. CSV is the canonical catalogue for XLSX export.
"""
import csv,json,hashlib,subprocess,re,zipfile
from pathlib import Path
import pandas as pd
import numpy as np
from data_common import DATA,ROOT,sha256,write_json

CAT=DATA/'catalog'
COLUMNS='nome_da_variavel descricao fonte link_dado_original periodo periodicidade hipotese papel tipo_variavel unidade granularidade_espacial arquivo_local formato_arquivo versao_fonte data_acesso status resolucao_espacial sistema_referencia_crs observacoes'.split()
DESCRIPTIONS={
 'codigo_ibge':'Codigo territorial IBGE de sete digitos; identificador textual, sem harmonizacao historica automatica.',
 'municipio':'Nome do municipio na fonte ou no cadastro IBGE associado.',
 'ano':'Ano civil informado na serie; em autos IBAMA, ano da lavratura.',
 'mes':'Mes civil da acumulacao de precipitacao, de 1 a 12.',
 'produto':'Produto agropecuario identificado pela categoria SIDRA.',
 'producao_t':'Quantidade produzida informada pela PAM, em toneladas.',
 'area_plantada_ha':'Area plantada informada pela PAM, em hectares.',
 'area_colhida_ha':'Area colhida informada pela PAM, em hectares.',
 'rendimento_medio_kg_ha':'Rendimento medio publicado pelo IBGE/PAM.',
 'yield_soja_kg_ha_it':'Rendimento publicado apenas para soja; missing nas linhas de milho.',
 'yield_calculado_kg_ha':'Producao em toneladas multiplicada por 1000 e dividida pela area colhida positiva.',
 'yield_diferenca_kg_ha':'Rendimento calculado menos rendimento publicado; verificacao de consistencia.',
 'efetivo_bovino':'Efetivo do rebanho bovino publicado pela PPM, em cabecas.',
 'native_veg_ha_it':'Soma municipal das areas de classes nativas candidatas 3,4,5,6,49,11,12,50.',
 'native_veg_share_it':'Area nativa candidata dividida pela soma de todas as classes mapeadas no municipio e ano.',
 'native_veg_ha_lag1':'Area nativa do ano imediatamente anterior, exigindo continuidade anual dentro do codigo.',
 'native_veg_share_lag1':'Fracao nativa do ano imediatamente anterior, exigindo continuidade anual dentro do codigo.',
 'area_mapeada_ha':'Soma das areas de todas as classes e biomas do municipio no XLSX MapBiomas.',
 'class_id':'Codigo de classe MapBiomas, cuja legenda original esta preservada.',
 'area_ha':'Area de uma classe MapBiomas na intersecao municipio-bioma-ano, em hectares.',
 'precip_mm':'Media municipal ponderada por cos(latitude) da precipitacao acumulada mensal CHIRPS.',
 'fracao_pixels_validos':'Soma dos pesos de pixels validos dividida pela soma dos pesos dos pixels atribuidos ao municipio.',
 'precip_mm_anual':'Soma dos 12 totais mensais de precipitacao municipal; missing se faltam meses.',
 'preco_nominal':'Preco mensal original em USD, com unidade comercial identificada na coluna unidade.',
 'valor_original':'Valor ou simbolo exatamente preservado da fonte antes de conversao numerica.',
 'ln_price':'Logaritmo natural do preco nominal estritamente positivo.',
 'dln_price':'Diferenca mensal do logaritmo natural, dentro de cada produto internacional.',
 'n_autos_ibama_it':'Contagem de registros IBAMA com ID valido, por municipio declarado e ano de lavratura, todos status.',
 'valor_multas_ibama_it':'Soma dos valores nominais disponiveis dos autos elegiveis; nao mede pagamento ou multa efetivamente cobrada.',
 'n_autos_ibama_espacial':'Contagem de autos com ID valido e ponto dentro de municipio da malha 2024, por ano de lavratura.',
 'valor_multas_ibama_espacial':'Soma nominal disponivel na variante espacial; municipio definido pelo ponto, com datum ainda provisório.',
 'codigo_ibge_espacial':'Codigo da malha 2024 contendo o ponto; missing se nenhum poligono contem a coordenada.',
 'diverge_codigo_informado':'Indica divergencia entre codigo municipal informado e codigo obtido da coordenada.',
 'valor_multa_nominal':'Conversao do campo VAL_AUTO_INFRACAO de virgula decimal para numero, sem deflator.',
 'flag_id_duplicado':'ID repetido no arquivo de eventos, incluindo repeticoes do ID vazio; todos os casos permanecem identificados.',
 'flag_id_ausente':'Identificador do auto vazio na fonte original.',
 'flag_codigo_mt':'Codigo informado tem sete digitos e prefixo 51; nao certifica compatibilidade historica.',
 'n_valores_ausentes':'Quantidade de autos elegiveis sem valor monetario numerico no grupo.',
 'variavel_raster':'Nome exato do raster GAEZ que identifica variavel, manejo, regime, CO2 e cultura.',
 'valor_medio':'Media municipal ponderada por cos(latitude) do raster GAEZ identificado; unidade varia entre sx e yx.',
 'n_pixels_validos':'Numero de centros de pixel validos incluidos na agregacao espacial.',
 'elevation_mean_m':'Media de elevacao DSM GLO-90 sobre centros de pixels dentro do municipio.',
 'elevation_min_m':'Menor elevacao DSM valida entre os pixels municipais.',
 'elevation_max_m':'Maior elevacao DSM valida entre os pixels municipais.',
 'n_pixels':'Quantidade de pixels DSM incluidos na agregacao.',
 'soma_fracoes':'Soma das fracoes municipais dos tres biomas; lacunas nao renormalizadas.',
 'linha_excel':'Numero de linha, base 1, da celula na planilha CONAB original.',
 'coluna_excel':'Numero de coluna, base 1, da celula na planilha CONAB original.',
 'conteudo':'Conteudo da celula nao vazia da planilha CONAB; nao e automaticamente um custo comparavel.',
 'aba':'Nome original da aba que identifica local, ano e possivelmente tecnologia.',
 'harmonizacao_historica_validada':'Sempre falso nesta entrega; cadastro de presenca nao constitui crosswalk historico.',
}

SPECS=[
 ('H1','conv_total_it conv_agric_it conv_past_it','CORE','MapBiomas Brasil','https://brasil.mapbiomas.org/downloads/estatisticas/','municipio','anual','1985-2024 cobertura; transicoes nao obtidas','LACUNA','Obter transicoes pixel a pixel da mesma colecao e denominador nativo t-1; diferenca de estoques nao serve.'),
 ('H1-a','price_soja_t price_milho_t price_boi_t','CORE','CEPEA / IMEA / CONAB','https://www.gov.br/conab/pt-br/atuacao/informacoes-agropecuarias/precos-agropecuarios','mercado/regiao','diaria/mensal','serie local nao obtida','LACUNA','CEPEA HTTP403; IMEA falha TLS; CONAB consulta com codigo de seguranca. Pink Sheet nao substitui retorno local.'),
 ('H1-a','price_soja price_milho price_carne_bovina ln_price dln_price','ROBUSTEZ','Banco Mundial','https://www.worldbank.org/en/research/commodity-markets','internacional','mensal','1960-01 a 2026-08','OBTIDA','USD nominal; carne bovina internacional nao e boi gordo MT; dln mensal, sem indice de retorno.'),
 ('H1-a','suitability_soja_i suitability_milho_i potential_yield_soja_i potential_yield_milho_i','CORE','FAO/IIASA','https://www.fao.org/gaez/gaezv4/en','raster/municipio','periodo-base','clima 1961-1990; base de terras v4 de 2010','CANDIDATA','sx 0-10000 e yx kg materia seca/ha; sequeiro; alto/baixo insumo; sem CO2. Base 2010 nao e automaticamente predeterminada para 1985.'),
 ('H1-a','efetivo_bovino','CONTROLE','IBGE/PPM','https://sidra.ibge.gov.br/tabela/3939','municipio','anual','1974-2025 requisitado; cobertura efetiva no perfil','OBTIDA','Preservar valores e simbolos SIDRA; periodo-base da proxy pecuaria ainda nao escolhido.'),
 ('H1-a','shock_return_it','CORE','Derivacao futura','https://www.fao.org/gaez/gaezv4/en','municipio','anual','nao definido','NAO_CONSTRUIDA','Soma dln(P[k,t-1])*S[i,k]; faltam preco local, escala, produtos e base pecuaria; nao somar indices heterogeneos.'),
 ('H1','cost_soja cost_milho','ROBUSTEZ','CONAB','https://www.gov.br/conab/pt-br/atuacao/informacoes-agropecuarias/custos-de-producao/planilhas-de-custos-de-producao','local/tecnologia','safra','soja 1997-2026; milho 1997-2025 e 2005-2025 nos nomes oficiais','BRUTA','Planilhas multicidades e tecnologias; verificar unidade e mudancas por aba antes de concatenar.'),
 ('H1','cost_pecuaria','ROBUSTEZ','IMEA','https://wap.imea.com.br/imea-site/relatorios-mercado','regiao','a verificar','nao confirmado','LACUNA','Fonte investigada; sem serie comparavel validada.'),
 ('H1-b','n_autos_ibama_it valor_multas_ibama_it','CORE','IBAMA','https://dadosabertos.ibama.gov.br/dataset/fiscalizacao-auto-de-infracao','municipio','evento/anual','ver perfil validacao','CANDIDATA','Municipio informado; data lavratura; todos status; zeros nao preenchidos; endogeneidade e geocodificacao pendentes.'),
 ('H1-b','n_embargos_ibama_it area_embargada_ibama_it','CORE','IBAMA','https://dadosabertos.ibama.gov.br/dataset/fiscalizacao-termo-de-embargo','evento/municipio','evento/anual','historico e coordenadas baixados; principal falhou','PARCIAL','Tabela principal e SHP oficial HTTP404; nao inferir numero de embargos do numero de coordenadas/historicos.'),
 ('H1-b','municipio_prioritario_amazonia_it municipio_prioritario_cerrado_it municipio_sob_controle_it','CORE','MMA','https://www.gov.br/mma/pt-br/assuntos/controle-ao-desmatamento-queimadas-e-ordenamento-ambiental-territorial/controle-do-desmatamento-1/municipios-prioritarios-da-amazonia','municipio','eventos normativos','historico nao reconstruido','PARCIAL','Pagina atual preservada; documento historico retornou HTML; lista responde ao desmatamento, nao e exogena.'),
 ('H1-b','car_regularizacao_it','EXPLORATORIA','SFB/SICAR','https://www.gov.br/car/pt-br/central-de-conteudo/boletins-informativos-do-car','imovel/municipio','estoques em datas','nao confirmado','LACUNA','COBERTURA TEMPORAL INSUFICIENTE PARA O PAINEL PRINCIPAL; nao retroceder estoque atual. HTTP401 na aquisicao.'),
 ('H1/H2','elevation_i','CONTROLE','Copernicus','https://registry.opendata.aws/copernicus-dem/','raster/municipio','estatica','estatica','CANDIDATA','GLO-90 DSM, inclui vegetacao/edificacoes; media por centros de pixel; nao e modelo de terreno nu.'),
 ('H1/H2','slope_i terrain_ruggedness_i','ROBUSTEZ','Copernicus','https://registry.opendata.aws/copernicus-dem/','raster/municipio','estatica','estatica','INSUMO_OBTIDO','Rasters DEM preservados. Derivadas requerem metrica, projecao, vizinhanca e validacao; nao calculadas.'),
 ('H2','yield_soja_kg_ha_it producao_t area_plantada_ha area_colhida_ha rendimento_medio_kg_ha','CORE','IBGE/PAM','https://sidra.ibge.gov.br/tabela/1612','municipio','anual','1974-2025 requisitado; cobertura por variavel no perfil','OBTIDA','PAM sem mistura RAMMT; rendimento calculado confrontado com publicado; simbolos originais preservados.'),
 ('H2','precip_mm','CORE','UCSB Climate Hazards Center','https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_monthly/tifs/','raster/municipio','mensal','1981-2025 alvo de aquisicao','CANDIDATA','v2 separado; malha2024, centros de pixel e pesos cos(latitude); nivel fisico nao e choque.'),
 ('H2','precip_anomaly precip_zscore precip_deficit precip_excess','CORE','UCSB Climate Hazards Center','https://chc.ucsb.edu/data/chirps/','municipio','anual candidato','depende de 30 anos completos','CANDIDATA','Alternativas 1981-2010 e 1991-2020; ano civil exploratorio; deficit/excesso nao publicados como balanco hidrico.'),
 ('H2','temp_mean temp_max temp_min heat_extreme_days','ROBUSTEZ','Copernicus/ERA5-Land','https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land-monthly-means?tab=overview','raster/municipio','horaria/mensal','1950-presente na fonte; nao adquirido','REQUER_ACESSO','Sem .cdsapirc; exige conta/aceite CDS; pedido preparado para media mensal. Extremos diarios exigem horarios.'),
 ('H2','water_deficit','ROBUSTEZ','Derivacao meteorologica','https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land-monthly-means?tab=overview','municipio','janela agricola','nao definido','NAO_CONSTRUIDA','Nenhuma formula consolidada encontrada; nao equiparar deficit de chuva a balanco hidrico.'),
 ('H2','native_veg_ha_it native_veg_share_it native_veg_ha_lag1 native_veg_share_lag1','CORE','MapBiomas Brasil','https://doi.org/10.58053/MapBiomas/SJZOLT','municipio','anual','1985-2024; lag 1986-2024','CANDIDATA','Colecao10.1; classes 3,4,5,6,49,11,12,50; denominador soma classes; 9 linhas em quarentena; 141 municipios.'),
 ('H2-a','biome_amazonia_share_i biome_cerrado_share_i biome_pantanal_share_i biome_class_i','CORE','IBGE','https://geoftp.ibge.gov.br/informacoes_ambientais/estudos_ambientais/biomas/vetores/','municipio','estatica','biomas2019 / malha2024','CANDIDATA','Area EPSG5880; classes70/80/90%; 142 municipios; vintage2019 mantido separado da atualizacao2025.'),
 ('H2','calendario_soja','CONTROLE','MAPA/ZARC','https://www.gov.br/agricultura/pt-br/assuntos/riscos-seguro/programa-nacional-de-zoneamento-agricola-de-risco-climatico/portarias/2025-2026/mato-grosso-mt','municipio/solo/ciclo','safra','2025/2026 obtida','BRUTA','Portaria372; nao aplicar janela contemporanea retroativamente; extracao de todas safras ainda pendente.'),
 ('H2','validacao_inmet','ROBUSTEZ','INMET','https://portal.inmet.gov.br/dadoshistoricos','estacao','horaria','nao auditado por estacao','FONTE_INVESTIGADA','Requer selecao de estacoes e continuidade; nao coletar indiscriminadamente.'),
 ('H1/H2','credito_rural','CONTROLE','BCB/SICOR','https://www.bcb.gov.br/estabilidadefinanceira/tabelas-credito-rural-proagro','operacao/municipio','evento','desde2013 na fonte','FONTE_INVESTIGADA','Nao coletado sem fundamento de inclusao; pode ser mecanismo endogeno, nao controle automatico.'),
]

def spec_for(path):
    s=str(path).lower()
    tests=[('pam_',14),('t1612',14),('ppm',4),('t3939',4),('worldbank',2),('prices',2),('gaez',3),('conab',6),('copdem',12),('topography',12),('autos',8),('auto_infracao',8),('embargo',9),('ibama',8),('chirps',15),('era5',17),('biom',20),('zarc',21),('mma',10),('car_',11),('inmet',22),('bcb',23)]
    if 'mapbiomas' in s or 'native_veg' in s:return SPECS[19]
    for token,i in tests:
        if token in s:return SPECS[i]
    return ('H1/H2','metadados','CONTROLE','IBGE','https://servicodados.ibge.gov.br/','municipio','estatica','nao aplicavel','METADADOS','Documento auxiliar; nao e variavel econometrica.')

def main():
    manifests=[]
    for p in sorted(CAT.glob('acquisition*.jsonl')):
        for line in p.read_text(encoding='utf-8').splitlines():
            r=json.loads(line);r['manifesto']=p.name;manifests.append(r)
    provenance={r['arquivo_local']:r for r in manifests if r.get('status')=='BAIXADO'}
    failures=[r for r in manifests if r.get('status')=='FALHA']
    write_json('catalog/falhas_aquisicao_h1_h2.json',failures)
    matrix=[]
    for h,variables,priority,source,url,spatial,freq,period,status,note in SPECS:
        for variable in variables.split():
            matrix.append(dict(hipotese=h,variavel_conceitual=variable,variavel_operacional=variable,prioridade=priority,fonte_preferencial=source,fonte_alternativa='ver alternativas e relatorio',granularidade_espacial=spatial,periodicidade_original=freq,periodicidade_analitica='estatica' if freq=='estatica' else 'anual; a validar',periodo_disponivel=period,periodo_utilizavel='nao homologado; ver perfis',status_no_repositorio=status,arquivo_existente='',acao_necessaria=note,observacao_metodologica=note))
    inventory=[];catalog=[];profiles=[]
    for p in sorted(DATA.rglob('*')):
        if not p.is_file() or 'catalog' in p.relative_to(DATA).parts:continue
        rel=p.relative_to(ROOT).as_posix();prov=provenance.get(rel,{})
        h,variables,priority,source,url,spatial,freq,period,status,note=spec_for(p)
        digest=sha256(p)
        verified=prov.get('sha256')==digest if prov else None
        magic=p.open('rb').read(12)
        valid_format=not (p.suffix.lower()=='.pdf' and not magic.startswith(b'%PDF'))
        record=dict(arquivo=rel,bytes=p.stat().st_size,sha256=digest,hash_confere_manifesto=verified,formato_valido=valid_format,fonte=source,url=prov.get('url',url),data_acesso=prov.get('data_acesso',''),versao=prov.get('versao',''),nome_local=p.name,licenca_restricoes='CC BY 4.0' if 'mapbiomas' in rel else 'ver termos da fonte; nao presumir dominio publico',status='FORMATO_INCORRETO_PRESERVADO' if not valid_format else ('BRUTO' if '/raw/' in rel else 'DERIVADO'))
        inventory.append(record)
        crs='';resolution=''; columns=[]
        if p.suffix=='.tif':
            import rasterio
            with rasterio.open(p) as src:
                crs=str(src.crs);resolution=str(src.res)
        if p.name in ['MT_Municipios_2024.zip','Biomas_250mil_2019.zip']:crs='EPSG:4674'
        if p.suffix=='.csv' and '/processed/' in rel:
            d=pd.read_csv(p,low_memory=False,dtype={'codigo_ibge':str})
            if d.empty:continue
            columns=list(d.columns)
            keys=['codigo_ibge'] if 'codigo_ibge' in d else []
            for k in ['ano','mes','produto','class_id','biome','variavel_raster','variavel','data']:
                if k in d:keys.append(k)
            if 'SEQ_AUTO_INFRACAO' in d:keys=['SEQ_AUTO_INFRACAO']
            if 'linha_excel' in d:keys=['arquivo_origem','aba','linha_excel','coluna_excel']
            if 'quarentena' in p.name:keys=['municipality','biome','class_id']
            if not keys:keys=list(d.columns)
            if 'ano' in d:period=f'{d.ano.min()}-{d.ano.max()}'
            elif 'data' in d:period=f'{d.data.min()} a {d.data.max()}'
            numeric=d.select_dtypes(include='number')
            stats={c:{str(k):float(v) if pd.notna(v) else None for k,v in numeric[c].describe(percentiles=[.01,.25,.5,.75,.99]).items()} for c in numeric}
            outliers={c:int(((numeric[c]<numeric[c].quantile(.25)-1.5*(numeric[c].quantile(.75)-numeric[c].quantile(.25))) | (numeric[c]>numeric[c].quantile(.75)+1.5*(numeric[c].quantile(.75)-numeric[c].quantile(.25)))).sum()) for c in numeric}
            coverage=[]
            if 'codigo_ibge' in d and 'ano' in d:
                for code,g in d.groupby('codigo_ibge'):
                    years=sorted(int(y) for y in g.ano.dropna().unique())
                    coverage.append({'codigo_ibge':code,'ano_min':min(years) if years else None,'ano_max':max(years) if years else None,'anos_ausentes_internos':sorted(set(range(min(years),max(years)+1))-set(years)) if years else []})
            profiles.append({'arquivo':rel,'n':len(d),'schema':{c:str(t) for c,t in d.dtypes.items()},'chaves':keys,'duplicatas':int(d.duplicated(keys).sum()),'municipios':int(d.codigo_ibge.nunique()) if 'codigo_ibge' in d else None,'periodo':period,'missing':d.isna().sum().to_dict(),'estatisticas':stats,'outliers_iqr_apenas_sinalizacao':outliers,'cobertura':coverage})
        for col in columns or [p.stem]:
            col_period=period
            if columns and 'ano' in d and col in d.select_dtypes(include='number').columns:
                valid_years=d.loc[d[col].notna(),'ano'].dropna()
                col_period=f'{int(valid_years.min())}-{int(valid_years.max())}' if len(valid_years) else 'sem valores numericos validos'
            kind='AGREGADA' if '/processed/' in rel else 'OBSERVADA'
            if any(token in p.name for token in ['pam_soja','ppm_bovinos','prices__worldbank','eventos_MT']):kind='OBSERVADA'
            if any(t in col for t in ['lag1','share','anomaly','zscore','ln_price','diferenca','calculado','class_']):kind='DERIVADA'
            unit='nao aplicavel / ver dicionario da fonte'
            if 'kg_ha' in col:unit='kg/ha'
            elif 'ha' in col and 'share' not in col and 'class' not in col:unit='ha'
            elif 'share' in col:unit='fracao 0-1'
            elif 'precip' in col and 'zscore' not in col:unit='mm'
            elif 'multa' in col and 'valor' in col:unit='moeda nominal da fonte; nao deflacionada'
            elif col=='producao_t':unit='t'
            elif col=='efetivo_bovino':unit='cabecas'
            elif col.startswith('elevation'):unit='m'
            if 'chirps' in rel:
                crs=crs or 'EPSG:4326';resolution=resolution or '0.05 grau'
                if p.name.startswith('chirps-v2.0.'):
                    period=p.name[12:19].replace('.','-');unit='mm/mes'
            row=dict(zip(COLUMNS,['']*len(COLUMNS)))
            row.update(nome_da_variavel=col,descricao=col+'; '+note,fonte=source,link_dado_original=prov.get('url',url),periodo=col_period,periodicidade=freq,hipotese=h,papel=priority,tipo_variavel=kind,unidade=unit,granularidade_espacial=spatial,arquivo_local=rel,formato_arquivo='GeoTIFF.gz' if p.name.endswith('.tif.gz') else p.suffix.removeprefix('.'),versao_fonte=prov.get('versao','ver nome do arquivo e linhagem'),data_acesso=prov.get('data_acesso','ver manifesto dos inputs'),status=record['status'] if not valid_format else status,resolucao_espacial=resolution,sistema_referencia_crs=crs,observacoes=note)
            if p.name.startswith('chirps-v2.0.'):row['periodo']=period
            if col in DESCRIPTIONS:row['descricao']=DESCRIPTIONS[col]
            if col.endswith('__original'):row['descricao']='Valor ou simbolo original SIDRA para '+col.removesuffix('__original')+'; nao imputado.'
            if col.startswith('biome_') and col.endswith('_share_i'):row['descricao']='Area de '+col[6:-8]+' na intersecao com o municipio dividida pela area municipal inteira em EPSG:5880.'
            if col.startswith('biome_class_'):row['descricao']='Bioma com maior fracao se ela atinge '+col.rsplit('_',1)[-1]+'%; caso contrario, misto.'
            if col.startswith('precip_anomaly_'):row['descricao']='Total anual menos media climatologica '+col.removeprefix('precip_anomaly_').replace('_','-')+'; exige 30 anos completos.';row['tipo_variavel']='DERIVADA'
            if col.startswith('precip_zscore_'):row['descricao']='Anomalia dividida pelo desvio-padrao amostral da normal indicada, com 30 anos completos.';row['unidade']='desvios-padrao';row['tipo_variavel']='DERIVADA'
            if col.startswith('precip_deficit_'):row['descricao']='max(-anomalia, 0), preservando missing; deficit de precipitacao, nao balanco hidrico.';row['tipo_variavel']='DERIVADA'
            if col.startswith('precip_excess_'):row['descricao']='max(anomalia, 0), preservando missing; excesso de precipitacao.';row['tipo_variavel']='DERIVADA'
            if 'collection9_' in rel:row['periodo']='1985-2023';row['observacoes']='Alternativa colecao9 preservada; XLSX nao contem transicoes, apesar do titulo do dataset.'
            if '/chirps_v2_mt/' in rel:row['status']='INTERMEDIARIO_SUPERADO';row['observacoes']='Recorte exploratorio com arredondamento; substituido aditivamente por chirps_v2_mt_fullbounds, sem apagar o arquivo.'
            if p.suffix in ['.html','.json','.xml'] or 'source_documents' in rel:row['papel']='DOCUMENTACAO';row['tipo_variavel']='NAO_APLICAVEL'
            if 'gaez_v4_6190' in rel:
                row['unidade']='indice 0-10000' if 'sx' in p.name else 'kg materia seca/ha'
            if 'copdem90' in rel and p.suffix=='.tif':row['unidade']='m';row['periodicidade']='estatica'
            if '/raw/raster/' in rel and (p.suffix=='.tif' or p.name.endswith('.tif.gz')):
                row['granularidade_espacial']='tile geoespacial' if 'copdem' in rel else 'raster global'
            if '/raw/vector/' in rel and p.suffix=='.zip':row['formato_arquivo']='Shapefile (ZIP)'
            if 'auto_infracao_csv.zip' in rel:row['formato_arquivo']='CSV (ZIP)'
            if p.name.endswith(('.part','.interrupted')):row['status']='DOWNLOAD_INCOMPLETO_NAO_USAR'
            catalog.append(row)
    for row in matrix:
        found=[c['arquivo_local'] for c in catalog if c['nome_da_variavel']==row['variavel_operacional']]
        aliases={
            'suitability_soja_i':('h1__suitability_yield__gaez_v4_6190__candidatos.csv','valor_medio; variavel_raster=sxHr0_soy/sxLr0_soy'),
            'suitability_milho_i':('h1__suitability_yield__gaez_v4_6190__candidatos.csv','valor_medio; variavel_raster=sxHr0_mze/sxLr0_mze'),
            'potential_yield_soja_i':('h1__suitability_yield__gaez_v4_6190__candidatos.csv','valor_medio; variavel_raster=yxHr0_soy/yxLr0_soy'),
            'potential_yield_milho_i':('h1__suitability_yield__gaez_v4_6190__candidatos.csv','valor_medio; variavel_raster=yxHr0_mze/yxLr0_mze'),
            'elevation_i':('topography__copdem90__municipio_candidato.csv','elevation_mean_m'),
            'biome_class_i':('h2__biome_share__ibge2019_malha2024__candidato.csv','biome_class_70; biome_class_80; biome_class_90'),
            'precip_anomaly':('h2__precip_anomaly__chirps_v2__ano_civil_candidatos.csv','precip_anomaly_1981_2010; precip_anomaly_1991_2020'),
            'precip_zscore':('h2__precip_anomaly__chirps_v2__ano_civil_candidatos.csv','precip_zscore_1981_2010; precip_zscore_1991_2020'),
            'precip_deficit':('h2__precip_anomaly__chirps_v2__ano_civil_candidatos.csv','precip_deficit_1981_2010; precip_deficit_1991_2020'),
            'precip_excess':('h2__precip_anomaly__chirps_v2__ano_civil_candidatos.csv','precip_excess_1981_2010; precip_excess_1991_2020'),
            'price_soja':('h1__prices__worldbank__mensal_robustez.csv','preco_nominal; variavel=price_soja'),
            'price_milho':('h1__prices__worldbank__mensal_robustez.csv','preco_nominal; variavel=price_milho'),
            'price_carne_bovina':('h1__prices__worldbank__mensal_robustez.csv','preco_nominal; variavel=price_carne_bovina'),
        }
        if row['variavel_conceitual'] in aliases:
            fname,actual=aliases[row['variavel_conceitual']]
            found=['2_INTI/data/processed/tabular/'+fname];row['variavel_operacional']=actual
        row['arquivo_existente']=';'.join(sorted(set(found)))
        if not found:
            r=dict.fromkeys(COLUMNS,'')
            r.update(nome_da_variavel=row['variavel_operacional'],descricao=row['observacao_metodologica'],fonte=row['fonte_preferencial'],link_dado_original=next(s[4] for s in SPECS if row['variavel_operacional'] in s[1].split()),periodo=row['periodo_disponivel'],periodicidade=row['periodicidade_original'],hipotese=row['hipotese'],papel=row['prioridade'],tipo_variavel='DERIVADA' if row['status_no_repositorio']=='NAO_CONSTRUIDA' else 'A_DEFINIR',granularidade_espacial=row['granularidade_espacial'],status=row['status_no_repositorio']+'; nome conceitual, consultar variantes',observacoes='Sem arquivo com este nome operacional exato; nao indica dado analitico pronto.')
            catalog.append(r)
    carbon=dict.fromkeys(COLUMNS,'')
    carbon.update(nome_da_variavel='Emissions in billion metric tons',descricao='Emissoes globais contextuais; 86 linhas, sem fonte autenticada no arquivo.',fonte='NAO_IDENTIFICADA_NO_ARQUIVO',periodo='1940-2025',periodicidade='anual',hipotese='CONTEXTO',papel='CONTEXTO',tipo_variavel='OBSERVADA',unidade='bilhoes de toneladas metricas',granularidade_espacial='global',arquivo_local='1_SUYANA/data/carbon_emissions.xlsx',formato_arquivo='xlsx',status='NAO_APROVEITAR_NO_PAINEL_H1_H2',observacoes='Original preservado fora de 2_INTI/data; nenhum dado novo fora da pasta exigida.')
    catalog.append(carbon)
    for variable,unit in [('price_soja','USD/t'),('price_milho','USD/t'),('price_carne_bovina','USD/kg')]:
        template=next(r for r in catalog if r['nome_da_variavel']=='preco_nominal')
        r=template.copy();r.update(nome_da_variavel=variable,unidade=unit,descricao='Valor de preco_nominal nas linhas em que variavel='+variable+'; mercado internacional, sem deflator.')
        catalog.append(r)
    for r in catalog:
        if re.match(r'^\d{4}-\d{2}-\d{2}T',r['data_acesso']):r['data_acesso']='UTC: '+r['data_acesso']
    catalog.sort(key=lambda r:(0 if '/processed/' in r['arquivo_local'] else 1 if r['arquivo_local'] else 2,r['arquivo_local'],r['nome_da_variavel']))
    pd.DataFrame(matrix).to_csv(CAT/'matriz_dados_h1_h2.csv',index=False,encoding='utf-8-sig')
    pd.DataFrame(inventory).to_csv(CAT/'inventario_arquivos_dados_h1_h2.csv',index=False,encoding='utf-8-sig')
    pd.DataFrame(catalog,columns=COLUMNS).to_csv(CAT/'data_catalogo_variaveis_h1_h2.csv',index=False,encoding='utf-8-sig')
    # UTC timestamps with microseconds are provenance identifiers, not Excel dates.
    with (CAT/'data_catalogo_variaveis_h1_h2.csv').open(encoding='utf-8-sig',newline='') as f:
        write_json('catalog/data_catalogo_variaveis_h1_h2.values.json',list(csv.reader(f)))
    write_json('catalog/perfis_validacao_h1_h2.json',profiles)
    # Current local branch checkpoint remains authoritative, not hardcoded old prose.
    baseline=pd.read_csv(CAT/'baseline_repositorio_sha256.csv',dtype=str)
    changed=[r.arquivo for r in baseline.itertuples() if sha256(ROOT/r.arquivo)!=r.sha256]
    report={'branch':subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip(),'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'originais_alterados':changed,'arquivos_dados':len(inventory),'catalogo_linhas':len(catalog),'perfis_tabelas':len(profiles),'falhas_http_rede':len(failures),'hashes_divergentes':[x['arquivo'] for x in inventory if x['hash_confere_manifesto'] is False],'formato_incorreto':[x['arquivo'] for x in inventory if not x['formato_valido']]}
    write_json('catalog/verificacao_preservacao_h1_h2.json',report)
    assert not changed and not report['hashes_divergentes']
    print(json.dumps(report,ensure_ascii=False),flush=True)

if __name__=='__main__':main()
