#!/usr/bin/env python3
"""
README Generator for LAR_Messi Project
Automatically updates documentation from source code
"""

import subprocess
import os
from datetime import datetime
from pathlib import Path

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
README_PATH = PROJECT_ROOT / "README.md"
SRC_DIR = PROJECT_ROOT / "src"
EXCLUDE_DIRS = {'.git', '__pycache__', '.idea', 'venv', '.github', '.vscode'}
EXCLUDE_FILES = {'generate_readme.py'}


def get_git_version():
    """Get current Git tag/commit"""
    try:
        return subprocess.check_output(
            ["git", "describe", "--always", "--tags"],
            cwd=PROJECT_ROOT,
            text=True
        ).strip()
    except subprocess.CalledProcessError:
        return "dev"


def generate_module_docs():
    """Generate API documentation using lazydocs"""
    subprocess.run([
        "lazydocs",
        "--output-path", str(PROJECT_ROOT / "docs"),
        "--no-watermark",
        str(SRC_DIR)
    ], check=True)


def generate_directory_tree(start_path, exclude_dirs=None, exclude_files=None, indent='', is_root=True):
    """Generate directory tree structure as a string"""
    if exclude_dirs is None:
        exclude_dirs = EXCLUDE_DIRS
    if exclude_files is None:
        exclude_files = EXCLUDE_FILES
    start_path = Path(start_path)

    if start_path.name in exclude_dirs:
        return ''

    tree = []
    if is_root:
        tree.append(f"{start_path.name}/")

    try:
        children = sorted(start_path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
    except PermissionError:
        return '\n'.join(tree)

    for index, item in enumerate(children):
        if item.name in exclude_dirs or (item.is_file() and item.name in exclude_files):
            continue

        is_last = index == len(children) - 1
        connector = '└── ' if is_last else '├── '
        current_indent = indent + connector
        tree_line = f"{indent}{connector}{item.name}"

        if item.is_dir():
            tree_line += '/'
            tree.append(tree_line)
            next_indent = indent + ('    ' if is_last else '│   ')
            subtree = generate_directory_tree(item, exclude_dirs, exclude_files, next_indent, False)
            if subtree:
                tree.append(subtree)
        else:
            tree.append(tree_line)

    return '\n'.join(tree)


def build_readme_content():
    """Construct README content with dynamic values"""
    project_structure = generate_directory_tree(PROJECT_ROOT, EXCLUDE_DIRS, EXCLUDE_FILES)
    project_structure_code = f"```\n{project_structure}\n```"

    team_members = [
        "Adam Hendrych",
        "David Horňáček",
        "Adam Hejtmánek"
    ]
    formatted_team = ',\n'.join(team_members[:-1]) + '\n' + team_members[-1]

    return f"""# ⚽ LAR_Messi - Autonomous TurtleBot Soccer Player  
*Precision Robotic Football System*  

![Robotic Soccer Demo](./docs/media/robot_score.gif)  
*Real-time demonstration of the autonomous scoring system*

## 🏆 System Overview
An autonomous robotic platform that enables TurtleBot to play soccer through:

- **Computer Vision** - Real-time ball and goal detection
- **Path Planning** - Optimal scoring trajectory calculation
- **Precision Control** - Velocity-regulated movement system
- **Decision Making** - 12-state finite state machine

**Technology Stack**:  
![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python&logoColor=white)   
![OpenCV](https://img.shields.io/badge/OpenCV-4.5+-green?logo=opencv&logoColor=white)        
![ROS](https://img.shields.io/badge/ROS-Noetic-purple?logo=ros&logoColor=white)     
![RealSense](https://img.shields.io/badge/Intel_RealSense-D435-red?logo=intel&logoColor=white)

## 🗂️ Project Structure
{project_structure_code}

## 📚 Documentation
[Sphinx auto-generated documentation](./docs/_build/html/index.html)

## 💻 Installation

### Clone repository:
```bash
git clone https://github.com/Papouc/LAR_Messi
cd LAR_Messi
```

### Install dependencies
pip install -r requirements.txt

### Run program
python src/main.py

## 📊 System Architecture

------Dodelava David

## ✅ Code Quality

### Run PEP8 check
```bash
  flake8 src/
```
### Expected output:
```bash
  0 errors found
```


## 👥 Team Members  
Adam Hendrych,
David Horňáček,
Adam Hejtmánek

📅 Last Updated: {datetime.now().strftime("%Y-%m-%d")}
🏷️ Version: {get_git_version()}
"""
