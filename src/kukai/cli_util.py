import inquirer
import os
from pathlib import Path


def get_inq_group(data: dict) -> str:
    sel_key = get_inq_key(data)
    selected = get_inq_list(sel_key)
    return selected


def get_inq_key(data: dict) -> list:
    selection = []
    for key in data:
        sel = ("--> " + key, key)
        selection.append(sel)
    question = [
        inquirer.List(
            "group", message="Template Menu", choices=selection, carousel=True
        ),
    ]
    answer = inquirer.prompt(question)
    sel_group = answer["group"]
    return data[sel_group]


def get_inq_list(data: list) -> str:
    os.system("clear")
    selection = []
    for element in data:
        sel = (" * " + element, element)
        selection.append(sel)
    question = [
        inquirer.List(
            "element", message="Template Menu", choices=selection, carousel=True
        ),
    ]
    answer = inquirer.prompt(question)
    ret = answer["element"]
    return ret


def create_inq_list(data: dict):
    os.system("clear")
    folder = Path()
    parsed = data
    selection = []
    for s in parsed["sub"]:
        sel = ("--> " + s, s)
        selection.append(sel)
    for s in parsed["template"]:
        sel = (" * " + s, s)
        selection.append(sel)
    question = [
        inquirer.List(
            "template", message="Template Menu", choices=selection, carousel=True
        ),
    ]
    answer = inquirer.prompt(question)
    ret = answer["template"]
    if answer["template"] in parsed["sub"]:
        ret += "/"
        ret += create_inq_list(folder / answer["template"])
    return ret


def path_complete(text, state):
    cwd = os.getcwd()
    selection = []
    for path in Path(cwd).iterdir():
        if path.is_dir():
            selection.append(path.name)
    return selection[state % len(selection)]


def get_path():
    question = [
        inquirer.Text(
            "path",
            message="Enter Destination path",
            autocomplete=path_complete,
        ),
    ]
    answer = inquirer.prompt(question)
    return Path(answer["path"])
