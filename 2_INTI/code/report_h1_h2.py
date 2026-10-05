"""Refresh human-readable validation and final delivery counts from evidence."""
from data_paths import data_path
import json,subprocess
from pathlib import Path
import pandas as pd
from data_common import DATA,ROOT,sha256

def readable(text):
    import re
    for word in ['MapBiomas','CHIRPS','GAEZ','IBAMA','CONAB','ZARC','Copernicus','GLO','EPSG','CDS','SHP','CSV','XLSX','JSON','MT','HTTP','CORE','SHA','PAM','PPM','MMA','SICOR','INMET']:
        text=re.sub(r'(?<=[a-záéíóúâêôãõç])(?='+word+r'\b)', ' ',text)
        text=re.sub(r'\b'+word+r'(?=\d)',word+' ',text)
    text=re.sub(r'(?<=\d)(?=anos\b|meses\b|arquivos\b|commits\b|ZIPs\b|rasters\b|tiles\b|feições\b|kg\b|m²\b)', ' ',text)
    for a,b in [('branchmain','branch main'),('contaCDS','conta CDS'),('aceiteCDS','aceite CDS'),('EPSG4326','EPSG:4326'),('EPSG4674','EPSG:4674'),('EPSG5880','EPSG:5880'),('de142','de 142'),('os142','os 142'),('dos142','dos 142'),('e28','e 28'),('117commits','117 commits'),('28ZIPs','28 ZIPs'),('seis trabalhadores','seis trabalhadores')]:text=text.replace(a,b)
    return text

def main():
    c=DATA/'catalog'
    profiles=json.loads((c/'perfis_validacao_h1_h2.json').read_text(encoding='utf-8'))
    status=json.loads((c/'verificacao_preservacao_h1_h2.json').read_text(encoding='utf-8'))
    ib=json.loads((c/'ibama_validacao_eventos.json').read_text(encoding='utf-8'))
    geo=json.loads((c/'ibama_geocodificacao.json').read_text(encoding='utf-8'))
    inv=pd.read_csv(c/'inventario_arquivos_dados_h1_h2.csv')
    lines=['# Validação dos dados H1/H2','', '## Integridade e preservação','',f"Branch `{status['branch']}`; HEAD `{status['head']}`. Originais alterados: {len(status['originais_alterados'])}. Hashes divergentes: {len(status['hashes_divergentes'])}.",'','Hashes/tamanhos e formato por arquivo estão no inventário; estatísticas por coluna (mínimo, máximo, média, desvio, mediana, p1/p25/p75/p99), missing, chaves e anos ausentes internos estão em `perfis_validacao_h1_h2.json`. Outliers IQR apenas sinalizados, sem remoção ou imputação. Nenhum período foi escolhido por significância.','', '## Tabelas finais e intermediárias auditadas','','| Arquivo | Linhas | Municípios | Período presente | Repetições de chave |','|---|---:|---:|---|---:|']
    for r in profiles:lines.append(f"| {Path(r['arquivo']).name} | {r['n']} | {r['municipios'] if r['municipios'] is not None else 'n/a'} | {r['periodo']} | {r['duplicatas']} |")
    lines+=['','Repetições nos eventos/geocodificação IBAMA são identificadores vazios: não foram apagadas. Tabelas agregadas têm chaves únicas. Linhas PAM incluem símbolos sem valor numérico; presença da linha não equivale a observação válida. O CSV de custos é uma transcrição indexada de células, não uma série de custos homologada.','', '## Verificações substantivas','', '- PAM: produção(t) ×1000 / área colhida(ha) comparada ao rendimento publicado; discrepância absoluta máxima inferior a1kg/ha. Área zero não gera divisão válida.', '- MapBiomas10.1: MD5 oficial do XLSX conferido; chaves classe/bioma/município/ano únicas; fração nativa entre0e1; defasagem por município/ano consecutivo; nove linhas não associadas preservadas separadamente.', '- Biomas: CRS originalEPSG4674; áreaEPSG5880; frações não renormalizadas; soma municipal mínima0,998745. Correção projetada documentada separadamente.',f"- IBAMA: {ib['n_mt']} eventosMT, {ib['ids_ausentes']} IDs ausentes, {ib['ids_duplicados_nao_vazios']} repetições de IDs não vazios, {ib['data_invalida']} datas não interpretadas e {ib['valores_ausentes']} valores monetários ausentes. A agregação reconcilia com eventos elegíveis.",f"- GeocodificaçãoIBAMA: {geo['n_coordenadas_bbox']} coordenadas dentro do bbox, {geo['n_sem_poligono']} sem polígono e {geo['divergencias_codigo']} divergências de código. CRS das coordenadas é hipótese provisória. Nenhuma substituição automática do código informado.",'- GAEZ: oito variantes sequeiro/1961–1990/semCO₂; índices sx limitados a0–10000; valores yx em matéria seca. Não confundir classes categóricas com índices contínuos.', '- Copernicus:101 tiles originais, cobertura dos142 municípios; média entre mínimo/máximo. DSM não equivale a terreno nu.','- CHIRPS: integridadeGZIP, CRS/resolução/bandas/extent registrados; negativos inclusiveNoData-9999 excluídos; recorte final expande bordas para conter integralmente o bbox. Anos exigem12meses; climatologias exigem30anos; zscore exige desvio positivo. Nenhuma anomalia é calculada com normal incompleta.','', '## Falhas e restrições preservadas','', '- O suposto PDF históricoMMA é HTML de redirecionamento e não serve como documento normativo. Permanece com status FORMATO_INCORRETO_PRESERVADO.', '- Metadados MapBiomas da coleção9 anunciam transições, mas a planilha contém somente cobertura. Não há taxa de conversão válida entregue.', '- CEPEA403, CAR401, IMEA_TLS, embargos404, URLSTAC404; a alternativaDEM via listagem oficial funcionou. Consultar `falhas_aquisicao_h1_h2.json`.', '- Um downloadCHIRPS foi interrompido tecnicamente para permitir aquisição concorrente. Eventual arquivo `.interrupted` não é raster válido de análise e permanece catalogado como incompleto.', '- Coleta de temperaturaCDS não executada: não há configuração `.cdsapirc`; pedido público preparado, sem segredos.', '', '## Testes','', 'No checkpoint não havia suíte de testes identificada. Foi executado o script de auditoria preexistente antes dos downloads. Foram adicionados testes de integridade do original, MD5MapBiomas, chaves, símbolosSIDRA, produtividade, defasagem, taxonomia/quarentena, biomas, preços, reconciliaçãoIBAMA, GAEZ, climatologias e coberturaDEM. Resultado da execução final: `testes_h1_h2.txt`. A inspeção visual do catálogoXLSX cobre a única aba; CSV/XLSX são confrontados célula a célula.']
    (c/'validacao_dados_h1_h2.md').write_text(readable('\n'.join(lines)+'\n'),encoding='utf-8')
    files=subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z'],cwd=ROOT).decode('utf-8').split('\0')
    new=[{'arquivo':name,'bytes':(ROOT/name).stat().st_size} for name in files if name and (ROOT/name).is_file()]
    pd.DataFrame(new).to_csv(c/'novos_arquivos_h1_h2.csv',index=False,encoding='utf-8-sig')
    n_chirps=len(list((data_path('raw/raster/chirps_v2')).glob('*.tif.gz')))
    report=f'''# Entrega da auditoria e preparação H1/H2

## Resultado

O repositório foi preservado na branchmain, HEAD `{status['head']}`. Há catálogo, matriz, linhagem, inventário, relatórios e derivados candidatos. **O painel completo ainda não está pronto para estimação: faltam insumos centrais e decisões de comparabilidade.** Nenhum modelo final foi estimado.

### A. Existia e foi reaproveitado

Sete arquivos originais de metadados/geometria e seu manifesto, função de aquisição, scripts de descoberta/auditoria, README e textos metodológicos. BaselineSHA256 cobre210arquivos e permanece sem alteração. Inventário/histórico também examinaram117commits e28ZIPs.

### B. Ajustes necessários

Correções aditivas da prosa fixa do auditor antigo; ambientePython isolado; validação do conteúdoHTTP; associação nominalMapBiomas com quarentena; parser de datasIBAMA com formatos mistos; reparo de uma geometria apenas após projeção; recorteCHIRPS corrigido para conter o bbox inteiro. Nenhum arquivo do checkpoint foi sobrescrito.

### C. Baixado agora

PAM soja/milho ePPM bovina emJSON; XLSXMapBiomas10.1 e alternativa9; biomasIBGE2019; PinkSheet mensal; autosIBAMA e coordenadas/histórico de embargos; três planilhas de custosCONAB; portariaZARC sojaMT; oito rastersGAEZv4;101COGsCopernicusGLO90; {n_chirps}/540 rastersCHIRPSv2 mensais; documentação e respostas oficiais. São {len(inv)} arquivos de dados/documentação/intermediários no inventário, totalizando {inv.bytes.sum()/1024**3:.2f}GiB; formatos brutos e falhas foram preservados.

### D. Construído agora

TabelasPAM/PPM; componentes e verificação da produtividade; coberturaMapBiomas por classe/bioma/ano; estoque/fração/defasagem de vegetação candidatos; preços internacionais nominais e logs/diferenças mensais; eventos e agregaçõesIBAMA declaradas e espaciais separadas; células de custosMT indexadas; frações/classes70/80/90% de biomas; oito variantesGAEZ municipais; elevação municipal; recortes e agregaçõesCHIRPS; anomalias candidatas com duas normais. SemShockReturn definitivo.

### E–F. Lacunas, acesso e procedimento

- Conversão bruta anual para agricultura/pastagem: não obtida; cobertura líquida não substitui transições. Requer mapas alinhados da mesma coleção ou extração autenticadaGEE; verificar asset/coleção e disponibilizar resultados locais antes de construir o denominador.
- Preços brasileiros/MT: CEPEA403; IMEA falhaTLS; consultaCONAB requer código de segurança. Acessar portais oficiais e exportar série nominal/documentação para `raw/tabular`, mantendo URL/data/unidade. Não foi enviado pedido ou mensagem a terceiros.
- Embargos: recurso principalCSV eSHP indicado pelo catálogo404. Coordenadas/histórico adquiridos não bastam para contar eventos/área com identidade e unidade seguras.
- HistóricoMMA: página atual preservada; link histórico retornaHTML. Faltam entrada/saída e normas autenticadas por município, inclusiveCerrado. Situação atual não retroagida.
- ERA5-Land: contaCDS, aceite da licença e configuração externa necessárias; pedido preparado em `era5land_request_candidate.json`/`acquire_era5land.py`. Nenhuma credencial inventada ou escrita noGit.
- CAR: acesso401 e histórico inadequado ao horizonte longo. Marcação explícita de cobertura insuficiente. INMET/SICOR investigados, sem coleta indiscriminada nem inclusão automática.
- Calendário: portaria2025/26 obtida; histórico de janelas e extração por solo/ciclo/município pendentes. Déficit hídrico, extremos térmicos, declividade e rugosidade não construídos sem definição adequada.

### G–J. Coberturas e períodos

| Componente | Cobertura potencial | Suporte espacial |
|---|---|---|
| PAM |1974–2025 com missing; presença de linhas não equivale a observação válida |142 códigos na resposta |
| PPM retornada |1974–2024, apesar de pedido até2025 |141 códigos |
| MapBiomas10.1 |1985–2024; estoque defasado1986–2024 |141 municípios; harmonização pendente |
| CHIRPSv2 |1981–2025 é a janela de aquisição completa planejada; disponibilidade efetiva consta na validação |malha2024 de142 municípios |
| IBAMA |1987–2026 nos eventosMT;2026 incompleto |município informado e pontos em variantes separadas |
| PinkSheet |jan1960–ago2026 |mercados internacionais |
| GAEZ/biomas/topografia |período-base/estáticos |142 municípios da malha2024 |

**Período máximo potencial:**1974–2025 para produção local;1985–2024 para vegetação no vintage preservado. **Período comum de todos osCORE:**indisponível, pois conversão e preços locais não foram obtidos. **H1 potencial:**1986–2024 sob mesma coleção e defasagem, ainda inviável como painel completo. **H2 potencial com chuva:**1986–2024, condicionado à janela, à normal e à harmonização territorial; com temperaturaCORE, a interseção também permanece indisponível. Não há período empírico consolidado encontrado a substituir.

### K–L. Arquivos e localização

Todos os novos dados estão sob `2_INTI/data/raw`, `interim`, `processed` e `catalog`; scripts permanecem em `2_INTI/code`. Lista integral dos novos arquivos: `novos_arquivos_h1_h2.csv`. Catálogo de variáveis emCSV/XLSX; inventário de dados comSHA256, bytes e fontes em `inventario_arquivos_dados_h1_h2.csv`. Nenhum download novo foi colocado emSUYANA.

### M–N. Verificação

`validacao_dados_h1_h2.md`, perfisJSON e `testes_h1_h2.txt` registram os testes, estatísticas, falhas e limites. Não há alteração de arquivos originais nem divergência de hashes de downloads no último inventário. CatálogoXLSX possui inspeção visual e comparação comCSV; não foram estimadas regressões.

### O–P. Riscos e decisões pendentes

1. Harmonizar Boa Esperança do Norte/Sorriso/Nova Ubiratã e demais mudanças municipais. AlternativaA: unidades compostas constantes, com perda de detalhe;B: malhas históricas e crosswalk, mais trabalho e cobertura variável. Recomendação: validar suporte comum antes de combinar variáveis.
2. ManterMapBiomas10.1 ou migrar integralmente para11; não misturar numerador/denominador. Definir classes nativas, mosaico de usos e silvicultura no destino da conversão.
3. Definir preços locais versus choques internacionais, moeda/deflator, agregação/defasagem, escalasGAEZ e proxy pecuária predeterminada. BaseGAEZ2010 exige cautela para anos anteriores; não foi escolhida automaticamente como identificação.
4. Clima: v2 versusv3; normal1981–2010 versus1991–2020; ano civil versus janela agrícola. Alternativas de normal têm coberturas semelhantes, mas alteram referência e possível uso de informação futura. Recomendação provisória: escolher janela documentada e normal prévia compatível com identificação.
5. Instituições: autos, multas, embargos e priorização podem responder ao próprio desmatamento. Defasagem não elimina endogeneidade. Geocodificação precisa autenticar datum e resolver divergências.
6. Limiar de bioma70/80/90%, papel da temperatura, controles físicos/crédito e metodologia dos custos permanecem decisões científicas. Nenhum deles foi incorporado por significância ou conveniência.

Não houvecommit/push. O checkpoint permanece no histórico e todas as adições ficam disponíveis para revisão local.
'''
    (c/'relatorio_final_h1_h2.md').write_text(readable(report),encoding='utf-8')

if __name__=='__main__':main()
