"""Síntese de todos os modelos e contrastes predefinidos, sem filtro por p."""
from utilitarios import *
c=pd.read_csv(PASTA/'modelos_coeficientes.csv');m=pd.read_csv(PASTA/'modelos_resumo.csv')
def tabela(d):
 cab='| '+' | '.join(d.columns)+' |\n| '+' | '.join(['---']*len(d.columns))+' |\n'
 return cab+'\n'.join('| '+' | '.join(str(v) for v in linha)+' |' for linha in d.itertuples(index=False,name=None))+'\n'
rows=m[['id','N','municipios','clusters_ano','ajuste_tipo','ajuste','cov_correcao']].copy();rows['ajuste']=rows.ajuste.round(4)
principal=c[c.id.str.startswith(('P02','P03')) & c.termo.isin(['expo_soja','expo_milho','fiscal','preco_fiscal'])][['id','termo','coef','ic95_inf','ic95_sup','p']].copy()
for x in ['coef','ic95_inf','ic95_sup','p']:principal[x]=principal[x].round(5)
texto='''# Síntese dos experimentos executados

Foram estimados 24 modelos, com todos os resultados preservados, incluindo associações compatíveis com zero e de sinais contrários. A informação disponível não identifica causalidade nem permite uma decisão isolada de confirmar/rejeitar H1.

## Dados e seleção

3.384 pares na grade, 2.772 conversões válidas em 137 municípios. A inclusão de fiscalização defasada reduz a amostra a 1.140 pares em 128 municípios (23 anos). M01C e M02 compartilham a amostra; P01–P03 também. A cobertura não é aleatória. Pantanal: quatro municípios na grade e apenas um na amostra fixa; sem regressões próprias. Os 265 zeros agrícolas foram mantidos. O CSV não permite reconstruir a validade geográfica dos mapas ou as médias mensais de preços.

## O que os ajustes mostram

OLS simples associa preços mais elevados a menores taxas de conversão; tendências e omissões impedem interpretar isso como resposta causal. OLS múltipla e sua versão em amostra comum mostram que acrescentar fiscalização muda também quais observações são utilizáveis. As tabelas preservam as duas comparações.

No TWFE P02, as exposições soja×aptidão e milho×aptidão da agricultura têm IC que incluem zero. Na pastagem, a exposição soja×aptidão é positiva com intervalo próximo de zero; ao acrescentar preço×fiscalização (P03), seu IC passa a incluir zero. Isso evidencia sensibilidade à especificação, não prova de ausência ou presença do mecanismo. A associação positiva das autuações com conversão agrícola pode refletir resposta às infrações, e não efeito de fiscalização aumentando conversão.

PPML e logit fracional preservam zeros e a escala apropriada, mas não incluem FE municipal; não são testes equivalentes ao TWFE. Hectares, frações e suas ligações respondem a perguntas diferentes. As quatro covariâncias GLM precisaram de correção PSD; comparar com SE brutos e cluster municipal e evitar inferência forte. Efeitos marginais são apenas o componente diferencial por aptidão, sem efeito comum anual identificado.

As ITS estimam queda de nível na segmentação pós-2006 e mudança positiva na segmentação pós-2012, mas as séries estão sujeitas a políticas concorrentes, antecipação e tendência. O placebo 2010 também apresenta mudanças de inclinação. Nenhuma dessas estimativas mede o efeito causal da Moratória ou do Código Florestal. Não houve RDD, DiD ou event study estimado.

## Grade integral e amostras

ITS têm 95 municípios agregados, não 95 clusters independentes do choque temporal. Seus N são anos, e clusters ficam em zero porque a inferência usa HAC. R² de OLS, R² transformado de painel e pseudo-ajuste GLM não são critérios intercambiáveis de seleção.

'''+tabela(rows)+'''
## Coeficientes TWFE de interesse

Taxas em pontos percentuais; exposições usam preço e aptidão em DP; fiscalização representa 10 autos anteriores válidos. IC95 e p usam covariância two-way com correção PSD quando necessária e t com 22 graus de liberdade. Sem ajuste de multiplicidade; nenhum modelo foi escolhido pelo p-valor.

'''+tabela(principal)+'''
## Entregáveis e verificação

`modelos_coeficientes.csv`: 220 coeficientes, SE/IC/p, interpretação, alertas, ajustes e metadados. `modelos_resumo.csv`: 24 ajustes. `amostras_perdas.csv`: exclusões sequenciais. `marginais_*.csv`: efeitos diferenciais GLM. `auditoria_*.csv`: distribuição, suporte, taxa e absorção. `sensibilidade_*.csv`: cluster municipal ou HAC lag2. `cov_bruta_*.csv`: matrizes anteriores à correção PSD.

A correção PSD foi necessária em cinco ajustes; não foi acionada por significância. Os 90 SE brutos associados a variâncias negativas permanecem ausentes nessa coluna, com alerta; os SE principais corrigidos são finitos. Dados, textos e demais arquivos rastreados foram preservados. Os sete notebooks foram executados integralmente em kernels novos, e N, perdas, amostras comuns, coeficientes e hashes foram conferidos. Logs e versões: `2_INTI/audit/testes_chap1_20261023`.

Commit e push para main autorizados pelo usuário em 23/10/2026. Consulte o histórico do Git para a publicação do pacote. Limitações metodológicas e fontes oficiais estão em LEIA_ME.md. A estratégia .tex não foi validada nem alterada.
'''
(PASTA/'SINTESE.md').write_text(texto)
# Grade final registra a comparação adicional em amostra comum.
m[['id','titulo','vd','vi','estimador','fe']].to_csv(PASTA/'grade_planejada.csv',index=False)

# Recorte substantivo solicitado: exclui interceptos e dummies de FE.
termos=['z_p_soja','z_p_milho','z_p_boi','expo_soja','expo_milho','fiscal','preco_fiscal']
h1=c[c.termo.isin(termos)].merge(pd.read_csv(PASTA/'sensibilidades_covariancia.csv')[['id','termo','se_sensibilidade','p_sensibilidade']],on=['id','termo'],validate='one_to_one')
h1.to_csv(PASTA/'resultados_H1.csv',index=False)
com_p=h1[h1.p.lt(.05)][['id','termo','coef','se','ic95_inf','ic95_sup','p','N','cov_correcao','p_sensibilidade']].copy()
for col in ['coef','se','ic95_inf','ic95_sup','p','p_sensibilidade']:com_p[col]=com_p[col].round(6)
with (PASTA/'SINTESE.md').open('a') as f:
 f.write('\n## Pergunta sobre significância\n\n'+str(len(com_p))+' de '+str(len(h1))+' coeficientes de preços, fiscalização e interações têm p<0,05 na inferência principal, sem correção por múltiplas comparações. Não inclui interceptos, dummies FE, aptidões isoladas ou quebras temporais. O arquivo resultados_H1.csv preserva todo o recorte, inclusive resultados não significativos. A coluna p_sensibilidade usa cluster municipal. Nenhum desses resultados, isoladamente, confirma H1 ou causalidade.\n\n'+tabela(com_p))
