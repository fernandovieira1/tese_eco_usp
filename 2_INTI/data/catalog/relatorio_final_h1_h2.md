# Entrega da auditoria e preparação H1/H2

## Resultado

O repositório foi preservado na branch main, HEAD `e5c8ece0c4516a79e2cef0b293ae2ce13f1259ce`. Há catálogo, matriz, linhagem, inventário, relatórios e derivados candidatos. **O painel completo ainda não está pronto para estimação: faltam insumos centrais e decisões de comparabilidade.** Nenhum modelo final foi estimado.

### A. Existia e foi reaproveitado

Sete arquivos originais de metadados/geometria e seu manifesto, função de aquisição, scripts de descoberta/auditoria, README e textos metodológicos. BaselineSHA256 cobre210 arquivos e permanece sem alteração. Inventário/histórico também examinaram117 commits e 28 ZIPs.

### B. Ajustes necessários

Correções aditivas da prosa fixa do auditor antigo; ambientePython isolado; validação do conteúdo HTTP; associação nominal MapBiomas com quarentena; parser de datas IBAMA com formatos mistos; reparo de uma geometria apenas após projeção; recorte CHIRPS corrigido para conter o bbox inteiro. Nenhum arquivo do checkpoint foi sobrescrito.

### C. Baixado agora

PAM soja/milho e PPM bovina em JSON; XLSXMapBiomas10.1 e alternativa9; biomasIBGE2019; PinkSheet mensal; autos IBAMA e coordenadas/histórico de embargos; três planilhas de custos CONAB; portaria ZARC soja MT; oito rastersGAEZv4;101COGsCopernicusGLO90; 540/540 rastersCHIRPSv2 mensais; documentação e respostas oficiais. São 1512 arquivos de dados/documentação/intermediários no inventário, totalizando 9.00GiB; formatos brutos e falhas foram preservados.

### D. Construído agora

Tabelas PAM/PPM; componentes e verificação da produtividade; cobertura MapBiomas por classe/bioma/ano; estoque/fração/defasagem de vegetação candidatos; preços internacionais nominais e logs/diferenças mensais; eventos e agregações IBAMA declaradas e espaciais separadas; células de custos MT indexadas; frações/classes70/80/90% de biomas; oito variantes GAEZ municipais; elevação municipal; recortes e agregações CHIRPS; anomalias candidatas com duas normais. SemShockReturn definitivo.

### E–F. Lacunas, acesso e procedimento

- Conversão bruta anual para agricultura/pastagem: não obtida; cobertura líquida não substitui transições. Requer mapas alinhados da mesma coleção ou extração autenticadaGEE; verificar asset/coleção e disponibilizar resultados locais antes de construir o denominador.
- Preços brasileiros/MT: CEPEA403; IMEA falhaTLS; consulta CONAB requer código de segurança. Acessar portais oficiais e exportar série nominal/documentação para `raw/tabular`, mantendo URL/data/unidade. Não foi enviado pedido ou mensagem a terceiros.
- Embargos: recurso principal CSV e SHP indicado pelo catálogo404. Coordenadas/histórico adquiridos não bastam para contar eventos/área com identidade e unidade seguras.
- Histórico MMA: página atual preservada; link histórico retornaHTML. Faltam entrada/saída e normas autenticadas por município, inclusiveCerrado. Situação atual não retroagida.
- ERA5-Land: conta CDS, aceite da licença e configuração externa necessárias; pedido preparado em `era5land_request_candidate.json`/`acquire_era5land.py`. Nenhuma credencial inventada ou escrita noGit.
- CAR: acesso401 e histórico inadequado ao horizonte longo. Marcação explícita de cobertura insuficiente. INMET/SICOR investigados, sem coleta indiscriminada nem inclusão automática.
- Calendário: portaria2025/26 obtida; histórico de janelas e extração por solo/ciclo/município pendentes. Déficit hídrico, extremos térmicos, declividade e rugosidade não construídos sem definição adequada.

### G–J. Coberturas e períodos

| Componente | Cobertura potencial | Suporte espacial |
|---|---|---|
| PAM |1974–2025 com missing; presença de linhas não equivale a observação válida |142 códigos na resposta |
| PPM retornada |1974–2024, apesar de pedido até2025 |141 códigos |
| MapBiomas 10.1 |1985–2024; estoque defasado1986–2024 |141 municípios; harmonização pendente |
| CHIRPSv2 |1981–2025 é a janela de aquisição completa planejada; disponibilidade efetiva consta na validação |malha2024 de 142 municípios |
| IBAMA |1987–2026 nos eventos MT;2026 incompleto |município informado e pontos em variantes separadas |
| PinkSheet |jan1960–ago2026 |mercados internacionais |
| GAEZ/biomas/topografia |período-base/estáticos |142 municípios da malha2024 |

**Período máximo potencial:**1974–2025 para produção local;1985–2024 para vegetação no vintage preservado. **Período comum de todos os CORE:**indisponível, pois conversão e preços locais não foram obtidos. **H1 potencial:**1986–2024 sob mesma coleção e defasagem, ainda inviável como painel completo. **H2 potencial com chuva:**1986–2024, condicionado à janela, à normal e à harmonização territorial; com temperatura CORE, a interseção também permanece indisponível. Não há período empírico consolidado encontrado a substituir.

### K–L. Arquivos e localização

Todos os novos dados estão sob `2_INTI/data/raw`, `interim`, `processed` e `catalog`; scripts permanecem em `2_INTI/code`. Lista integral dos novos arquivos: `novos_arquivos_h1_h2.csv`. Catálogo de variáveis em CSV/XLSX; inventário de dados comSHA256, bytes e fontes em `inventario_arquivos_dados_h1_h2.csv`. Nenhum download novo foi colocado emSUYANA.

### M–N. Verificação

`validacao_dados_h1_h2.md`, perfis JSON e `testes_h1_h2.txt` registram os testes, estatísticas, falhas e limites. Não há alteração de arquivos originais nem divergência de hashes de downloads no último inventário. Catálogo XLSX possui inspeção visual e comparação com CSV; não foram estimadas regressões.

### O–P. Riscos e decisões pendentes

1. Harmonizar Boa Esperança do Norte/Sorriso/Nova Ubiratã e demais mudanças municipais. AlternativaA: unidades compostas constantes, com perda de detalhe;B: malhas históricas e crosswalk, mais trabalho e cobertura variável. Recomendação: validar suporte comum antes de combinar variáveis.
2. ManterMapBiomas10.1 ou migrar integralmente para11; não misturar numerador/denominador. Definir classes nativas, mosaico de usos e silvicultura no destino da conversão.
3. Definir preços locais versus choques internacionais, moeda/deflator, agregação/defasagem, escalas GAEZ e proxy pecuária predeterminada. BaseGAEZ2010 exige cautela para anos anteriores; não foi escolhida automaticamente como identificação.
4. Clima: v2 versusv3; normal1981–2010 versus1991–2020; ano civil versus janela agrícola. Alternativas de normal têm coberturas semelhantes, mas alteram referência e possível uso de informação futura. Recomendação provisória: escolher janela documentada e normal prévia compatível com identificação.
5. Instituições: autos, multas, embargos e priorização podem responder ao próprio desmatamento. Defasagem não elimina endogeneidade. Geocodificação precisa autenticar datum e resolver divergências.
6. Limiar de bioma70/80/90%, papel da temperatura, controles físicos/crédito e metodologia dos custos permanecem decisões científicas. Nenhum deles foi incorporado por significância ou conveniência.

Não houvecommit/push. O checkpoint permanece no histórico e todas as adições ficam disponíveis para revisão local.
