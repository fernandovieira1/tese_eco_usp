# Reprodução e dependências

Na raiz do repositório:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 /tmp/chap1-notebooks-env/bin/python 2_INTI/chapters/chap1/stats/modelos/testes7/reproduzir.py
```

Pode-se substituir o interpretador por ambiente Python3.12 externo ao Git com requirements.txt. Usa utilitários auditáveis testes2/metodos.py, executor testes2/executar.py e preparação testes6/apoio.py, todos preservados. Não incorpora dependências ou cópia do painel. Fonte exata verificada por SHA; auxílio EDA não participa das regressões. ordem.json define dois notebooks em kernels novos; outputs locais substituídos em reexecução, dados/textos e rodadas anteriores conferidos por hash. Semente20261023; cálculos determinísticos.

ESTRATEGIA.md foi escrita antes das estimações. RESULTADOS.md contém integralmente ajustes, nulos, sensibilidades e limites. CONCLUSAO_GERAL.md integra as rodadas sem substituir seus registros. Os arquivos CSV uniformes e matrizes cov_* permitem recomputar contrastes. VARIACAO_RETIDA.csv mede perda de variação identificadora. A validação independente compara FEbioma com PanelOLS e tendências com dummies explícitas.

Publicação ampliada bloqueada pela revisão automática no chat principal; nenhuma tentativa de commit/push nesta etapa.
