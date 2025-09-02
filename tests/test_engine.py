from pathlib import Path
import toml

from kukai.engine import CookieEngine, FileEngine


def test_import():
    assert True

def test_cookie_engine(tmp_path):
    context = { "project_name": "TestIng", "author": "Maxil Must"}
    cc_path = Path("tests/data/cc")
    dest_path = Path(tmp_path)
    toml_path = dest_path / "testing/testing.toml"
    dest_path.mkdir(exist_ok=True)
    CookieEngine.create(cc_path, dest_path, context)
    data = toml.load(str(toml_path))
    golden = {'data': {'name': 'TestIng', 'slug': 'testing', 'author': 'Maxil Must'}}
    assert data == golden

def test_file_engine(tmp_path):
    template_file = Path("tests/data/file/jinja_template.toml")
    dest_path = Path(tmp_path)
    #dest_path = Path("out")
    dest_path.mkdir(exist_ok=True)
    context = { "project_name": "TestIng", "author": "Maxil Must"}
    FileEngine.create(template_file, dest_path, context)
    toml_path = dest_path / "jinja_template.toml"
    data = toml.load(str(toml_path))
    golden = {'data': {'name': "TestIng"}}
    assert data == golden
