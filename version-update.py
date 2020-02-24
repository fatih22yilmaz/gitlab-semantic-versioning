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


def tag_repo(tag, npa_username, npa_password, ci_repository_url):
    push_url = re.sub(r'([a-z]+://)[^@]*(@.*)', rf'\g<1>{npa_username}:{npa_password}\g<2>', ci_repository_url)

    git("remote", "set-url", "--push", "origin", push_url)
    git("tag", tag)
    git("push", "origin", tag)


def default_tag():
    return str(date.today()) + ".1"


def main():
    env_list = ["CI_REPOSITORY_URL", "NPA_USERNAME", "NPA_PASSWORD", "CI_COMMIT_SHA"]
    [verify_env_var_presence(e) for e in env_list]

    ci_repository_url = os.environ["CI_REPOSITORY_URL"]
    npa_username = os.environ["NPA_USERNAME"]
    npa_password = os.environ["NPA_PASSWORD"]
    ci_commit_sha = os.environ["CI_COMMIT_SHA"]

    git("fetch", "--tags", "-f")

    try:
        already_tagged_commit_tag = git("describe", "--tags", "--abbrev=0", ci_commit_sha)
    except subprocess.CalledProcessError:
        print("Commit is not tagged before.")
    else:
        # Skip already tagged commits
        if already_tagged_commit_tag:
            print("Already tagged commit, commit tag: ", already_tagged_commit_tag)
            return 0

    try:
        latest_tag = git("describe", "--abbrev=0", "--tags").decode().strip()
    except subprocess.CalledProcessError:
        # Default to version {Date}.1 if no tags are available
        version = default_tag()
    else:
        version = bump(latest_tag)

    tag_repo(version, npa_username, npa_password, ci_repository_url)
    print("Commit SHA:", ci_commit_sha, "Tag:", version)

    return 0


if __name__ == "__main__":
    sys.exit(main())
