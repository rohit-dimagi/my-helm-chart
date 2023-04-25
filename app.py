import os
from github import Github

# replace with your own personal access token
ACCESS_TOKEN = os.environ.get('GITHUB_TOKEN')
COMMIT_MSG = os.environ.get('COMMIT_MESSAGE')
REPO_NAME = os.environ.get('GITHUB_REPOSITORY')

g = Github(ACCESS_TOKEN)

# get the repository where you want to create the release
repo = g.get_user().get_repo(REPO_NAME)

# create the release
release = repo.create_git_release(
    tag="0.0.1",
    name="TEST",
    message=COMMIT_MSG,
)

# add the release notes to the release
release.update_release(body=COMMIT_MSG)
