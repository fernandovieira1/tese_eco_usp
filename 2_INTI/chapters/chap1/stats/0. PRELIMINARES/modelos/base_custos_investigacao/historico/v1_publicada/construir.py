"""Custos CONAB de referência; nominal preservado, sem atribuição municipal."""
import csv
import hashlib
import json
import math
import re
import statistics as st
from collections import defaultdict
from pathlib import Path
P=Path(__file__).resolve().parent;F=P/'fontes'
CONCEITOS={'A':'custeio_lavoura','B':'outras_despesas_pos_colheita','C':'despesas_financeiras','D':'custo_variavel','E':'depreciacoes','F':'outros_fixos','G':'custo_fixo','H':'custo_operacional_conab','I':'renda_fatores','J':'custo_total_conab'}
LEAF={'A','B','C','E','F','I'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ler(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def out(name,rows,cols=None):
    with (P/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=cols or list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
def js(name,x):(P/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def number(s):
    s=s.strip().replace(' ','')
    if not re.fullmatch(r'-?\d+[.,\d]*',s):return None
    if ',' in s:s=s.replace('.','').replace(',','.')
    return float(s)
def converter(valor,cambio,cpi,cpi_base):
    # BRL nominal -> USD nominal -> USD2024; não usa IPCA.
    if any(x is None for x in [valor,cambio,cpi,cpi_base]):return None
    assert cambio>0 and cpi>0 and cpi_base>0
    return valor/cambio*cpi_base/cpi

def construir():
    manifest=json.loads((F/'manifesto_entradas.json').read_text())
    for f in manifest:assert sha(P/f['arquivo'])==f['sha256'],f['arquivo']
    meta={r['id_serie']:r for r in ler(F/'metadados_series.csv')};quality={r['id_serie']:r for r in ler(F/'qualidade_por_serie.csv')}
    assert len(meta)==len(quality)==188 and set(meta)==set(quality)
    long=ler(F/'custos_agregados_longos.csv');ha=[r for r in long if r['unidade']=='BRL_nominal/ha']
    assert len(ha)==1880 and len({(r['id_serie'],r['conceito']) for r in ha})==1880
    strict_source={(r['id_serie'],r['conceito']):r for r in ler(F/'custos_ha_estritos.csv')}
    cp=ler(F/'bls_fred_CPIAUCNS_1960_2024.csv');cpi={r['observation_date'][:7]:float(r['CPIAUCNS']) for r in cp}
    assert len(cpi)==len(cp);cpi_base=st.mean(cpi[f'2024-{m:02d}'] for m in range(1,13))
    fxrows=ler(F/'bcb_sgs3698_monthly_brl_per_usd_1997_2026.csv')
    fx={r['month']:float(r['brl_per_usd']) for r in fxrows}
    assert len(fx)==len(fxrows)==357
    assert list(fx)==[f'{1997+i//12}-{i%12+1:02d}' for i in range(357)]
    fxraw=json.loads((F/'bcb_sgs3698_1997_2026.json').read_text())
    for i,(raw,r) in enumerate(zip(fxraw,fxrows)):
        assert raw['data']==f'01/{i%12+1:02d}/{1997+i//12}' and raw['valor']==r['brl_per_usd']
        assert math.isfinite(fx[r['month']]) and fx[r['month']]>0
    assert len(fxraw)==357
    cells={};cellcount=0
    for f in (F/'conab_celulas').glob('*.csv'):
        data=ler(f);keys={(r['aba'],int(r['linha_excel']),int(r['coluna_excel'])) for r in data}
        assert len(keys)==len(data);cellcount+=len(data)
        cells[f.name]={(r['aba'],int(r['linha_excel']),int(r['coluna_excel'])):r['conteudo'] for r in data}
    rows=[];checks=[];agg=defaultdict(dict)
    for r in ha:agg[r['id_serie']][r['conceito']]=r
    for sid,concepts in agg.items():
        assert set(concepts)==set(CONCEITOS)
        for target,terms in [('D','ABC'),('G','EF'),('H','DG'),('J','HI')]:
            delta=float(concepts[target]['valor'])-sum(float(concepts[t]['valor']) for t in terms)
            checks.append({'0_id_serie':sid,'0_teste':target+'='+ '+'.join(terms),'2_residuo_brl_ha':delta,'4_tolerancia':.05,'4_aprovado':abs(delta)<=.050000001})
    for r in ha:
        sid=r['id_serie'];m=meta[sid];q=quality[sid];v=float(r['valor']);assert math.isfinite(v) and v>=0
        cell=cells[m['arquivo']][m['aba'],int(r['linha_excel']),int(r['coluna_excel'])]
        assert cell==r['valor_original'] and number(cell)==v
        strict=q['estrito']=='True';assert strict==((sid,r['conceito']) in strict_source)
        if strict:assert strict_source[sid,r['conceito']]['valor']==r['valor']
        month=m['data_base'][:7];index=cpi.get(month);exchange=fx.get(month)
        usd=converter(v,exchange,index,cpi_base)
        row={'0_id_registro':sid+'_'+r['conceito'],'0_id_serie':sid,'0_fonte':'CONAB','0_cultura_sistema':m['cultura'],'0_localidade_aba':m['praca_aba'],'0_localidade_cabecalho':m['praca_cabecalho'],'0_tecnologia':m['tecnologia'],'0_safra_inicio':m['safra_inicio'],'0_safra_fim':m['safra_fim'],'0_data_base':m['data_base'],'0_precisao_data_base':m['precisao_data_base'],'0_ano_data_base':m['ano_data_base'],'0_mes_referencia_moeda':month,'0_conceito_original':r['conceito'],'0_rotulo_original':r['rotulo_original'],'0_conceito_harmonizado_interno':CONCEITOS[r['conceito']],'0_unidade_original':r['unidade'],'0_natureza':'pacote modal/estimado de referência; não gasto municipal observado','2_custo_brl_nominal_ha':r['valor'],'2_valor_original_texto':r['valor_original'],'2_produtividade_modal_kg_ha':m['produtividade_kg_ha'],'2_cambio_brl_usd':exchange if exchange is not None else '','2_cpi_u_mes':index if index else '','2_custo_usd2024_ha':usd if usd is not None else '','4_elegivel_estrito_nominal':strict,'4_candidato_nominal':q['candidato'],'4_status': 'apto_referencia_nominal' if strict else 'quarentena','4_motivos_exclusao':q['motivos_exclusao_estrito'],'4_flag_ex_ant':m['ex_ant'],'4_periodo_alvo_2001_2024':m['elegivel_periodo_2001_2024'],'4_data_diverge_ano_aba':m['data_fora_ano_aba'],'4_status_conversao_moeda':'convertido_media_cambio_mensal' if usd is not None else 'cpi_ou_cambio_mes_indisponivel','4_elegivel_usd2024':False,'4_criterio_cambio':'SGS3698 média mensal de venda BRL/USD, mês da data-base; aproximação mensal mesmo quando data diária','4_projecao_municipal_validada':False,'0_arquivo_origem':m['arquivo'],'0_aba':m['aba'],'0_linha_excel':r['linha_excel'],'0_coluna_excel':r['coluna_excel']}
        for flag in ['flag_identidades_ok','flag_unidades_ok','flag_participacoes_ok','flag_territorio_ok','flag_verificacao_faltante']:row['4_'+flag]=q[flag]
        rows.append(row)
    out('custos_referencia_completos.csv',rows)
    out('custos_referencia_estritos.csv',[r for r in rows if r['4_elegivel_estrito_nominal']])
    out('custos_quarentena.csv',[r for r in rows if not r['4_elegivel_estrito_nominal']])
    out('auditoria_identidades.csv',checks)
    # Componentes numerados: valor/coluna iguais à fonte, sem harmonização entre instituições.
    components=[];sums=[]
    for sid,m in meta.items():
        source=cells[m['arquivo']];ag=agg[sid];colset={int(r['coluna_excel']) for r in ag.values()};labelset={int(r['rotulo_coluna']) for r in ag.values()}
        assert len(colset)==len(labelset)==1
        valuecol=colset.pop();labelcol=labelset.pop()
        sackcols={int(r['coluna_excel']) for r in long if r['id_serie']==sid and r['unidade']=='BRL_nominal/60kg'}
        assert len(sackcols)==1
        sackcol=sackcols.pop();assert sackcol>valuecol
        limits=sorted((int(ag[c]['linha_excel']),c) for c in LEAF)
        members=defaultdict(list)
        for (sheet,line,col),label in source.items():
            if sheet!=m['aba'] or col!=labelcol or not re.match(r'^\s*\d+\s*[-.)]',label):continue
            upcoming=[(rr,c) for rr,c in limits if rr>line]
            if not upcoming:continue
            limit,block=upcoming[0]
            candidates=[(c,source.get((sheet,line,c),'')) for c in range(valuecol,sackcol) if number(source.get((sheet,line,c),'')) is not None]
            actualcol,raw=candidates[0] if len(candidates)==1 else (valuecol,'')
            value=number(raw)
            code=re.match(r'^\s*(\d+(?:\.\d+)*)(?:\s|[.)-])',label)
            code=code[1] if code else ''
            item={'0_id_componente':f'{sid}_{line}_{actualcol}','0_id_serie':sid,'0_fonte':'CONAB','0_cultura_sistema':m['cultura'],'0_localidade':m['praca_aba'],'0_tecnologia':m['tecnologia'],'0_safra_inicio':m['safra_inicio'],'0_safra_fim':m['safra_fim'],'0_data_base':m['data_base'],'0_bloco_conab':block,'0_codigo_item':code,'4_coluna_ambigua':len(candidates)>1,'0_regra_coluna':'único número no intervalo [cabeçalho ha,cabeçalho60kg)','0_rotulo_componente_original':label,'0_unidade':'BRL_nominal/ha','2_valor_brl_nominal_ha':value if value is not None else '','2_texto_original':raw,'4_valor_valido':value is not None and math.isfinite(value) and value>=0,'4_serie_estrita_nominal':quality[sid]['estrito'],'0_arquivo_origem':m['arquivo'],'0_aba':sheet,'0_linha_excel':line,'0_coluna_excel':actualcol}
            members[block].append(item)
        for block in sorted(LEAF):
            items=members[block]
            for item in items:
                children=[x for x in items if x['0_codigo_item'].startswith(item['0_codigo_item']+'.')]
                item['4_cabecalho_sem_valor_com_subitens']=bool(children) and not item['4_valor_valido'] and item['2_texto_original']==''
                item['4_hierarquia_ambigua']=bool(children) and item['4_valor_valido'] and item['2_valor_brl_nominal_ha']>0 and any(x['4_valor_valido'] and x['2_valor_brl_nominal_ha']>0 for x in children)
            monetary=[x for x in items if not x['4_cabecalho_sem_valor_com_subitens']]
            complete=bool(monetary) and all(x['4_valor_valido'] for x in monetary) and not any(x['4_hierarquia_ambigua'] for x in items)
            total=sum(x['2_valor_brl_nominal_ha'] for x in monetary) if complete else None
            delta=total-float(ag[block]['valor']) if total is not None else None
            ok=delta is not None and abs(delta)<=.050000001
            sums.append({'0_id_serie':sid,'0_bloco_conab':block,'0_n_componentes':len(items),'2_soma_componentes':total if total is not None else '','2_agregado_original':ag[block]['valor'],'2_residuo':delta if delta is not None else '','4_verificacao_completa':complete,'4_soma_aprovada':ok,'4_tolerancia_brl_ha':.05})
            for item in items:
                item['4_soma_bloco_aprovada']=ok
                item['4_elegivel_componente_nominal']=ok and quality[sid]['estrito']=='True' and item['4_valor_valido']
                item['4_motivo_restricao']='' if item['4_elegivel_componente_nominal'] else ';'.join(x for x in ['serie_nao_estrita' if quality[sid]['estrito']!='True' else '', 'bloco_nao_reconciliado' if not ok else ''] if x)
                components.append(item)
    assert len({r['0_id_componente'] for r in components})==len(components)
    approved={sid:all(x['4_soma_aprovada'] for x in sums if x['0_id_serie']==sid) for sid in meta}
    strict_ids={sid for sid,q in quality.items() if q['estrito']=='True' and approved[sid]}
    for r in rows:
        previous=r['4_elegivel_estrito_nominal'];r['4_estrito_auditoria_anterior']=previous
        r['4_componentes_serie_reconciliados']=approved[r['0_id_serie']]
        r['4_elegivel_estrito_nominal']=r['0_id_serie'] in strict_ids
        r['4_elegivel_usd2024']=r['4_elegivel_estrito_nominal'] and r['2_custo_usd2024_ha']!=''
        r['4_status']='apto_referencia_nominal' if r['4_elegivel_estrito_nominal'] else 'quarentena'
        if not approved[r['0_id_serie']]:r['4_motivos_exclusao']+=';componentes_nao_reconciliados'
    for r in components:
        r['4_elegivel_componente_nominal']=r['4_elegivel_componente_nominal'] and r['0_id_serie'] in strict_ids
        if r['0_id_serie'] not in strict_ids:r['4_motivo_restricao']+=';serie_fora_estrito_atual'
    out('custos_referencia_completos.csv',rows)
    out('custos_referencia_estritos.csv',[r for r in rows if r['4_elegivel_estrito_nominal']])
    out('custos_quarentena.csv',[r for r in rows if not r['4_elegivel_estrito_nominal']])
    out('componentes_nominais.csv',components);out('auditoria_componentes.csv',sums)
    out('series_referencia.csv',[r for r in rows if r['0_conceito_original']=='H'])
    coverage=[]
    for crop in sorted({m['cultura'] for m in meta.values()}):
        for status in ['todas','estritas','quarentena']:
            ms=[m for sid,m in meta.items() if m['cultura']==crop and (status=='todas' or (sid in strict_ids)==(status=='estritas'))]
            coverage.append({'0_cultura':crop,'0_conjunto':status,'0_series':len(ms),'0_pracas':len({m['praca_aba'] for m in ms}),'0_safra_inicio_min':min(int(m['safra_inicio']) for m in ms),'0_safra_fim_max':max(int(m['safra_fim']) for m in ms),'0_tecnologias':';'.join(sorted({m['tecnologia'] for m in ms}))})
    out('cobertura.csv',coverage)
    qualityvars=[]
    for col in ['2_custo_brl_nominal_ha','2_produtividade_modal_kg_ha','2_cambio_brl_usd','2_cpi_u_mes','2_custo_usd2024_ha']:
        vs=[float(r[col]) for r in rows if r[col]!='']
        qualityvars.append({'0_variavel':col,'0_observados':len(vs),'0_ausentes':len(rows)-len(vs),'0_zeros':sum(v==0 for v in vs),'2_minimo':min(vs) if vs else '','2_maximo':max(vs) if vs else ''})
    out('qualidade_variaveis.csv',qualityvars)
    from construir_imea import construir_imea
    imea=construir_imea()
    summary={'series_estritas_auditoria_anterior':sum(q['estrito']=='True' for q in quality.values()),'series':len(meta),'agregados_ha':len(rows),'series_estritas':len({r['0_id_serie'] for r in rows if r['4_elegivel_estrito_nominal']}),'agregados_estritos':sum(r['4_elegivel_estrito_nominal'] for r in rows),'componentes':len(components),'componentes_elegiveis':sum(r['4_elegivel_componente_nominal'] for r in components),'blocos_componentes':len(sums),'blocos_aprovados':sum(r['4_soma_aprovada'] for r in sums),'identidades_aprovadas':sum(r['4_aprovado'] for r in checks),'identidades':len(checks),'celulas_fontes':cellcount,'cpi_base_media2024':cpi_base,'usd2024_preenchidos':sum(r['2_custo_usd2024_ha']!='' for r in rows),'usd2024_estritos':sum(r['4_elegivel_usd2024'] for r in rows),'imea_linhas':imea['celulas'],'imea_candidatos_descritivos':imea['candidatos_descritivos'],'sem_regressoes':True}
    js('resumo.json',summary)
    js('manifesto.json',{'entradas':manifest,'hashes_saidas':{f.name:sha(f) for f in sorted(P.glob('*.csv'))},'sem_aleatoriedade':True,'python_dependencias':'biblioteca padrão; nenhuma dependência em complemento local externo após cópia de fontes'})
    print(json.dumps(summary,ensure_ascii=False))
if __name__=='__main__':construir()
