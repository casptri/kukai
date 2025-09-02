import click
from pathlib import Path

from kukai.util import RepoExtraction
from kukai.core import KukaiCore

from kukai.cli_util import get_inq_group


@click.group()
def kukai():
    pass


@kukai.group("repo")
def repo():
    """Manage repo configuration"""
    pass


@repo.command()
@click.argument("name")
def add(name):
    """Add a repo to configuration

    Adds a repo to local or global configuration file.

    Example:

        kukai repo add kukai.toml
    """
    core = KukaiCore()
    if not core.add_repo(name):
        print("repo already added")


@repo.command("list")
def repo_list():
    """Print all repos added to configuration"""
    core = KukaiCore()
    for entry in core.get_repos():
        click.echo("")
        location = entry.get("location")
        click.echo(f"File: {location}")
        with Path(location).open("r") as fd:
            data = fd.read()
        click.echo(data)


@repo.command(hidden=True)
def data():
    core = KukaiCore()
    data = core.get_data()
    print(data)


@kukai.command()
@click.argument("tag")
def tag(tag):
    """Show all templates with the tag"""
    core = KukaiCore()
    collection = core.get_collection()
    templates = collection.get_tags(tag)
    if len(templates) == 0:
        click.echo(f"{tag} not found")
        tags = collection.get_near_tag(tag)
        response = click.confirm(f"Did you mean {tags}?", default=True)
        if response:
            templates = collection.get_tags(tags)
    for t in templates:
        click.echo(t)


@kukai.command()
@click.option("-t", "--tag", default=None, help="Only show templates with the tag")
def menu(tag):
    """Get a selection menu for templates to create"""
    core = KukaiCore()
    collection = core.get_collection()
    group = collection.get_grouped(tag)
    selection = get_inq_group(group)
    template = collection.get_name(selection)
    if not template:
        click.echo("No template found")
        return
    dest_path = Path()
    ctx = template.get_context()
    for key, value in ctx:
        answer = click.prompt(f"{key}", default=value)
        ctx.add_context({key: answer})
    context = ctx.as_dict()
    template.create(dest_path, context)


@kukai.command()
def list():
    """List all templates"""
    core = KukaiCore()
    collection = core.get_collection()
    templates = collection.get()
    for t in templates:
        click.echo(t)


@kukai.command()
@click.argument("repo")
def create(repo):
    """Create a template direct by location

    Arguments:

        repo: Path or url to a template

    Example:

        kukai create tests/data/cc-folder/cc-0/
    """
    repo_path = Path(repo)
    if repo_path.exists():
        extraction = RepoExtraction(repo_path.resolve())
        template = extraction.get_template()

    else:
        core = KukaiCore()
        collection = core.get_collection()
        template = collection.get_name(repo)
        if not template:
            click.echo(f"{repo} is not a template")
            return
    dest_path = Path()
    ctx = template.get_context()
    for key, value in ctx:
        if type(value) is bool:
            answer = click.confirm(f"{key}", default=value)
        else:
            answer = click.prompt(f"{key}", default=value)
        ctx.add_context({key: answer})
    context = ctx.as_dict()
    template.create(dest_path, context)
