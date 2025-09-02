from kukai.util import ContextParser


def test_cc_context():
    ctx = ContextParser("tests/data/cc/cookiecutter.json")
    default_context = {'project_name': 'Kukai Test Data', 'project_slug': 'kukai_test_data', 'author': 'Max Muster'}
    print(ctx.as_dict())
    assert default_context == ctx.as_dict()

    name = { "project_name": "TestIng",}
    ctx.add_context(name)
    compare_context = {'project_name': 'TestIng', 'project_slug': 'testing', 'author': 'Max Muster'}
    assert compare_context == ctx.as_dict()

    author = {"author": "Maxil Must"}
    ctx.add_context(author)
    compare_context = {'project_name': 'TestIng', 'project_slug': 'testing', 'author': 'Maxil Must'}
    assert compare_context == ctx.as_dict()


def test_file_context():
    ctx = ContextParser("tests/data/file/kukai.toml")
    default_context = {'project_name': 'Kukai File Test', 'project_slug': 'kukai_file_test', 'author': 'Max Muster'}
    assert default_context == ctx.as_dict(), f"{ctx.as_dict()}"

    name = { "project_name": "TestIng",}
    ctx.add_context(name)
    compare_context = {'project_name': 'TestIng', 'project_slug': 'testing', 'author': 'Max Muster'}
    assert compare_context == ctx.as_dict()
 
    author = {"author": "Maxil Must"}
    ctx.add_context(author)
    compare_context = {'project_name': 'TestIng', 'project_slug': 'testing', 'author': 'Maxil Must'}
    assert compare_context == ctx.as_dict()

def prompt(key):
    prompt_answer = {'project_name': 'TestIng', 'project_slug': 'testing', 'author': 'Maxil Must'}
    return prompt_answer[key]

def test_context_iterator():
    ctx = ContextParser("tests/data/cc/cookiecutter.json")
    default_context = {'project_name': 'Kukai Test Data', 'project_slug': 'kukai_test_data', 'author': 'Max Muster'}
    assert default_context == ctx.as_dict(), f"{ctx.as_dict()}"

    additional_context = {'project_name': 'Testy prj'}
    ctx.add_context(additional_context)
    for key, value in ctx:
        print(f"ask: {value}")
        answer = prompt(key)
        ctx.add_context({key: answer})
        print(f"input: {answer}")
