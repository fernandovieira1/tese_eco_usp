"""Recorte determinístico da base2 publicada; somente biblioteca padrão Python."""
import csv
import hashlib
import json
import math
from pathlib import Path

PASTA = Path(__file__).resolve().parent
ORIGEM = PASTA.parent / 'base2/painel_h1_v2.csv'
COMMIT = '1cbab8246114ecef0d2a80b55a068ea1cf4cf1c3'
HASH = '9c68a0b66006a06c7369dcc331877b2ccc45f6bf5790303e0497ba726cf5838d'
META = []

def campo(nome, papel, definicao, unidade, fonte, limite='Ausentes preservados; sem imputação.'):
    META.append(dict(variavel=nome, papel=papel, definicao=definicao, unidade=unidade,
                     fonte=fonte, campo_origem=nome, transformacao='Cópia textual exata da base2.', limitacoes=limite))

for nome, unidade in [('codigo_ibge','código de 7 dígitos'),('ano','ano civil'),('municipio','nome')]:
    campo(nome,'chave',nome,unidade,'Base2 publicada; suporte municipal IBGE 141')
for atividade in ['agricultura','pastagem']:
    campo('conversao_ha__'+atividade,'VD','Conversão bruta de vegetação nativa para '+atividade,'ha','MapBiomas 10.1','Zeros registrados preservados; origem absoluta de zeros não certificada; 612 ausentes.')
    campo('taxa_conversao__'+atividade,'VD','Conversão ha / vegetação nativa inicial','fração 0–1','MapBiomas 10.1','Não é percentual; modelos anteriores multiplicaram por 100 para pontos percentuais.')
campo('y_nativa_inicial_ha','denominador','Estoque inicial de vegetação nativa do par de anos','ha','MapBiomas 10.1')
for produto in ['soja','milho','carne_bovina']:
    campo('preco_real_usd2024_media_anual_lag1__'+produto,'VI econômica','Preço mundial real médio do ano anterior','USD2024/kg' if produto=='carne_bovina' else 'USD2024/t','Banco Mundial; deflação CPI-U','Já defasado: outcome 2001–2024 usa 2000–2023. Não preço local ou retorno; absorvido por FE anual.')
for cultura,sufixo in [('soja','soy'),('milho','mze')]:
    campo(f'capacidade_valor__{cultura}__gaez_yxHr0_{sufixo}','VI aptidão','Rendimento potencial alto insumo, sequeiro','kg matéria seca/ha','GAEZ','Clima 1961–1990; terras 2010. Não lucro ou rendimento comercial; não estritamente predeterminado; absorvido por FE municipal.')
campo('bioma_predominante','território','Bioma predominante municipal','categoria','IBGE biomas','Não localiza a conversão; não identifica ecótono; atributo estático.')
for bioma in ['amazonia','cerrado','pantanal']:
    campo('biome_'+bioma+'_share_i','território','Fração territorial municipal do bioma '+bioma,'fração','IBGE biomas','Sem renormalização; soma aproximada; não localiza a conversão.')
AUTO='n_autos_flora__ibama_espacial'
PARCIAL='flag_contagem_flora_parcial__ibama_espacial'
LAG='n_autos_flora_elegiveis_lag1__ibama_espacial'
campo(AUTO,'VI institucional','Contagem espacial contemporânea de autos Flora','autos','IBAMA','Pode ser parcial; autuações não são eficácia, pagamento ou exogeneidade.')
campo(PARCIAL,'qualidade institucional','True indica contagem parcial; vazio não certifica completude','booleano/NA','IBAMA')
for nome,definicao,unidade in [
 ('precip_mm_anual','Chuva no ano civil','mm'),
 ('precip_anomaly_1981_2000','Chuva anual menos média histórica 1981–2000','mm'),
 ('meses_validos','Meses com precipitação válida','meses'),
 ('meses_cobertura_conhecida','Meses com cobertura conhecida','meses'),
 ('fracao_pixels_minima','Mínima fração mensal de pixels válidos','fração'),
 ('flag_ano_incompleto','Indicador de ano incompleto','booleano'),
 ('media_1981_2000','Média anual histórica usada na anomalia','mm'),
 ('count_1981_2000','Número de anos válidos da referência histórica','anos')]:
    campo('v2__'+nome,'clima/qualidade',definicao,unidade,'CHIRPS v2','Ano civil, não calendário agrícola; chuva não usada nas sete rodadas anteriores.')
for nome,definicao,unidade in [
 ('y_cobertura_completa','Cobertura cartográfica completa do par','booleano'),
 ('y_fracao_area_valida_par','Fração de área válida no par','fração'),
 ('y_flag_denominador_zero','Estoque inicial igual a zero','booleano'),
 ('y_flag_denominador_ausente','Estoque inicial ausente','booleano')]:
    campo('v2__'+nome,'qualidade conversão',definicao,unidade,'MapBiomas 10.1; IBGE_MT_2023_141')
FLAGS = {
 'conversao_valida__agricultura':'Conversão agrícola válida (2772)',
 'zero_conversao_registrado__agricultura':'Zero agrícola registrado (265)',
 'conversao_valida__pastagem':'Conversão pastagem válida (2772)',
 'zero_conversao_registrado__pastagem':'Zero pastagem registrado (0)',
 'desfecho_ausente_cobertura_par':'Desfecho ausente por cobertura do par (612)',
 'amostra_conversao_ambos':'Ambos desfechos válidos; núcleo econômico completo (2772)',
 'autos_flora_elegivel_t':'Autos não negativos com parcialidade explicitamente False (1526)',
 'autos_flora_elegivel_lag1':'Autos elegíveis no ano consecutivo anterior (1444)',
 'amostra_fiscal_lag1':'Ambos desfechos e autos anteriores elegíveis (1140)',
 'amostra_conversao_chuva':'Ambos desfechos e chuva disponíveis (2772)'}
for nome,definicao in FLAGS.items():
    campo('v2__flag_'+nome,'flag amostral/qualidade',definicao,'booleano','Construção publicada da base2','Máscara, não exclusão de linhas; não garante ausência de viés de seleção.')
COLUNAS = [m['variavel'] for m in META]
META.append(dict(variavel=LAG,papel='VI institucional defasada',definicao='Autos elegíveis do mesmo município no ano t−1 consecutivo',unidade='autos',fonte='IBAMA via base2',campo_origem=AUTO+'; '+PARCIAL+'; codigo_ibge; ano',transformacao='Filtrar valor finito >=0 e parcialidade False antes da defasagem por chave.',limitacoes='NA preservado; 2001 sem predecessor nesta base; sem divisão por 10; endogeneidade permanece.'))

def numero(valor):
    return float(valor) if valor else None

def elegivel(linha):
    valor=numero(linha[AUTO])
    return valor is not None and math.isfinite(valor) and valor>=0 and linha[PARCIAL].lower()=='false'

def defasar(linhas):
    # Lookup exato impede atravessar lacunas de anos ou municípios.
    valores={(r['codigo_ibge'],int(r['ano'])): r[AUTO] if elegivel(r) else '' for r in linhas}
    return [valores.get((r['codigo_ibge'],int(r['ano'])-1),'') for r in linhas]

def escrever(nome,linhas,colunas):
    with (PASTA/nome).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=colunas,lineterminator='\n');w.writeheader();w.writerows(linhas)

def construir():
    assert hashlib.sha256(ORIGEM.read_bytes()).hexdigest()==HASH, 'Base2 difere da versão publicada.'
    with ORIGEM.open(encoding='utf-8-sig',newline='') as f: original=list(csv.DictReader(f))
    saida=[{**{c:r[c] for c in COLUNAS}, LAG:lag} for r,lag in zip(original,defasar(original))]
    escrever('painel_h1_base3_v1.csv',saida,COLUNAS+[LAG])
    escrever('dicionario_variaveis.csv',META,list(META[0]))
    qualidade=[]
    for c in COLUNAS+[LAG]:
        vals=[r[c] for r in saida if r[c]!='']; nums=[]
        for v in vals:
            try: nums.append(float(v))
            except ValueError: pass
        qualidade.append(dict(variavel=c,observados=len(vals),ausentes=len(saida)-len(vals),zeros_numericos=sum(v==0 for v in nums),verdadeiros=sum(v.lower()=='true' for v in vals),minimo=min(nums) if nums else '',maximo=max(nums) if nums else ''))
    escrever('qualidade_variaveis.csv',qualidade,list(qualidade[0]))
    amostras=[]
    for c in COLUNAS:
        if c.startswith('v2__flag_'):
            r=[x for x in saida if x[c]=='True']
            amostras.append(dict(flag=c,N=len(r),municipios=len({x['codigo_ibge'] for x in r}),anos=len({x['ano'] for x in r})))
    escrever('amostras.csv',amostras,list(amostras[0]))
    manifesto=dict(versao='base3_v1',fonte='../base2/painel_h1_v2.csv',commit_fonte=COMMIT,sha256_fonte=HASH,linhas=len(saida),colunas=len(COLUNAS)+1,dependencias='Python >=3.9; somente biblioteca padrão',aleatoriedade='Nenhuma; semente não aplicável',hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(PASTA.glob('*.csv'))})
    (PASTA/'manifesto.json').write_text(json.dumps(manifesto,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'linhas':len(saida),'colunas':len(COLUNAS)+1,'sha256_painel':manifesto['hashes']['painel_h1_base3_v1.csv']}))

if __name__=='__main__': construir()
