# Revisão da base paralela de custos — 24/10/2026

Regra autorizada: excluir por conceito somente divergência válida estritamente superior a 10% do agregado oficial, ou incompatibilidade qualitativa demonstrada. Valores oficiais preservados. Fronteira de 10%, zeros e ausência testados. Ambiguidades contábeis/geográficas não excluem automaticamente custos; comparações indisponíveis permanecem explicitamente não verificadas.

Pasta de entrada: `2_INTI/chapters/chap1/stats/modelos/base_custos_investigacao/BASE_PARA_USO`. Somente CUSTOS_AGRICULTURA.csv, CUSTOS_PECUARIA.csv, DICIONARIO.csv e LEIA_ME.md.

Agricultura: 247 linhas, 230 com custos e 17 ausentes; 1.831 conceitos nominais. CONAB: 163 linhas após consolidar uma cópia documental, 1.630 conceitos; IMEA: 84 linhas, 201 conceitos. Recuperação bruta frente à seleção antiga: 79 referências/790 conceitos CONAB e 2 referências/6 conceitos IMEA. A consolidação remove apenas uma cópia da apresentação principal, mantendo ambos IDs e todas as fontes no histórico/resultados completos. Geografia conflitante não resolvida por inferência.

Pecuária: 124 linhas, 93 com custos e 31 ausentes, 279 conceitos. Unidade R$/arroba vendida preservada. Nenhum custo municipal ou por bioma imputado.

Nenhuma comparação válida dos dados atuais excedeu 10%; nenhuma exclusão qualitativa monetária adicional demonstrada. Primavera soja 2011 (~4,005%) foi recuperada; Sorriso 2011 e hierarquias ambíguas de 2012 permanecem com flags. Os 135 registros agrícolas e 72 pecuários fora do recorte foram separados em resultados completos, não classificados como erros. Não se preencheu moeda/data incerta.

Verificação: seis testes PASS, incluindo duas construções em diretórios temporários limpos somente com as entradas e o script incluídos. Notebook de construção executado: três células, zero erros. Todos os 164 arquivos anteriores preservados por hash e mapa antes→depois. A construção atual não depende de arquivos externos à pasta nem de rede. O histórico conserva caminhos originais internos e bytes; reprodução da versão antiga exige restaurar seu layout, com helper documentado, sem executar modelos nesta revisão.

Base3 v4 preservada: SHA256 a98dbe320efc784543cf43372a5903de32434be5871304178f2f9d49daaf1c3b. Nenhum modelo reestimado. Resultados preditivos antigos são condicionais à amostra anterior. Nenhum staging, commit ou push nesta etapa; Git mostra os caminhos antigos como removidos porque foram realocados, e os novos caminhos continuam locais/ignorados. Toda alteração rastreada está dentro da pasta autorizada.

Evidências detalhadas: auditoria/CRITERIO_E_DIFERENCAS.md, resumo.json, comparacoes_por_conceito.csv, diferencas_elegibilidade.csv, duplicatas_consolidadas.csv, mapa_reorganizacao.csv, manifesto_build.json e validacao_final.json. Continuidade: publicação e eventual atualização econométrica exigem nova instrução.

## Publicação autorizada — verificação do conteúdo preparado

Após autorização explícita do usuário, preparação de commit restrita à base paralela e a este relatório. Cópia limpa via checkout-index: construção PASS, seis testes PASS (incluindo duas reproduções internas), notebook PASS com três células. Diff verificado com reconhecimento de CRLF; nenhum erro de whitespace restante. Os 154 arquivos substantivos históricos são publicados byte a byte; dez caches locais registrados no mapa não integram Git. Nenhuma alteração de base3 ou reestimação. Não há workflows em .github/workflows. A confirmação do hash remoto será fornecida após o push.
