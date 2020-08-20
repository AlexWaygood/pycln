"""
Pycln regex utility.
"""
import os
import re
from functools import lru_cache
from pathlib import Path
from typing import List, Pattern

import typer
from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern

# Constants.
INCLUDE = "include"
EXCLUDE = "exclude"
GITIGNORE = ".gitignore"
NOQA_REGEX = r"#.*noqa.*"
INCLUDE_REGEX = r".*\.pyi?$"
EXCLUDE_REGEX = r"(\.eggs|\.git|\.hg|\.mypy_cache|__pycache__|\.nox|\.tox|\.venv|\.svn|buck-out|build|dist)/"


def safe_compile(str_regex: str, type_: str) -> Pattern[str]:
    """
    Safely compile [--include, --exclude] options regex.

    :param str_regex: an str regex to be complied.
    :param type_: 'include' OR 'exclude'.
    :returns: complied regex.
    """
    try:
        compiled: Pattern[str] = re.compile(str_regex, re.IGNORECASE)
        return compiled
    except re.error:
        typer.secho(
            f"Invalid regular expression for {type_} given: '{str_regex}'",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit()


def is_included(name: str, regex: Pattern[str]) -> bool:
    """
    Check if the file/directory name match include pattern.

    :param name: file/directory name to check.
    :param regex: include regex pattern.
    :returns: True if the name match else False.
    """
    return bool(regex.fullmatch(name))


def is_excluded(name: str, regex: Pattern[str]) -> bool:
    """
    Check if the file/directory name match exclude pattern.

    :param name: file/directory name to check.
    :param regex: exclude regex pattern.
    :returns: True if the name match else False.
    """
    return bool(regex.fullmatch(name))


@lru_cache
def get_gitignore(root: Path) -> PathSpec:
    """
    Return a PathSpec matching gitignore content if present.

    :param root: a path to search on.
    :returns: PathSpec matching gitignore content if present.
    """
    gitignore_path = os.path.join(root, GITIGNORE)
    gitignore_lines: List[str] = []

    if os.path.isfile(gitignore_path) and root:
        with open(gitignore_path) as gitignore_file:
            gitignore_lines = gitignore_file.readlines()

    return PathSpec.from_lines(GitWildMatchPattern, gitignore_lines)


def has_noqa(line: str) -> bool:
    """
    Check if the line has `# noqa` to skip.
    """
    return bool(re.search(NOQA_REGEX, line, re.IGNORECASE))
