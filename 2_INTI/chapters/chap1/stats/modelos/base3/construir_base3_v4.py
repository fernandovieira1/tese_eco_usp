"""Receitas internacionais de referência; primeiro contemporâneas, depois lags."""
import csv
import hashlib
import json
import math
import statistics as st
from pathlib import Path
from construir_base3_v2 import planilha_xml
P=Path(__file__).resolve().parent
V3=P/'painel_h1_base3_v3.csv'
HASH_V3='3012731110295b43967e1aaf5765a44f4946f05e09be91b9172e959aa9a7eaf5'
CULTURAS=['soja','milho'];MEDIDAS=['total','por_ha_colhido'];VERSOES=['','lag1','lag2','media_lag1_lag2']
def campo(crop,measure,version=''):
    return f'2_receita_bruta_estimada_usd2024_{measure}'+('_'+version if version else '')+'__'+crop
NOVAS=[campo(c,m,v) for c in CULTURAS for m in MEDIDAS for v in VERSOES]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ler(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def escrever(name,rows):
    with (P/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
def js(name,x):(P/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def numero(x):
    if x=='':return None
    n=float(x);assert math.isfinite(n) and n>=0;return n

def receitas(price,quantity,area):
    # Zero observado é preservado; denominador não positivo não é válido.
    total=price*quantity if price is not None and quantity is not None else None
    perha=total/area if total is not None and area is not None and area>0 else None
    return total,perha

def anteriores(values,municipio,ano):
    lag1=values.get((municipio,ano-1));lag2=values.get((municipio,ano-2))
    media=(lag1+lag2)/2 if lag1 is not None and lag2 is not None else None
    return lag1,lag2,media

def precos():
    files={'fontes_v2/pink_sheet_monthly_20260930.xlsx':'9fdcfa8a2aed9a1bb545a10c1a5ce036c6a0acd4766f450424ca800b4b5a0225','fontes_v2/bls_fred_CPIAUCNS_1960_2024.csv':'ba0db2b6b08846707e78e79dc8035548477ffbb141ff1687341d0f1a2f7d7a24','fontes_v4/precos_contemporaneos_pt_conferencia.csv':'db433027785e79e600fa3fe90f1da01fd2f6191345adf55b950bd0d411ef69af'}
    for f,h in files.items():assert sha(P/f)==h,f
    raw=planilha_xml(P/'fontes_v2/pink_sheet_monthly_20260930.xlsx')
    rows=[r for r in raw if isinstance(r.get('A'),str) and len(r['A'])==7 and r['A'][4]=='M']
    assert len({r['A'] for r in rows})==len(rows)
    wb={r['A']:r for r in rows};cp=ler(P/'fontes_v2/bls_fred_CPIAUCNS_1960_2024.csv')
    assert len({r['observation_date'][:7] for r in cp})==len(cp)
    cpi={r['observation_date'][:7]:float(r['CPIAUCNS']) for r in cp};base=st.mean(cpi[f'2024-{m:02d}'] for m in range(1,13))
    ref={int(r['ano']):r for r in ler(P/'fontes_v4/precos_contemporaneos_pt_conferencia.csv')}
    annual=[];monthly=[];lookup={}
    for year in range(2001,2025):
        for crop,col in [('soja','Y'),('milho','AE')]:
            vals=[]
            for month in range(1,13):
                nominal=float(wb[f'{year}M{month:02d}'][col]);index=cpi[f'{year}-{month:02d}']
                assert math.isfinite(nominal) and nominal>0 and math.isfinite(index) and index>0
                real=nominal*base/index;vals.append(real)
                monthly.append(dict(ano=year,mes=month,cultura=crop,nominal_usd_t=nominal,cpi_u=index,real_usd2024_t=real))
            avg=st.mean(vals);lookup[year,crop]=avg
            diff=avg-float(ref[year]['preco_real_usd2024_media_anual__'+crop]);assert abs(diff)<1e-9
            annual.append(dict(ano=year,cultura=crop,meses=12,preco_contemporaneo_usd2024_t=avg,diferenca_pt=diff))
    escrever('precos_mensais_receitas_v4.csv',monthly);escrever('precos_anuais_receitas_v4.csv',annual)
    js('auditoria_pre_construcao_v4.json',{'status':'APTO_COM_LIMITES','hashes_fontes':files,'anos_precos':[2001,2024],'meses_por_cultura':288,'cpi_base_media2024':base,'precos_contemporaneos_nao_lag1':True,'producao_pre2001':'Não disponível em fonte local harmonizada; não derivar de variações anuais','limite2024':'XLSX local em dois leitores e PT; confronto oficial externo anterior somente até2023','regra_ha':'total/área colhida positiva; comparar rendimento kg/ha com tolerância1kg/ha','regra_lags':'Chaves exatas município/ano t−1 e t−2; média estrita','sem_imputacao':True})
    return lookup,files

def construir():
    assert sha(V3)==HASH_V3
    original=ler(V3);assert len(original)==3384 and len(original[0])==54
    assert len({(r['0_codigo_ibge'],r['0_ano']) for r in original})==3384
    prices,files=precos();values={};diagnostics=[]
    for crop in CULTURAS:
        for measure in MEDIDAS:values[crop,measure]={}
        differences=[];ratios=[]
        for r in original:
            year=int(r['0_ano']);mun=r['0_codigo_ibge'];price=prices[year,crop]
            quantity=numero(r['2_producao_t__'+crop]);area=numero(r['2_area_colhida_ha__'+crop]);yield_obs=numero(r['2_rendimento_medio_kg_ha__'+crop])
            total,perha=receitas(price,quantity,area)
            values[crop,'total'][mun,year]=total;values[crop,'por_ha_colhido'][mun,year]=perha
            if perha is not None and yield_obs is not None:
                delta=abs(perha-price*yield_obs/1000);tolerance=price/1000*(1+1e-9)+1e-8
                assert delta<=tolerance
                differences.append(delta);ratios.append(delta/tolerance)
        diagnostics.append(dict(cultura=crop,comparacoes=len(differences),max_diferenca_usd2024_ha=max(differences),max_fracao_tolerancia=max(ratios),criterio='preço/1000 × (1 kg/ha+1e-9) +1e-8 numérico'))
    escrever('identidades_receitas_v4.csv',diagnostics)
    output=[]
    for r in original:
        new={};mun=r['0_codigo_ibge'];year=int(r['0_ano'])
        for crop in CULTURAS:
            for measure in MEDIDAS:
                current=values[crop,measure][mun,year]
                for version,value in zip(VERSOES,[current,*anteriores(values[crop,measure],mun,year)]):
                    new[campo(crop,measure,version)]='' if value is None else value
        output.append({**r,**new})
    escrever('painel_h1_base3_v4.csv',output)
    lineage=[]
    for crop in CULTURAS:
        for measure in MEDIDAS:
            for version in VERSOES:
                for year in range(2001,2025):
                    offsets=[0] if not version else ([1,2] if version=='media_lag1_lag2' else [int(version[-1])])
                    years=[year-lag for lag in offsets]
                    lineage.append(dict(variavel=campo(crop,measure,version),ano_resultado=year,
                        ano_preco_componente1=years[0],ano_quantidade_componente1=years[0],
                        ano_preco_componente2=years[1] if len(years)==2 else '',
                        ano_quantidade_componente2=years[1] if len(years)==2 else '',
                        anos_producao_no_suporte=all(y>=2001 for y in years),
                        usa_coluna_preco_lag1_como_contemporanea=False,
                        receita_formada_antes_de_defasar=True))
    escrever('rastreamento_anos_receitas_v4.csv',lineage)

    coverage=[]
    for c in NOVAS:
        for year in ['TODOS',*map(str,range(2001,2025))]:
            rows=[r for r in output if year=='TODOS' or r['0_ano']==year];valid=[r for r in rows if r[c]!='']
            coverage.append(dict(variavel=c,ano=year,N=len(rows),validos=len(valid),ausentes=len(rows)-len(valid),zeros=sum(r[c]==0 for r in valid),municipios_validos=len({r['0_codigo_ibge'] for r in valid})))
    escrever('cobertura_receitas_v4.csv',coverage)
    dic=ler(P/'dicionario_variaveis_v3.csv');extra=[]
    for crop in CULTURAS:
        for measure in MEDIDAS:
            for version in VERSOES:
                name=campo(crop,measure,version);d={k:'' for k in dic[0]}
                d.update(posicao=55+len(extra),grupo=2,nome_anterior=name[2:],nome_novo=name,justificativa='Derivada econômica; receita internacional de referência.',papel='Receita estimada contemporânea' if not version else 'Proxy retrospectiva, não expectativa observada',definicao=f'Receita {measure} de {crop}; versão {version or "contemporânea"}',unidade='USD2024' if measure=='total' else 'USD2024/ha colhido',fonte='PAM na v3; World Bank Pink Sheet/CPI-U auditados',campo_origem=f'2_producao_t__{crop}; 2_area_colhida_ha__{crop}; preço contemporâneo em precos_anuais_receitas_v4.csv; 0_codigo_ibge; 0_ano',transformacao='R(t)=P(t)×Q(t); Rha(t)=R(t)/área colhida(t)>0; '+('t contemporâneo' if not version else ('média estrita de R(t−1) e R(t−2)' if version=='media_lag1_lag2' else 'receita em t−'+version[-1]+' por chave consecutiva')),limitacoes='Não receita recebida ou lucro; preços internacionais; vintages retrospectivos; endogeneidade permanece; 1999/2000 indisponíveis; NA preservado; receita/ha depende de rendimento.',variavel=name)
                extra.append(d)
    escrever('dicionario_variaveis_v4.csv',dic+extra);escrever('dicionario_adendo_v4.csv',extra)
    js('manifesto_v4.json',{'versao':'base3_v4','linhas':3384,'colunas':70,'campos_acrescentados':NOVAS,'fonte_v3_sha256':HASH_V3,'fonte_v3_commit':'0a2cd309ab6b724ccd9266a54deb0f086843e3b9','hashes_fontes':files,'sha256_painel':sha(P/'painel_h1_base3_v4.csv'),'auditoria_sha256':sha(P/'auditoria_pre_construcao_v4.json'),'dicionario_sha256':sha(P/'dicionario_variaveis_v4.csv'),'rastreamento_anos_sha256':sha(P/'rastreamento_anos_receitas_v4.csv'),'dependencias':'Python>=3.9 stdlib; leitor OOXML construir_base3_v2.py publicado','aleatoriedade':'nenhuma','sem_modelos':True})
    print(json.dumps({'linhas':3384,'colunas':70,'sha256':sha(P/'painel_h1_base3_v4.csv')}))
if __name__=='__main__':construir()
