"""Tests for GitHub commands."""
import os
import pytest
from unittest.mock import patch, MagicMock
from expression import Result, Ok, Error
from fcship.commands.github.cli import (
    github_repos,
    github_branches,
    github_issues,
    github_issue,
    github_pr_create,
    github_repo_delete,
    get_github_token,
    create_github_context
)
from fcship.commands.github.main import (
    list_repositories,
    list_branches,
    list_issues,
    download_issue_body,
    create_pull_request,
    delete_repository
)

def test_get_github_token_success():
    """Test successful GitHub token retrieval."""
    with patch.dict('os.environ', {'GITHUB_TOKEN': 'test_token'}):
        result = None
        for step in get_github_token():
            result = step
        
        assert result.is_ok()
        assert result.ok == 'test_token'

def test_get_github_token_failure():
    """Test GitHub token retrieval failure."""
    with patch.dict('os.environ', {}, clear=True):
        result = None
        for step in get_github_token():
            result = step
        
        assert result.is_error()
        assert "GITHUB_TOKEN environment variable not set" in str(result.error)

def test_create_github_context_success():
    """Test successful GitHub context creation."""
    with patch.dict('os.environ', {'GITHUB_TOKEN': 'test_token'}):
        result = None
        for step in create_github_context('test_repo'):
            result = step
        
        assert result.is_ok()
        assert result.ok.token == 'test_token'
        assert result.ok.repo_name == 'test_repo'

def test_create_github_context_failure():
    """Test GitHub context creation failure."""
    with patch.dict('os.environ', {}, clear=True):
        result = None
        for step in create_github_context('test_repo'):
            result = step
        
        assert result.is_error()
        assert "GITHUB_TOKEN environment variable not set" in str(result.error)

@patch('fcship.commands.github.main.Github')
def test_list_repositories_success(mock_github):
    """Test successful repository listing."""
    # Set up mocks
    mock_user = MagicMock()
    mock_repo = MagicMock()
    mock_repo.name = "test-repo"
    mock_repo.description = "Test repository"
    mock_repo.stargazers_count = 5
    mock_repo.language = "Python"
    mock_repo.private = False
    
    mock_user.get_repos.return_value = [mock_repo]
    mock_github.return_value.get_user.return_value = mock_user
    
    with patch.dict('os.environ', {'GITHUB_TOKEN': 'test_token'}):
        result = None
        for step in github_repos():
            result = step
        
        assert result.is_ok()
        mock_github.assert_called_once_with('test_token')
        mock_user.get_repos.assert_called_once()

@patch('fcship.commands.github.main.Github')
def test_github_branches_success(mock_github):
    """Test successful branch listing."""
    # Set up mocks
    mock_user = MagicMock()
    mock_repo = MagicMock()
    mock_branch = MagicMock()
    mock_branch.name = "main"
    mock_branch.commit.sha = "abcdef1234567890"
    mock_branch.protected = False
    
    mock_repo.get_branches.return_value = [mock_branch]
    mock_user.get_repo.return_value = mock_repo
    mock_github.return_value.get_user.return_value = mock_user
    
    with patch.dict('os.environ', {'GITHUB_TOKEN': 'test_token'}):
        result = None
        for step in github_branches('test-repo'):
            result = step
        
        assert result.is_ok()
        mock_github.assert_called_once_with('test_token')
        mock_user.get_repo.assert_called_once_with('test-repo')
        mock_repo.get_branches.assert_called_once()

@patch('fcship.commands.github.main.Github')
def test_github_issues_success(mock_github):
    """Test successful issue listing."""
    # Set up mocks
    mock_user = MagicMock()
    mock_repo = MagicMock()
    mock_issue = MagicMock()
    mock_issue.number = 1
    mock_issue.title = "Test issue"
    mock_issue.user.login = "testuser"
    mock_issue.labels = []
    mock_issue.comments = 0
    
    mock_repo.get_issues.return_value = [mock_issue]
    mock_user.get_repo.return_value = mock_repo
    mock_github.return_value.get_user.return_value = mock_user
    
    with patch.dict('os.environ', {'GITHUB_TOKEN': 'test_token'}):
        result = None
        for step in github_issues('test-repo'):
            result = step
        
        assert result.is_ok()
        mock_github.assert_called_once_with('test_token')
        mock_user.get_repo.assert_called_once_with('test-repo')
        mock_repo.get_issues.assert_called_once_with(state='open')

@patch('fcship.commands.github.main.Github')
def test_github_issue_success(mock_github):
    """Test successful issue detail retrieval."""
    # Set up mocks
    mock_user = MagicMock()
    mock_repo = MagicMock()
    mock_issue = MagicMock()
    mock_issue.number = 1
    mock_issue.title = "Test issue"
    mock_issue.user.login = "testuser"
    mock_issue.created_at = "2024-02-27"
    mock_issue.state = "open"
    mock_issue.body = "Test issue body"
    
    mock_repo.get_issue.return_value = mock_issue
    mock_user.get_repo.return_value = mock_repo
    mock_github.return_value.get_user.return_value = mock_user
    
    with patch.dict('os.environ', {'GITHUB_TOKEN': 'test_token'}):
        result = None
        for step in github_issue('test-repo', 1):
            result = step
        
        assert result.is_ok()
        mock_github.assert_called_once_with('test_token')
        mock_user.get_repo.assert_called_once_with('test-repo')
        mock_repo.get_issue.assert_called_once_with(number=1)

@patch('fcship.commands.github.main.Github')
def test_github_pr_create_success(mock_github):
    """Test successful pull request creation."""
    # Set up mocks
    mock_user = MagicMock()
    mock_repo = MagicMock()
    mock_pr = MagicMock()
    mock_pr.number = 1
    mock_pr.html_url = "https://github.com/user/repo/pull/1"
    
    mock_repo.create_pull.return_value = mock_pr
    mock_user.get_repo.return_value = mock_repo
    mock_github.return_value.get_user.return_value = mock_user
    
    with patch.dict('os.environ', {'GITHUB_TOKEN': 'test_token'}):
        result = None
        for step in github_pr_create('test-repo', 'Test PR', 'Test body', 'feature', 'main'):
            result = step
        
        assert result.is_ok()
        mock_github.assert_called_once_with('test_token')
        mock_user.get_repo.assert_called_once_with('test-repo')
        mock_repo.create_pull.assert_called_once_with(
            title='Test PR',
            body='Test body',
            head='feature',
            base='main'
        )

@patch('fcship.commands.github.main.Github')
def test_github_repo_delete_success(mock_github):
    """Test successful repository deletion."""
    # Set up mocks
    mock_user = MagicMock()
    mock_repo = MagicMock()
    
    mock_user.get_repo.return_value = mock_repo
    mock_github.return_value.get_user.return_value = mock_user
    
    with patch.dict('os.environ', {'GITHUB_TOKEN': 'test_token'}):
        result = None
        for step in github_repo_delete('test-repo', True):
            result = step
        
        assert result.is_ok()
        mock_github.assert_called_once_with('test_token')
        mock_user.get_repo.assert_called_once_with('test-repo')
        mock_repo.delete.assert_called_once()

def test_github_repo_delete_no_confirm():
    """Test repository deletion without confirmation."""
    with patch.dict('os.environ', {'GITHUB_TOKEN': 'test_token'}):
        result = None
        for step in github_repo_delete('test-repo', False):
            result = step
        
        assert result.is_error()
        assert "Please confirm deletion with --confirm flag" in result.error