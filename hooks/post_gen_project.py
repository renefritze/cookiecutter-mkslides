#!/usr/bin/env python

import os
import sys
import subprocess


def _precommit():
    try:
        from pre_commit import main
    except ImportError:
        print("Please install pre-commit")
        return

    main.main(["install"])
    main.main(["run", "-a"])


def _git_init():
    try:
        subprocess.check_output(["git", "--version"])
    except (PermissionError, FileNotFoundError, subprocess.CalledProcessError) as e:
        print("Please install git")
        return False
    subprocess.check_output(["git", "init"])
    subprocess.check_output(["git", "add", "."])
    try:
        subprocess.check_output(["git", "commit", "-m", "initial commit"])
    except subprocess.CalledProcessError:
        subprocess.run(["git", "commit", "-m", "initial commit", "--no-verify"])
    return True


def _install():
    subprocess.check_output(["make", "install"])
    subprocess.call(["make"])


if __name__ == "__main__":
    if "{{ cookiecutter.create_git_repository|lower }}" != "yes":
        sys.exit(0)

    if _git_init():
        _precommit()
    _install()
