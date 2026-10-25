# Incorporação autorizada de custos H1 — 25/10/2026

Construção concluída; publicação autorizada posteriormente pelo autor. Autorização explícita do autor para todas as 27 colunas. Estado inicial limpo; nenhuma edição manual encontrada. Backup local dos sete arquivos antes da operação em `antes/` (não necessário à reprodução e não publicado); histórico publicado v4 mantido integralmente no local original.

Base completa: 3384 × 97; grupo 2: 3384 × 67; dicionário: 97 entradas. Grupos 1/3/4: 3384 × 29/12/10, bytes inalterados. Sete índices idênticos; chaves únicas município/ano; união dos grupos igual à completa, sem produto cartesiano. Projeção dos 70 campos originais igual textualmente à base anterior. Os 27 custos mantêm ordem, nomes, strings, vazios e zeros da fonte aprovada. 17045 valores preenchidos e 74323 ausentes entre 91.368 células de custos; replicações regionais não são observações independentes.

Testes: cinco testes de incorporação e três de separação aprovados. Incluem duas reproduções em diretórios temporários limpos a partir da v4 histórica e fonte publicada, comparação byte a byte com o conjunto ativo, idempotência, colisões, proteção contra chaves/índices inválidos, preservação de edição manual coerente, recomposição e proteção do separador contra sobrescrita. `git diff --check` aprovado. Nenhum notebook ativo de construção existia nessa pasta; rotina e testes completos são scripts Python de biblioteca padrão, executáveis sem notebook/rede. Não houve regressões ou reestimações econométricas.

Arquivos de dados alterados: BASE_COMPLETA_H1.csv, GRUPO_2_ECONOMICOS.csv, DICIONARIO.csv, LEIA_ME.md. Rotinas alteradas: separar_grupos_h1.py e testar_grupos_h1.py. Novos: incorporar_custos_h1.py e testar_incorporacao_custos_h1.py, em processamento. Os dois scripts novos foram incluídos explicitamente no escopo de publicação, sem modificar a regra geral de exclusão do repositório.

Reprodução: `python 2_INTI/chapters/chap1/stats/FERNANDO/processamento/incorporar_custos_h1.py --base 2_INTI/chapters/chap1/stats/modelos/base3/BASES_PARA_USO --destino /tmp/h1_repro_novo` (destino vazio). O padrão usa a base ativa, preserva alterações não monetárias coerentes e recusa colisões diferentes de custos. O separador agora aponta ao conjunto ativo e hashes atualizados, portanto não restaura silenciosamente a versão de 70 campos.

Limites preservados: custos aproximados regionais/estaduais, fonte/conceito/sistema/ano/unidade separados; uma praça é suporte fraco; NA não zero; sem interpolação; pecuária R$/arroba vendida nominal. CONAB H e IMEA COT não se tornam equivalentes. A disponibilidade ex ante não foi validada. Metadados originais fora da pasta de uso permanecem acessíveis; seu indicador de aprovação é histórico da etapa candidata. A aprovação atual permite incorporação, não certifica custos reais municipais.

Fontes paralelas e históricos não foram modificados. Os testes/notebooks da etapa regional que certificavam a NÃO incorporação no commit anterior são evidência histórica, não controles do novo conjunto aprovado. O controle vigente de preservação é a projeção exata das 70 variáveis e hashes dos grupos 1/3/4, acima.

Hashes finais e cobertura por cada coluna estão em resultado.json; manifesto_final.json abrange arquivos ativos e rotinas. Logs dos oito testes estão nesta pasta.

Validação pré-publicação: clone limpo do HEAD 72c3e6b531881762b821547015cb916ecc3951c9 com apenas o patch staged autorizado (13 arquivos). Os oito testes passaram novamente, incluindo as duas reproduções e idempotência. Nenhuma dependência local ignorada necessária à execução; scripts usam biblioteca padrão. Não há diretório .github/workflows no repositório.
