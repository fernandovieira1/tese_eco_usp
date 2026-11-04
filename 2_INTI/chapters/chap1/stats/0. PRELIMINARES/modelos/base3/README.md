# Base3 v1 — núcleo incremental para H1

Recorte da base2 publicada no commit `1cbab8246114ecef0d2a80b55a068ea1cf4cf1c3`, conferida byte a byte com o Git. São **3.384 linhas, 141 municípios, 2001–2024 e 42 colunas**: 41 campos copiados textualmente e uma defasagem institucional materializada. Bases anteriores e fontes permanecem intactas.

A seleção segue o objeto econômico e a qualidade de mensuração, sem usar p-valores. Nenhuma regressão, imputação, coleta nova ou previsão foi executada nesta construção.

## Conteúdo e uso

- Desfechos: conversão bruta de vegetação nativa para agricultura e pastagem, em hectares e fração do estoque inicial de vegetação nativa. As taxas são frações; multiplicar por 100 apenas quando a especificação exigir pontos percentuais. Não medem conversão específica para soja ou milho.
- Incentivos econômicos: preços mundiais reais de soja, milho e carne bovina, já defasados. Os resultados de 2001–2024 usam preços de 2000–2023. Essa temporalidade é herdada da construção publicada, não uma nova conferência da fonte mensal. Unidades distintas: soja/milho USD2024/t e carne USD2024/kg. Não representam preços locais, lucro ou retorno esperado líquido.
- Aptidão: GAEZ alto insumo e sequeiro de soja e milho, em kg de matéria seca/ha; clima 1961–1990 e referência de terras 2010. Não equivale a rendimento comercial ou lucro; a referência de terras exige cautela temporal.
- Instituições: contagem espacial contemporânea de autos Flora, parcialidade e contagem elegível do ano anterior. O campo novo `n_autos_flora_elegiveis_lag1__ibama_espacial` está em **autos**, sem divisão por 10. Aceita apenas contagens finitas, não negativas e parcialidade explicitamente falsa (independentemente de maiúsculas), antes de buscar o mesmo município no ano consecutivo anterior. Parcialidade ausente não aprova a observação. O primeiro ano não tem predecessor nesta base. Autuações não medem pagamento ou eficácia e podem responder à própria conversão.
- Território: bioma predominante e três frações municipais originais, sem renormalização ou classificação de ecótonos. Não localizam a conversão dentro do município. Pouco suporte do Pantanal exige cautela nas futuras especificações.
- Clima: chuva anual civil e anomalia frente a 1981–2000, com média de referência, número de anos, meses válidos, cobertura conhecida e mínima fração de pixels. Não representa calendário agrícola. Não foi usada nas sete rodadas anteriores.
- Qualidade: cobertura cartográfica do par, fração válida, flags do denominador, ausências, zeros registrados e máscaras amostrais. Metadados constantes de origem: MapBiomas 10.1, malha IBGE_MT_2023_141; detalhes permanecem na base2.

Os preços comuns são absorvidos por efeitos fixos anuais; aptidão e biomas invariantes, por efeitos municipais. Interações serão definidas nas especificações, não pré-calculadas nesta base. Confiabilidade de mensuração não significa efeito estatístico demonstrado ou identificação causal.

## Amostras e limites

O painel-mestre nunca é truncado: 2.772 linhas têm ambos os desfechos válidos; 1.140 também têm autos anteriores elegíveis. Cada desfecho conserva 612 ausentes. Agricultura tem 265 zeros registrados; pastagem nenhum zero observado. A construção não certifica integralmente se algum zero foi preenchido na cadeia anterior. Ausentes não foram convertidos em zero e nenhum valor inválido foi descartado silenciosamente.

As máscaras publicadas são preservadas e conferidas contra a nova defasagem. Elas não corrigem seleção amostral. A soma das frações de bioma é aproximada; a validação admite erro cartográfico absoluto inferior a 0,002, sem alterar os dados. Não inferir localização ecológica a partir dessa aproximação.

## Reprodução

Na raiz do repositório, com Python >=3.9 e somente biblioteca padrão:

```bash
python 2_INTI/chapters/chap1/stats/modelos/base3/construir_base3.py
python 2_INTI/chapters/chap1/stats/modelos/base3/testar_base3.py
```

O construtor exige o hash exato da base2 publicada e recria somente CSVs/manifesto dentro desta pasta. Os testes conferem preservação textual, chaves, cardinalidade, unidades, finitude, taxas/denominador, faltas, zeros, máscaras e defasagem (inclusive em dados sintéticos com lacunas). `validacao.json` registra duas reproduções idênticas; `manifesto.json` identifica origem e hashes. Não há aleatoriedade ou dependência instalada/versionada. Alteração legítima da fonte exige nova versão explícita.

## Próximo incremento

Manter rendimento observado defasado em bloco complementar, fora deste núcleo. Juros, crédito, insumos e custos observados/modelados exigem preparação e decisão próprias; não estão incorporados. Custos previstos não foram autorizados pelo diagnóstico como substitutos de custos municipais. A proposta testes8 não foi executada. O complemento CONAB, o piloto e as revisões locais não integram esta entrega.

Arquivos: [dicionário](dicionario_variaveis.csv), [qualidade](relatorio_qualidade.md), [amostras](amostras.csv), [painel](painel_h1_base3_v1.csv), [manifesto](manifesto.json).
