from enum import Enum
import os
from loguru import logger
from github import Github

class GithubVariables(Enum):
    """
    All supported Github environments
    """

    GITHUB = {
        "owner": "GITHUB_REPOSITORY_OWNER",
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
            "owner": self.variable_value("owner"),
            "name": self.parse_repository(self.variable_value("repo")),
            "commit_sha": self.variable_value("commit_sha"),
            "token": self.variable_value("token"),
            "commit_message": self.variable_value("commit_message"),
            "chart_name": self.variable_value("chart_name"),
            "chart_version": self.variable_value("chart_version")
        }
        try:
            self.gh_conn = Github(self.repo_details['token'])
            self.repo = self.gh_conn.get_repo(f"{self.repo_details['owner']}/{self.repo_details['name']}")
            logger.debug("Github Connection Established Successfully")
        except Exception as e:
            logger.error(f"Not able to Connect with Github API. Error: {e}")
            
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
        logger.warning(f"Missing {error_message} variable/s")
    
    def commit_msg(self):
        if self.repo_details['commit_message'] is None:
            commit = self.repo.get_commit(self.repo_details["commit_sha"])
            commit_msg= commit.commit.message
            return commit_msg
        return self.repo_details['commit_message']
    
    def tag_name(self):
        return f"{self.repo_details['chart_name']}-{self.repo_details['chart_version']}"

    def is_release_exist(self) -> bool: 
        """
        Check if the release already exists.
        """
        relase_name = self.tag_name()
        try:
            if self.repo.get_release(relase_name):
                logger.info(f"Release {relase_name} Already Exist, Skipping")
                return True
        except:
            return False

    def is_tag_exist(self) -> bool:
        """
        Check if we have release with the current commit sha.
        """
        tag_name = self.tag_name()
        if tag_name in [tag.name for tag in self.repo.get_tags()]:
            logger.info(f"Tag {tag_name} Already Exist, Skipping")
            return True
        
        return False

    def create_tag(self) -> str:
        """
        Create git tag
        """
        tag_name = self.tag_name()
        commit_msg= self.commit_msg()
        self.repo.create_git_tag(
            tag_name, 
            commit_msg,
            self.repo_details['commit_sha'],
            'commit'
        )

    def create_release(self) -> str:
        """
        Create a GitHub release
        """  
        tag_name = self.tag_name()
        commit_msg= self.commit_msg()
        
        self.repo.create_git_release(
            tag_name,
            tag_name,
            commit_msg,
            draft=False,
            prerelease=False
        )      
    
    def create_release_if_not_exist(self):
        if not self.is_tag_exist(): 
            self.create_tag()
        if not self.is_release_exist():
            self.create_release()
                
cs = GitHubRelease()
cs.create_release_if_not_exist()
