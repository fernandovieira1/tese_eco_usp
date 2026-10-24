# Custos: comece pela base para uso

Abra **[BASE_PARA_USO](BASE_PARA_USO/LEIA_ME.md)**. Ela contém somente os dois datasets largos, um dicionário e instruções curtas. Agricultura e pecuária ficam separadas por unidade. Não são custos municipais observados.

A seleção atual mantém o valor oficial e exclui um conceito apenas quando há divergência quantitativa estritamente acima de 10% em comparação válida, ou incompatibilidade qualitativa demonstrada que comprometa esse conceito. Ambiguidade, falta de conferência, diferença de até 10% e indisponibilidade de moeda geram flags, não exclusão automática da planilha.

- [Processamento e testes](processamento): construção da seleção atual, notebook e reprodução.
- [Auditoria](auditoria): diferenças por conceito, comparações, mapa de reorganização e hashes.
- [Resultados completos](resultados): todas as referências e períodos, inclusive fora de 2001–2024.
- [Histórico v1](historico/v1_publicada): cópia integral e imutável do pacote anterior, incluindo fontes, critérios estritos e resultados preditivos. Fontes permanecem nessa cópia, sem duplicação.

**Os modelos anteriores são condicionais à amostra estrita antiga. Não foram reestimados nem validados na seleção atual.** A base3 v4 permanece intacta. Publicação desta revisão autorizada em 24/10/2026.

Reproduzir: `python processamento/construir_uso.py`; testar: `python processamento/testar_uso.py`. Notebook atual: `processamento/construcao_base_para_uso.ipynb`. Python padrão basta para scripts; Jupyter exige nbformat/nbclient/ipykernel. Todas as entradas estão preservadas no histórico dentro desta pasta. Não há dependência de complementos locais externos nem coleta de rede para o build atual.
