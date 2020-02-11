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
    if len(split) != 2:
        print("Latest tag is not properly formatted, tag is not contain date field or patch number, default tag "
              "format applying...")
        print("Latest Tag: ", latest)
        return default_tag()
    tag_date_string = split[0]
    version = split[1]

    try:
        tag_date = datetime.strptime(tag_date_string, "%Y-%m-%d").date()
    except:
        print("Latest tag is not properly formatted, date field is not standard default tag format applying...")
        print("Latest Tag: ", latest)
        return default_tag()

    if not version.isnumeric():
        print("Latest tag is not properly formatted, version field is not numeric, default tag format applying...")
        print("Latest Tag: ", latest)
        return default_tag()

    if tag_date == date.today():
        version = int(version) + 1
    else:
        tag_date = tag_date.today()
        version = 1
    return str(tag_date) + "." + str(version)


def tag_repo(tag):
    repository_url = os.environ["CI_REPOSITORY_URL"]
    username = os.environ["NPA_USERNAME"]
    password = os.environ["NPA_PASSWORD"]

    push_url = re.sub(r'([a-z]+://)[^@]*(@.*)', rf'\g<1>{username}:{password}\g<2>', repository_url)

    git("remote", "set-url", "--push", "origin", push_url)
    git("tag", tag)
    git("push", "origin", tag)


def default_tag():
    return str(date.today()) + ".1"


def main():
    env_list = ["CI_REPOSITORY_URL", "NPA_USERNAME", "NPA_PASSWORD"]
    [verify_env_var_presence(e) for e in env_list]

    git("fetch", "--tags", "-f")
    try:
        latest_tag = git("describe", "--abbrev=0", "--tags").decode().strip()
        latest_tagged_commit_id = git("rev-list", "-n", "1", latest_tag)
        latest_commit_id = git("log", "--format=%H", "-n", "1")
    except subprocess.CalledProcessError:
        # Default to version 1.0.0 if no tags are available
        version = default_tag()
    else:
        # Skip already tagged commits
        if latest_tagged_commit_id == latest_commit_id:
            print("Already tagged commit, latest tag: ", latest_tag)
            return 0

        version = bump(latest_tag)

    tag_repo(version)
    print(version)

    return 0


if __name__ == "__main__":
    sys.exit(main())
