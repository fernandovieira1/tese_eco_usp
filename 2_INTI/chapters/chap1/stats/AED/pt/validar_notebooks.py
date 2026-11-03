"""Valida estrutura e executa cópias em audit; nunca salva outputs nos originais."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

import nbformat
from nbclient import NotebookClient

from gerar_notebooks import DICIONARIO, PASTA, extrair_blocos


def raiz():
    for pasta in PASTA.parents:
        if (pasta / '2_INTI/RESEARCH_PROTOCOL.md').exists():
            return pasta
    raise FileNotFoundError('Raiz da tese não encontrada.')


def hash_arquivo(caminho):
    h = hashlib.sha256()
    with caminho.open('rb') as fonte:
        for bloco in iter(lambda: fonte.read(8 * 1024 * 1024), b''):
            h.update(bloco)
    return h.hexdigest()


def executar_um(caminho, saida):
    inicio = time.perf_counter()
    nb = nbformat.read(caminho, as_version=4)
    try:
        NotebookClient(nb, timeout=600, kernel_name='python3',
                       resources={'metadata': {'path': str(PASTA)}}).execute()
        resultado = dict(notebook=caminho.name, ok=True,
                         figuras=sum('image/png' in o.get('data', {}) for c in nb.cells for o in c.get('outputs', [])))
    except Exception as exc:
        resultado = dict(notebook=caminho.name, ok=False, erro=str(exc))
    resultado['segundos'] = round(time.perf_counter() - inicio, 2)
    nbformat.write(nb, saida / caminho.name)
    (saida / (caminho.stem + '.json')).write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(resultado, ensure_ascii=True))
    return resultado['ok']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--executar', action='store_true', help='Executar todos os notebooks com os CSVs reais.')
    parser.add_argument('--permitir-saidas', action='store_true',
                        help='Valida notebooks de variáveis já executados sem exigir outputs vazios.')
    parser.add_argument('--saida', type=Path, default=raiz() / '2_INTI/audit/aed_chap1_20261013/execucao')
    parser.add_argument('--um', type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    saida = args.saida.resolve()
    audit = (raiz() / '2_INTI/audit').resolve()
    if not saida.is_relative_to(audit):
        raise ValueError('Gravar validação dentro de 2_INTI/audit/.')
    saida.mkdir(parents=True, exist_ok=True)
    if args.um:
        return 0 if executar_um(args.um, saida) else 1
    blocos, pendencias = extrair_blocos(DICIONARIO)
    esperados = {b['nome'] + '.ipynb' for b in blocos}
    encontrados = {p.name for p in PASTA.glob('*.ipynb')}
    # O notebook integrado tem protocolo e execução próprios; não é uma 26ª candidata.
    complementares = {'painel_anual_2001_2024.ipynb'}
    if esperados - encontrados or encontrados - esperados - complementares:
        raise AssertionError({'faltam': sorted(esperados - encontrados),
                              'sobram': sorted(encontrados - esperados - complementares)})
    for nome in encontrados & complementares:
        integrado = nbformat.read(PASTA / nome, as_version=4)
        nbformat.validate(integrado)
        assert integrado.metadata.get('painel_aed', {}).get('fontes') == 25
        for cell in integrado.cells:
            if cell.cell_type == 'code':
                compile(cell.source, nome, 'exec')
    for bloco in blocos:
        nb = nbformat.read(PASTA / (bloco['nome'] + '.ipynb'), as_version=4)
        nbformat.validate(nb)
        fases = [c.source.splitlines()[0] for c in nb.cells if c.cell_type == 'markdown' and c.source.startswith('## FASE ')]
        assert len(fases) == 6 and all(f.startswith(f'## FASE {i}:') for i, f in enumerate(fases, 1))
        conteudo = '\n'.join(c.source for c in nb.cells)
        for nota in bloco['notas'] + pendencias:
            assert nota in conteudo, (bloco['nome'], nota)
        assert nb.metadata['aed']['caminhos'] == bloco['caminhos']
        assert nb.metadata['aed'].get('harmonizacao') == 'passos_1_2_v1'
        assert '### Passos 1 e 2 — Construção executada das variáveis' in conteudo
        assert 'resultado_construcao = construir_variavel' in conteudo
        assert 'exportar_resultado(resultado_construcao, RAIZ)' in conteudo
        for cell in nb.cells:
            if cell.cell_type == 'code':
                compile(cell.source, str(bloco['nome']), 'exec')
                if not args.permitir_saidas:
                    assert not cell.outputs and cell.execution_count is None
    print(f'Estrutura, sintaxe, notas e caminhos: {len(blocos)} notebooks OK.')
    if not args.executar:
        return 0
    fontes = {raiz() / c.replace('\\', '/') for b in blocos for c in b['caminhos']}
    fontes.add(DICIONARIO)
    fontes.add(raiz() / '2_INTI/chapters/chap1/text/0_introduction.tex')
    antes = {str(p.relative_to(raiz())): hash_arquivo(p) for p in sorted(fontes)}

    def rodar(nome):
        proc = subprocess.run([sys.executable, __file__, '--um', str(PASTA / nome), '--saida', str(saida)],
                              capture_output=True, text=True, encoding='utf-8', errors='replace',
                              env={**__import__('os').environ, 'PYTHONUTF8': '1'})
        (saida / (nome + '.log')).write_text(proc.stdout + '\n' + proc.stderr, encoding='utf-8')
        print(nome, 'OK' if proc.returncode == 0 else 'FALHOU', flush=True)
        return proc.returncode == 0

    with ThreadPoolExecutor(max_workers=2) as executor:
        resultados = list(executor.map(rodar, sorted(esperados)))
    depois = {str(p.relative_to(raiz())): hash_arquivo(p) for p in sorted(fontes)}
    relatorio = {'notebooks': len(blocos), 'sucessos': sum(resultados),
                 'fontes_preservadas': antes == depois, 'sha256_antes': antes, 'sha256_depois': depois}
    (saida / 'resultado.json').write_text(json.dumps(relatorio, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in relatorio.items() if not k.startswith('sha256')}, ensure_ascii=True))
    return 0 if all(resultados) and antes == depois else 1


if __name__ == '__main__':
    raise SystemExit(main())
