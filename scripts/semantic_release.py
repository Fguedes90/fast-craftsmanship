#!/usr/bin/env python3
"""
Semantic Version bump utility for fast-craftsmanship.

This script parses commit messages and determines the appropriate version
bump (major, minor, patch) based on conventional commit messages.

Commit types that trigger version bumps:
- feat: -> minor version bump
- fix: -> patch version bump
- BREAKING CHANGE: -> major version bump

Usage:
    python semantic_release.py [--dry-run]
"""

import argparse
import re
import subprocess
import sys
from enum import Enum, auto
from typing import List, Optional, Tuple


class BumpType(Enum):
    NONE = auto()
    PATCH = auto()
    MINOR = auto()
    MAJOR = auto()


def get_latest_tag() -> Optional[str]:
    """Get the latest tag from git."""
    try:
        tag = subprocess.check_output(
            ["git", "describe", "--tags", "--abbrev=0"], 
            stderr=subprocess.DEVNULL, 
            text=True
        ).strip()
        return tag
    except subprocess.CalledProcessError:
        # No tags exist yet
        return None


def get_commits_since_tag(tag: Optional[str]) -> List[str]:
    """Get all commits since the given tag."""
    if tag:
        cmd = ["git", "log", f"{tag}..HEAD", "--pretty=format:%s"]
    else:
        cmd = ["git", "log", "--pretty=format:%s"]
    
    return subprocess.check_output(cmd, text=True).splitlines()


def determine_bump_type(commits: List[str]) -> BumpType:
    """
    Determine what kind of version bump is needed based on commit messages.
    
    Rules:
    - If any commit contains "BREAKING CHANGE:", bump major
    - If any commit starts with "feat:", bump minor
    - If any commit starts with "fix:", bump patch
    - Otherwise, no bump
    """
    bump = BumpType.NONE
    
    for commit in commits:
        if "BREAKING CHANGE:" in commit:
            return BumpType.MAJOR
        
        if commit.startswith("feat:"):
            bump = max(bump, BumpType.MINOR)
        elif commit.startswith("fix:"):
            bump = max(bump, BumpType.PATCH)
    
    return bump


def get_current_version() -> str:
    """Get the current version from pyproject.toml."""
    with open("pyproject.toml", "r") as f:
        content = f.read()
    
    match = re.search(r'version = ["\']([^"\']+)["\']', content)
    if not match:
        raise Exception("Could not find version in pyproject.toml")
    
    return match.group(1)


def bump_version(current: str, bump_type: BumpType) -> str:
    """Bump the version according to semantic versioning rules."""
    if bump_type == BumpType.NONE:
        return current
    
    major, minor, patch = map(int, current.split("."))
    
    if bump_type == BumpType.MAJOR:
        return f"{major + 1}.0.0"
    elif bump_type == BumpType.MINOR:
        return f"{major}.{minor + 1}.0"
    elif bump_type == BumpType.PATCH:
        return f"{major}.{minor}.{patch + 1}"
    
    return current


def update_version_in_files(new_version: str) -> None:
    """Update version in pyproject.toml."""
    with open("pyproject.toml", "r") as f:
        lines = f.readlines()
    
    # Procurar e atualizar a versão na seção [project]
    in_project_section = False
    for i, line in enumerate(lines):
        if line.strip() == "[project]":
            in_project_section = True
        elif line.strip().startswith("[") and line.strip().endswith("]"):
            in_project_section = False
        
        # Atualizar apenas a linha de versão na seção [project]
        if in_project_section and line.strip().startswith("version ="):
            lines[i] = f'version = "{new_version}"\n'
    
    with open("pyproject.toml", "w") as f:
        f.writelines(lines)


def create_tag_and_push(new_version: str) -> None:
    """Create a new git tag and push it."""
    subprocess.run(["git", "add", "pyproject.toml"])
    subprocess.run(["git", "commit", "-m", f"bump: version {new_version}"])
    subprocess.run(["git", "tag", f"v{new_version}"])
    subprocess.run(["git", "push"])
    subprocess.run(["git", "push", "--tags"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Semantic version management")
    parser.add_argument("--dry-run", action="store_true", help="Don't modify files or create tags")
    parser.add_argument("--bump", choices=["patch", "minor", "major"], 
                        help="Force a specific version bump type")
    args = parser.parse_args()
    
    # Get current version
    current_version = get_current_version()
    
    if args.bump:
        # Manual bump type specified
        if args.bump == "major":
            bump_type = BumpType.MAJOR
        elif args.bump == "minor":
            bump_type = BumpType.MINOR
        else:
            bump_type = BumpType.PATCH
    else:
        # Determine bump type from commits
        latest_tag = get_latest_tag()
        commits = get_commits_since_tag(latest_tag)
        bump_type = determine_bump_type(commits)
    
    # Calculate new version
    new_version = bump_version(current_version, bump_type)
    
    # Print results
    print(f"Current version: {current_version}")
    print(f"Bump type: {bump_type.name}")
    print(f"New version: {new_version}")
    
    if args.dry_run:
        print("\nDry run - no changes made")
        return 0
    
    if bump_type == BumpType.NONE:
        print("\nNo version bump needed")
        return 0
    
    # Update files
    update_version_in_files(new_version)
    
    # Create tag and push
    create_tag_and_push(new_version)
    
    print(f"\nSuccessfully bumped version to {new_version} and pushed to remote")
    return 0


if __name__ == "__main__":
    sys.exit(main())