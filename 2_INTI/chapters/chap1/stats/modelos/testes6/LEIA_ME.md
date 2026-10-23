# Reprodução local

Use Python 3.12 e as versões de requirements.txt em ambiente virtual fora do repositório. Na raiz, execute:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 /tmp/chap1-notebooks-env/bin/python 2_INTI/chapters/chap1/stats/modelos/testes6/reproduzir.py
```

Ou substitua o interpretador por outro ambiente com as dependências registradas. Os caminhos são relativos aos scripts. Requer CSV original com SHA registrado e testes2/metodos.py + executar.py, preservados e auditáveis. A reexecução sobrescreve apenas saídas derivadas da própria rodada; verifica integridade de dados/textos/rodada1 e hashes das rodadas2–5. Não altera a tese ou envia arquivos ao Git. ordem.json fixa a sequência de kernels novos. Semente20261023, sem sorteio nesta rodada.

Auditoria usa o painel EDA apenas para inventário de colunas/hash, nunca para substituir dados. Arquivos COEFICIENTES, MODELOS, TESTES_CONJUNTOS, MAGNITUDES, SENSIBILIDADES, PERDAS e cov_* documentam todos os ajustes. IC são pontuais; Holm limitado às famílias declaradas. Covariâncias e interações estão em apoio.py e no utilitário comum; notebooks mostram a grade e interpretação.

Ocorrência técnica: primeiro gerador Markdown dependia de tabulate ausente; substituído por formatação simples, sem instalar dependência. Estimações e validação numérica não falharam. A execução final cobre a correção.
