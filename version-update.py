#!/usr/bin/env python3
import os
import re
import subprocess
import sys
from datetime import date, datetime


def git(*args):
    return subprocess.check_output(["git"] + list(args))


def verify_env_var_presence(name):
    if name not in os.environ:
        raise Exception(f"Expected the following environment variable to be set: {name}")


def bump(latest):
    split = latest.split('.')
    dateString = split[0]
    date = datetime.strptime(dateString, "%Y-%m-%d").date()
    version = split[1]
    if date == date.today():
        version = int(version) + 1
    else:
        date = date.today()
        version = 1
    return str(date) + "." + str(version)


def tag_repo(tag):
    repository_url = os.environ["CI_REPOSITORY_URL"]
    username = os.environ["NPA_USERNAME"]
    password = os.environ["NPA_PASSWORD"]

    push_url = re.sub(r'([a-z]+://)[^@]*(@.*)', rf'\g<1>{username}:{password}\g<2>', repository_url)

    git("remote", "set-url", "--push", "origin", push_url)
    git("tag", tag)
    git("push", "origin", tag)


def main():
    env_list = ["CI_REPOSITORY_URL", "NPA_USERNAME", "NPA_PASSWORD"]
    [verify_env_var_presence(e) for e in env_list]

    git("fetch", "--tags")
    try:
        latest = git("describe", "--abbrev=0", "--tags").decode().strip()
    except subprocess.CalledProcessError:
        # Default to version 1.0.0 if no tags are available
        version = str(date.today()) + ".0"
    else:
        # Skip already tagged commits
        if '-' not in latest:
            print(latest)
            return 0

        version = bump(latest)

    tag_repo(version)
    print(version)

    return 0


if __name__ == "__main__":
    sys.exit(main())