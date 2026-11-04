from pathlib import Path
import sys
p=Path(__file__).resolve().parent;sys.path.insert(0,str(p.parent/'testes2'))
from metodos import *
c=pd.read_csv(p/'COEFICIENTES.csv');m=pd.read_csv(p/'MODELOS.csv');g=pd.read_csv(p/'MAGNITUDES.csv');j=pd.read_csv(p/'TESTES_CONJUNTOS.csv')
def table(d):return '| '+' | '.join(d.columns)+' |\n| '+' | '.join(['---']*len(d.columns))+' |\n'+'\n'.join('| '+' | '.join(str(v) for v in row)+' |' for row in d.round(6).itertuples(index=False,name=None))+'\n'
rows=[]
for ident in m[m.id.str.startswith('C0')].id:
 sub=c[c.id.eq(ident)].set_index('termo');mm=m[m.id.eq(ident)].iloc[0]
 for metodo in ['DK1','DK2','DK3','municipio','two_way_bruto']:
  cv=pd.read_csv(p/f'cov_{ident}_{metodo}.csv',index_col=0)
  for cultura in ['soja','milho']:
   names=[f'expo_{cultura}_l{l}' for l in [1,2,3]];value=sub.loc[names,'coef'].sum();var=cv.loc[names,names].to_numpy().sum();se=np.sqrt(var) if var>=0 else np.nan;df=mm.municipios-1 if metodo=='municipio' else mm.anos-1;crit=stats.t.ppf(.975,df)
   rows.append(dict(id=ident,cultura=cultura,covariancia=metodo,soma=value,se=se,ic95_inf=value-crit*se,ic95_sup=value+crit*se,p=2*stats.t.sf(abs(value/se),df)))
s=pd.DataFrame(rows);s['p_holm']=np.nan
for name,ix in s.groupby('covariancia').groups.items():
 valid=s.loc[ix,'p'].notna();ii=s.loc[ix].index[valid]
 s.loc[ii,'p_holm']=multipletests(s.loc[ii,'p'],method='holm')[1]
s.to_csv(p/'SENSIBILIDADE_CUMULATIVOS.csv',index=False)
text='''# Resultados — rodada 4

346 ajustes: 22 substantivos, 2 referências e 322 refits diagnósticos leave-one-out. Não são 346 desenhos independentes. Todas as reestimações e exclusões foram registradas, sem escolha de observação pelo resultado. Seis notebooks concluídos; a rodada1 e fontes foram preservadas.

## O que os diagnósticos discriminam

A associação estática soja×aptidão/pastagem mantém o sinal em todas exclusões individuais de município/ano. Nas exclusões anuais, o coeficiente varia entre 0,0912 e 0,1202 pp; nas municipais, entre 0,0932 e 0,1161. Isso afasta a explicação estrita de que um único município ou ano produz o sinal da especificação de referência; não elimina confundimento comum nem valida causalidade. Milho/agricultura pode trocar de sinal em exclusões isoladas e permanece impreciso.

A soma dinâmica de soja/pastagem é 0,1637 com tendências municipais (IC95 [0,0985;0,2290]), mas 0,0102 com FE bioma×ano (IC95 [−0,0436;0,0640]). Nesse segundo controle, milho/pastagem soma 0,1287 (IC95 [0,0533;0,2042]). Portanto, é instável atribuir a co-movimentação diferencial a um produto específico. Isso é compatível com confundimento/heterogeneidade de choques, mas não identifica quais políticas, custos ou mecanismos os geraram. Na janela pós2010, a soma milho/agricultura é negativa sob inferência DK, contraponto à versão universal de resposta positiva; T=14 e o resultado exige cautela adicional de inferência.

Os testes conjuntos das diferenças de slopes Amazônia−Cerrado não rejeitam após multiplicidade e seus IC são amplos. Isso não demonstra homogeneidade entre biomas. A classificação por predominância municipal limita qualquer interpretação de geografia do desmatamento. Pantanal não foi forçado a fornecer um efeito próprio.

A evidência de curvatura agrícola não passa a correção dos testes conjuntos substantivos; não escolher um limiar de preço a posteriori. As margens de ocorrência e taxa estritamente positiva são imprecisas. Ausência de rejeição não implica ausência de mecanismo ou conservação ativa. O modelo condicionado a positivos tem seleção pela VD e é apenas descritivo.

Fixar o estoque de referência de 2001 altera pouco a associação soja/pastagem no núcleo. Assim, o movimento anual do denominador, sozinho, não explica esse coeficiente nessa especificação. O estoque2001 continua endógeno/selecionado. O painel fixo mantém sinais de pastagem, mas a precisão individual se reduz após multiplicidade. Isso não justifica assumir missing-at-random.

## Por que mais uma rodada

Alguns Wald F das equações com seis lags ficaram extremamente elevados na janela de 14 anos. A etapa5 terá foco exclusivo em inferência sob poucos blocos temporais, não novos regressores. Testes assintóticos fortes não tornam o desenho identificado. A validade de independência/simetria entre blocos também precisará ser explicitada; não há teste finito exato garantido por estes dados observacionais.

## Resumo da influência

'''+table(pd.read_csv(p/'RESUMO_INFLUENCIA.csv'))+'''\n## Coeficientes substantivos (refits integrais no CSV)\n\n'''+table(c[~c.id.str.startswith('I_')][['id','termo','coef','ic95_inf','ic95_sup','p','p_holm','N','anos']])+'''\n## Somas dinâmicas\n\n'''+table(g[g.contraste.str.startswith('Soma')][['id','contraste','estimativa','ic95_inf','ic95_sup','p','p_holm']])+'''\n## Testes conjuntos substantivos\n\n'''+table(j[~j.id.str.startswith('I')][['id','termos','F','p','p_holm']])+'''\n## Reprodução\n\n`python reproduzir.py` com requirements.txt em ambiente externo. COEFICIENTES.csv/MODELOS.csv/TESTES_CONJUNTOS.csv contêm tudo; RESUMO_INFLUENCIA.csv e auditoria_retiradas.csv permitem rastrear exclusões. MAGNITUDES.csv contém slopes, derivadas e contrastes; SENSIBILIDADE_CUMULATIVOS.csv usa a covariância completa das somas. Protocolos, hashes e validação registrados antes/depois; logs em 2_INTI/audit/testes4. Nenhum commit/push/publicação.\n'''
(p/'RESULTADOS.md').write_text(text)

# A família de Holm não engloba automaticamente a busca sequencial.
with (p/'RESULTADOS.md').open('a') as f:
 f.write('\n## Escopo da multiplicidade e da adaptação\n\nHolm aplica-se somente às famílias registradas nesta rodada, com tamanho em n_familia nos CSVs. As rodadas foram adaptadas aos diagnósticos anteriores e reutilizam os mesmos dados: a correção por família/rodada não controla integralmente o erro da busca sequencial nem converte exploração em teste confirmatório. Uma confirmação independente exige protocolo externo/prévio e dados novos ou identificação adicional.\n')
