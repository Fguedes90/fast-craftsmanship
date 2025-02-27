from github import Github
from expression import Ok, Error, Result, effect
from fcship.tui.display import (
    DisplayContext,
    success_message,
    error_message,
    warning_message,
    display_rule
)
from fcship.tui.tables import (
    TableRow,
    create_multi_column_table,
    display_table
)
from rich.console import Console

@effect.result[None, str]()
def list_repositories(token: str, display_ctx: DisplayContext = None):
    """Lists all repositories for the authenticated user in a formatted table."""
    if display_ctx is None:
        display_ctx = DisplayContext(console=Console())
        
    try:
        g = Github(token)
        user = g.get_user()
        
        # Display header
        yield from display_rule(display_ctx, "GitHub Repositories")
        
        # Prepare table data
        headers = ["Name", "Description", "Stars", "Language", "Private"]
        rows = []
        
        for repo in user.get_repos():
            rows.append([
                repo.name,
                repo.description or "",
                str(repo.stargazers_count),
                repo.language or "N/A",
                "Yes" if repo.private else "No"
            ])
            
        # Create and display table
        table_result = yield from create_multi_column_table(
            "Your Repositories",
            headers,
            rows
        )
        if table_result.is_ok():
            yield from display_table(table_result.ok)
            yield from success_message(display_ctx, f"Found {len(rows)} repositories")
        else:
            yield from error_message(display_ctx, "Failed to create repository table")
            
    except Exception as e:
        yield from error_message(display_ctx, f"Error listing repositories", details=str(e))
        return Error(str(e))
    
    return Ok(None)

@effect.result[None, str]()
def delete_repository(token: str, repo_name: str, display_ctx: DisplayContext = None):
    """Deletes a repository if the name matches exactly."""
    if display_ctx is None:
        display_ctx = DisplayContext(console=Console())
        
    try:
        g = Github(token)
        user = g.get_user()
        
        yield from warning_message(display_ctx, f"Attempting to delete repository '{repo_name}'")
        
        try:
            repo = user.get_repo(repo_name)
            repo.delete()
            yield from success_message(display_ctx, f"Repository '{repo_name}' deleted successfully")
        except Exception as e:
            yield from error_message(display_ctx, f"Error deleting repository '{repo_name}'", details=str(e))
            return Error(str(e))
            
    except Exception as e:
        yield from error_message(display_ctx, "Failed to initialize GitHub client", details=str(e))
        return Error(str(e))
        
    return Ok(None)

@effect.result[None, str]()
def list_branches(token: str, repo_name: str, display_ctx: DisplayContext = None):
    """Lists all branches of a given repository in a formatted table."""
    if display_ctx is None:
        display_ctx = DisplayContext(console=Console())
        
    try:
        g = Github(token)
        user = g.get_user()
        
        try:
            repo = user.get_repo(repo_name)
            
            # Display header
            yield from display_rule(display_ctx, f"Branches in {repo_name}")
            
            # Prepare table data
            headers = ["Branch Name", "Last Commit", "Protected"]
            rows = []
            
            for branch in repo.get_branches():
                rows.append([
                    branch.name,
                    branch.commit.sha[:7],
                    "Yes" if branch.protected else "No"
                ])
                
            # Create and display table
            table_result = yield from create_multi_column_table(
                f"Branches in {repo_name}",
                headers,
                rows
            )
            if table_result.is_ok():
                yield from display_table(table_result.ok)
                yield from success_message(display_ctx, f"Found {len(rows)} branches")
            else:
                yield from error_message(display_ctx, "Failed to create branch table")
                
        except Exception as e:
            yield from error_message(display_ctx, f"Error listing branches for repository '{repo_name}'", details=str(e))
            return Error(str(e))
            
    except Exception as e:
        yield from error_message(display_ctx, "Failed to initialize GitHub client", details=str(e))
        return Error(str(e))
        
    return Ok(None)

@effect.result[None, str]()
def list_issues(token: str, repo_name: str, display_ctx: DisplayContext = None):
    """Lists all open issues of a given repository in a formatted table."""
    if display_ctx is None:
        display_ctx = DisplayContext(console=Console())
        
    try:
        g = Github(token)
        user = g.get_user()
        
        try:
            repo = user.get_repo(repo_name)
            
            # Display header
            yield from display_rule(display_ctx, f"Open Issues in {repo_name}")
            
            # Prepare table data
            headers = ["Number", "Title", "Author", "Labels", "Comments"]
            rows = []
            
            for issue in repo.get_issues(state='open'):
                labels = ", ".join([label.name for label in issue.labels]) or "None"
                rows.append([
                    f"#{issue.number}",
                    issue.title,
                    issue.user.login,
                    labels,
                    str(issue.comments)
                ])
                
            # Create and display table
            table_result = yield from create_multi_column_table(
                f"Open Issues in {repo_name}",
                headers,
                rows
            )
            if table_result.is_ok():
                yield from display_table(table_result.ok)
                yield from success_message(display_ctx, f"Found {len(rows)} open issues")
            else:
                yield from error_message(display_ctx, "Failed to create issues table")
                
        except Exception as e:
            yield from error_message(display_ctx, f"Error listing issues for repository '{repo_name}'", details=str(e))
            return Error(str(e))
            
    except Exception as e:
        yield from error_message(display_ctx, "Failed to initialize GitHub client", details=str(e))
        return Error(str(e))
        
    return Ok(None)

@effect.result[None, str]()
def download_issue_body(token: str, repo_name: str, issue_number: int, display_ctx: DisplayContext = None):
    """Downloads and displays the body of a specific issue from a given repository."""
    if display_ctx is None:
        display_ctx = DisplayContext(console=Console())
        
    try:
        g = Github(token)
        user = g.get_user()
        
        try:
            repo = user.get_repo(repo_name)
            issue = repo.get_issue(number=issue_number)
            
            # Display header
            yield from display_rule(display_ctx, f"Issue #{issue_number} from {repo_name}")
            
            # Display issue details
            yield from success_message(display_ctx, f"Title: {issue.title}")
            yield from success_message(display_ctx, f"Author: {issue.user.login}")
            yield from success_message(display_ctx, f"Created: {issue.created_at}")
            yield from success_message(display_ctx, f"Status: {issue.state}")
            
            # Display issue body
            yield from display_rule(display_ctx, "Issue Body")
            if issue.body:
                yield from success_message(display_ctx, issue.body)
            else:
                yield from warning_message(display_ctx, "No description provided")
                
        except Exception as e:
            yield from error_message(display_ctx, f"Error downloading issue #{issue_number} from repository '{repo_name}'", details=str(e))
            return Error(str(e))
            
    except Exception as e:
        yield from error_message(display_ctx, "Failed to initialize GitHub client", details=str(e))
        return Error(str(e))
        
    return Ok(None)

@effect.result[None, str]()
def create_pull_request(token: str, repo_name: str, title: str, body: str, head: str, base: str, display_ctx: DisplayContext = None):
    """Creates a pull request in a given repository with visual feedback."""
    if display_ctx is None:
        display_ctx = DisplayContext(console=Console())
        
    try:
        g = Github(token)
        user = g.get_user()
        
        try:
            repo = user.get_repo(repo_name)
            
            # Display header
            yield from display_rule(display_ctx, f"Creating Pull Request in {repo_name}")
            
            # Show PR details before creation
            yield from success_message(display_ctx, f"Title: {title}")
            yield from success_message(display_ctx, f"From: {head} → {base}")
            
            # Create PR
            pull = repo.create_pull(title=title, body=body, head=head, base=base)
            
            # Display success message with PR details
            yield from success_message(display_ctx, "Pull request created successfully!")
            yield from success_message(display_ctx, f"PR #{pull.number}: {pull.html_url}")
            
        except Exception as e:
            yield from error_message(display_ctx, f"Error creating pull request in repository '{repo_name}'", details=str(e))
            return Error(str(e))
            
    except Exception as e:
        yield from error_message(display_ctx, "Failed to initialize GitHub client", details=str(e))
        return Error(str(e))
        
    return Ok(None)
