from nox import session


@session
def lint(session):
    session.install('ruff')
    session.run('ruff', 'check', 'src/kukai')

@session(python=["3.10", "3.11", "3.12"])
def tests(session):
    session.install("pytest", ".")
    session.run("pytest")

@session
def format(session):
    session.install('ruff')
    session.run('ruff', 'format', 'src/kukai')

@session
def typecheck(session):
    session.install('ty')
    session.install('uv')
    session.run('uv', 'sync', '--locked', '--active', '--no-dev')
    session.run('ty', 'check', '--exclude', 'noxfile.py')

@session
def security(session):
    session.run('trivy', 'fs', '--scanners', 'vuln,secret,misconfig', 'src', external=True)

@session
def docs(session):
    session.install("mkdocs")
    session.install("mkdocs-material")
    session.install("mkdocs-click")
    session.install("mkdocstrings[python]")
    session.install(".")
    session.run('mkdocs','build')

