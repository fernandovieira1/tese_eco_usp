"""Download-only artifacts: source fingerprints, tables, figures and reproducible OLS."""
from __future__ import annotations

from datetime import datetime, timezone
import importlib.metadata
import io
import json
import zipfile

import nbformat
import numpy as np
import pandas as pd

from .data import APP, sha256
from .presentation import booktabs


def json_text(value):
    def cast(x):
        if isinstance(x, (np.integer, np.floating, np.bool_)):
            return x.item()
        return str(x)
    return json.dumps(value, ensure_ascii=False, indent=2, default=cast)


def csv_bytes(frame, index=True):
    return frame.to_csv(index=index).encode('utf-8-sig')


def manifest(meta, filters):
    return {'created_utc': datetime.now(timezone.utc).isoformat(), 'source': meta,
        'filters': filters, 'versions': {p: importlib.metadata.version(p) for p in ['pandas', 'numpy', 'scipy', 'statsmodels', 'streamlit', 'plotly']},
        'code_sha256': {str(p.relative_to(APP)): sha256(p) for p in sorted(APP.rglob('*.py')) if 'tests' not in p.parts},
        'interpretation': 'Associações exploratórias; não constitui teste causal de H1 nem escolha definitiva da especificação.'}


def model_notebook():
    nb = nbformat.v4.new_notebook()
    nb.cells = [
        nbformat.v4.new_markdown_cell('# OLS exploratória — Capítulo 1\n\nExtraia o ZIP e abra este notebook na mesma pasta. '
            'A matriz exportada contém intercepto, efeitos fixos e transformações exatamente como estimados. '
            'A amostra comum já foi selecionada; para alterar a regra amostral ou a defasagem, parta do painel canônico indicado no manifesto. '
            'Confira unidades, fontes e `especificacao.json` antes de ampliar a análise. '
            'A exportação não transforma associações em efeitos causais.'),
        nbformat.v4.new_code_cell("from pathlib import Path\nimport json\nimport numpy as np\nimport pandas as pd\nimport statsmodels.api as sm\n"
            "pasta = Path.cwd()\nmeta = json.loads((pasta / 'manifesto.json').read_text(encoding='utf-8'))\n"
            "config = json.loads((pasta / 'especificacao.json').read_text(encoding='utf-8'))\n"
            "amostra = pd.read_csv(pasta / 'amostra_modelo.csv', dtype={'codigo_ibge': str})\n"
            "X = pd.read_csv(pasta / 'matriz_modelo.csv')\ny = amostra[config['spec']['y']]\n"
            "assert not amostra.duplicated(['codigo_ibge', 'ano']).any()\n"
            "assert len(X) == len(y) and np.isfinite(X.to_numpy()).all() and np.isfinite(y).all()\n"
            "display(pd.Series(config['summary']))\nconfig['spec']"),
        nbformat.v4.new_code_cell("base = sm.OLS(y, X, missing='raise').fit()\n"
            "cov = config['spec'].get('cov', 'HC3')\n"
            "if cov == 'HC3':\n    resultado = base.get_robustcov_results(cov_type='HC3', use_t=True)\n"
            "elif cov == 'nonrobust':\n    resultado = base\n"
            "else:\n    chaves = {'cluster_entity': ['codigo_ibge'], 'cluster_year': ['ano'], 'cluster_twoway': ['codigo_ibge', 'ano']}[cov]\n"
            "    grupos = [pd.factorize(amostra[c], sort=True)[0] for c in chaves]\n"
            "    grupos = grupos[0] if len(grupos) == 1 else np.column_stack(grupos)\n"
            "    resultado = base.get_robustcov_results(cov_type='cluster', groups=grupos, use_correction=True, df_correction=True, use_t=True)\n"
            "coeficientes = pd.DataFrame({'coef': resultado.params, 'se': resultado.bse, 'p': resultado.pvalues}, index=X.columns)\n"
            "esperado = pd.read_csv(pasta / 'coeficientes.csv', index_col=0)\n"
            "np.testing.assert_allclose(coeficientes.loc[esperado.index, ['coef', 'se']], esperado[['coef', 'se']], rtol=1e-6, atol=1e-9, equal_nan=True)\n"
            "display(coeficientes.loc[esperado.index])"),
        nbformat.v4.new_markdown_cell('## Próximas decisões científicas\n\n'
            '- Justificar Y, timing e unidades; preservar a distinção entre fluxo bruto e estoque.\n'
            '- Comparar especificações em amostra comum e verificar dependência temporal/espacial, poucos clusters, endogeneidade e suporte territorial.\n'
            '- Com efeitos de ano, preços comuns são absorvidos; com efeitos municipais, atributos fixos são absorvidos.\n'
            '- PAM histórica e GAEZ medem conceitos distintos; registros IBAMA não medem diretamente eficácia institucional.\n'
            '- Verificar modelos adequados a zeros, assimetria e proporções antes de escolher a especificação final.\n\n'
            'No repositório, `h1lab.models.fit_model(painel_integral, filtros, especificacao)` permite refazer transformações e a seleção amostral. '
            'Consulte o README do dashboard para importar o módulo em outro notebook.')]
    nb.metadata['kernelspec'] = {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}
    return nbformat.writes(nb)


def model_bundle(model, meta, filters):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('manifesto.json', json_text(manifest(meta, filters)))
        config = {k: model[k] for k in ['spec', 'summary', 'scales', 'warnings']}
        archive.writestr('especificacao.json', json_text(config))
        cols = list(dict.fromkeys(['codigo_ibge', 'ano', 'municipio', 'bioma_dominante', model['spec']['y'], *model['terms']]))
        archive.writestr('amostra_modelo.csv', csv_bytes(model['sample'][cols], index=False))
        archive.writestr('matriz_modelo.csv', csv_bytes(model['design'], index=False))
        archive.writestr('coeficientes.csv', csv_bytes(model['coefficients']))
        archive.writestr('perdas_amostrais.csv', csv_bytes(model['ledger'], index=False))
        archive.writestr('diagnosticos.csv', csv_bytes(model['diagnostics'], index=False))
        archive.writestr('reproduzir_ols.ipynb', model_notebook())
    return buffer.getvalue()


def evidence_bundle(entries, meta, filters, note, bridge):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('manifesto.json', json_text(manifest(meta, filters)))
        report = ['# Caderno de evidências — Capítulo 1', '', bridge, '', '## Notas do autor', '', note]
        for i, entry in enumerate(entries, 1):
            prefix = f'evidencia_{i:02d}'
            archive.writestr(f'{prefix}.csv', csv_bytes(entry['table']))
            archive.writestr(f'{prefix}.tex', booktabs(entry['table'], entry['title'], entry['note']))
            archive.writestr(f'{prefix}_contexto.json', json_text(entry['context']))
            if entry.get('figure'):
                archive.writestr(f'{prefix}.html', entry['figure'])
            report += ['', f"## {i}. {entry['title']}", '', entry['note'], '', f'Tabela: {prefix}.csv; fragmento: {prefix}.tex.']
        archive.writestr('caderno.md', '\n'.join(report))
        archive.writestr('LEIA-ME.txt', 'As notas são exploratórias. Cada evidência inclui seus próprios filtros, configuração e hashes; evidências de recortes distintos não são automaticamente comparáveis. Fragmentos LaTeX requerem booktabs e revisão da largura. Nenhum arquivo da tese foi alterado.\n')
    return buffer.getvalue()
