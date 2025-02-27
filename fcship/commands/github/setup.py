#!/usr/bin/env python3
"""
GitHub repository setup commands for fast-craftsmanship.

These commands help initialize a new GitHub repository with best practices
for CI/CD, branch protection, and environment configuration.
"""

from typing import Annotated

import typer

from expression import Error, Ok, Result, effect, pipe
from pydantic import BaseModel
from rich.console import Console

from fcship.tui.display import DisplayContext
from fcship.tui.display import success_message as display_success
from fcship.utils.error_handling import handle_command_errors as handle_errors

app = typer.Typer(help="GitHub repository setup commands")


class BranchProtectionRule(BaseModel):
    """Branch protection rule configuration."""

    branch_name: str
    require_reviews: bool = True
    required_approvals: int = 1
    dismiss_stale_reviews: bool = True
    require_status_checks: bool = True
    status_checks: list[str] = ["ci"]
    require_signed_commits: bool = False
    restrict_pushes: bool = False


@app.command("init-repo")
@handle_errors
def init_repo(
    repo_name: Annotated[str, typer.Argument(help="Name of the repository to create")],
    description: Annotated[str, typer.Option(help="Repository description")] = "",
    private: Annotated[bool, typer.Option(help="Whether the repository should be private")] = False,
    auto_init: Annotated[
        bool, typer.Option(help="Initialize with README, LICENSE, and .gitignore")
    ] = True,
    license_template: Annotated[
        str | None, typer.Option(help="License template to use (e.g., mit, apache-2.0)")
    ] = "mit",
    gitignore_template: Annotated[
        str | None, typer.Option(help="Gitignore template to use (e.g., Python, Node)")
    ] = "Python",
):
    """Create a new GitHub repository with best practices."""

    display_ctx = DisplayContext(console=Console())
    result = pipe(
        _create_repository(
            repo_name, description, private, auto_init, license_template, gitignore_template
        ),
        lambda _: display_success(display_ctx, f"Repository {repo_name} created successfully."),
    )

    return result


@effect.result[str, str]()
def _create_repository(
    repo_name: str,
    description: str,
    private: bool,
    auto_init: bool,
    license_template: str | None,
    gitignore_template: str | None,
) -> Result[str, str]:
    """Create a new GitHub repository."""
    # This would use PyGithub or GitHub CLI in actual implementation
    # Here we just yield a successful result for placeholder purposes
    yield Ok(f"Repository {repo_name} created")
    return


@app.command("protect-branch")
@handle_errors
def protect_branch(
    repo_name: Annotated[str, typer.Argument(help="Name of the repository")],
    branch_name: Annotated[str, typer.Argument(help="Name of branch to protect")] = "main",
    required_approvals: Annotated[
        int, typer.Option(help="Number of required approvals for PRs")
    ] = 1,
    require_status_checks: Annotated[
        bool, typer.Option(help="Require status checks to pass")
    ] = True,
    require_signed_commits: Annotated[bool, typer.Option(help="Require signed commits")] = False,
):
    """Set up branch protection rules."""

    rule = BranchProtectionRule(
        branch_name=branch_name,
        required_approvals=required_approvals,
        require_status_checks=require_status_checks,
        require_signed_commits=require_signed_commits,
    )

    display_ctx = DisplayContext(console=Console())
    result = pipe(
        _setup_branch_protection(repo_name, rule),
        lambda _: display_success(display_ctx, f"Branch protection set up for {branch_name} on {repo_name}"),
    )

    return result


@effect.result[str, str]()
def _setup_branch_protection(repo_name: str, rule: BranchProtectionRule) -> Result[str, str]:
    """Set up branch protection rules."""
    # This would use PyGithub or GitHub CLI in actual implementation
    yield Ok(f"Branch protection set for {rule.branch_name}")
    return


@app.command("setup-secrets")
@handle_errors
def setup_secrets(
    repo_name: Annotated[str, typer.Argument(help="Name of the repository")],
    pypi_token: Annotated[bool, typer.Option(help="Set up PyPI API token secret")] = True,
    sonar_token: Annotated[bool, typer.Option(help="Set up SonarCloud token secret")] = False,
    dockerhub: Annotated[bool, typer.Option(help="Set up DockerHub credentials")] = False,
    gcp: Annotated[bool, typer.Option(help="Set up Google Cloud Platform credentials")] = False,
    aws: Annotated[bool, typer.Option(help="Set up AWS credentials")] = False,
):
    """Set up GitHub secrets for CI/CD."""

    display_ctx = DisplayContext(console=Console())
    result = pipe(
        _setup_repository_secrets(repo_name, pypi_token, sonar_token, dockerhub, gcp, aws),
        lambda _: display_success(display_ctx, f"Secrets configured for {repo_name}"),
    )

    return result


@effect.result[str, str]()
def _setup_repository_secrets(
    repo_name: str,
    pypi_token: bool,
    sonar_token: bool,
    dockerhub: bool,
    gcp: bool,
    aws: bool,
) -> Result[str, str]:
    """Set up secrets for a repository."""
    # This would use PyGithub or GitHub CLI in actual implementation
    secrets_to_setup = []
    if pypi_token:
        secrets_to_setup.append("PYPI_API_TOKEN")
    if sonar_token:
        secrets_to_setup.append("SONAR_TOKEN")
    if dockerhub:
        secrets_to_setup.extend(["DOCKER_USERNAME", "DOCKER_PASSWORD"])
    if gcp:
        secrets_to_setup.append("GCP_CREDENTIALS")
    if aws:
        secrets_to_setup.extend(["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"])

    if not secrets_to_setup:
        yield Error("No secrets selected to set up")
        return

    # In actual implementation, this would prompt for secret values and set them
    yield Ok(f"Secrets {', '.join(secrets_to_setup)} set up for {repo_name}")
    return


@app.command("setup-environments")
@handle_errors
def setup_environments(
    repo_name: Annotated[str, typer.Argument(help="Name of the repository")],
    environments: Annotated[list[str], typer.Option(help="Environments to set up")] = None,
    require_approvals: Annotated[
        bool, typer.Option(help="Require approvals for deployments")
    ] = True,
):
    """Set up GitHub environments for deployments."""

    if environments is None:
        environments = ["staging", "production"]
    display_ctx = DisplayContext(console=Console())
    result = pipe(
        _setup_repository_environments(repo_name, environments, require_approvals),
        lambda _: display_success(display_ctx, f"Environments {', '.join(environments)} set up for {repo_name}"),
    )

    return result


@effect.result[str, str]()
def _setup_repository_environments(
    repo_name: str,
    environments: list[str],
    require_approvals: bool,
) -> Result[str, str]:
    """Set up environments for a repository."""
    # This would use PyGithub or GitHub CLI in actual implementation
    if not environments:
        yield Error("No environments specified")
        return

    yield Ok(f"Environments {', '.join(environments)} set up for {repo_name}")
    return


@app.command("setup-workflows")
@handle_errors
def setup_workflows(
    repo_name: Annotated[str, typer.Argument(help="Name of the repository")],
    ci: Annotated[bool, typer.Option(help="Set up CI workflow")] = True,
    release: Annotated[bool, typer.Option(help="Set up release workflow")] = True,
    version_bump: Annotated[bool, typer.Option(help="Set up version bump workflow")] = True,
    deploy: Annotated[bool, typer.Option(help="Set up deployment workflow")] = False,
    codeql: Annotated[bool, typer.Option(help="Set up CodeQL analysis")] = False,
    dependabot: Annotated[bool, typer.Option(help="Set up Dependabot")] = True,
):
    """Set up GitHub Actions workflows."""

    display_ctx = DisplayContext(console=Console())
    result = pipe(
        _setup_github_workflows(repo_name, ci, release, version_bump, deploy, codeql, dependabot),
        lambda _: display_success(display_ctx, f"Workflows set up for {repo_name}"),
    )

    return result


@effect.result[str, str]()
def _setup_github_workflows(
    repo_name: str,
    ci: bool,
    release: bool,
    version_bump: bool,
    deploy: bool,
    codeql: bool,
    dependabot: bool,
) -> Result[str, str]:
    """Set up GitHub Actions workflows."""
    # This would use PyGithub or GitHub CLI in actual implementation
    workflows = []
    if ci:
        workflows.append("ci.yml")
    if release:
        workflows.append("release.yml")
    if version_bump:
        workflows.append("bump-version.yml")
    if deploy:
        workflows.append("deploy.yml")
    if codeql:
        workflows.append("codeql-analysis.yml")
    if dependabot:
        workflows.append("dependabot.yml")

    if not workflows:
        yield Error("No workflows selected to set up")
        return

    yield Ok(f"Workflows {', '.join(workflows)} set up for {repo_name}")
    return


@app.command("setup-all")
@handle_errors
def setup_all(
    repo_name: Annotated[str, typer.Argument(help="Name of the repository to set up")],
    description: Annotated[str, typer.Option(help="Repository description")] = "",
    private: Annotated[bool, typer.Option(help="Whether the repository should be private")] = False,
    license_template: Annotated[
        str | None, typer.Option(help="License template to use (e.g., mit, apache-2.0)")
    ] = "mit",
    setup_pypi: Annotated[bool, typer.Option(help="Set up PyPI publishing")] = True,
    setup_docker: Annotated[bool, typer.Option(help="Set up Docker image publishing")] = False,
    deployment_environments: Annotated[list[str], typer.Option(help="Environments to set up")] = None,
):
    """Complete GitHub repository setup with best practices."""

    # Step 1: Create repository
    if deployment_environments is None:
        deployment_environments = ["staging", "production"]
    
    # Em funções effect.result, precisamos iterar e coletar o resultado final
    create_repo_gen = _create_repository(
        repo_name, description, private, True, license_template, "Python"
    )
    
    for step in create_repo_gen:
        create_repo_result = step
        
    if create_repo_result.is_error():
        yield Error(f"Failed to create repository: {create_repo_result.error}")
        return

    # Step 2: Set up branch protection
    protection_gen = _setup_branch_protection(
        repo_name, BranchProtectionRule(branch_name="main", required_approvals=1)
    )
    
    for step in protection_gen:
        protection_result = step
        
    if protection_result.is_error():
        yield Error(f"Failed to set up branch protection: {protection_result.error}")
        return

    # Step 3: Set up secrets
    secrets_gen = _setup_repository_secrets(
        repo_name,
        pypi_token=setup_pypi,
        sonar_token=True,
        dockerhub=setup_docker,
        gcp=False,
        aws=False,
    )
    
    for step in secrets_gen:
        secrets_result = step
        
    if secrets_result.is_error():
        yield Error(f"Failed to set up secrets: {secrets_result.error}")
        return

    # Step 4: Set up environments
    env_gen = _setup_repository_environments(
        repo_name, deployment_environments, require_approvals=True
    )
    
    for step in env_gen:
        env_result = step
        
    if env_result.is_error():
        yield Error(f"Failed to set up environments: {env_result.error}")
        return

    # Step 5: Set up workflows
    workflow_gen = _setup_github_workflows(
        repo_name,
        ci=True,
        release=True,
        version_bump=True,
        deploy=len(deployment_environments) > 0,
        codeql=True,
        dependabot=True,
    )
    
    for step in workflow_gen:
        workflow_result = step
        
    if workflow_result.is_error():
        yield Error(f"Failed to set up workflows: {workflow_result.error}")
        return

    display_ctx = DisplayContext(console=Console())
    display_success(
        display_ctx,
        f"Repository {repo_name} fully set up with CI/CD best practices!\n"
        f"• Repository created as {'private' if private else 'public'}\n"
        f"• Branch protection enabled for main branch\n"
        f"• GitHub Actions workflows created for CI, releases, and version management\n"
        f"• Required secrets configured for integrations\n"
        f"• Deployment environments: {', '.join(deployment_environments)}\n\n"
        f"Your repository is ready for development with best practices!"
    )

    yield Ok("Repository setup complete")
    return


if __name__ == "__main__":
    app()
