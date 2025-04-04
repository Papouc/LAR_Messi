#!/usr/bin/env python3
"""
README Generator for LAR_Messi Project
Automatically updates documentation from source code
"""

import subprocess
from datetime import datetime
from pathlib import Path

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
README_PATH = PROJECT_ROOT / "README.md"
SRC_DIR = PROJECT_ROOT / "src"


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


def build_readme_content():
    """Construct README content with dynamic values"""
    return f"""# 🤖 LAR_Messi - Autonomous TurtleBot Soccer Player  
**Precision Robotic Football System**  

![Robotic Soccer Demo](./docs/media/robot_score.gif)  
*Real-time demonstration of autonomous scoring system*

## 🏆 Overview
[Your static overview content here...]

## 📂 Project Structure
[Your directory structure diagram...]

## 🚀 Installation
[Your installation instructions...]

## 🧠 System Architecture
[Your Mermaid diagram...]

## 📝 Technical Report
[Your technical content...]

## ✅ Quality Assurance
[Your quality checks...]

## 👥 Development Team
[Your team table...]

---

📅 **Last Updated**: {datetime.now().strftime("%Y-%m-%d")}  
🏷️ **Version**: {get_git_version()}

---

> **Maintenance Tip**: Update documentation after code changes  
> ```bash
> python docs/generate_readme.py
> ```
"""


if __name__ == "__main__":
    print("Generating documentation...")
    generate_module_docs()

    print("Updating README...")
    with open(README_PATH, "w") as f:
        f.write(build_readme_content())

    print(f"README updated at {README_PATH}")