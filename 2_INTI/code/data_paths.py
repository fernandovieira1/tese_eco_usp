"""Physical chapter directories and explicit routing of the research inputs.

``data/catalog`` retains the original acquisition evidence. Shared inputs are
ordinary independent copies. Historical filenames (including h1__/h2__) stay
unchanged: directory membership describes their current analytical use.
"""
from pathlib import Path
import hashlib
import shutil

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / '2_INTI' / 'data'


def logical_relative(relative):
    value = str(relative).replace('\\', '/').removeprefix('2_INTI/data/')
    path = Path(value)
    if path.is_absolute() or '..' in path.parts:
        raise ValueError('Data path must be relative and remain inside data')
    if path.parts and path.parts[0] in ('chap1', 'chap2'):
        path = Path(*path.parts[1:])
    return path


def chapters_for(relative):
    """Return destinations; the first chapter is the canonical reading copy."""
    path = logical_relative(relative)
    name = path.as_posix().lower()
    if name == 'catalog' or name.startswith('catalog/'):
        return ()
    if name.startswith('interim/') or name.startswith(('raw/raster/chirps', 'raw/raster/era5')):
        return ('chap2', 'chap1')
    if name.startswith(('raw/tabular/ibama', 'raw/tabular/conab',
                        'raw/tabular/worldbank', 'raw/vector/ibama')):
        return ('chap1',)
    if name.startswith(('processed/tabular/h1__autos', 'processed/tabular/h1__costs',
                        'processed/tabular/h1__prices')):
        return ('chap1',)
    # Municipal agriculture, vegetation, physical capacity, geography and the
    # small climate aggregates may serve both chapters. Documentation is copied
    # as evidence, without implying that every source is an adopted regressor.
    return ('chap1', 'chap2')


def data_paths(relative):
    path = logical_relative(relative)
    chapters = chapters_for(path)
    paths = [DATA / chapter / path for chapter in chapters] if chapters else [DATA / path]
    for target in paths:
        if not target.resolve().is_relative_to(DATA.resolve()):
            raise ValueError('Destination outside 2_INTI/data')
    return paths


def data_path(relative, chapter=None):
    """Resolve a complete logical filename, or a homogeneous source directory."""
    if chapter is None:
        return data_paths(relative)[0]
    if chapter not in chapters_for(relative):
        raise ValueError(f'{relative} is not assigned to {chapter}')
    return DATA / chapter / logical_relative(relative)


def legacy_repository_path(path):
    """Normalize old and relocated provenance identifiers for comparison."""
    value = str(path).replace('\\', '/')
    if value.startswith('2_INTI/data/'):
        return '2_INTI/data/' + logical_relative(value).as_posix()
    return value


def resolve_repository_path(path):
    value = str(path).replace('\\', '/')
    if value.startswith('2_INTI/data/'):
        return data_path(value)
    return ROOT / value


def file_sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def sync_shared(relative, *, replace=False):
    """Copy a produced/acquired file to other chapters, checking its bytes.

    Brutos must use replace=False. Regenerable processed outputs may explicitly
    replace their previous chapter copies after the canonical output is saved.
    """
    paths = data_paths(relative)
    source = paths[0]
    digest = file_sha256(source)
    for target in paths[1:]:
        if target.exists():
            if file_sha256(target) == digest:
                continue
            if not replace:
                raise ValueError(f'Different existing shared copy: {target}')
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        if file_sha256(target) != digest:
            raise ValueError(f'Copy verification failed: {target}')
    return source
