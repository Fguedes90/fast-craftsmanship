"""Git utility functions for the commit command."""

import os
import subprocess

from dataclasses import dataclass


@dataclass
class GitFileStatus:
    """Status of a file in git."""

    path: str
    original_path: str | None = None
    staged: bool = False

    @property
    def display_path(self) -> str:
        """Get path for display, including rename information."""
        if self.original_path:
            return f"{self.original_path} -> {self.path}"
        return self.path


@dataclass
class GitStatus:
    """Git status information."""

    added: list[GitFileStatus] = None
    modified: list[GitFileStatus] = None
    deleted: list[GitFileStatus] = None
    renamed: list[GitFileStatus] = None
    untracked: list[GitFileStatus] = None

    def __post_init__(self):
        """Initialize empty lists."""
        self.added = self.added or []
        self.modified = self.modified or []
        self.deleted = self.deleted or []
        self.renamed = self.renamed or []
        self.untracked = self.untracked or []

    def has_changes(self) -> bool:
        """Check if there are any changes."""
        return any([self.added, self.modified, self.deleted, self.renamed, self.untracked])

    def all_files(self) -> set[str]:
        """Get all file paths."""
        files = set()
        for status_list in [self.added, self.modified, self.deleted, self.renamed, self.untracked]:
            files.update(file.path for file in status_list)
        return files


class GitCommands:
    """Git command wrapper."""

    @staticmethod
    def get_git_root() -> str:
        """Get the root directory of the git repository."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return os.getcwd()

    @staticmethod
    def get_relative_path(path: str) -> str:
        """Convert absolute path to path relative to git root."""
        git_root = GitCommands.get_git_root()
        try:
            return os.path.relpath(path, git_root)
        except ValueError:
            return path

    @staticmethod
    def run_git_command(command: list[str], check: bool = True) -> tuple[str, str]:
        """Run a git command and return stdout and stderr."""
        git_root = GitCommands.get_git_root()
        current_dir = os.getcwd()
        try:
            os.chdir(git_root)
            result = subprocess.run(command, capture_output=True, text=True, check=check)
            return result.stdout, result.stderr
        finally:
            os.chdir(current_dir)

    @staticmethod
    def detect_renames_with_similarity() -> dict[str, str]:
        """Detect renamed files using git's similarity index."""
        try:
            # Stage all changes to check for renames
            GitCommands.run_git_command(["git", "add", "-N", "."], check=False)

            # Get renamed files using git's similarity detection
            stdout, _ = GitCommands.run_git_command(
                ["git", "diff", "--find-renames=90%", "--name-status"], check=False
            )

            renames = {}
            for line in stdout.splitlines():
                if line.startswith("R"):
                    parts = line.split("\t")
                    if len(parts) >= 3:
                        old_file = parts[1].strip()
                        new_file = parts[2].strip()
                        renames[new_file] = old_file

            # Also check staged changes
            stdout, _ = GitCommands.run_git_command(
                ["git", "diff", "--cached", "--find-renames=90%", "--name-status"], check=False
            )

            for line in stdout.splitlines():
                if line.startswith("R"):
                    parts = line.split("\t")
                    if len(parts) >= 3:
                        old_file = parts[1].strip()
                        new_file = parts[2].strip()
                        renames[new_file] = old_file

            return renames
        except Exception as e:
            print(f"Error detecting renames: {e}")
            return {}

    @staticmethod
    def stage_rename(old_file: str, new_file: str) -> None:
        """Stage a rename operation."""
        try:
            # Remove the old file from the index
            GitCommands.run_git_command(["git", "rm", "--cached", old_file], check=False)
            # Stage the new file
            GitCommands.run_git_command(["git", "add", new_file], check=False)
        except Exception:
            pass

    @staticmethod
    def get_status() -> GitStatus:
        """Get current git status."""
        status = GitStatus()

        # First detect any renames
        renames = GitCommands.detect_renames_with_similarity()

        # Get current status
        stdout, _ = GitCommands.run_git_command(
            ["git", "status", "--porcelain", "-uall", "--untracked-files=all"], check=False
        )

        # Track processed files
        processed = set()

        # First handle renames
        for new_file, old_file in renames.items():
            if new_file not in processed and old_file not in processed:
                file_status = GitFileStatus(path=new_file, original_path=old_file, staged=True)
                status.renamed.append(file_status)
                processed.add(new_file)
                processed.add(old_file)

                # Check for modifications after rename
                diff = GitCommands.get_file_diff(new_file)
                if diff.strip():
                    mod_status = GitFileStatus(path=new_file, staged=True)
                    status.modified.append(mod_status)

        # Process remaining files
        for line in stdout.splitlines():
            if not line:
                continue

            index_status = line[0]
            work_tree_status = line[1]
            file_info = line[3:].strip()

            # Skip processed files
            if file_info in processed:
                continue

            # Handle other statuses
            file_status = GitFileStatus(path=file_info, staged=index_status in "MADRC")

            if index_status == "A" or work_tree_status == "A":
                status.added.append(file_status)
            elif index_status == "M" or work_tree_status == "M":
                status.modified.append(file_status)
            elif index_status == "D" or (
                work_tree_status == "D" and file_info not in renames.values()
            ):
                status.deleted.append(file_status)
            elif index_status == "?" and work_tree_status == "?":
                status.untracked.append(file_status)

            processed.add(file_info)

        return status

    @staticmethod
    def stage_changes(status: GitStatus) -> None:
        """Stage all changes in the given status."""
        # First handle renames to maintain the rename detection
        for file in status.renamed:
            if file.original_path:
                GitCommands.stage_rename(file.original_path, file.path)

        # Then stage other changes
        for status_type in ["added", "modified", "untracked"]:
            for file in getattr(status, status_type):
                GitCommands.stage_file(file.path)

        # Handle deletions last
        for file in status.deleted:
            GitCommands.run_git_command(["git", "rm", "--cached", file.path], check=False)

    @staticmethod
    def get_file_diff(file_path: str, staged: bool = False) -> str:
        """Get the diff for a specific file."""
        rel_path = GitCommands.get_relative_path(file_path)
        command = ["git", "diff"]
        if staged:
            command.append("--cached")
        command.extend(["--", rel_path])
        stdout, _ = GitCommands.run_git_command(command, check=False)
        return stdout

    @staticmethod
    def stage_file(file: str) -> None:
        """Stage a specific file."""
        rel_path = GitCommands.get_relative_path(file)
        GitCommands.run_git_command(["git", "add", "--", rel_path], check=False)

    @staticmethod
    def unstage_file(file: str) -> None:
        """Unstage a specific file."""
        rel_path = GitCommands.get_relative_path(file)
        GitCommands.run_git_command(["git", "reset", "--", rel_path], check=False)

    @staticmethod
    def make_commit(message: str) -> None:
        """Create a git commit with the given message."""
        GitCommands.run_git_command(["git", "commit", "-m", message])


# For backward compatibility
get_git_root = GitCommands.get_git_root
get_relative_path = GitCommands.get_relative_path
get_file_diff = GitCommands.get_file_diff
stage_file = GitCommands.stage_file
unstage_file = GitCommands.unstage_file
make_commit = GitCommands.make_commit
