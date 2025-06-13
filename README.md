# Git-like Content Tracker

## Overview
This project is a simplified implementation of a Git-like content tracker written in Python. It provides basic functionality to manage and track changes in files, similar to Git. The commands implemented include:

- `init`: Initialize a new repository.
- `add`: Stage files for the next commit.
- `commit`: Create a snapshot of the repository state.
- `log`: Display commit history.
- `read`: Read and display file contents.

## Features
- **Repository Initialization**: Creates a `.git` directory with necessary subdirectories and files.
- **File Staging**: Hashes file contents and stores them in the `.git/objects` directory.
- **Commit Creation**: Saves a snapshot of the repository state.
- **Commit History**: Traverses and displays commit history.
- **File Reading**: Reads and displays the contents of a specified file.

## Requirements
- Python 3.9 or higher

## Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```bash
   cd Git_Implementation
   ```

## Usage
### Initialize a Repository
```bash
python libwyag.py init <directory>
```
This command initializes a new repository in the specified directory.

### Stage Files
```bash
python libwyag.py add <file1> <file2> ...
```
Stages the specified files for the next commit.

### Create a Commit
```bash
python libwyag.py commit "Commit message"
```
Creates a new commit with the provided message.

### View Commit History
```bash
python libwyag.py log
```
Displays the commit history.

### Read File Contents
```bash
python libwyag.py read <file>
```
Reads and displays the contents of the specified file.

## Testing
To test the functionality of the commands:
1. Initialize a repository:
   ```bash
   python libwyag.py init test_repo
   ```
2. Create a file and stage it:
   ```bash
   echo "Hello, World!" > test_repo/hello.txt
   python libwyag.py add test_repo/hello.txt
   ```
3. Commit the changes:
   ```bash
   python libwyag.py commit "Initial commit"
   ```
4. View the commit history:
   ```bash
   python libwyag.py log
   ```
5. Read the file contents:
   ```bash
   python libwyag.py read test_repo/hello.txt
   ```

## Debugging
Detailed logs are generated for each command to trace the execution process. Logs are displayed in the console.

## Future Enhancements
- Implement branching and merging functionality.
- Optimize file and directory operations for better performance.
- Add support for more Git-like commands.


