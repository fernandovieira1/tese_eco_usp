"""Atribuição candidata: regional primeiro, depois estadual PUBLICADA compatível."""
from collections import Counter,defaultdict

def construir(e,out):
 ag,pec=e.sources()
 candidates=e.read(out/'resultados/lista_candidatas.csv')
 panel=e.read(out/'resultados/PAINEL_SOMENTE_REGIONAL.csv')
 original=e.read(out/'resultados/METADADOS_SOMENTE_REGIONAL.csv')
 state={};state_rows=[]
 # Exact source sheets distinguish statewide publication from conflicting municipality labels.
 allowed={'Soja_GMO_MT','Milho_MT','Bovinocultura - Cria','Bovinocultura - Rec. e Eng.','Bovinocultura - Ciclo comp.'}
 for kind,rows in [('agricola',ag),('pecuaria',pec)]:
  for r in rows:
   if r['0_fonte']!='IMEA' or r['4_alerta_geografia']!='referencia_estadual' or r['0_aba_origem'] not in allowed or r['0_localidade_literal']!='MATO GROSSO':continue
   year=r['0_safra_fim'] if kind=='agricola' else r['0_ano_rotulo']
   if not year or not 2001<=int(year)<=2024:continue
   if r['0_natureza'] not in ['consolidado','consolidado_conforme_rotulo']:continue
   if 'asterisco_ambiguo' in r['4_alertas_fonte']:continue
   activity='milho_safra_nao_harmonizada' if kind=='agricola' and r['0_atividade']=='milho' else r['0_atividade']
   duration=int(r['0_safra_fim'])-int(r['0_safra_inicio']) if kind=='agricola' else 0
   source='IMEA_'+kind
   for c in candidates:
    if (source,activity,r['0_sistema_tecnologia'],r['0_natureza'],str(duration))!=(c['fonte'],c['atividade'],c['sistema'],c['natureza'],c['duracao_safra']):continue
    concept,currency=c['conceito'],c['moeda'];metric=concept+'_'+currency
    if not r['2_'+metric] or r['4_'+concept+'_elegivel_'+currency]!='True':continue
    key=c['variavel'],year
    assert key not in state,('mais de uma referência estadual para mesma chave',key)
    record=dict(variavel=c['variavel'],ano=year,id_fonte=r['0_id_referencia'],fonte=source,atividade=activity,sistema=r['0_sistema_tecnologia'],conceito=concept,moeda=currency,unidade='R$/ha' if kind=='agricola' else 'R$/arroba vendida',natureza=r['0_natureza'],periodo_literal=r['0_periodo_literal'],aba_origem=r['0_aba_origem'],snapshot=r['0_snapshot'],valor=r['2_'+metric],alertas_fonte=r['4_alertas_fonte'],tipo='estadual_publicada')
    state[key]=record;state_rows.append(record)
 e.write(out/'resultados/REFERENCIAS_ESTADUAIS_PUBLICADAS.csv',state_rows)
 bykey={(r['0_codigo_ibge'],r['0_ano']):r for r in panel}
 metas=[];coverage=defaultdict(Counter);summary=defaultdict(Counter);unique=defaultdict(set)
 for m in original:
  code,year,var=m['0_codigo_ibge'],m['0_ano'],m['variavel'];row=bykey[code,year]
  ref=state.get((var,year));scope='regional' if row[var] else 'estadual_publicada' if ref else 'ausente'
  ids=m['id_ref'] if scope=='regional' else ref['id_fonte'] if ref else ''
  if scope=='estadual_publicada':row[var]=ref['valor']
  metadata={k:m[k] for k in ['0_codigo_ibge','0_ano','variavel','fonte','atividade','sistema','conceito','moeda','natureza','regra_ano']}
  metadata.update(unidade='USD2024/ha' if m['moeda']=='usd2024' else 'R$/arroba vendida' if m['atividade']=='pecuaria' else 'R$/ha',mesorregiao_ibge2016=m['4_mesorregiao_ibge2016_codigo'],origem_atribuicao=scope,id_referencia=ids,ano_referencia=year if scope!='ausente' else '',n_pracas=m['n_pracas'] if scope=='regional' else '',n_referencias=m['n_referencias'] if scope=='regional' else '1' if ref else '',iqr=m['iqr'] if scope=='regional' else '',suporte=m['confiabilidade'] if scope=='regional' else 'referencia_estadual_publicada_nao_observacao_municipal' if ref else 'sem_referencia_compativel',incorporacao_aprovada=False,disponivel_exante_validado=False,limites_territoriais_verificados=False)
  metas.append(metadata);summary[var][scope]+=1;coverage[var,metadata['mesorregiao_ibge2016'],year][scope]+=1
  if ids:unique[var,scope].add(ids)
 e.write(out/'resultados/METADADOS_CUSTOS_MUNICIPAIS.csv',metas)
 e.write(out/'USO_CANDIDATOS/CUSTOS_MUNICIPAIS_CANDIDATOS.csv',panel)
 counts=[]
 lineage=e.read(out/'resultados/linhagem_regional.csv')
 for c in candidates:
  var=c['variavel'];n=summary[var];counts.append(dict(variavel=var,fonte=c['fonte'],atividade=c['atividade'],sistema=c['sistema'],conceito=c['conceito'],moeda=c['moeda'],n_regional=n['regional'],n_estadual=n['estadual_publicada'],n_vazio=n['ausente'],total=3384,antes_pct=100*n['regional']/3384,depois_pct=100*(3384-n['ausente'])/3384,referencias_regionais_distintas=len(unique[var,'regional']),referencias_estaduais_distintas=len(unique[var,'estadual_publicada']),referencias_originais_regionais_distintas=len({r['id_origem'] for r in lineage if r['id_referencia_regional'] in unique[var,'regional'] and r['conceito']==c['conceito'] and r['moeda']==c['moeda']}),pracas_regionais_distintas=len({r['praca'] for r in lineage if r['id_referencia_regional'] in unique[var,'regional'] and r['conceito']==c['conceito'] and r['moeda']==c['moeda']})))
 e.write(out/'resultados/COBERTURA_FALLBACK.csv',counts)
 e.write(out/'resultados/COBERTURA_FALLBACK_REGIAO_ANO.csv',[dict(variavel=v,mesocodigo=meso,ano=y,n_regional=n['regional'],n_estadual=n['estadual_publicada'],n_vazio=n['ausente'],total=sum(n.values()),antes_pct=100*n['regional']/sum(n.values()),depois_pct=100*(n['regional']+n['estadual_publicada'])/sum(n.values())) for (v,meso,y),n in sorted(coverage.items())])
 d=e.read(out/'USO_CANDIDATOS/DICIONARIO.csv');d=[r for r in d if not r['variavel'].startswith('REFERENCIAS_REGIONAIS::')]
 for r in d:
  if r['variavel'].startswith('2_'):r['descricao']='Candidato alternativo: mediana regional (inclusive uma praça com suporte fraco); faltando, estadual publicada da mesma fonte/atividade/sistema/conceito/moeda/ano. NA se ambas ausentes. Metadados por chave/variável em ../resultados/METADADOS_CUSTOS_MUNICIPAIS.csv; custos não observados municipalmente; incorporação pendente.'
 e.write(out/'USO_CANDIDATOS/DICIONARIO.csv',d)
 (out/'USO_CANDIDATOS/LEIA_ME.md').write_text('''# Abra CUSTOS_MUNICIPAIS_CANDIDATOS.csv

Dataframe separado para avaliação: **3.384 linhas (141 municípios ×2001–2024), sete índices H1 idênticos e27 custos em colunas**. DICIONARIO.csv explica cada alternativa. Os27 custos não são27 variáveis independentes; sistemas, fontes, conceitos e moedas permanecem separados.

Hierarquia: referência regional válida, inclusive praça única com suporte fraco; faltando, referência estadual **publicada** compatível da mesma fonte, atividade, sistema, conceito, moeda e ano. Sem ambas, NA (célula vazia), nunca zero imputado. Nenhuma interpolação temporal ou multiplicador municipal. Não há fallback estadual CONAB compatível nas entradas.

Agricultura CONAB: R$/ha e USD2024/ha separados. IMEA agrícola: R$/ha nominal, milho sem harmonização automática em1ª/2ª safra. Pecuária: R$/arroba VENDIDA nominal, nunca por hectare. Ano agrícola é fim da safra explícita. Não são custos reais observados por município nem informações exante comprovadas.

[Metadados por município/ano/variável](../resultados/METADADOS_CUSTOS_MUNICIPAIS.csv): regional/estadual/ausente, fonte, sistema, conceito, moeda, ano, n_pracas e suporte. [Cobertura antes/depois](../resultados/COBERTURA_FALLBACK.csv). [Referências regionais](../resultados/REFERENCIAS_REGIONAIS.csv) e [estaduais publicadas](../resultados/REFERENCIAS_ESTADUAIS_PUBLICADAS.csv) permitem rastrear valores. O cenário conservador está fora desta pasta, em resultados/cenario_conservador.

**CANDIDATO, não aprovado para incorporação.** Nenhuma coluna foi incorporada à BASE_COMPLETA_H1.csv ou ao grupo2. A publicação desta pasta não constitui aprovação para incorporar. Faça cópia para trabalho manual; reconstrução usa diretório novo, sem sobrescrever edições.
''')
 return counts
