"""Separa extratos existentes, sem harmonização, conversão ou atribuição municipal.
Executar com --out DIRETORIO_NOVO. Só usa a biblioteca padrão.
"""
import argparse
import collections
import csv
import hashlib
import json
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[7]
SOURCE = Path('2_INTI/chapters/chap1/stats/modelos/base_custos_investigacao/historico/v1_publicada')
INPUTS = {}

def read(rel):
    path = ROOT / SOURCE / rel
    INPUTS[str(SOURCE / rel)] = hashlib.sha256(path.read_bytes()).hexdigest()
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))

def packed(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))

def write(path, rows):
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)

def number(text):
    text = text.strip().replace(' ', '')
    if ',' in text:
        text = text.replace('.', '').replace(',', '.')
    return Decimal(text)

FIELDS = {
'id_registro':'Chave técnica fonte + série + conceito + unidade; não é código municipal.',
'fonte':'Instituição responsável: CONAB ou IMEA.',
'cultura':'soja ou milho; sistema/safra preservados em cultura_sistema_origem.',
'cultura_sistema_origem':'Categoria preexistente; milho_1a/milho_2a CONAB; IMEA não harmonizado em safras.',
'sistema_tecnologia':'Classificação ou rótulo preservado do extrato, sem inferência tecnológica nova.',
'localidade_aba':'Localidade extraída da aba CONAB; vazio quando não disponível.',
'localidade_cabecalho':'Localidade do cabeçalho CONAB, inclusive conflito; vazio para IMEA.',
'localidade_rotulo_original':'Rótulo geográfico IMEA; vazio para CONAB, cujas duas identificações ficam separadas.',
'abrangencia_origem':'IMEA: nível publicado; CONAB: referência de praça, com ambiguidades nas flags.',
'safra_rotulo_original':'Texto da safra preservado, inclusive asteriscos.',
'safra_inicio':'Ano inicial identificado no extrato; não é data da informação.',
'safra_fim':'Ano final identificado no extrato; não implica correspondência com PAM anual.',
'ano_rotulo_original':'Ano da aba CONAB ou rótulo IMEA; não substitui data-base.',
'data_base':'Data-base CONAB existente; IMEA vazio por falta de data nominal suficiente.',
'precisao_data_base':'dia/mês quando disponível no extrato.',
'periodo_rotulo_original':'Texto original da data CONAB ou período IMEA.',
'mes_referencia_rotulo':'Mês extraído dos rótulos IMEA quando disponível; não presume mês nominal de consolidado.',
'natureza':'CONAB modal/estimado; IMEA consolidado/mensal/estimativa conforme fonte.',
'flag_ex_ant':'Presença literal Ex-Ant CONAB; vazio para IMEA. Não valida informação ex ante.',
'conceito_codigo_extrato':'A–J classificados pelo extrator CONAB; COE/COT/CT IMEA. Não harmonizados entre fontes.',
'conceito_rotulo_original':'Rótulo literal CONAB; código de custo IMEA preservado do extrato.',
'valor':'Número em representação decimal copiado do extrato, sem cálculo; vazio significa NA.',
'valor_texto_extrato':'Texto preservado da célula CONAB ou representação armazenada no extrato IMEA.',
'unidade_original':'BRL_nominal/ha, BRL_nominal/60kg ou R$/ha, preservadas; não somar unidades.',
'moeda':'BRL. Não há conversão cambial ou deflação nesta entrega.',
'arquivo_extrato':'Caminho relativo à raiz Git do extrato que contém o valor.',
'registro_extrato':'Número da linha de dados, base 1 sem cabeçalho, no arquivo_extrato.',
'id_serie_origem':'Identificador preservado da série; não é unidade independente de cada conceito.',
'arquivo_planilha_origem':'Nome da planilha indicado pela origem; bruto não reextraído nesta etapa.',
'sha256_planilha_origem':'Hash documentado do XLSX IMEA; ausente se não disponível.',
'arquivo_celulas_origem':'Extrato de células CONAB, caminho relativo à raiz Git.',
'aba_origem':'Aba da planilha de origem.',
'celula_origem':'Coordenada A1 IMEA quando disponível.',
'linha_excel':'Linha 1-based CONAB; vazio para IMEA, cuja coordenada está em celula_origem.',
'coluna_excel':'Coluna 1-based CONAB; vazio para IMEA.',
'alertas_extrato_json':'Flags históricas preservadas (qualidade, ambiguidades, seleção), não nova aprovação.',
'notas_origem_json':'Notas originais IMEA da aba/índice, ou cabeçalho CONAB preservado.',
}

def build():
    meta = {r['id_serie']: r for r in read('fontes/metadados_series.csv')}
    conab = read('fontes/custos_agregados_longos.csv')
    prior = {r['0_id_serie']: r for r in read('custos_referencia_completos.csv')}
    cells = {}
    for filename in sorted({m['arquivo'] for m in meta.values()}):
        records = read('fontes/conab_celulas/' + filename)
        cells[filename] = {(r['aba'], r['linha_excel'], r['coluna_excel']): r for r in records}
        assert len(cells[filename]) == len(records)
    rows = []
    for index, r in enumerate(conab, 1):
        if r['unidade'] not in {'BRL_nominal/ha', 'BRL_nominal/60kg'}:
            continue  # participações não são valores monetários de custo
        m = meta[r['id_serie']]
        cell = cells[m['arquivo']][m['aba'], r['linha_excel'], r['coluna_excel']]
        assert cell['conteudo'] == r['valor_original']
        assert number(cell['conteudo']) == Decimal(r['valor'])
        flags = {k: v for k, v in prior[r['id_serie']].items() if k.startswith('4_') and not any(t in k for t in ['conversao', 'cambio', 'usd2024'])}
        flags.update({k: m[k] for k in ['conflito_praca', 'praca_ambigua', 'data_fora_ano_aba']})
        flags['formula_letra_inconsistente'] = r['formula_letra_inconsistente']
        row = dict.fromkeys(FIELDS, '')
        row.update(id_registro='CONAB:'+r['id_serie']+':'+r['conceito']+':'+r['unidade'], fonte='CONAB', cultura='soja' if m['cultura']=='soja' else 'milho', cultura_sistema_origem=m['cultura'], sistema_tecnologia=m['tecnologia'], localidade_aba=m['praca_aba'], localidade_cabecalho=m['praca_cabecalho'], abrangencia_origem='referência de praça', safra_rotulo_original=m['safra_texto'], safra_inicio=m['safra_inicio'], safra_fim=m['safra_fim'], ano_rotulo_original=m['ano_aba'], data_base=m['data_base'], precisao_data_base=m['precisao_data_base'], periodo_rotulo_original=m['data_base_texto'], natureza='custo modal/estimado publicado; não gasto municipal observado', flag_ex_ant=m['ex_ant'], conceito_codigo_extrato=r['conceito'], conceito_rotulo_original=r['rotulo_original'], valor=r['valor'], valor_texto_extrato=r['valor_original'], unidade_original=r['unidade'], moeda='BRL', arquivo_extrato=str(SOURCE/'fontes/custos_agregados_longos.csv'), registro_extrato=str(index), id_serie_origem=r['id_serie'], arquivo_planilha_origem=cell['arquivo_origem'], arquivo_celulas_origem=str(SOURCE/'fontes/conab_celulas'/m['arquivo']), aba_origem=m['aba'], linha_excel=r['linha_excel'], coluna_excel=r['coluna_excel'], alertas_extrato_json=packed(flags), notas_origem_json=packed({'cabecalho':m['cabecalho']}))
        rows.append(row)
    raw = read('fontes/imea/imea_regional_key_costs.csv')
    notes = read('fontes/imea/imea_regional_source_notes.csv')
    imea = read('custos_imea_referencia.csv')
    lookup = {(r['source_file'],r['sheet'],r['source_column']): (i,r) for i,r in enumerate(raw,1)}
    assert len(lookup)==len(raw)
    for r in imea:
        concept = r['0_conceito_original'].lower()
        index, original = lookup[r['0_arquivo_xlsx_origem'],r['0_aba'],r['0_celula'].rstrip('0123456789')]
        assert original[concept] == r['2_custo_brl_declarado_ha']
        assert original[concept+'_cell'] == r['0_celula']
        row = dict.fromkeys(FIELDS, '')
        row.update(id_registro=r['0_id_registro'], fonte='IMEA', cultura=r['0_cultura'], cultura_sistema_origem=r['0_sistema_safra'], sistema_tecnologia=r['0_tecnologia_rotulo_original'], localidade_rotulo_original=r['0_localidade_original'], abrangencia_origem=r['0_nivel_geografico'], safra_rotulo_original=r['0_safra_rotulo_original'], safra_inicio=r['0_safra_inicio'], safra_fim=r['0_safra_fim'], ano_rotulo_original=r['0_ano_rotulo_original'], periodo_rotulo_original=r['0_periodo_rotulo_original'], mes_referencia_rotulo=r['0_mes_referencia_rotulo'], natureza=r['0_natureza_rotulo_original'], conceito_codigo_extrato=r['0_conceito_original'], conceito_rotulo_original=r['0_conceito_original'], valor=original[concept], valor_texto_extrato=original[concept], unidade_original=original['unit'], moeda='BRL', arquivo_extrato=str(SOURCE/'fontes/imea/imea_regional_key_costs.csv'), registro_extrato=str(index), id_serie_origem=r['0_id_serie'], arquivo_planilha_origem=original['source_file'], sha256_planilha_origem=original['source_sha256'], aba_origem=original['sheet'], celula_origem=original[concept+'_cell'], alertas_extrato_json=packed({k:v for k,v in r.items() if k.startswith('4_')}), notas_origem_json=packed([n for n in notes if n.get('source_file')==original['source_file'] and n.get('sheet') in {original['sheet'],'Indice'}]))
        rows.append(row)
    assert len(rows)==4345 and len({r['id_registro'] for r in rows})==len(rows)
    assert {r['cultura'] for r in rows}=={'soja','milho'}
    keys=[(r['fonte'],r['arquivo_planilha_origem'],r['aba_origem'],r['celula_origem'],r['linha_excel'],r['coluna_excel']) for r in rows]
    assert len(set(keys))==len(keys)
    assert sum(r['valor']=='' for r in rows)==60
    for r in rows:
        if r['valor']:
            assert Decimal(r['valor']).is_finite()
    return rows

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    rows=build()
    args.out.mkdir(parents=True,exist_ok=False)
    write(args.out/'CUSTOS_ORIGINAIS_SOJA_MILHO.csv',rows)
    write(args.out/'DICIONARIO.csv',[{'campo':k,'descricao':v} for k,v in FIELDS.items()])
    counts=collections.Counter((r['fonte'],r['cultura_sistema_origem'],r['conceito_codigo_extrato'],r['unidade_original']) for r in rows)
    print(json.dumps({'linhas':len(rows),'ausentes':sum(not r['valor'] for r in rows),'contagens': [{'fonte':k[0],'cultura_sistema':k[1],'conceito':k[2],'unidade':k[3],'n':v} for k,v in sorted(counts.items())],'hashes_insumos':INPUTS,'sha256_csv':hashlib.sha256((args.out/'CUSTOS_ORIGINAIS_SOJA_MILHO.csv').read_bytes()).hexdigest()},ensure_ascii=False,indent=2))
