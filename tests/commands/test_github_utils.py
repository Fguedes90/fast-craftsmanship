"""Tests for GitHub API utilities."""

import os
from unittest.mock import MagicMock, patch

from expression import Error, Ok, Result, effect
from github.GithubException import GithubException

from fcship.commands.github.github_utils import (
    create_dependabot_config,
    create_repository,
    create_workflow_file,
    get_github_client,
    get_github_token,
    set_branch_protection,
    setup_environment,
    setup_repository_secret,
    setup_workflow_templates,
)
from fcship.tui.input import get_user_input


def test_get_github_token_from_env():
    """Test getting GitHub token from environment variable."""
    with patch.dict("os.environ", {"GITHUB_TOKEN": "test_token"}):
        result = None
        for step in get_github_token():
            result = step

        assert result.is_ok()
        assert result.ok == "test_token"


def test_get_github_token_from_input():
    """Test getting GitHub token from user input."""
    with patch.dict("os.environ", {}, clear=True):
        mock_input = MagicMock(return_value=Ok("user_input_token"))

        with patch("fcship.commands.github.github_utils.get_user_input", mock_input):
            result = None
            for step in get_github_token():
                result = step

            assert result.is_ok()
            assert result.ok == "user_input_token"


def test_get_github_token_empty_input():
    """Test getting GitHub token with empty user input."""
    with patch.dict("os.environ", {}, clear=True):
        mock_input = MagicMock(return_value=Ok(""))

        with patch("fcship.commands.github.github_utils.get_user_input", mock_input):
            result = None
            for step in get_github_token():
                result = step

            assert result.is_error()
            assert "GitHub token is required" in result.error


def test_get_github_client_success():
    """Test successful GitHub client creation."""
    with patch.dict("os.environ", {"GITHUB_TOKEN": "test_token"}):
        mock_github = MagicMock()
        mock_user = MagicMock()
        mock_user.login = "test_user"
        mock_github.get_user.return_value = mock_user

        # Create generator-like mock for get_github_token
        def mock_token_generator():
            yield Ok("test_token")
            return

        with patch("fcship.commands.github.github_utils.Github", return_value=mock_github):
            with patch("fcship.commands.github.github_utils.get_github_token", return_value=mock_token_generator()):
                result = None
                for step in get_github_client():
                    result = step

                assert result.is_ok()
                assert result.ok == mock_github


def test_get_github_client_auth_failure():
    """Test GitHub client creation with authentication failure."""
    with patch.dict("os.environ", {"GITHUB_TOKEN": "invalid_token"}):
        mock_github = MagicMock()
        mock_github.get_user.side_effect = GithubException(401, {"message": "Bad credentials"})

        with patch("fcship.commands.github.github_utils.Github", return_value=mock_github):
            result = None
            for step in get_github_client():
                result = step

            assert result.is_error()
            assert "GitHub authentication failed" in result.error


def test_get_github_client_general_error():
    """Test GitHub client creation with general error."""
    with patch.dict("os.environ", {"GITHUB_TOKEN": "test_token"}):
        mock_github = MagicMock()
        mock_github.get_user.side_effect = Exception("General error")

        with patch("fcship.commands.github.github_utils.Github", return_value=mock_github):
            result = None
            for step in get_github_client():
                result = step

            assert result.is_error()
            assert "Failed to create GitHub client" in result.error


def test_create_repository_success():
    """Test successful repository creation."""
    mock_github = MagicMock()
    mock_user = MagicMock()
    mock_repo = MagicMock()
    mock_repo.name = "test-repo"
    
    mock_user.create_repo.return_value = mock_repo
    mock_github.get_user.return_value = mock_user

    # Create generator-like mock for get_github_client
    def mock_client_generator():
        yield Ok(mock_github)
        return

    with patch("fcship.commands.github.github_utils.get_github_client", return_value=mock_client_generator()):
        result = None
        for step in create_repository("test-repo", "Test description", True, True, "mit", "Python"):
            result = step

        assert result.is_ok()
        assert result.ok == mock_repo
        mock_user.create_repo.assert_called_once_with(
            name="test-repo",
            description="Test description",
            private=True,
            auto_init=True,
            license_template="mit",
            gitignore_template="Python",
        )


def test_create_repository_github_exception():
    """Test repository creation with GitHub exception."""
    mock_github = MagicMock()
    mock_user = MagicMock()
    mock_user.create_repo.side_effect = GithubException(422, {"message": "Repository already exists"})
    mock_github.get_user.return_value = mock_user

    # Create generator-like mock for get_github_client
    def mock_client_generator():
        yield Ok(mock_github)
        return

    with patch("fcship.commands.github.github_utils.get_github_client", return_value=mock_client_generator()):
        result = None
        for step in create_repository("test-repo"):
            result = step

        assert result.is_error()
        assert "Failed to create repository" in result.error


def test_create_repository_general_exception():
    """Test repository creation with general exception."""
    mock_github = MagicMock()
    mock_user = MagicMock()
    mock_user.create_repo.side_effect = Exception("General error")
    mock_github.get_user.return_value = mock_user

    # Create generator-like mock for get_github_client
    def mock_client_generator():
        yield Ok(mock_github)
        return

    with patch("fcship.commands.github.github_utils.get_github_client", return_value=mock_client_generator()):
        result = None
        for step in create_repository("test-repo"):
            result = step

        assert result.is_error()
        assert "An error occurred" in result.error


def test_set_branch_protection_success():
    """Test successful branch protection setting."""
    mock_github = MagicMock()
    mock_user = MagicMock()
    mock_repo = MagicMock()
    mock_branch = MagicMock()
    
    mock_user.login = "test_user"
    mock_github.get_user.return_value = mock_user
    mock_github.get_repo.return_value = mock_repo
    mock_repo.get_branch.return_value = mock_branch

    # Create generator-like mock for get_github_client
    def mock_client_generator():
        yield Ok(mock_github)
        return

    with patch("fcship.commands.github.github_utils.get_github_client", return_value=mock_client_generator()):
        result = None
        for step in set_branch_protection("test-repo", "main", 2, True, ["status-check"], True):
            result = step

        assert result.is_ok()
        assert "Branch protection set for main" in result.ok
        mock_repo.get_branch.assert_called_once_with("main")
        mock_branch.edit_protection.assert_called_once_with(
            required_approving_review_count=2,
            enforce_admins=True,
            dismiss_stale_reviews=True,
            require_code_owner_reviews=False,
            required_linear_history=True,
            allow_force_pushes=False,
            allow_deletions=False,
            require_signed_commits=True,
            required_status_checks=["status-check"],
        )


def test_set_branch_protection_github_exception():
    """Test branch protection setting with GitHub exception."""
    mock_github = MagicMock()
    mock_user = MagicMock()
    mock_repo = MagicMock()
    
    mock_user.login = "test_user"
    mock_github.get_user.return_value = mock_user
    mock_github.get_repo.return_value = mock_repo
    mock_repo.get_branch.side_effect = GithubException(404, {"message": "Branch not found"})

    with patch("fcship.commands.github.github_utils.get_github_client") as mock_get_client:
        mock_get_client.return_value = Ok(mock_github)
        
        result = None
        for step in set_branch_protection("test-repo", "non-existent-branch"):
            result = step

        assert result.is_error()
        assert "Failed to set branch protection" in result.error


def test_set_branch_protection_general_exception():
    """Test branch protection setting with general exception."""
    mock_github = MagicMock()
    mock_user = MagicMock()
    
    mock_user.login = "test_user"
    mock_github.get_user.return_value = mock_user
    mock_github.get_repo.side_effect = Exception("General error")

    with patch("fcship.commands.github.github_utils.get_github_client") as mock_get_client:
        mock_get_client.return_value = Ok(mock_github)
        
        result = None
        for step in set_branch_protection("test-repo"):
            result = step

        assert result.is_error()
        assert "An error occurred" in result.error


def test_setup_repository_secret_success():
    """Test successful repository secret setup."""
    mock_github = MagicMock()
    mock_user = MagicMock()
    mock_repo = MagicMock()
    
    mock_user.login = "test_user"
    mock_github.get_user.return_value = mock_user
    mock_github.get_repo.return_value = mock_repo

    with patch("fcship.commands.github.github_utils.get_github_client") as mock_get_client:
        mock_get_client.return_value = Ok(mock_github)
        
        result = None
        for step in setup_repository_secret("test-repo", "SECRET_NAME", "secret_value"):
            result = step

        assert result.is_ok()
        assert "Secret SECRET_NAME created/updated" in result.ok
        mock_repo.create_secret.assert_called_once_with("SECRET_NAME", "secret_value")


def test_setup_repository_secret_github_exception():
    """Test repository secret setup with GitHub exception."""
    mock_github = MagicMock()
    mock_user = MagicMock()
    mock_repo = MagicMock()
    
    mock_user.login = "test_user"
    mock_github.get_user.return_value = mock_user
    mock_github.get_repo.return_value = mock_repo
    mock_repo.create_secret.side_effect = GithubException(422, {"message": "Invalid secret name"})

    with patch("fcship.commands.github.github_utils.get_github_client") as mock_get_client:
        mock_get_client.return_value = Ok(mock_github)
        
        result = None
        for step in setup_repository_secret("test-repo", "INVALID/SECRET", "secret_value"):
            result = step

        assert result.is_error()
        assert "Failed to set secret" in result.error


def test_setup_repository_secret_general_exception():
    """Test repository secret setup with general exception."""
    mock_github = MagicMock()
    mock_user = MagicMock()
    mock_repo = MagicMock()
    
    mock_user.login = "test_user"
    mock_github.get_user.return_value = mock_user
    mock_github.get_repo.return_value = mock_repo
    mock_repo.create_secret.side_effect = Exception("General error")

    with patch("fcship.commands.github.github_utils.get_github_client") as mock_get_client:
        mock_get_client.return_value = Ok(mock_github)
        
        result = None
        for step in setup_repository_secret("test-repo", "SECRET_NAME", "secret_value"):
            result = step

        assert result.is_error()
        assert "An error occurred" in result.error


def test_setup_environment_success():
    """Test successful environment setup."""
    mock_github = MagicMock()
    mock_user = MagicMock()
    mock_repo = MagicMock()
    mock_environment = MagicMock()
    mock_protection_rules = MagicMock()
    
    mock_user.login = "test_user"
    mock_github.get_user.return_value = mock_user
    mock_github.get_repo.return_value = mock_repo
    mock_repo.create_environment.return_value = mock_environment
    mock_environment.protection_rules = mock_protection_rules

    with patch("fcship.commands.github.github_utils.get_github_client") as mock_get_client:
        mock_get_client.return_value = Ok(mock_github)
        
        result = None
        for step in setup_environment("test-repo", "production", True, ["reviewer1", "reviewer2"]):
            result = step

        assert result.is_ok()
        assert "Environment production created" in result.ok
        mock_repo.create_environment.assert_called_once_with("production")
        mock_protection_rules.set_required_reviewers.assert_called_once_with(["reviewer1", "reviewer2"])


def test_setup_environment_no_approvals():
    """Test environment setup without approval requirements."""
    mock_github = MagicMock()
    mock_user = MagicMock()
    mock_repo = MagicMock()
    mock_environment = MagicMock()
    mock_protection_rules = MagicMock()
    
    mock_user.login = "test_user"
    mock_github.get_user.return_value = mock_user
    mock_github.get_repo.return_value = mock_repo
    mock_repo.create_environment.return_value = mock_environment
    mock_environment.protection_rules = mock_protection_rules

    with patch("fcship.commands.github.github_utils.get_github_client") as mock_get_client:
        mock_get_client.return_value = Ok(mock_github)
        
        result = None
        for step in setup_environment("test-repo", "development", False):
            result = step

        assert result.is_ok()
        assert "Environment development created" in result.ok
        mock_repo.create_environment.assert_called_once_with("development")
        mock_protection_rules.set_required_reviewers.assert_not_called()


def test_setup_environment_github_exception():
    """Test environment setup with GitHub exception."""
    mock_github = MagicMock()
    mock_user = MagicMock()
    mock_repo = MagicMock()
    
    mock_user.login = "test_user"
    mock_github.get_user.return_value = mock_user
    mock_github.get_repo.return_value = mock_repo
    mock_repo.create_environment.side_effect = GithubException(422, {"message": "Environment already exists"})

    with patch("fcship.commands.github.github_utils.get_github_client") as mock_get_client:
        mock_get_client.return_value = Ok(mock_github)
        
        result = None
        for step in setup_environment("test-repo", "production"):
            result = step

        assert result.is_error()
        assert "Failed to set up environment" in result.error


def test_setup_environment_general_exception():
    """Test environment setup with general exception."""
    mock_github = MagicMock()
    mock_user = MagicMock()
    mock_repo = MagicMock()
    
    mock_user.login = "test_user"
    mock_github.get_user.return_value = mock_user
    mock_github.get_repo.return_value = mock_repo
    mock_repo.create_environment.side_effect = Exception("General error")

    with patch("fcship.commands.github.github_utils.get_github_client") as mock_get_client:
        mock_get_client.return_value = Ok(mock_github)
        
        result = None
        for step in setup_environment("test-repo", "production"):
            result = step

        assert result.is_error()
        assert "An error occurred" in result.error


def test_create_workflow_file_new_file():
    """Test creating a new workflow file."""
    mock_github = MagicMock()
    mock_user = MagicMock()
    mock_repo = MagicMock()
    
    mock_user.login = "test_user"
    mock_github.get_user.return_value = mock_user
    mock_github.get_repo.return_value = mock_repo
    # Simulate file not found
    mock_repo.get_contents.side_effect = GithubException(404, {"message": "Not Found"})

    with patch("fcship.commands.github.github_utils.get_github_client") as mock_get_client:
        mock_get_client.return_value = Ok(mock_github)
        
        result = None
        for step in create_workflow_file("test-repo", "ci.yml", "workflow content"):
            result = step

        assert result.is_ok()
        assert "Workflow file ci.yml created/updated" in result.ok
        mock_repo.get_contents.assert_called_once_with(".github/workflows/ci.yml")
        mock_repo.create_file.assert_called_once_with(
            path=".github/workflows/ci.yml", 
            message="Create ci.yml workflow", 
            content="workflow content"
        )
        mock_repo.update_file.assert_not_called()


def test_create_workflow_file_update_existing():
    """Test updating an existing workflow file."""
    mock_github = MagicMock()
    mock_user = MagicMock()
    mock_repo = MagicMock()
    mock_file = MagicMock()
    
    mock_user.login = "test_user"
    mock_github.get_user.return_value = mock_user
    mock_github.get_repo.return_value = mock_repo
    mock_file.sha = "abc123"
    mock_repo.get_contents.return_value = mock_file

    with patch("fcship.commands.github.github_utils.get_github_client") as mock_get_client:
        mock_get_client.return_value = Ok(mock_github)
        
        result = None
        for step in create_workflow_file("test-repo", "ci.yml", "updated workflow content"):
            result = step

        assert result.is_ok()
        assert "Workflow file ci.yml created/updated" in result.ok
        mock_repo.get_contents.assert_called_once_with(".github/workflows/ci.yml")
        mock_repo.update_file.assert_called_once_with(
            path=".github/workflows/ci.yml", 
            message="Update ci.yml workflow", 
            content="updated workflow content",
            sha="abc123"
        )
        mock_repo.create_file.assert_not_called()


def test_create_workflow_file_github_exception():
    """Test workflow file creation with GitHub exception."""
    mock_github = MagicMock()
    mock_user = MagicMock()
    mock_repo = MagicMock()
    
    mock_user.login = "test_user"
    mock_github.get_user.return_value = mock_user
    mock_github.get_repo.return_value = mock_repo
    mock_repo.get_contents.side_effect = GithubException(404, {"message": "Not Found"})
    mock_repo.create_file.side_effect = GithubException(422, {"message": "Invalid file path"})

    with patch("fcship.commands.github.github_utils.get_github_client") as mock_get_client:
        mock_get_client.return_value = Ok(mock_github)
        
        result = None
        for step in create_workflow_file("test-repo", "invalid/path.yml", "workflow content"):
            result = step

        assert result.is_error()
        assert "Failed to create workflow file" in result.error


def test_create_workflow_file_general_exception():
    """Test workflow file creation with general exception."""
    mock_github = MagicMock()
    mock_user = MagicMock()
    mock_repo = MagicMock()
    
    mock_user.login = "test_user"
    mock_github.get_user.return_value = mock_user
    mock_github.get_repo.return_value = mock_repo
    mock_repo.get_contents.side_effect = Exception("General error")

    with patch("fcship.commands.github.github_utils.get_github_client") as mock_get_client:
        mock_get_client.return_value = Ok(mock_github)
        
        result = None
        for step in create_workflow_file("test-repo", "ci.yml", "workflow content"):
            result = step

        assert result.is_error()
        assert "An error occurred" in result.error


def test_create_dependabot_config_success():
    """Test successful dependabot config creation."""
    mock_github = MagicMock()
    mock_user = MagicMock()
    mock_repo = MagicMock()
    
    mock_user.login = "test_user"
    mock_github.get_user.return_value = mock_user
    mock_github.get_repo.return_value = mock_repo
    # Simulate file not found
    mock_repo.get_contents.side_effect = GithubException(404, {"message": "Not Found"})

    with patch("fcship.commands.github.github_utils.get_github_client") as mock_get_client:
        mock_get_client.return_value = Ok(mock_github)
        
        result = None
        for step in create_dependabot_config("test-repo", ["pip", "npm"]):
            result = step

        assert result.is_ok()
        assert "Dependabot configuration created/updated" in result.ok
        mock_repo.get_contents.assert_called_once_with(".github/dependabot.yml")
        mock_repo.create_file.assert_called_once()
        assert "package-ecosystem: \"pip\"" in mock_repo.create_file.call_args[1]["content"]
        assert "package-ecosystem: \"npm\"" in mock_repo.create_file.call_args[1]["content"]


def test_create_dependabot_config_default_pkg_manager():
    """Test dependabot config creation with default package manager."""
    mock_github = MagicMock()
    mock_user = MagicMock()
    mock_repo = MagicMock()
    
    mock_user.login = "test_user"
    mock_github.get_user.return_value = mock_user
    mock_github.get_repo.return_value = mock_repo
    # Simulate file not found
    mock_repo.get_contents.side_effect = GithubException(404, {"message": "Not Found"})

    with patch("fcship.commands.github.github_utils.get_github_client") as mock_get_client:
        mock_get_client.return_value = Ok(mock_github)
        
        result = None
        for step in create_dependabot_config("test-repo"):
            result = step

        assert result.is_ok()
        assert "Dependabot configuration created/updated" in result.ok
        mock_repo.create_file.assert_called_once()
        assert "package-ecosystem: \"pip\"" in mock_repo.create_file.call_args[1]["content"]


def test_create_dependabot_config_github_exception():
    """Test dependabot config creation with GitHub exception."""
    mock_github = MagicMock()
    mock_user = MagicMock()
    mock_repo = MagicMock()
    
    mock_user.login = "test_user"
    mock_github.get_user.return_value = mock_user
    mock_github.get_repo.return_value = mock_repo
    mock_repo.get_contents.side_effect = GithubException(404, {"message": "Not Found"})
    mock_repo.create_file.side_effect = GithubException(422, {"message": "Invalid file path"})

    with patch("fcship.commands.github.github_utils.get_github_client") as mock_get_client:
        mock_get_client.return_value = Ok(mock_github)
        
        result = None
        for step in create_dependabot_config("test-repo"):
            result = step

        assert result.is_error()
        assert "Failed to create dependabot configuration" in result.error

def test_setup_workflow_templates_success():
    """Test successful workflow templates setup."""
    with patch("fcship.commands.github.github_utils.create_workflow_file") as mock_create_workflow:
        # Return success for all workflow files
        mock_create_workflow.side_effect = [
            Ok("CI workflow created"),
            Ok("Release workflow created"),
            Ok("Bump version workflow created"),
        ]
        
        result = None
        for step in setup_workflow_templates("test-repo"):
            result = step

        assert result.is_ok()
        assert result.ok["ci.yml"] is True
        assert result.ok["release.yml"] is True
        assert result.ok["bump-version.yml"] is True
        assert mock_create_workflow.call_count == 3


def test_setup_workflow_templates_partial_success():
    """Test workflow templates setup with partial success."""
    with patch("fcship.commands.github.github_utils.create_workflow_file") as mock_create_workflow:
        # Return success for CI and failure for others
        mock_create_workflow.side_effect = [
            Ok("CI workflow created"),
            Error("Failed to create release workflow"),
            Error("Failed to create bump version workflow"),
        ]
        
        result = None
        for step in setup_workflow_templates("test-repo"):
            result = step

        assert result.is_ok()
        assert result.ok["ci.yml"] is True
        assert result.ok["release.yml"] is False
        assert result.ok["bump-version.yml"] is False
        assert mock_create_workflow.call_count == 3

"""Tests for GitHub API utilities to increase coverage."""

import os
from unittest.mock import MagicMock, patch

from expression import Error, Ok, Result, effect
from github.GithubException import GithubException

import fcship.commands.github.github_utils as github_utils
from fcship.tui.display import DisplayError
from fcship.tui.input import get_user_input


def test_coverage_get_github_token():
    """Test GitHub token retrieval for coverage."""
    # Test getting token from environment variable
    with patch.dict("os.environ", {"GITHUB_TOKEN": "test_token"}):
        result = None
        for step in github_utils.get_github_token():
            result = step
        assert result.is_ok()
        assert result.ok == "test_token"

    # Define a function that returns the mocked user input
    @effect.result[str, DisplayError]()
    def mock_user_input_success(message):
        yield Ok("user_input_token")
        return

    @effect.result[str, DisplayError]()
    def mock_user_input_empty(message):
        yield Ok("")
        return
    
    @effect.result[str, DisplayError]()
    def mock_user_input_error(message):
        yield Error(DisplayError.Input("Failed to get input", ""))
        return

    # Test getting token from user input (success)
    with patch.dict("os.environ", {}, clear=True):
        with patch("fcship.commands.github.github_utils.get_user_input", mock_user_input_success):
            result = None
            for step in github_utils.get_github_token():
                result = step
            assert result.is_ok()
            assert result.ok == "user_input_token"

    # Test getting token from user input (empty input)
    with patch.dict("os.environ", {}, clear=True):
        with patch("fcship.commands.github.github_utils.get_user_input", mock_user_input_empty):
            result = None
            for step in github_utils.get_github_token():
                result = step
            assert result.is_error()
            assert "GitHub token is required" in result.error

    # Test getting token from user input (error)
    with patch.dict("os.environ", {}, clear=True):
        with patch("fcship.commands.github.github_utils.get_user_input", mock_user_input_error):
            result = None
            for step in github_utils.get_github_token():
                result = step
            assert result.is_error()


def test_coverage_get_github_client():
    """Test GitHub client creation for coverage."""
    # Define mock token functions
    @effect.result[str, str]()
    def mock_token_success():
        yield Ok("test_token")
        return
    
    @effect.result[str, str]()
    def mock_token_error():
        yield Error("Token error")
        return
    
    # Test successful client creation
    mock_github = MagicMock()
    mock_user = MagicMock()
    mock_user.login = "test_user"
    mock_github.get_user.return_value = mock_user

    with patch("fcship.commands.github.github_utils.get_github_token", return_value=mock_token_success()):
        with patch("fcship.commands.github.github_utils.Github", return_value=mock_github):
            result = None
            for step in github_utils.get_github_client():
                result = step
            assert result.is_ok()
            assert result.ok == mock_github

    # Test token retrieval failure
    with patch("fcship.commands.github.github_utils.get_github_token", return_value=mock_token_error()):
        result = None
        for step in github_utils.get_github_client():
            result = step
        assert result.is_error()
        assert result.error == "Token error"

    # Test GitHub authentication failure
    mock_github = MagicMock()
    mock_github.get_user.side_effect = GithubException(401, {"message": "Bad credentials"})
    
    with patch("fcship.commands.github.github_utils.get_github_token", return_value=mock_token_success()):
        with patch("fcship.commands.github.github_utils.Github", return_value=mock_github):
            result = None
            for step in github_utils.get_github_client():
                result = step
            assert result.is_error()
            assert "GitHub authentication failed" in result.error

    # Test general exception
    mock_github = MagicMock()
    mock_github.get_user.side_effect = Exception("General error")
    
    with patch("fcship.commands.github.github_utils.get_github_token", return_value=mock_token_success()):
        with patch("fcship.commands.github.github_utils.Github", return_value=mock_github):
            result = None
            for step in github_utils.get_github_client():
                result = step
            assert result.is_error()
            assert "Failed to create GitHub client" in result.error


def test_coverage_create_repository():
    """Test repository creation for coverage."""
    # Define mock client functions
    mock_github = MagicMock()
    mock_user = MagicMock()
    mock_repo = MagicMock()
    mock_user.create_repo.return_value = mock_repo
    mock_github.get_user.return_value = mock_user
    
    @effect.result[github_utils.Github, str]()
    def mock_client_success():
        yield Ok(mock_github)
        return
    
    @effect.result[github_utils.Github, str]()
    def mock_client_error():
        yield Error("Client error")
        return
    
    # Test successful repository creation
    with patch("fcship.commands.github.github_utils.get_github_client", return_value=mock_client_success()):
        result = None
        for step in github_utils.create_repository(
            "test-repo", "Test description", True, True, "mit", "Python"
        ):
            result = step
        assert result.is_ok()
        assert result.ok == mock_repo
        mock_user.create_repo.assert_called_once_with(
            name="test-repo",
            description="Test description",
            private=True,
            auto_init=True,
            license_template="mit",
            gitignore_template="Python",
        )

    # Test client creation failure
    with patch("fcship.commands.github.github_utils.get_github_client", return_value=mock_client_error()):
        result = None
        for step in github_utils.create_repository("test-repo"):
            result = step
        assert result.is_error()
        assert result.error == "Client error"

    # Test GitHub exception
    mock_github_ex = MagicMock()
    mock_user_ex = MagicMock()
    mock_user_ex.create_repo.side_effect = GithubException(422, {"message": "Repository already exists"})
    mock_github_ex.get_user.return_value = mock_user_ex
    
    @effect.result[github_utils.Github, str]()
    def mock_client_github_ex():
        yield Ok(mock_github_ex)
        return
    
    with patch("fcship.commands.github.github_utils.get_github_client", return_value=mock_client_github_ex()):
        result = None
        for step in github_utils.create_repository("test-repo"):
            result = step
        assert result.is_error()
        assert "Failed to create repository" in result.error

    # Test general exception
    mock_github_gen_ex = MagicMock()
    mock_user_gen_ex = MagicMock()
    mock_user_gen_ex.create_repo.side_effect = Exception("General error")
    mock_github_gen_ex.get_user.return_value = mock_user_gen_ex
    
    @effect.result[github_utils.Github, str]()
    def mock_client_gen_ex():
        yield Ok(mock_github_gen_ex)
        return
    
    with patch("fcship.commands.github.github_utils.get_github_client", return_value=mock_client_gen_ex()):
        result = None
        for step in github_utils.create_repository("test-repo"):
            result = step
        assert result.is_error()
        assert "An error occurred" in result.error
def test_coverage_set_branch_protection():
    """Test branch protection settings for coverage."""
    # Define mock client function
    mock_github = MagicMock()
    mock_user = MagicMock()
    mock_repo = MagicMock()
    mock_branch = MagicMock()
    
    mock_user.login = "test_user"
    mock_github.get_user.return_value = mock_user
    mock_github.get_repo.return_value = mock_repo
    mock_repo.get_branch.return_value = mock_branch
    
    @effect.result[github_utils.Github, str]()
    def mock_client_success():
        yield Ok(mock_github)
        return
    
    @effect.result[github_utils.Github, str]()
    def mock_client_error():
        yield Error("Client error")
        return
    
    # Test successful branch protection
    with patch("fcship.commands.github.github_utils.get_github_client", return_value=mock_client_success()):
        result = None
        for step in github_utils.set_branch_protection(
            "test-repo", "main", 2, True, ["status-check"], True
        ):
            result = step
        assert result.is_ok()
        assert "Branch protection set for main" in result.ok
        mock_github.get_repo.assert_called_with("test_user/test-repo")
        mock_repo.get_branch.assert_called_with("main")
        mock_branch.edit_protection.assert_called_once()

    # Test client error
    with patch("fcship.commands.github.github_utils.get_github_client", return_value=mock_client_error()):
        result = None
        for step in github_utils.set_branch_protection("test-repo"):
            result = step
        assert result.is_error()
        assert result.error == "Client error"

    # Test GitHub exception
    mock_github_ex = MagicMock()
    mock_user_ex = MagicMock()
    mock_repo_ex = MagicMock()
    
    mock_user_ex.login = "test_user"
    mock_github_ex.get_user.return_value = mock_user_ex
    mock_github_ex.get_repo.return_value = mock_repo_ex
    mock_repo_ex.get_branch.side_effect = GithubException(404, {"message": "Branch not found"})
    
    @effect.result[github_utils.Github, str]()
    def mock_client_github_ex():
        yield Ok(mock_github_ex)
        return
    
    with patch("fcship.commands.github.github_utils.get_github_client", return_value=mock_client_github_ex()):
        result = None
        for step in github_utils.set_branch_protection("test-repo", "non-existent-branch"):
            result = step
        assert result.is_error()
        assert "Failed to set branch protection" in result.error

    # Test general exception
    mock_github_gen_ex = MagicMock()
    mock_user_gen_ex = MagicMock()
    
    mock_user_gen_ex.login = "test_user"
    mock_github_gen_ex.get_user.return_value = mock_user_gen_ex
    mock_github_gen_ex.get_repo.side_effect = Exception("General error")
    
    @effect.result[github_utils.Github, str]()
    def mock_client_gen_ex():
        yield Ok(mock_github_gen_ex)
        return
    
    with patch("fcship.commands.github.github_utils.get_github_client", return_value=mock_client_gen_ex()):
        result = None
        for step in github_utils.set_branch_protection("test-repo"):
            result = step
        assert result.is_error()
        assert "An error occurred" in result.error


def test_coverage_create_workflow_file():
    """Test workflow file creation for coverage."""
    # Define mock client function
    mock_github = MagicMock()
    mock_user = MagicMock()
    mock_repo = MagicMock()
    
    mock_user.login = "test_user"
    mock_github.get_user.return_value = mock_user
    mock_github.get_repo.return_value = mock_repo
    # File doesn't exist
    mock_repo.get_contents.side_effect = GithubException(404, {"message": "Not Found"})
    
    @effect.result[github_utils.Github, str]()
    def mock_client_success():
        yield Ok(mock_github)
        return
    
    # Test creating a new workflow file
    with patch("fcship.commands.github.github_utils.get_github_client", return_value=mock_client_success()):
        result = None
        for step in github_utils.create_workflow_file("test-repo", "ci.yml", "workflow content"):
            result = step
        assert result.is_ok()
        assert "Workflow file ci.yml created/updated" in result.ok
        mock_repo.get_contents.assert_called_with(".github/workflows/ci.yml")
        mock_repo.create_file.assert_called_once()

    # Test updating an existing workflow file
    mock_github_update = MagicMock()
    mock_user_update = MagicMock()
    mock_repo_update = MagicMock()
    mock_file = MagicMock()
    
    mock_user_update.login = "test_user"
    mock_github_update.get_user.return_value = mock_user_update
    mock_github_update.get_repo.return_value = mock_repo_update
    mock_file.sha = "abc123"
    mock_repo_update.get_contents.return_value = mock_file
    
    @effect.result[github_utils.Github, str]()
    def mock_client_update():
        yield Ok(mock_github_update)
        return
    
    with patch("fcship.commands.github.github_utils.get_github_client", return_value=mock_client_update()):
        result = None
        for step in github_utils.create_workflow_file("test-repo", "ci.yml", "updated content"):
            result = step
        assert result.is_ok()
        assert "Workflow file ci.yml created/updated" in result.ok
        mock_repo_update.update_file.assert_called_once()

