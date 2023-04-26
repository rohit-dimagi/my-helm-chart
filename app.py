from enum import Enum
import os
from loguru import logger
from github import Github
import github

class GithubVariables(Enum):
    """
    All supported Github environments
    """

    GITHUB = {
        "repo": "GITHUB_REPOSITORY",
        "branch": "GITHUB_REF_NAME",
        "commit_sha": "GITHUB_SHA",
        "token": "GITHUB_TOKEN",
        "commit_message": "COMMIT_MESSAGE",
        "chart_name": "CHART_NAME",
        "chart_version": "CHART_VERSION"
    }
    
class GitHubRelease:
    """
    Connection to the GitHub API
    """

    def __init__(self):
        self.repo_details = {
            "name": self.parse_repository(self.variable_value("repo")),
            "commit_sha": self.variable_value("commit_sha"),
            "token": self.variable_value("token"),
            "commit_message": self.variable_value("commit_message"),
            "chart_name": self.variable_value("chart_name"),
            "chart_version": self.variable_value("chart_version")
        }
        print(self.repo_details)
        self.gh_conn = Github(self.repo_details['token'])
        self.repo = self.gh_conn.get_user().get_repo(self.repo_details['name'])

    @staticmethod
    def parse_repository(repo_name: str) -> str:
        """
        Parse repository, and if it contains the owner,
        then it will get only the name of the repo
        """

        if not repo_name:
            return repo_name
        splitter = repo_name.split("/", 1)
        if len(splitter) > 1:
            return splitter[1]
        return splitter[0]

    @staticmethod
    def variable_value(variable_key: str) -> str:
        """
        Gets respective variables from os.env.
        If it doesn't exist, but it is required, it will raise an error.
        """

        errors = []
        for variable in GithubVariables:
            if value := os.getenv(variable.value[variable_key], None):
                return value
            errors.append(variable.value[variable_key])

        error_message = " and/or ".join(errors)
        print (f"Missing {error_message} variable/s")
    
    def create_release(self) -> str:
        """
        Create a GitHub release
        """
        tag_name = f"{self.repo_details['chart_name']}-{self.repo_details['chart_version']}"
        self.repo.create_git_release(
            tag_name,
            tag_name,
            self.repo_details['commit_message'],
            draft=False,
            prerelease=False
        )


    def is_release_exist(self) -> bool: 
        """
        Check if the release already exists.
        """
        relase_name = f"{self.repo_details['chart_name']}-{self.repo_details['chart_version']}"
        try:
            if self.repo.get_release(relase_name):
                logger.debug(f"Release {relase_name} Already Exist")
                return True
        except:
            return False

    def is_tag_exist(self) -> bool:
        """
        Check if we have release with the current commit sha.
        """
        tag_name = f"{self.repo_details['chart_name']}-{self.repo_details['chart_version']}"
        if tag_name in [tag.name for tag in self.repo.get_tags()]:
            logger.debug(f"Tag {tag_name} Already Exist")
            return True
        
        return False

    def create_tag(self) -> str:
        """
        Create git tag
        """
        tag_name = f"{self.repo_details['chart_name']}-{self.repo_details['chart_version']}"
        self.repo.create_git_tag(
            tag_name, 
            self.repo_details['commit_message'],
            self.repo_details['commit_sha'],
            'commit'
        )
        

cs = GitHubRelease()
print(cs.is_tag_exist())
print(cs.is_release_exist())
print(cs.create_tag())
print(cs.create_release())