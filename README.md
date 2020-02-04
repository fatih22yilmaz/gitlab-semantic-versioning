# gitlab-semantic-versioning

Docker image that can be used to automatically version projects. 

## How is the version determined?

Versions are being maintained using git tags.

If no git tag is available, the first version update will result in version (current-date).1.
If git tags are available, it will determine whether to update date part or the patch part.

## Prerequisites

### API token and group

To extract the labels from merge requests, we need an API token to access the Gitlab API. Unfortunately, [GitLab doesn't yet support non-user specific access tokens](https://gitlab.com/gitlab-org/gitlab-ee/issues/756). 

Ask your GitLab administrator to add a dummy user `${group_name}_npa` to GitLab with access only to your project group. Log in with this user, and create a [personal access token](https://gitlab.wbaa.pl.ing.net/profile/personal_access_tokens) with api scope access.

Copy the generated API token and keep it available for the next section.

### Group-level variables

The NPA username and token need to be injected into the version-update container as environment variables. For this, we'll use group-level variables. 

Go to your group's variables section under `Settings` -> `CI / CD`.

Add the following variables:

| Key             | Value                                                                |
|-----------------|----------------------------------------------------------------------|
| NPA_USERNAME    | The name of the NPA user created for your group: `${group_name}_npa` |
| NPA_PASSWORD    | The personal access token with API scope generated for the NPA user  |

## Pipeline configuration

The pipeline configuration below will:

-It demonstrates tagging the project and passing the tag to other stages. 

```
stages:
  - version
  - echo

version:
  stage: version
  image: cayro/gitlab-semantic-versioning:latest
  tags:
    - runner-tag
  script:
    - python3 /version-update/version-update.py
    - TAG=$(git describe --tags --always)
    - echo "export TAG=$TAG" > .variables
  artifacts:
    paths:
      - .variables
  only:
    - develop

echo:
  stage: echo
  tags:
    - runner-tag
  only:
    - develop
  before_script:
    - source .variables
  script:
    - echo $TAG
```