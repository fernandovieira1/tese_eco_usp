"""Consolida registros já estimados; não seleciona modelos por ajuste/p-valor."""
from reproduzir import *

def js(x): return json.dumps(clean(x),ensure_ascii=False,sort_keys=True)
def technical(c,s):
    expr=f'L{s["lags"][c]}_calendario({c})' if s.get('lags',{}).get(c) else c
    t=s.get('transforms',{}).get(c,'level')
    return f'ln({expr})' if t=='log' else f'ln(1+{expr})' if t=='log1p' else expr
def formula(s):
    terms=[technical(c,s) for c in s['xs']]+[f'[{technical(l,s)}]*[{technical(r,s)}]' for l,r in s.get('interactions',[])]
    return s['y']+' = β0 + '+' + '.join(f'β{i+1}·[{c}]' for i,c in enumerate(terms))+' + ε'
LIMIT='Pooled OLS associativo: heterogeneidade omitida, simultaneidade, tendência/choques anuais comuns e dependência espacial. Cluster municipal não absorve efeitos fixos nem corrige choques comuns entre municípios. Valores-p sem ajuste pela exploração de 200 especificações. Sem exclusão de outliers.'

def main():
    data,cat,meta=load_data()
    rr=json.loads((HERE/'resultados_completos.json').read_text(encoding='utf-8'))
    cc=json.loads((HERE/'amostra_comum.json').read_text(encoding='utf-8'))
    checks=json.loads((HERE/'conferencia_dashboard.json').read_text(encoding='utf-8'))
    metadata=json.loads((HERE/'metadata.json').read_text(encoding='utf-8'))
    planned=json.loads((HERE/'plano_pre_estimacao.json').read_text(encoding='utf-8'))
    byid={r['plan']['id']:r for r in rr}
    results=[['Variável dependente','Variáveis Independentes','R2']]
    details=[['Variável dependente','Variáveis Independentes','ID do modelo','Tipo de registro','Nomes técnicos dos Xs','Fórmula estimada','Classe','Família econômica','R2','R2 ajustado','N','Parâmetros (inclui intercepto)','GL residuais','GL inferência t','Período efetivo','Municípios','Anos','ID amostra SHA256','Cobertura territorial','N por ano','N por bioma','N inicial dos filtros','Excluídos por cobertura de Y','Excluídos após cobertura (ausência/domínio)','Ausências por variável antes da amostra comum','Filtros','Transformações e defasagens','Erros-padrão','Número de grupos municipais','Justificativa econômica','Sinais esperados','Referências locais consultadas','Problemas e limitações','Prioridade posterior','Razão da prioridade','Posto / condição normalizada','Diagnóstico de influência / previsões','Modelo original / confronto','Resumo dos termos centrais','Flags parciais IBAMA na amostra']]
    coefficients=[['ID do modelo','Termo','Coeficiente','Erro-padrão','Estatística do teste','Valor-p','Limite inferior do IC 95%','Limite superior do IC 95%','Método de inferência']]
    methods=[['Categoria','Item','Conteúdo','Origem / localização']]
    def note(cat,item,content,source='Execução local e rotinas h1lab'):
        methods.append([cat,item,str(content),source])
    def interpretation(r):
        p=r['plan']; local=p['local']; y=p['spec']['y']; s=r['summary']
        if local not in [22,42,46]:
            return 'Exploratória complementar','Mantida integralmente no plano. Comparar apenas com mesma dependente e amostra; ausência de destaque não equivale a exclusão da variável.'
        rationale={22:'Base parcimoniosa de H1: preço próprio, capacidade GAEZ, vegetação inicial, área e clima. Oferece referência com maior cobertura para as interações.',
                   42:'Heterogeneidade preço × capacidade, mantendo componentes e controles. Preserva mecanismo central de H1 mesmo sem ganho de ajuste ou significância.',
                   46:'Condicionamento preço × registros IBAMA em t−1. Prioridade temática provisória; perdas de cobertura, parcialidade e seleção fiscalizatória tornam a inferência especialmente frágil.'}[local]
        if local==42 and 'agricultura' in y: rationale+=' Interação negativa nas amostras originais: não confirma a previsão positiva simples de capacidade.'
        if local==42 and y=='taxa_conversao__pastagem': rationale+=' R2 ajustado menor que o modelo sem interação; efeito próximo de zero e impreciso. Retida pelo mecanismo, sem vantagem estatística.'
        if local==46 and y=='taxa_conversao__pastagem': rationale+=' Interação praticamente nula; na amostra comum o ajuste é inferior à base. Requer melhor proxy institucional antes de aprofundar.'
        return 'Candidata provisória para etapa com FE',rationale
    def central(coefs):
        return '; '.join(f'{v["term"]}: b={v["coef"]:.8g}, EP={v["se"]:.6g}, p={v["p"]:.6g}' for v in coefs if 'preco' in v['term'] or ' × ' in v['term'])
    def coefrows(mid,coefs):
        for v in coefs:
            coefficients.append([mid,v['term'],*[v[k] if v[k] is not None else 'Indisponível' for k in ['coef','se','t','p','ci_low','ci_high']], 'Cluster por município; correção finita; t com G−1 GL'])
    for r in rr:
        p=r['plan']; s=r['summary']; spec=p['spec']; mid=p['id']; label=pretty(spec['y'])
        results.append([label,p['description'],s['R2']])
        priority,reason=interpretation(r)
        losses=r['ledger']; missing=r['missing']
        limitations=LIMIT+' '+(' '.join(r['warnings']))
        if any('ibama' in c for c in spec['xs']): limitations+=' IBAMA: sem imputar ausências a zero; contagens/somas parciais preservadas conforme dashboard. Flags parciais discriminadas na última coluna. Ausência de registro não é eficácia nula. Multas não são pagamentos.'
        if 'D' in p['keys']: limitations+=' PAM histórica depende de produção observada e mínimo de 7 anos em 1991–2000; cobertura seletiva.'
        if 'C' in p['keys'] and spec['y'].endswith('pastagem'): limitations+=' GAEZ milho é proxy agrícola, não capacidade forrageira nem potencial pecuário direto.'
        if spec['y'].startswith('taxa'): limitations+=' Y em fração; para pontos percentuais multiplicar coeficientes por 100. OLS pode prever fora de [0,1]. Estoque inicial também é denominador: controle não cria identidade exata, mas afeta interpretação.'
        if 'W' in p['keys']: limitations+=' Chuva t−1 usa ano civil exato; 2001 perde suporte porque não há 2000 no painel carregado.'
        diag=f'Cook máximo={r["max_cook"]:.5g}; Cook>4/N={r["cooks_gt_4n"]}; previsões negativas={r["pred_negative"]}; previsões >1 (taxas)={r["pred_gt1"]}; nenhuma remoção.'
        details.append([label,p['description'],mid,'Original — conta na meta', '; '.join(spec['xs']),formula(spec),
          'Simples' if len(spec['xs'])==1 else 'Múltipla',p['family'],s['R2'],s['R2 ajustado'],s['N'],len(r['coef']),s['Graus de liberdade residuais'],s['Graus de liberdade da inferência'],
          f'{r["sample_min"]}–{r["sample_max"]}',s['Municípios'],s['Anos'],r['sample_id'], '; '.join(r['municipalities']),js(r['years']),js(r['biomes']),
          losses[0]['N'],losses[0]['N']-losses[1]['N'],losses[1]['N']-losses[2]['N'],js(missing),js(FILTERS),js({'transforms':spec['transforms'],'lags':spec['lags'],'interactions':spec['interactions']}),
          'Cluster por município; correção amostral finita; t, G−1 GL',s['clusters']['codigo_ibge'],p['rationale'],p['signs'],p['refs'],limitations,priority,reason,
          f'Posto completo={len(r["coef"])}; condição={s["Condição (colunas normalizadas)"]:.7g}',diag,'Não se aplica',central(r['coef']),js(r['partial_ibama'])])
        coefrows(mid,r['coef'])
    for c in cc:
        r=byid[c['original']]; p=r['plan']; s=c['summary']; original=r['summary']
        row=details[1+list(byid).index(c['original'])].copy()
        row[2]=c['id']; row[3]='Conferência em amostra comum — fora da meta de 200'
        row[8:18]=[s['R2'],s['R2 ajustado'],s['N'],len(c['coef']),s['Graus de liberdade residuais'],s['Graus de liberdade da inferência'],f'{c["min"]}–{c["max"]}',s['Municípios'],s['Anos'],c['sample_id']]
        row[18]='; '.join(c['municipalities']); row[19]='Mesmas chaves da interseção documentada em Metodologia'; row[20]='Interseção das candidatas da dependente'
        row[21:25]=['Não se aplica: conferência','Não se aplica','Não se aplica','N original='+str(original['N'])+'; exclusões até interseção='+str(original['N']-s['N'])]
        row[28]=s['clusters']['codigo_ibge']; row[33]='Conferência, não nova candidata'; row[34]='Comparação dos modelos locais 22, 42 e 46 exatamente nos mesmos pares município-ano; lag calculado antes de mascarar Y fora da interseção.'
        row[35]=f'Posto completo={len(c["coef"])}; condição={s["Condição (colunas normalizadas)"]:.7g}'
        row[36]='Não recontado nesta linha; diagnósticos originais acima.'
        row[37]=f'Original {c["original"]}: N={original["N"]}; R2={original["R2"]:.9g}; R2aj={original["R2 ajustado"]:.9g}; comum R2aj={s["R2 ajustado"]:.9g}'
        row[38]=central(c['coef']); row[39]='Não recontado para esta conferência; verificar registro original e amostra.'
        details.append(row); coefrows(c['id'],c['coef'])
    note('Escopo','Entrega','200 especificações originais válidas: 50 para cada dependente. 12 reestimações em amostra comum e 4 conferências AppTest não contam como novos modelos. Nenhum efeito fixo estimado.')
    note('Conclusão','Leitura econômica','Associações negativas dos preços próprios nas candidatas; resultados não confirmam a previsão positiva simples de retorno. Tendências, choques comuns e heterogeneidade territorial podem explicar os sinais. Preservar preços e interações centrais de H1 na próxima etapa.')
    note('Conclusão','Escala versus intensidade','Pastagem em hectares apresenta ajuste maior (candidata M072: R2aj=0,3454) que sua taxa (M172: 0,0848). Controlar escala é economicamente importante; não comparar R2 entre dependentes como critério de validade.')
    note('Conclusão','Agricultura','M022/M042/M046 (ha) e M122/M142/M146 (taxa) cobrem baseline, preço × capacidade e preço × IBAMA. Ganho de ajuste da interação de aptidão é pequeno e seu sinal é negativo. Ajustes baixos, sobretudo da taxa, limitam capacidade explicativa.')
    note('Conclusão','Pastagem','M072/M092/M096 (ha) e M172/M192/M196 (taxa). Na taxa, interação de aptidão não melhora R2aj e interação institucional é imprecisa. Preservadas como perguntas de H1, com prioridade estatística reduzida.')
    for r in rr:
        if r['plan']['local'] in [22,42,46]:
            prior,why=interpretation(r); s=r['summary']; co=next(c for c in cc if c['original']==r['plan']['id'])
            note('Candidatas',r['plan']['id']+' — '+pretty(r['plan']['spec']['y']),f'{why} Original: N={s["N"]}, G={s["Municípios"]}, R2aj={s["R2 ajustado"]:.8f}. Interseção: N={co["summary"]["N"]}, R2aj={co["summary"]["R2 ajustado"]:.8f}. '+central(r['coef']),r['plan']['refs'])
    note('Inferência','Limites',LIMIT)
    note('Inferência','Interações','Os termos principais são mantidos. Efeito marginal do preço em modelo com produto P×X = bP + bPX·X, na escala transformada de X. Coeficiente do preço isolado refere-se a X=0. Para GAEZ z, zero é a média municipal original; log1p IBAMA zero equivale a zero autos. Não interpretar bP sozinho como efeito médio.')
    note('Inferência','Magnitudes','Y hectares preservado. Y taxa em fração, sem multiplicar por 100. Preço é ln do preço real defasado: aumento de 1% implica aproximadamente 0,01 vezes a inclinação marginal de preço em unidades de Y. ln(estoque/área) é transformação de X, não log de Y. log1p usa unidades originais e preserva zeros válidos.')
    note('Etapa futura','Efeitos fixos','Investigar painéis com heterogeneidade territorial/temporal, exposições preço × capacidade e condicionamento institucional. Níveis comuns de preço serão absorvidos por FE anuais; atributos GAEZ fixos por FE municipais. Rever identificação e componentes de interações antes de estimar. Nenhum desses modelos foi estimado aqui.')
    note('Plano','Registro anterior ao ajuste',planned['created']+'; plano_pre_estimacao.json SHA256='+sha256(HERE/'plano_pre_estimacao.json')+'; cinquenta especificações manuais por destino, reutilizadas entre ha e taxa. Sem busca exaustiva, ordem de variáveis ou escala linear para fabricar modelos. Sem substituições de especificações. Candidatas locais 22/42/46 definidas por mecanismo, sem maximização de R2.')
    note('Dados','Base canônica',str(CSV)+'; SHA256='+meta['csv_sha256'],str(CSV))
    note('Dados','Painel','3.384 pares município-ano; 141 municípios; 2001–2024; 296 colunas de origem; sem chaves duplicadas. 299 colunas após metadados municipais/bioma. Todos os biomas e municípios, sem coorte balanceada obrigatória na OLS.')
    note('Dados','Qualidade Y','Exigir y_cobertura_completa=True. Dos 3.384 pares, 2.772 passam cobertura, ou 612 excluídos. Casos completos finitos para cada modelo, sem imputar, winsorizar ou excluir extremos. Ausências marginais por X sobrepõem-se e não devem ser somadas.')
    note('Dados','Dependentes e origem','MapBiomas coleção 10.1 conforme y_colecao no painel, transição de vegetação nativa em t−1 para agricultura ou pastagem em t. Fluxos brutos em ha. Taxa = conversao_ha__destino / y_nativa_inicial_ha, na mesma máscara; não é variação líquida. Y não foi transformado.',str(DICIO))
    note('Dados','Validação das taxas',js(metadata['ratio_checks'])+'; diferenças compatíveis com arredondamento de ponto flutuante, sem reconstruir ou substituir os Y originais.')
    note('Dados','Denominador e escala','y_nativa_inicial_ha é vegetação em t−1 na máscara das transições. area_referencia_ha é área mapeada em 2000, um controle de escala predeterminado; não se afirma ser área cadastral legal. Controle de estoque em taxas demanda interpretação por também ser denominador de Y.')
    note('Dados','IBAMA','Sem qualquer preenchimento de ausências com zero, em equivalência com este pt_h1. Contagens parciais e somas parciais que são numéricas continuam no modelo; sua presença é explicitada por especificação. Na candidata institucional há 358 contagens parciais entre 1.221 observações. t−1 não elimina resposta endógena da fiscalização a pressões persistentes.')
    note('Dados','Crédito e governança','Não há medida direta adequada de crédito/governança no catálogo inspecionado. Não substituir por contadores de qualidade, códigos ou metadados. IBAMA aproxima registros administrativos, sem medir governança geral ou eficácia.')
    note('Dados','Ausência de informação futura','PAM 1991–2000 e área de 2000 antecedem o painel; preços e IBAMA já em t−1; clima em t−1 por ano civil; estoque de vegetação inicial é t−1. GAEZ é potencial biofísico sob cenário, não previsão econômica histórica nem variável instrumental validada. Evitar produtividades/estoques agropecuários contemporâneos por simultaneidade.')
    note('Rotinas','Modelo','h1lab.data.load_data → h1lab.models.prepare_sample → fit_model. sm.OLS com const explícita, fe=none, cov=cluster_entity, require_y=True. Posto, variação, tamanho amostral, GL e grupos validados pela própria rotina. Não incluir IDs como X. Sem centragem/absorção de FE.')
    note('Rotinas','Defasagens','calendar_lag usa chave (codigo_ibge,ano) e ano civil exato no painel completo antes dos filtros. W recebe uma defasagem adicional; colunas já lag1 de preço, rebanho e IBAMA não recebem lag adicional. Sem preencher lacunas.')
    note('Rotinas','Comparação comum','Modelos locais 22/42/46 de cada dependente: interseção exata das chaves. Mantém-se o painel completo para construir lags e mascara-se apenas Y fora da interseção. Todas as comparações têm N=1.221. Resultados originais da aba Resultados permanecem intactos. IDs CC_Mxxx nas abas Detalhes/Coeficientes, fora da meta.')
    note('Rotinas','Falhas e incidentes','Zero falhas econométricas e zero substituições. Incidente no script de teste: tentou alterar o controle desabilitado de lag de Y; corrigido para não interagir com ele. Conferências comuns refeitas preservando anos anteriores para lags; validado N igual à interseção. Reexecuções de conferência não são novas especificações.')
    note('Dashboard','Instância local','Porta 8503: PID 19428 inspecionado via linha de comando, app.py do pt_h1 correto. Instância reutilizada; acessado http://localhost:8503. Processo filho aponta Python312 base (normal para venv Windows); lote e AppTest usam .venv/Scripts/python.exe.')
    note('Dashboard','Forma e limite da conferência','Quatro modelos conferidos acionando controles e botão Estimar OLS no app.py por Streamlit AppTest, com sessões independentes da sessão do navegador. Inclui M001/M101 simples e M072/M172 múltiplos. N, chaves de amostra, coeficientes e R2 internos comparados numericamente. Não se afirma conferência visual manual de 200 modelos. UI exibe R2 ajustado nas métricas e R2 na seção estatísticas completas.')
    for check in checks:
        note('Dashboard',check['id'],js(check),'conferir_dashboard.py; app.py; h1lab/model_view.py')
    note('Rastreabilidade','Início / fim',metadata['started']+' / '+metadata['finished']+'; fuso UTC−03:00 (America/Sao_Paulo).')
    note('Rastreabilidade','Git',metadata['git_branch']+'; HEAD='+metadata['git_head']+'; estado inicial limpo. Sem branch nova, worktree, commit ou push. Código original e base preservados.')
    note('Rastreabilidade','Versões',js({k:metadata[k] for k in ['python','python_executable','numpy','pandas','statsmodels']}))
    for key,value in metadata['code_hashes'].items(): note('Rastreabilidade','SHA256 código '+key,value,key)
    for key,value in meta['text_sources_sha256'].items(): note('Fontes','Texto consultado '+key,'SHA256='+value,key)
    note('Fontes','Documentação e instruções','AGENTS.md; 2_INTI/RESEARCH_PROTOCOL.md; pt_h1/README.md; app.py; h1lab/data.py, models.py, model_view.py, ui.py, narrative.py; config/selection.json; dicionário; introdução H1/REF7–REF10; revisão das subseções pertinentes. Referências autor/ano transcritas da revisão local, sem auditoria dos artigos originais.')
    note('Fontes','Catálogo e dicionário',str(DICIO)+'; SHA256='+meta['dictionary_sha256']+'; seleção SHA256='+meta['selection_sha256']+'; seleção e ponte textual correspondem aos notebooks/textos atuais.')
    command=f'& "{ROOT / ".venv/Scripts/python.exe"}" -X utf8 "{HERE / "reproduzir.py"}"'
    note('Reprodução','Diretório de execução',str(APP))
    note('Reprodução','Comando completo',f'& "{HERE / "reproduzir_tudo.ps1"}" — estima/retoma, confere 4 modelos no app, consolida as quatro abas, exporta com backup do Excel existente e reabre para verificar.')
    note('Reprodução','1. Estimar / retomar',command+'; plano persistido, JSON por ID e amostras por ID permitem retomar. Não há chamadas a LLM no loop.')
    note('Reprodução','2. Conferir dashboard',f'& "{ROOT / ".venv/Scripts/python.exe"}" -X utf8 "{HERE / "conferir_dashboard.py"}"')
    note('Reprodução','3. Consolidar Excel',f'& "{ROOT / ".venv/Scripts/python.exe"}" -X utf8 "{HERE / "preparar_excel.py"}"; em seguida executar exportar.mjs com Node bundled. O módulo artifact-tool está vinculado ao runtime pelo node_modules local da subpasta.')
    note('Reprodução','Streamlit',f'& "{ROOT / ".venv/Scripts/python.exe"}" -m streamlit run app.py --server.port 8503; acessar http://localhost:8503')
    used=sorted(set(c for r in rr for c in [r['plan']['spec']['y'],*r['plan']['spec']['xs']]))
    for c in used:
        row=cat.loc[c]
        note('Dicionário / interface',pretty(c),f'{c}; definição: {row.definition}; unidade: {row.unit}; variação: {row.variation}; disponibilidade integral={int(data[c].notna().sum())}/3384',str(DICIO))
    for p in planned['models']:
        note('Plano inicial',p['id']+' — '+pretty(p['spec']['y']),formula(p['spec'])+'\n'+p['rationale']+'\nEspecificação JSON: '+js(p['spec']),p['refs'])
    # Exact territorial and temporal identifiers retained inside workbook, by distinct sample.
    seen=set()
    for r in rr:
        sid=r['sample_id']
        if sid in seen: continue
        seen.add(sid)
        sample=pd.read_csv(HERE/(r['plan']['id']+'_amostra.csv'),dtype={'codigo_ibge':str})
        for year,g in sample.groupby('ano'):
            note('Chaves da amostra',sid+' / '+str(year),','.join(sorted(g.codigo_ibge)), 'Identificadores, nunca regressores')
    note('Integridade','Reabertura','Verificação por openpyxl em modo somente leitura após exportação: quatro abas, 200 modelos originais, 50/Y, R2 numérico com precisão, nenhum par Y/especificação duplicado; IDs e coeficientes correspondentes. O registro final verificacao.json registra as asserções executadas.')
    # Embed batch and test sources so methodology and plan survive loss of sidecar files.
    for filename in ['reproduzir_tudo.ps1','reproduzir.py','conferir_dashboard.py','exportar.mjs','verificar_excel.py']:
        lines=(HERE/filename).read_text(encoding='utf-8').splitlines()
        for i in range(0,len(lines),12): note('Código de reprodução',f'{filename} / linhas {i+1}–{min(i+12,len(lines))}','\n'.join(lines[i:i+12]),filename)
    assert len(results)==201 and len(details)==213
    assert all(len(row)==len(details[0]) for row in details)
    dump(HERE/'excel_payload.json',clean({'Resultados':results,'Detalhes':details,'Coeficientes':coefficients,'Metodologia':methods}))
    print(f'Conteúdo: 200 originais, 12 conferências comuns, {len(coefficients)-1} termos, {len(methods)-1} linhas de metodologia.')

if __name__=='__main__':main()
