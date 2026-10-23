from pathlib import Path
import pandas as pd
p=Path(__file__).resolve().parent;b=pd.read_csv(p/'BOOTSTRAP.csv')
def table(d):return '| '+' | '.join(d.columns)+' |\n| '+' | '.join(['---']*len(d.columns))+' |\n'+'\n'.join('| '+' | '.join(str(v) for v in row)+' |' for row in d.round(6).itertuples(index=False,name=None))+'\n'
text='''# Resultados — rodada 5

Oito equações de referência (já estudadas, reestimadas para a inferência), 16 restrições escalares em dois tamanhos de bloco: 32 exercícios wild bootstrap e 36.480 padrões de sinais enumerados. Nenhuma variância degenerada. A hipótese nula foi imposta, os FE foram reestimados via projeção e padrões selecionados foram conferidos contra reestimação direta. O padrão com todos pesos +1 reproduz a estatística observada. Não houve erro Monte Carlo; isso não torna o teste exato nem valida independência/simetria de blocos.

A soma dinâmica soja/pastagem, sem choques específicos de bioma, tem p wild bruto 0,0078125 e Holm 0,125 com blocos de três anos; com dois anos, p bruto 0,0019531 e Holm 0,03125. Não escolher dois anos porque rejeita. A associação estática soja/pastagem tem p wild 0,08594 (blocos3) e 0,04639 (blocos2), ambos sem rejeição após Holm. O resultado dinâmico milho/pastagem sob FE bioma×ano tem p wild 0,015625/0,03125, mas Holm 0,234375/0,4375. Assim, há sinal associativo em especificações, mas sua força inferencial depende de pressupostos temporais e família de testes.

Na janela de 14 anos, três anos por bloco geram somente cinco blocos e 32 padrões. Num teste bilateral com simetria, a resolução mínima é 2/32=0,0625. A falta de rejeição em 5% nessa janela não pode ser interpretada como ausência de efeito. O IC95 exportado é DK assintótico, não IC bootstrap; não foi feita inversão de bootstrap nem teste de equivalência. Nem a enumeração nem a multiplicidade removem confundimento.

Não serão abertas novas rodadas de busca de especificação. As etapas anteriores examinaram questões econômicas/estatísticas distintas; esta etapa mostrou que a força dos p-valores também depende de poucos blocos temporais. Permanecem associações condicionais e limites de mensuração/identificação, não H1 aceita ou rejeitada causalmente. CONCLUSAO_RODADAS.md integra o que foi discriminado, o que permanece aberto e os dados necessários.

## Todos os exercícios

'''+table(b[['id','contraste','estimativa','se_DK2','ic95_DK_inf','ic95_DK_sup','p_DK2','bloco_anos','blocos','padroes','p_wild','p_wild_holm','N','anos']])+'''\n## Reprodução\n\nInstalar requirements.txt em ambiente externo e executar `python reproduzir.py`. Usa metodos.py e executar.py de testes2, sem editar a rodada1. bootstrap_blocos.py contém a restrição e projeção explicitamente. CSVs comprimidos guardam todos os padrões; sinal 0 na assinatura binária significa −1 e sinal 1 significa +1. BOOTSTRAP.csv registra cada restrição, tamanho de bloco, p e verificações. Estratégia, hashes e execução estão em ESTRATEGIA.md/METADADOS.json/EXECUCAO.json/VALIDACAO.json; log em 2_INTI/audit/testes5. Sem commit/push/publicação.\n'''
(p/'RESULTADOS.md').write_text(text)

# A família de Holm não engloba automaticamente a busca sequencial.
with (p/'RESULTADOS.md').open('a') as f:
 f.write('\n## Escopo da multiplicidade e da adaptação\n\nHolm aplica-se somente às famílias registradas nesta rodada, com tamanho em n_familia nos CSVs. As rodadas foram adaptadas aos diagnósticos anteriores e reutilizam os mesmos dados: a correção por família/rodada não controla integralmente o erro da busca sequencial nem converte exploração em teste confirmatório. Uma confirmação independente exige protocolo externo/prévio e dados novos ou identificação adicional.\n')

with (p/'RESULTADOS.md').open('a') as f:
 f.write('\n## Resolução discreta e Holm\n\nCom oito blocos Rademacher, o menor p bilateral enumerado é 2/256=0,0078125. Na família de 16 restrições, o primeiro limiar de Holm é 0,05/16=0,003125: essa combinação não pode rejeitar nenhuma hipótese pelo procedimento Holm, mesmo no resultado mais extremo. Com cinco blocos, o limite bilateral é 0,0625. Portanto, a ausência de rejeição ajustada em blocos3 é também uma limitação matemática da resolução e da família escolhida, não evidência empírica de nulidade. Os p brutos, a sensibilidade blocos2 e os IC DK devem ser lidos juntamente com esse limite. Mudar pesos/refinamento bootstrap não forneceria por si só novos choques independentes nem exogeneidade.\n')
