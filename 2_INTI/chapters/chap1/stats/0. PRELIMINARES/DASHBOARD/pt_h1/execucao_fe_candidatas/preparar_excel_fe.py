from estimar_fe import *
def txt(x):return json.dumps(clean(x),ensure_ascii=False,sort_keys=True)
def term_expression(term,spec):
    if ' × ' in term:
        a,b=term.split(' × ');return '('+term_expression(a,spec)+') × ('+term_expression(b,spec)+')'
    lag=spec.get('lags',{}).get(term,0);tr=spec.get('transforms',{}).get(term,'level')
    ex=f'L{lag}_calendario({term})' if lag else term
    return f'ln({ex})' if tr=='log' else f'ln(1+{ex})' if tr=='log1p' else ex
def conclusion(r):
    mid=r['plan']['id']
    if mid in ['M022','M072','M122','M172']:
        return 'Base TWFE: preço próprio, aptidão e área não têm coeficientes isolados identificáveis. Examina variação de vegetação inicial e clima dentro do município após choques anuais comuns.'
    if mid in ['M042','M142']:
        return 'Interação preço × aptidão permanece negativa (p≈0,01). Associação contrária à previsão positiva simples; considerar heterogeneidade de tendências e oportunidades em áreas já abertas. Não confirma causalidade.'
    if mid=='M092':return 'Interação preço da carne × aptidão agrícola positiva (p≈0,047), próxima ao limiar convencional. Proxy GAEZ milho não é aptidão pecuária direta; evidência exploratória frágil e distinta da taxa.'
    if mid=='M192':return 'Interação preço × aptidão imprecisa (p≈0,894) e praticamente sem ganho de R² parcial. Manter a pergunta econômica, sem evidência estatística nesta especificação.'
    return 'Interação preço × IBAMA imprecisa com TWFE. O sinal pooled não demonstra condicionamento institucional robusto. Cobertura seletiva e contagens parciais exigem cautela.'

def main():
    rr=json.loads((HERE/'resultados_fe.json').read_text(encoding='utf-8'))
    meta=json.loads((HERE/'metadata_fe.json').read_text(encoding='utf-8'))
    source=meta['source'];full,cat,_=load_data()
    mainrows=[['Candidata','Variável dependente','N comum','R2 pooled original','R2 TWFE total','R2 TWFE parcial aos FE','Conclusão exploratória','Municípios / clusters','Período','R2 apenas FE','R2 ajustado pooled','R2 ajustado TWFE','R2 pooled termos identificáveis','Δ R2 total (TWFE − pooled)','Termos absorvidos','Termos identificáveis TWFE','Interação: b pooled','Interação: p pooled','Interação: b TWFE','Interação: p TWFE','ID da amostra','Recomendação posterior']]
    comparisons=[['Candidata','Variável dependente','Termo técnico','Expressão e escala efetiva','Situação TWFE','b pooled original','EP pooled original','p pooled original','b pooled reduzido','p pooled reduzido','b TWFE','EP TWFE','p TWFE','IC 95% TWFE inferior','IC 95% TWFE superior','Δ b (TWFE − pooled original)','Comparação de sinais','N comum','Motivo / limite']]
    absorption=[['Candidata','Variável dependente','Termo técnico','Expressão e escala efetiva','Situação','Motivo','Absorvido por município isolado','Absorvido por ano isolado','Norma residual / norma original','DP residual após município + ano','N comum','Efeito sobre a especificação']]
    details=[['ID do ajuste','Candidata','Variável dependente','Modelo','N','Municípios / clusters','Anos','Período','R2 total','R2 ajustado','R2 parcial aos FE','RMSE = sqrt(SSE/N)','Parâmetros totais','GL residuais','GL inferência t','ID amostra','Fórmula / transformações','Termos absorvidos na TWFE','Ledger da amostra original','Ausências marginais originais','N por ano','N por bioma','Base municipal / anual das dummies','Erros-padrão','Flags IBAMA parciais','Singletons municipais','Validação FWL','Advertências e limites']]
    coefficients=[['ID do ajuste','Candidata','Modelo','Termo técnico','Tipo de termo','Coeficiente','Erro-padrão','Estatística t','Valor-p','IC 95% inferior','IC 95% superior','Situação / inferência']]
    methodology=[['Categoria','Item','Conteúdo','Origem']]
    def note(a,b,c,d='Execução local; h1lab/models.py'):methodology.append([a,b,str(c),d])
    diagnostics=[]
    for r in rr:
        mid=r['plan']['id'];spec=r['plan']['original_spec'];label=pretty(spec['y']);fits=r['fits']
        po=fits['Pooled original'];pr=fits['Pooled termos identificáveis'];tw=fits['TWFE município + ano'];s=tw['summary']
        pcoef={v['term']:v for v in po['coef']};rcoef={v['term']:v for v in pr['coef']};tcoef={v['term']:v for v in tw['coef']}
        inter=next((x for x in tw['terms'] if ' × ' in x),None)
        recommendation=('Priorizar entendimento do sinal negativo da interação e checar tendências/exposição, sem seleção pelo valor-p.' if mid in ['M042','M142'] else 'Investigar se a associação em ha reflete escala e oportunidade agrícola; evitar conclusão binária por p<0,05.' if mid=='M092' else 'Retida como hipótese provisória; melhorar mensuração institucional e avaliar suporte antes de ampliar o modelo.' if mid in ['M046','M096','M146','M196'] else 'Referência para aprofundamento; manter comparação na mesma amostra.')
        mainrows.append([mid,label,s['N'],po['summary']['R2'],s['R2'],s['R2 parcial aos efeitos fixos'],conclusion(r),s['Municípios'],f'{r["sample_min"]}–{r["sample_max"]}',r['fe_only_r2'],po['summary']['R2 ajustado'],s['R2 ajustado'],pr['summary']['R2'],s['R2']-po['summary']['R2'],'; '.join(r['absorbed']),'; '.join(r['kept']),pcoef[inter]['coef'] if inter else None,pcoef[inter]['p'] if inter else None,tcoef[inter]['coef'] if inter else None,tcoef[inter]['p'] if inter else None,r['sample_id'],recommendation])
        for a in r['absorption']:
            term=a['term'];pi=pcoef[term];ri=rcoef.get(term);ti=tcoef.get(term)
            status='Absorvido — coeficiente não identificado' if a['absorbed'] else 'Identificável'
            signs='Não comparável: absorvido' if ti is None else 'Mesmo sinal' if np.sign(pi['coef'])==np.sign(ti['coef']) else 'Mudança de sinal'
            comparisons.append([mid,label,term,term_expression(term,spec),status,pi['coef'],pi['se'],pi['p'],ri['coef'] if ri else None,ri['p'] if ri else None,ti['coef'] if ti else None,ti['se'] if ti else None,ti['p'] if ti else None,ti['ci_low'] if ti else None,ti['ci_high'] if ti else None,ti['coef']-pi['coef'] if ti else None,signs,s['N'],a['reason']+'. Diferença de coeficientes não é um teste formal entre estimadores.'])
            absorption.append([mid,label,term,term_expression(term,spec),status,a['reason'],a['entity_absorbed'],a['year_absorbed'],a['relative_residual_norm'],a['within_sd'],s['N'],'Retirado da matriz explícita; sua contribuição aditiva é contida nos FE. Não equivale a efeito zero.' if a['absorbed'] else 'Mantido, inclusive quando um ou ambos os componentes da interação são absorvidos.'])
        sample=pd.read_csv(HERE/(mid+'_amostra_transformada.csv'),dtype={'codigo_ibge':str})
        counts=sample.groupby('codigo_ibge').size();singletons=counts[counts.eq(1)].index.tolist()
        F=effects_design(sample)
        X=np.column_stack([F.to_numpy(float),sample[r['kept']].to_numpy(float)])
        U,sv,V=np.linalg.svd(X,full_matrices=False);hat=np.square(U).sum(axis=1)
        n_unit=int(np.isclose(hat,1,rtol=0,atol=1e-10).sum())
        diag={'candidate':mid,'singleton_municipalities':singletons,'singleton_count':len(singletons),'near_unit_leverage':n_unit,
          'clusters':int(s['Municípios']),'clusters_non_singletons':int(s['Municípios']-len(singletons)),
          'economic_coefficient_inference_finite':all(all(v[k] is not None and np.isfinite(v[k]) for k in ['coef','se','t','p','ci_low','ci_high']) for v in tw['coef'])}
        assert diag['economic_coefficient_inference_finite']
        diagnostics.append(diag)
        for model,fit in fits.items():
            prefix={'Pooled original':'PO','Pooled termos identificáveis':'PR','TWFE município + ano':'TW'}[model];fid=prefix+'_'+mid;ss=fit['summary']
            formula=spec['y']+' = '+('α_i + λ_t' if prefix=='TW' else 'β0')+' + '+' + '.join(term_expression(t,spec) for t in fit['terms'])+' + ε_it'
            limit='Associação exploratória; seleção entre 200 especificações não incorporada nos valores-p. FE não removem confundidores municipais variantes no tempo, simultaneidade, mensuração ou spillovers. Cluster municipal não controla dependência entre municípios.'
            if prefix=='TW':limit+=f' {len(singletons)} municípios têm uma observação e não identificam inclinações within; {n_unit} observações com alavancagem≈1. Resíduos studentizados e Cook podem ser indefinidos nesses pares; não houve exclusão. Inferência dos coeficientes econômicos finita e validada. Dummies e const dependem da categoria-base e não são interpretadas economicamente.'
            if mid in ['M046','M096','M146','M196']:limit+=' IBAMA mantém 358 observações com flag de contagem parcial entre 1.221; sem imputar ausências a zero.'
            if spec['y'].startswith('taxa'):limit+=' Taxa em fração; OLS não restringe previsões a [0,1]; vegetação inicial também é denominador.'
            details.append([fid,mid,label,model,ss['N'],ss['Municípios'],ss['Anos'],f'{r["sample_min"]}–{r["sample_max"]}',ss['R2'],ss['R2 ajustado'],ss['R2 parcial aos efeitos fixos'] if prefix=='TW' else None,ss['RMSE'],fit['parameters'],ss['Graus de liberdade residuais'],ss['Graus de liberdade da inferência'],fit['sample_id'],formula,'; '.join(r['absorbed']),txt(r['ledger']),txt(r['missing']),txt(r['per_year']),txt(r['per_biome']),f'{r["baseline_entity"]} / {r["baseline_year"]}' if prefix=='TW' else 'Não se aplica','Cluster município; correção finita; t com G−1 GL',txt(r['partial_ibama']),len(singletons),f'erro máximo slopes={r["fwl_beta_max_error"]:.8g}; resíduos={r["fwl_residual_max_error"]:.8g}' if prefix=='TW' else 'Pooled reproduzido; mesma chave amostral',limit+' '+' '.join(fit['warnings'])])
            for v in fit['all_coef']:
                is_fe=v['term'].startswith('FE_');const=v['term']=='const'
                coefficients.append([fid,mid,model,v['term'],'Dummy de efeito fixo' if is_fe else 'Intercepto / categoria-base' if const else 'Regressor econômico',*[v[k] for k in ['coef','se','t','p','ci_low','ci_high']],'Estimado; cluster município, correção finita; t com G−1 GL. '+('Coeficiente de normalização, sem interpretação estrutural.' if is_fe or const else '')])
            if prefix=='TW':
                for a in r['absorption']:
                    if a['absorbed']:coefficients.append([fid,mid,model,a['term'],'Regressor absorvido',None,None,None,None,None,None,'Não identificado, não igual a zero. '+a['reason']])
        note('Resultados',mid,conclusion(r)+f' N={s["N"]}; R2 pooled={po["summary"]["R2"]:.8f}; R2 TWFE total={s["R2"]:.8f}; R2 parcial={s["R2 parcial aos efeitos fixos"]:.8f}.',r['refs'])
    note('Escopo','Estimativas','12 candidatas previamente destacadas, sem nova seleção. 12 TWFE município+ano, 12 pooled originais e 12 pooled com os termos identificáveis, total de 36 ajustes. Mesma amostra dentro de cada trio; N=2.655 nas bases/interações de capacidade e N=1.221 nas institucionais. Não comparar especificações de amostras distintas como se fossem o mesmo recorte.')
    note('Preservação','Excel anterior',source['source']+'; SHA256 antes='+source['sha256']+'. Arquivo já apresentava modificação local ao iniciar esta etapa. Não foi regravado nem restaurado. Identificação das candidatas feita por ID e prioridade da aba Detalhes, respeitando sua ordenação atual.')
    note('Absorção','Regra','Preço próprio log real em t−1 comum por ano é absorvido por FE anuais. GAEZ z e ln(área de referência de 2000) são constantes por município e absorvidos por FE municipais. Três termos por candidata, 36 registros absorvidos. Nenhum coeficiente absorvido é registrado como zero ou estimado por pseudoinversa arbitrária.')
    note('Absorção','Teste numérico','Projeção dos Xs contra intercepto e dummies municipais/anuais na amostra de cada candidata. Absorção se ||M_FE x|| / ||x|| ≤ 1e−10. Também examinada absorção separada por município e por ano. Restante: posto completo e GL positivos, verificações de h1lab.models.fit_model.')
    note('Interações','Constituintes','Produtos formados após transformações e lags originais e antes da absorção. Na interação preço × aptidão, ambos os efeitos principais são contidos no espaço das dummies; o produto pode variar após projeção. Na interação preço × IBAMA, preço é absorvido e o termo log1p(autos t−1) é mantido. Não reconstruir interação depois de retirar componentes nem exigir suas inclinações isoladas quando não identificáveis.')
    note('Execução','Reuso do dashboard','Pooled original via load_data → fit_model(full,FILTERS,spec). A amostra transformada contém os mesmos pares, lags e produtos do pooled. Após diagnosticar absorção, fit_model(sample,FILTERS,spec_reduzida) estima pooled reduzido e TWFE com transformações vazias e lag0 para não aplicar duas vezes. Dados de origem e aplicativo preservados; nenhuma implementação alternativa de covariância.')
    note('Execução','Limite da interface','A interface original bloqueia a especificação quando contém regressoras absorvidas, sem descartá-las automaticamente. Esta execução documenta e retira explicitamente os termos não identificáveis antes de chamar a mesma rotina, mantendo os produtos previamente construídos. Não foi alterado o app para esconder absorção.')
    note('Amostra','Construção','Filtros 2001–2024, todos os três biomas, todos os municípios; require_y=True; exclusão conjunta por valores não finitos/domínios apenas para cada especificação original. Clima t−1 por ano civil exato no painel completo. 2001 não tem ano anterior no painel; período efetivo 2002–2024. Sem imputação de zeros, winsorização ou remoção de outliers/singletons.')
    note('Amostra','Pareamento','Hashes SHA256 calculados das chaves codigo_ibge,ano ordenadas e conferidos entre os três modelos de cada candidata e contra os registros do lote anterior. Dropar uma regressora absorvida não recupera observações excluídas antes da estimação. Amostras exatas embutidas por hash/ano abaixo e CSV transformado por candidata na subpasta de execução.')
    note('Amostra','Singletons e influência','Trio amplo: 137 municípios, sendo 3 com uma observação. Trio institucional: 130 municípios, sendo 9 com uma observação. Mantidos para equivalência amostral. Não trazem variação within própria; há alavancagem unitária e warnings de sqrt em resíduos studentizados clássicos do dashboard. Esses diagnósticos podem ser indefinidos; não são falhas das inclinações/inferências econômicas, que foram verificadas como finitas. GL e correção de cluster seguem a matriz completa com dummies, sem ajustes de software externo.')
    note('Inferência','Configuração','Statsmodels OLS; dummies explícitas de município e ano, intercepto e primeira categoria omitida. cov_type=cluster, groups=codigo_ibge, use_correction=True, df_correction=True, use_t=True. G=137 ou 130; GL t=G−1. Inclui todos os parâmetros FE na correção finita. Não agrupa por ano; choques comuns remanescentes/spillovers podem limitar inferência. P-valores exploratórios sem ajuste por multiplicidade.')
    note('Ajuste','R2 total versus parcial','R2 total=1−SSE/SST centrado de Y, inclui dummies. R2 parcial aos FE=1−SSE_TWFE/SSE_apenas_FE, com SSE_apenas_FE obtida projetando Y somente nos FE municipais e anuais na mesma amostra. Não é R2 de demeaning apenas municipal. Um R2 total maior é esperado pela expansão da matriz e não valida economicamente os Xs nem demonstra causalidade.')
    note('Ajuste','R2 ajustado e RMSE','R2 ajustado considera todos os parâmetros independentes, inclusive FE. RMSE exibido pelo dashboard = sqrt(SSE/N), diferente de sqrt(SSE/GL_resid). Em pooled, R2 parcial aos FE é deixado em branco nesta entrega para evitar equipará-lo ao parcial TWFE.')
    note('Coeficientes','Escalas e leitura','Y hectares preservado; taxa em fração (multiplicar coeficientes por 100 para pontos percentuais). Preço já é ln real em dólares2024 lag1; GAEZ z original; estoque/área ln; autos log1p; chuva em mm/ano defasada. Interação preço × aptidão é mudança da associação ao preço por 1 DP de aptidão; efeito de nível de preço comum não é identificável sob FE anuais. Coeficientes de FE e intercepto dependem da normalização.')
    note('Interpretação','Limites de H1','FE controlam diferenças municipais invariantes e choques anuais comuns, sem garantir identificação causal. Não resolvem endogeneidade da fiscalização, heterogeneidade de tendências, retorno líquido não observado ou mensuração. Aptidão milho em pastagem é oportunidade agrícola, não capacidade pecuária direta. A revisão local motiva mecanismos; artigos originais não foram auditados nesta etapa.')
    note('Validação','FWL independente','Para as 12 TWFE, projetar Y e X mantidos contra o mesmo F=[const,dummies município,dummies ano]; obter slopes por numpy.linalg.lstsq dos resíduos e comparar com o modelo completo. Resíduos finais e R2 parcial também conferidos. Inferência sempre vem do TWFE completo, nunca de regressão iid dos resíduos. Erros máximos e status nas abas Detalhes e nos JSON.')
    note('Rastreabilidade','Execução',meta['date']+'; Python='+meta['python_executable']+'; numpy='+meta['numpy']+'; pandas='+meta['pandas']+'; statsmodels='+meta['statsmodels']+'; branch=main; HEAD='+meta['git_head']+'. Sem commit/push/worktree/branch nova.')
    note('Rastreabilidade','CSV',str(CSV)+'; SHA256='+meta['data']['csv_sha256'])
    for path,digest in meta['code_hashes'].items():note('Rastreabilidade','Código '+path,'SHA256='+digest,path)
    note('Fontes','Instruções e fundamentação','AGENTS.md; 2_INTI/RESEARCH_PROTOCOL.md; pt_h1/README.md; h1lab/data.py e models.py; dicionário aed_chap1_pt_DICIO.ipynb; 0_introduction.tex, H1/REF7–REF9; 1_literature_review.tex, Preços, capacidade produtiva e usos alternativos da terra e Fiscalização e pressão econômica em Mato Grosso. Dados e textos não alterados.')
    for col in sorted(set(t for r in rr for t in [r['plan']['original_spec']['y'],*r['plan']['original_spec']['xs']])):
        note('Dicionário',pretty(col),col+'; '+cat.loc[col,'definition']+'; unidade='+cat.loc[col,'unit'],str(DICIO))
    note('Reprodução','Comando completo',f'& "{HERE / "reproduzir_fe.ps1"}"; executar a partir de qualquer diretório. Usa .venv do projeto para regressões e runtime bundled para Excel. O script verifica a preservação do arquivo anterior e faz backup datado se o novo Excel já existir.')
    for p in json.loads((HERE/'plano_fe.json').read_text(encoding='utf-8'))['models']:note('Plano anterior aos ajustes',p['id'],txt(p),'plano_fe.json')
    seen=set()
    for r in rr:
        if r['sample_id'] in seen:continue
        seen.add(r['sample_id'])
        sample=pd.read_csv(HERE/(r['plan']['id']+'_amostra_transformada.csv'),dtype={'codigo_ibge':str})
        for year,g in sample.groupby('ano'):note('Chaves amostrais',r['sample_id']+' / '+str(year),','.join(sorted(g.codigo_ibge)),'Identificadores para pareamento, não Xs numéricos')
    for diag in diagnostics:note('Diagnóstico',diag['candidate'],txt(diag))
    for name in ['extrair_candidatas.py','estimar_fe.py','reproduzir_fe.ps1','exportar_fe.mjs','verificar_fe.py']:
        path=HERE/name
        if path.exists():
            lines=path.read_text(encoding='utf-8').splitlines()
            for i in range(0,len(lines),10):note('Código de reprodução',f'{name}: linhas {i+1}–{min(i+10,len(lines))}','\n'.join(lines[i:i+10]),name)
    save('diagnosticos_fe.json',diagnostics)
    payload={'Resultados':mainrows,'Comparação':comparisons,'Absorção':absorption,'Detalhes':details,'Coeficientes':coefficients,'Metodologia':methodology}
    for sheet,rows in payload.items():assert all(len(row)==len(rows[0]) for row in rows),sheet
    save('excel_fe_payload.json',payload)
    audit=ROOT/'2_INTI/audit/fe_candidatas_20261018';audit.mkdir(parents=True,exist_ok=True)
    (audit/'RELATORIO_FE.md').write_text('# Candidatas H1 com efeitos fixos\n\n12 TWFE e 24 pooled, 36 ajustes. Comparação na mesma amostra por candidata.\n\n'+'\n\n'.join(r['plan']['id']+': '+conclusion(r) for r in rr)+'\n\nExcel anterior preservado: '+source['sha256']+'\n\nRegistros/reprodução: '+str(HERE)+'\n\nSem falhas econométricas. Warnings de influência por singletons registrados na metodologia. Sem commit ou push.\n',encoding='utf-8')
    print('Conteúdo consolidado: 12 candidatas, 36 ajustes, 36 absorções, '+str(len(coefficients)-1)+' termos/linhas de coeficientes.')

if __name__=='__main__':main()
