from abc import ABC, abstractmethod
from typing import Any, Dict, List


class GitHubClient(ABC):
    @abstractmethod
    def get_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        ...

    @abstractmethod
    def get_collaborators(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        ...

    @abstractmethod
    def get_branch_protection(
        self, owner: str, repo: str, branch: str
    ) -> Dict[str, Any]:
        ...

    @abstractmethod
    def update_branch_protection(
        self, owner: str, repo: str, branch: str, rules: Dict
    ) -> Dict[str, Any]:
        ...


class MockGitHubClient(GitHubClient):
    """In-memory mock that lets tests drive every failure mode."""

    def __init__(self) -> None:
        self.repos: Dict[str, Dict] = {}
        self.collaborators: Dict[str, List] = {}
        self.branch_protection: Dict[str, Dict] = {}
        self.actions_permissions: Dict[str, Dict] = {}

    def seed_repository(self, owner: str, repo: str, data: Dict) -> None:
        key = f"{owner}/{repo}"
        self.repos[key] = data

    def seed_branch_protection(
        self, owner: str, repo: str, branch: str, rules: Dict
    ) -> None:
        key = f"{owner}/{repo}:{branch}"
        self.branch_protection[key] = rules

    def get_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        key = f"{owner}/{repo}"
        if key not in self.repos:
            raise KeyError(f"Repository {key} not found")
        return self.repos[key]

    def get_collaborators(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        return self.collaborators.get(f"{owner}/{repo}", [])

    def get_branch_protection(
        self, owner: str, repo: str, branch: str
    ) -> Dict[str, Any]:
        key = f"{owner}/{repo}:{branch}"
        return self.branch_protection.get(key, {})

    def update_branch_protection(
        self, owner: str, repo: str, branch: str, rules: Dict
    ) -> Dict[str, Any]:
        key = f"{owner}/{repo}:{branch}"
        self.branch_protection[key] = rules
        return rules
