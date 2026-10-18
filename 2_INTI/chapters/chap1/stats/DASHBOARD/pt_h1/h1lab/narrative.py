"""Bridge to existing chapter arguments, without rewriting scientific text."""

H1 = 'A conversão de vegetação nativa para usos agropecuários depende da expectativa de retorno econômico e do ambiente institucional no qual essa decisão é tomada.'

BRIDGE = '''A introdução apresenta H1 como uma hipótese sobre incentivos econômicos condicionados pelo ambiente institucional. A descrição dos dados organiza evidências sobre essas dimensões; não identifica causalidade.

1. **Conversão e usos da terra** — introdução, REF7 e REF10; literatura, “Heterogeneidade territorial e contribuição do artigo”. Descrever fluxos brutos para agricultura e pastagem, estoques, distribuição territorial e cobertura. A variação líquida de um estoque não equivale à conversão de vegetação nativa.
2. **Preços e capacidade** — introdução, REF8; literatura, “Preços, capacidade produtiva e usos alternativos da terra”. Relacionar preços internacionais, produtividade observada (PAM) e capacidade potencial (GAEZ), distinguindo escalas, timing e variação entre municípios e dentro deles. Essas proxies não observam o retorno líquido privado.
3. **Instituições** — introdução, REF9; literatura, “Instituições, implementação e respostas aos incentivos”. Descrever a frequência, intensidade e cobertura dos registros do IBAMA, distinguindo associação informada e espacial. Mais autos podem acompanhar maior pressão ambiental ou fiscalização; não medem diretamente eficácia.
4. **Heterogeneidade e limites** — introdução, REF10–REF11; literatura, “Retornos privados e custos da conversão” e seção territorial. Comparar biomas e atividades, exibir N e suporte. Capacidade privada, produtividade e conversão não quantificam por si sós bem-estar ou custos ambientais.

O arquivo 2_mt_descriptive.tex contém texto provisório. O caderno fornece material para uma redação revisada pelo autor, mantendo a sequência: território e usos → distribuições e cobertura → incentivos e capacidade → instituições → associações exploratórias e limites. A introdução usa H1; a revisão ainda contém referências a H1-a/H1-b. O app organiza dimensões de H1 e não resolve essa nomenclatura editorial automaticamente.'''

QUESTIONS = {
    'Conversão de vegetação nativa': ('Onde e para qual uso a vegetação é convertida?', 'Separar agricultura e pastagem; distinguir fluxo bruto, taxa sobre vegetação inicial e estoque. Comparar uma coorte comum quando a cobertura varia.'),
    'Preços internacionais': ('Como variam os incentivos comuns ao longo do tempo?', 'A série é internacional e comum aos municípios. Repeti-la 141 vezes não cria 141 choques independentes; efeitos de ano absorvem seu nível.'),
    'Capacidade e produtividade': ('A resposta aos preços pode depender da capacidade local?', 'PAM mede produtividade observada; GAEZ, capacidade potencial sob cenários específicos. Não escolher entre proxies apenas por significância ou correlação.'),
    'Preços × capacidade e biomas': ('O mesmo preço se associa de forma diferente à conversão conforme a capacidade?', 'Examinar suporte e componentes da interação. Sua variação não garante exogeneidade nem identifica retorno líquido.'),
    'Instituições · IBAMA': ('Como os registros institucionais se distribuem junto à pressão de conversão?', 'Ausência de registro, contagem parcial e valor zero são situações distintas. A associação pode refletir resposta da fiscalização ao desmatamento.'),
    'Qualidade e cobertura': ('O que é observado e o que permanece desconhecido?', 'Flags são condições de mensuração. Uma flag ausente não significa False e um dado ausente não significa zero.'),
    'Estoques e uso da terra': ('Expansão, substituição de usos e intensificação contam a mesma história?', 'A composição dos estoques complementa os fluxos de conversão, mas não reconstrói todas as transições entre usos.'),
    'Pecuária': ('Como rebanho e área de pastagem se relacionam?', 'Lotação, efetivo e área representam dimensões diferentes. Conferir compatibilidade temporal dos estoques e denominadores antes de comparar.'),
    'Clima e precipitação': ('Condições ambientais ajudam a interpretar a heterogeneidade observada?', 'Separar normais climáticas fixas, precipitação anual e anomalias; conferir cobertura mensal e períodos de referência.'),
    'Biomas e relevo': ('Que diferenças persistentes delimitam a comparação territorial?', 'Bioma dominante é a maior fração municipal, não exclusividade. Atributos fixos são absorvidos pelos efeitos municipais; amostras pequenas limitam a comparação.')
}
