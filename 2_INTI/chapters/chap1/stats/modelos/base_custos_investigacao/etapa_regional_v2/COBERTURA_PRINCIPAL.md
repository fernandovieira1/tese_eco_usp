# Cobertura dos dois cenários

Principal exploratório: uma ou mais praças válidas, praça única marcada suporte fraco. Conservador: duas ou mais. Denominador3384 município-anos por custo alternativo, sem somar sistemas sobrepostos. Agricultura CONAB em USD2024/ha; pecuária em R$/arroba vendida nominal. Ano agrícola corresponde ao fim da safra.

| Atividade/sistema/conceito | Municípios exploratório | Anos exploratório | Regiões IBGE | Células exploratório | % | Células conservador | % |
|---|---:|---|---|---:|---:|---:|---:|
| soja/não declarada/conab_h | 77 | 2002;2003;2004;2005;2006;2007;2008;2009;2010;2011;2012;2013;2014;2015;2016;2017;2018 | 5101;5105 | 979 | 28.93 | 385 | 11.38 |
| pecuaria/recria_engorda/cot | 99 | 2020;2021;2022;2023;2024 | 5101;5103;5105 | 495 | 14.63 | 110 | 3.25 |
| milho_2a/OGM/conab_h | 77 | 2013;2014;2015;2016;2017;2018;2019;2020;2021;2022;2023;2024 | 5101;5105 | 869 | 25.68 | 660 | 19.50 |
| pecuaria/ciclo_completo/cot | 22 | 2020;2021;2022;2023;2024 | 5103 | 110 | 3.25 | 0 | 0.00 |
| soja/OGM/conab_h | 77 | 2008;2009;2010;2011;2012;2013;2014;2015;2016;2017;2018;2019;2020;2021;2022;2023;2024 | 5101;5105 | 1309 | 38.68 | 550 | 16.25 |
| soja/convencional explícita/conab_h | 77 | 2019 | 5101;5105 | 77 | 2.28 | 55 | 1.63 |
| milho_1a/não declarada/conab_h | 22 | 2002;2003;2004;2005;2006;2007;2008;2009;2010;2011;2012;2013;2014 | 5105 | 286 | 8.45 | 0 | 0.00 |
| milho_2a/não declarada/conab_h | 77 | 2001;2002;2003;2004;2005;2006;2007;2008;2009;2010;2011;2012;2013;2015;2016 | 5101;5105 | 561 | 16.58 | 165 | 4.88 |
| pecuaria/cria/cot | 119 | 2020;2021;2022;2023;2024 | 5101;5102;5104;5105 | 507 | 14.98 | 485 | 14.33 |

183 grupos regionais:178 têm algum custo numérico, sendo110 exclusivamente de uma praça e68 com algum conceito/moeda de pelo menos duas. Cinco grupos sem valores continuamNA. Os110 grupos pontuais passam a fornecer aproximações exploratórias; não são erros oficiais. Os48 casos sem localização/período válidos, estaduais ou com safra ambígua continuam fora da regionalização.

27 custos alternativos:12 CONAB (seis atividade/sistema×duas moedas),6 IMEA agrícola (dois estratos×três conceitos) e9 pecuários (três sistemas×três conceitos). Não são27 variáveis independentes. Principal3384×34: sete índices e27 valores monetários, todos com algum suporte. Conservador tem22 custos com suporte e cinco inteiramenteNA.

Metadados separados em resultados/METADADOS_PAINEL_CANDIDATO.csv:91368 linhas únicas de chave município/ano/variável, incluindoNA, suporte, n_pracas, fonte, região, período, dispersão e aprovação falsa. O arquivo conservador fica em resultados/cenario_conservador. Cobertura detalhada por região/atividade/ano está no respectivo subdiretório resultados.

Não houve relaxamento da seleção>10%, localização de conflitos, mistura de fontes/sistemas/conceitos ou preenchimento de anos/regiões ausentes. Nenhum custo incorporado à H1. Resultados preditivos permanecem idênticos. A mudança foi solicitada explicitamente após a avaliação e está registrada como revisão, não pré-especificação original.
