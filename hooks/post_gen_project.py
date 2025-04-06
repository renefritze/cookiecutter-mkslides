#!/usr/bin/env python

import os
import sys
import subprocess


def _precommit():

    subprocess.check_output(["uv", "run", "pre-commit", "install"])
    # first time can have failure due to formatting
    subprocess.run(["uv", "run", "pre-commit", "run", "-a"])
    subprocess.check_output(["uv", "run", "pre-commit", "run", "-a"])
    try:
        subprocess.check_output(["git", "add", "-u"])
        subprocess.check_output(
            [
                "git",
                "add",
                "uv.lock",
            ]
        )
        subprocess.check_output(["git", "commit", "--amend", "--no-edit"])
    except subprocess.CalledProcessError:
        pass


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
        subprocess.check_output(["git", "add", ".pre-commit-config.yaml"])
        subprocess.run(["git", "commit", "-m", "initial commit", "--no-verify"])
    return True


def _install():
    subprocess.check_output(["make", "install"])
    subprocess.call(["make"])


if __name__ == "__main__":

    if "{{ cookiecutter.create_git_repository|lower }}" != "yes":
        sys.exit(0)

    git_init_done = _git_init()

    _install()

    if git_init_done:
        _precommit()
        print("Pre-commit hooks installed and run successfully.")
