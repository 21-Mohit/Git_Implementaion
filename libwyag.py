import argparse
import configparser
from datetime import datetime
import grp, pwd
from fnmatch import fnmatch
import hashlib
from math import ceil
import os
import re
import stat
import sys
import zlib
import logging

# Configure logging to display INFO level messages
logging.basicConfig(
    level=logging.INFO,  # Set the logging level to INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'  # Format for log messages
)

logger = logging.getLogger('git')
logger.info('Initializing git CLI application')
logger.info('Setting up logging')

# GitRepository class definition

# Initialize the argument parser
argparser = argparse.ArgumentParser(description="The stupidest content tracker")

# Add subparsers for commands
argsubparsers = argparser.add_subparsers(title="Commands", dest="command")
argsubparsers.required = True
class GitRepository(object):
    """A git repository"""

    # Class attributes
    worktree = None  # Path to the working directory
    gitdir = None    # Path to the .git directory
    conf = None      # Configuration object for .git/config

    def __init__(self, path, force=False):
        """
        Initialize a GitRepository object.

        Args:
            path (str): Path to the working directory.
            force (bool): If True, bypass validation checks.
        """
        self.worktree = path
        self.gitdir = os.path.join(path, ".git")

        # Validate that the .git directory exists unless force is True
        if not (force or os.path.isdir(self.gitdir)):
            raise Exception(f"Not a Git repository {path}")

        # Initialize the configuration parser
        self.conf = configparser.ConfigParser()
        cf = repo_file(self, "config")  # Path to .git/config

        # Read the configuration file if it exists
        if cf and os.path.exists(cf):
            self.conf.read([cf])
        elif not force:
            raise Exception("Configuration file missing")

        # Validate the repository format version
        if not force:
            vers = int(self.conf.get("core", "repositoryformatversion"))
            if vers != 0:
                raise Exception(f"Unsupported repositoryformatversion: {vers}")


# Helper function to construct paths within the .git directory
def repo_path(repo, *path):
    """
    Construct a path under the repository's .git directory.

    Args:
        repo (GitRepository): The repository object.
        *path: Additional path components.

    Returns:
        str: The constructed path.
    """
    return os.path.join(repo.gitdir, *path)

def repo_file(repo, *path, mkdir=False):
    """Same as repo_path, but create dirname(*path) if absent.  For
example, repo_file(r, \"refs\", \"remotes\", \"origin\", \"HEAD\") will create
.git/refs/remotes/origin."""

    if repo_dir(repo, *path[:-1], mkdir=mkdir):
        return repo_path(repo, *path)

def repo_dir(repo, *path, mkdir=False):
    """Same as repo_path, but mkdir *path if absent if mkdir."""

    path = repo_path(repo, *path)

    if os.path.exists(path):
        if (os.path.isdir(path)):
            return path
        else:
            raise Exception(f"Not a directory {path}")

    if mkdir:
        os.makedirs(path)
        return path
    else:
        return None
    
def repo_create(path):
    """Create a new repository at path."""

    repo = GitRepository(path, True)

    # First, we make sure the path either doesn't exist or is an
    # empty dir.

    if os.path.exists(repo.worktree):
        if not os.path.isdir(repo.worktree):
            raise Exception (f"{path} is not a directory!")
        if os.path.exists(repo.gitdir) and os.listdir(repo.gitdir):
            raise Exception (f"{path} is not empty!")
    else:
        os.makedirs(repo.worktree)

    assert repo_dir(repo, "branches", mkdir=True)
    assert repo_dir(repo, "objects", mkdir=True)
    assert repo_dir(repo, "refs", "tags", mkdir=True)
    assert repo_dir(repo, "refs", "heads", mkdir=True)

    # .git/description
    with open(repo_file(repo, "description"), "w") as f:
        f.write("Unnamed repository; edit this file 'description' to name the repository.\n")

    # .git/HEAD
    with open(repo_file(repo, "HEAD"), "w") as f:
        f.write("ref: refs/heads/master\n")

    with open(repo_file(repo, "config"), "w") as f:
        config = repo_default_config()
        config.write(f)

    return repo

def repo_default_config():
    ret = configparser.ConfigParser()

    ret.add_section("core")
    ret.set("core", "repositoryformatversion", "0")
    ret.set("core", "filemode", "false")
    ret.set("core", "bare", "false")

    return ret

def cmd_init(args):
    logger.info(f'Initializing a new repository at {args.path}')
    repo_create(args.path)
    
argsp = argsubparsers.add_parser("init", help="Initialize a new, empty repository.")
argsp.add_argument("path",
                   metavar="directory",
                   nargs="?",
                   default=".",
                   help="Where to create the repository.")

# Add functionality for `add` command to stage files
def cmd_add(args):
    """Handle the 'add' command."""
    logger.info(f"Staging file(s): {args.files}")
    repo = GitRepository(os.getcwd())  # Initialize repository object
    # Logic to add files to the staging area
    for file in args.files:
        logger.info(f"Processing file: {file}")
        # Example: Compute hash and store in objects directory
        with open(file, "rb") as f:
            data = f.read()
            sha1 = hashlib.sha1(data).hexdigest()
            obj_path = os.path.join(repo.gitdir, "objects", sha1[:2], sha1[2:])
            os.makedirs(os.path.dirname(obj_path), exist_ok=True)
            with open(obj_path, "wb") as obj_file:
                obj_file.write(data)
    logger.info("Files staged successfully.")

argsp_add = argsubparsers.add_parser("add", help="Stage files for the next commit.")
argsp_add.add_argument("files", nargs="+", help="Files to stage.")

# Add functionality for `commit` command to create a snapshot
def cmd_commit(args):
    """Handle the 'commit' command."""
    logger.info(f"Creating commit with message: {args.message}")
    repo = GitRepository(os.getcwd())  # Initialize repository object
    # Logic to create a commit object
    tree_hash = "dummy_tree_hash"  # Replace with actual tree hash computation
    parent_hash = "dummy_parent_hash"  # Replace with actual parent hash lookup
    commit_data = f"tree {tree_hash}\nparent {parent_hash}\n\n{args.message}"
    sha1 = hashlib.sha1(commit_data.encode()).hexdigest()
    obj_path = os.path.join(repo.gitdir, "objects", sha1[:2], sha1[2:])
    os.makedirs(os.path.dirname(obj_path), exist_ok=True)
    with open(obj_path, "wb") as obj_file:
        obj_file.write(commit_data.encode())
    logger.info(f"Commit created successfully: {sha1}")

argsp_commit = argsubparsers.add_parser("commit", help="Create a new commit.")
argsp_commit.add_argument("message", help="Commit message.")

# Add functionality for `log` command to display commit history
def cmd_log(args):
    """Handle the 'log' command."""
    logger.info("Displaying commit history")
    repo = GitRepository(os.getcwd())  # Initialize repository object
    # Logic to traverse and display commit history
    current_commit = "dummy_commit_hash"  # Replace with actual HEAD lookup
    while current_commit:
        commit_path = os.path.join(repo.gitdir, "objects", current_commit[:2], current_commit[2:])
        with open(commit_path, "rb") as commit_file:
            commit_data = commit_file.read().decode()
            logger.info(f"Commit: {current_commit}\n{commit_data}")
            # Extract parent hash for next iteration
            current_commit = "dummy_parent_hash"  # Replace with actual parent hash extraction

argsp_log = argsubparsers.add_parser("log", help="Display commit history.")

# Define the main function
def main(argv=sys.argv[1:]):
    """
    Main entry point for the CLI.

    Args:
        argv (list): Command-line arguments (excluding the script name).
    """
    logging.info('Starting the git CLI application')
    args = argparser.parse_args(argv)
    logging.info(f'Parsed arguments: {args}')

    # Replace the match statement with if-elif conditions for compatibility with Python 3.9
    if args.command == "add":
        cmd_add(args)
    elif args.command == "commit":
        cmd_commit(args)
    elif args.command == "init":
        logger.info(f'Command: {args.command}') 
        cmd_init(args)
    elif args.command == "log":
        cmd_log(args)
    else:
        print("Bad command.")


# Ensure the main function is called when the script is executed directly
if __name__ == "__main__":
    main()