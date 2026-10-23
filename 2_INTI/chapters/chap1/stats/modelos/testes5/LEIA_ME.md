# Rodada 5 — resultados locais

Leia ESTRATEGIA.md (anterior à execução) e RESULTADOS.md. A síntese integrada está em ../testes5/CONCLUSAO_RODADAS.md. São análises exploratórias adaptativas: Holm por família não corrige integralmente a busca entre rodadas.

## Reprodução

Criar ambiente virtual fora do repositório, instalar requirements.txt de fonte PyPI e executar `python reproduzir.py` a partir desta pasta. Os módulos compartilhados são ../testes2/metodos.py e ../testes2/executar.py. Não copiam dados; leem o CSV do diretório pai. O SHA256 esperado é fixado: uma alteração da base exige nova revisão das estratégias/sínteses.

## Resultados

COEFICIENTES.csv e MODELOS.csv registram todas as especificações e títulos, VD/VI, FE, amostra, perdas, unidades, ajustes, inferência e limites. TESTES_CONJUNTOS.csv, MAGNITUDES.csv e SENSIBILIDADES.csv mantêm testes/magnitudes e covariâncias alternativas. PERDAS.csv registra etapas de casos completos; os CSVs consolidados distinguem perdas anteriores aos filtros por variável. Covariâncias detalhadas são salvas para modelos substantivos; os refits de influência guardam todos os coeficientes/SE/IC sem centenas de matrizes redundantes.

METADADOS.json, EXECUCAO.json, VALIDACAO.json, tentativas.jsonl e ARQUIVOS_SHA256.json documentam proveniência e execução. Logs de terminal em `2_INTI/audit/testes5/execucao_final.log` na raiz do repositório. Nenhuma falha foi omitida; código para dados fora do protocolo deve parar. Na rodada5, os IC são DK, não bootstrap.

Nenhum arquivo da rodada1 foi alterado. Rodada 5 não publicada: commit/push do escopo ampliado aguarda autorização no chat principal.
