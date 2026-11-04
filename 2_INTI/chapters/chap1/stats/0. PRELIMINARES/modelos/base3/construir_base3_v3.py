"""Apensa oito campos PAM publicados, sem imputar ou alterar a base3 v2."""
import csv
import hashlib
import json
import math
from pathlib import Path
P=Path(__file__).resolve().parent
V2=P/'painel_h1_base3_v2.csv'
FONTE=P.parent/'base2/painel_h1_v2.csv'
ORIGINAL=P.parent/'painel_municipal_descritiva_h1.csv'
HASH_V2='a12d0a47e9dda01542467b546325f9bb2e088b82ede60647eb88511f27340391'
HASH_FONTE='9c68a0b66006a06c7369dcc331877b2ccc45f6bf5790303e0497ba726cf5838d'
HASH_ORIGINAL='bc396a4f394ae60d6883205f2ca6e8d33b59a4fb419fc5d667591374c8f1c730'
TIPOS={'area_plantada_ha':('Área plantada','ha'),'area_colhida_ha':('Área colhida','ha'),'producao_t':('Produção física','t'),'rendimento_medio_kg_ha':('Rendimento observado','kg/ha')}
NOVAS=[f'{t}__{c}' for t in TIPOS for c in ['milho','soja']]
TOL=1.0+1e-9  # Precisão inteira kg/ha; não recalcular o valor informado.
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ler(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def out(name,rows,cols=None):
    with (P/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=cols or list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
def js(name,x):(P/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def key(r,prefix=''):return r[prefix+'codigo_ibge'],r[prefix+'ano']
def auditar():
    for p,h in [(V2,HASH_V2),(FONTE,HASH_FONTE),(ORIGINAL,HASH_ORIGINAL)]:assert sha(p)==h,p
    v2,src,orig=ler(V2),ler(FONTE),ler(ORIGINAL)
    lookup={key(r):r for r in src};old={key(r):r for r in orig}
    assert len(v2)==len(src)==len(orig)==len(lookup)==len(old)==3384
    assert set(lookup)==set(old)=={key(r,'0_') for r in v2}
    assert len({r['codigo_ibge'] for r in src})==141
    assert {int(r['ano']) for r in src}==set(range(2001,2025))
    for r in v2:assert r['0_municipio']==lookup[key(r,'0_')]['municipio']
    for r in src:
        assert len(r['codigo_ibge'])==7 and r['codigo_ibge'].isdigit()
        for c in NOVAS:assert r[c]==old[key(r)][c]  # Inclui ausências e tokens numéricos.
    qualidade=[];anomalias=[]
    for c in NOVAS:
        for ano in ['TODOS',*map(str,range(2001,2025))]:
            rows=[r for r in src if ano=='TODOS' or r['ano']==ano];vals=[];invalid=0
            for r in rows:
                if not r[c]:continue
                try:v=float(r[c])
                except ValueError:invalid+=1;continue
                if not math.isfinite(v) or v<0:invalid+=1
                else:vals.append(v)
            qualidade.append(dict(variavel='2_'+c,ano=ano,total=len(rows),validos=len(vals),ausentes=sum(not r[c] for r in rows),invalidos=invalid,zeros=sum(v==0 for v in vals),municipios_validos=len({r['codigo_ibge'] for r in rows if r[c]}),minimo=min(vals) if vals else '',maximo=max(vals) if vals else ''))
            assert invalid==0,'Valor inválido: registrar e interromper, sem descartar.'
    diagnosticos=[]
    for crop in ['milho','soja']:
        diffs=[];inversions=0;partial=0;comparavel=0
        for r in src:
            values=[r[f'{t}__{crop}'] for t in TIPOS]
            if any(values) and not all(values):partial+=1
            if not all(values):continue
            a,h,q,y=map(float,values)
            if h>a:
                inversions+=1;anomalias.append(dict(codigo_ibge=r['codigo_ibge'],ano=r['ano'],cultura=crop,motivo='colhida_maior_plantada',valor=h-a))
            if h>0:
                comparavel+=1;delta=y-1000*q/h;diffs.append(delta)
                if abs(delta)>TOL:anomalias.append(dict(codigo_ibge=r['codigo_ibge'],ano=r['ano'],cultura=crop,motivo='rendimento_fora_tolerancia',valor=delta))
            elif q>0:anomalias.append(dict(codigo_ibge=r['codigo_ibge'],ano=r['ano'],cultura=crop,motivo='producao_com_area_zero',valor=q))
        diagnosticos.append(dict(cultura=crop,comparaveis=comparavel,max_diferenca_abs_kg_ha=max(map(abs,diffs)),diferencas_acima_1=sum(abs(v)>TOL for v in diffs),area_colhida_maior_plantada=inversions,blocos_parciais=partial,tolerancia_kg_ha=TOL))
    out('qualidade_produtiva_v3.csv',qualidade);out('diagnosticos_produtivos_v3.csv',diagnosticos)
    out('inconsistencias_produtivas_v3.csv',anomalias,['codigo_ibge','ano','cultura','motivo','valor'])
    suporte=[]
    for label,pred in [('painel_mestre',lambda r:True),('oferta_soja',lambda r:all(r[f'{t}__soja'] for t in TIPOS)),('oferta_milho',lambda r:all(r[f'{t}__milho'] for t in TIPOS)),('oferta_ambas',lambda r:all(r[c] for c in NOVAS)),('conversao_e_oferta_ambas',lambda r:r['v2__flag_amostra_conversao_ambos']=='True' and all(r[c] for c in NOVAS))]:
        rows=[r for r in src if pred(r)];suporte.append(dict(amostra=label,N=len(rows),municipios=len({r['codigo_ibge'] for r in rows}),anos=len({r['ano'] for r in rows}),linhas_sem_suporte=3384-len(rows)))
    out('suporte_produtivo_v3.csv',suporte)
    audit={'status':'APTO_COM_LIMITACOES','fonte':str(FONTE.relative_to(P.parent)),'commit_fonte':'1cbab8246114ecef0d2a80b55a068ea1cf4cf1c3','hash_fonte':HASH_FONTE,'hash_original':HASH_ORIGINAL,'hash_v2':HASH_V2,'chaves_comuns':3384,'perda_join':0,'diagnosticos':diagnosticos,'inconsistencias':len(anomalias),'limite_territorial':'Compatibilidade por códigos do painel141; não é reconstrução retrospectiva das fronteiras históricas PAM. Não usa GM ou tabela142.','limite_simbolos':'Fonte publicada contém NA; símbolos SIDRA originais não estão individualizados nestes oito campos. Não é possível distinguir aqui cada razão de ausência. Nenhum NA convertido em zero.'}
    js('auditoria_pre_join_v3.json',audit)
    (P/'AUDITORIA_PRE_JOIN_V3.md').write_text('''# Auditoria anterior ao apensamento produtivo

Fonte: base2 publicada no commit1cbab8246114ecef0d2a80b55a068ea1cf4cf1c3, conferida por hash; oito campos idênticos aos do painel original. Fonte primária documentada: IBGE/PAM SIDRA1612. Área plantada e colhida em ha, produção em t, rendimento em kg/ha. Mesmos3384pares código/ano e141códigos; nomes municipais coincidem comv2. Sem perda no join, sem remapeamento de142unidades ou dadosGM. Isso não resolve alterações históricas de limites municipais.

Tolerância de consistência do rendimento:1kg/ha +1e-9 numérico, compatível com apresentação em unidades inteiras (arredondamento/truncamento), não prova documental da regra de arredondamento da fonte. Compare rendimento observado com1000×produção(t)/área colhida(ha), somente denominador positivo. Não corrigir os valores publicados. Casos fora da tolerância ou área colhida superior à plantada seriam preservados e listados em inconsistencias_produtivas_v3.csv.

Resultado: soja2615observações por campo (769NA,136municípios); milho3318 (66NA,141municípios). Nenhum zero numérico ou inválido observado. Sem área colhida maior que plantada; nenhuma diferença de rendimento acima da tolerância. Faltas não viramzero. As colunas atuais não retêm os símbolos brutos por célula: motivo específico da ausência e preenchimentos herdados não são integralmente certificados. Não declarar ausência de produção apenas porNA.

Decisão: apensar oito campos como candidatos/descritivos contemporâneos, sem truncar painel. Produção/área/rendimento podem responder a preços, clima e conversão; não são controles exógenos automáticos. Área de culturas não é conversão nativa; soja e milho podem ocupar a mesma terra em safras sucessivas. Não somar áreas como área física única. Não acrescentar culturas, pecuária, crédito ou defasagens.
''',encoding='utf-8')
    return v2,lookup,audit

def construir():
    v2,lookup,audit=auditar()  # Parecer e diagnósticos gravados antes do painel.
    final=[{**r,**{'2_'+c:lookup[key(r,'0_')][c] for c in NOVAS}} for r in v2]
    out('painel_h1_base3_v3.csv',final)
    dic=ler(P/'dicionario_variaveis_v2.csv');cols=list(dic[0]);adendo=[]
    for i,c in enumerate(NOVAS,47):
        tipo,crop=c.split('__');label,unit=TIPOS[tipo]
        d={k:'' for k in cols};d.update(posicao=i,grupo=2,nome_anterior=c,nome_novo='2_'+c,justificativa='Oferta produtiva contemporânea; grupo econômico/produtivo.',papel='Candidato/descritivo contemporâneo',definicao=label+' de '+crop,unidade=unit,fonte='IBGE/PAM SIDRA1612 via base2/painel_h1_v2.csv; commit '+audit['commit_fonte'],campo_origem=c,transformacao='Cópia textual por código IBGE e ano; somente prefixo 2_.',limitacoes='Não exógeno automaticamente; limites municipais históricos não reconstituídos; NA/símbolos sem imputação; áreas de safras não somáveis como terra única.',variavel='2_'+c)
        adendo.append(d)
    out('dicionario_variaveis_v3.csv',dic+adendo);out('dicionario_adendo_v3.csv',adendo)
    js('manifesto_v3.json',{'versao':'base3_v3','linhas':3384,'colunas':54,'municipios':141,'anos':[2001,2024],'campos_acrescentados':['2_'+c for c in NOVAS],'hash_v2_preservada':HASH_V2,'hash_fonte_base2':HASH_FONTE,'hash_original':HASH_ORIGINAL,'sha256_painel':sha(P/'painel_h1_base3_v3.csv'),'auditoria_pre_join_sha256':sha(P/'auditoria_pre_join_v3.json'),'dependencias':'Python>=3.9 biblioteca padrão; base3v2 e base2/original publicados','semente':'Não aplicável; determinístico','sem_modelos':True})
    print(json.dumps({'linhas':len(final),'colunas':len(final[0]),'hash':sha(P/'painel_h1_base3_v3.csv')}))
if __name__=='__main__':construir()
