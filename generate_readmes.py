#!/usr/bin/env python3
"""
DSPy-powered README generator that creates README.md files for all source folders
in a directory tree, working bottom-up to ensure subfolders are processed first.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List, Dict, Set
import dspy


class READMEGenerator(dspy.Signature):
    """Generate a comprehensive README.md file for a source code folder using expert technical writing."""
    folder_tree: str = dspy.InputField(desc="Complete folder structure showing all files and subfolders")
    folder_name: str = dspy.InputField(desc="Name of the folder being analyzed")
    subfolder_readmes: str = dspy.InputField(desc="Content from README files of subfolders for context")
    
    readme_content: str = dspy.OutputField(desc="Complete README.md content following technical writing best practices")


class EnhancedREADMEGenerator(dspy.Signature):
    """You are an expert technical writer specializing in clear, comprehensive documentation.

**Task**  
Generate a crisp, well-structured `README.md` for the folder described below.

**What to include**

1. **Project title & one-sentence tagline** – infer from folder name or main file.  
2. **Overview** – 1-2 short paragraphs explaining what the project is, why it exists, and the core problem it solves.  
3. **Badges** – leave placeholders (build status, license, etc.).  
4. **Table of Contents** – generate only if the README will have four or more second-level headings.  
5. **Features / key components** – 3-7 concise bullet points.  
6. **Quick start**  
   * *Prerequisites* (languages, runtimes, package managers).  
   * *Installation* (clone, install, build/run).  
7. **Usage examples** – at least one minimal CLI or code snippet.  
8. **Folder / file overview** – one-line purpose for each top-level item.  
9. **Contributing** – standard fork/branch/PR flow with placeholder links.  
10. **License** – detect license file; if none, insert "License TBD".  
11. **Acknowledgements / references** – leave empty section if nothing obvious.

**Formatting rules**

* Use GitHub-flavored Markdown.  
* Code blocks wrapped in triple backticks with language tags.  
* Consistent heading levels (`#`, `##`, `###`).  
* Wrap lines at ≤ 100 chars.  
* Be succinct; avoid filler words.

**Output**  
Return only the completed `README.md` content—no extra commentary, no outer markdown fences."""
    
    folder_tree: str = dspy.InputField(desc="Complete folder structure showing all files and subfolders")
    folder_name: str = dspy.InputField(desc="Name of the folder being analyzed")
    subfolder_readmes: str = dspy.InputField(desc="Content from README files of subfolders for context")
    
    readme_content: str = dspy.OutputField(desc="Complete README.md content following technical writing best practices")


class READMEModule(dspy.Module):
    """DSPy module for generating README files using expert technical writing."""
    
    def __init__(self):
        super().__init__()
        self.generate_readme = dspy.ChainOfThought(EnhancedREADMEGenerator)
    
    def forward(self, folder_path: Path, subfolder_readmes: Dict[str, str]) -> str:
        # Generate folder tree structure
        folder_tree = self._generate_folder_tree(folder_path)
        
        # Prepare subfolder README content for context
        subfolder_content = ""
        if subfolder_readmes:
            subfolder_content = "\n\n".join([
                f"## {subfolder} (subfolder context)\n{content[:500]}..." 
                for subfolder, content in subfolder_readmes.items()
            ])
        
        # Generate the README
        readme = self.generate_readme(
            folder_tree=folder_tree,
            folder_name=folder_path.name,
            subfolder_readmes=subfolder_content
        )
        
        return readme.readme_content
    
    def _generate_folder_tree(self, folder_path: Path, max_depth: int = 3, current_depth: int = 0) -> str:
        """Generate a tree-like representation of the folder structure."""
        if current_depth > max_depth:
            return ""
        
        tree_lines = []
        prefix = "  " * current_depth
        
        try:
            items = sorted(folder_path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
            for item in items:
                if item.name.startswith('.') and item.name not in ['.gitignore', '.env.example']:
                    continue
                
                # Skip common build/cache directories
                skip_dirs = {
                    'node_modules', '__pycache__', '.git', '.svn', '.hg',
                    'build', 'dist', 'target', 'bin', 'obj', '.venv', 'venv',
                    '.tox', '.pytest_cache', '.mypy_cache', 'coverage'
                }
                
                if item.is_dir() and item.name in skip_dirs:
                    continue
                
                if item.is_file():
                    tree_lines.append(f"{prefix}├── {item.name}")
                elif item.is_dir() and current_depth < max_depth:
                    tree_lines.append(f"{prefix}├── {item.name}/")
                    subtree = self._generate_folder_tree(item, max_depth, current_depth + 1)
                    if subtree:
                        tree_lines.append(subtree)
        except PermissionError:
            tree_lines.append(f"{prefix}[Permission Denied]")
        
        return "\n".join(tree_lines)


def is_source_folder(folder_path: Path) -> bool:
    """Check if a folder contains source code files."""
    source_extensions = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', '.cs', 
        '.rb', '.go', '.rs', '.php', '.swift', '.kt', '.scala', '.clj', '.hs',
        '.ml', '.fs', '.vb', '.dart', '.lua', '.r', '.jl', '.nim', '.zig',
        '.toml', '.yaml', '.yml', '.json', '.xml', '.sql', '.sh', '.bash',
        '.dockerfile', '.makefile', '.cmake', '.gradle'
    }
    
    # Also check for common source file names without extensions
    source_filenames = {
        'makefile', 'dockerfile', 'pipfile', 'gemfile', 'rakefile',
        'cargo.toml', 'package.json', 'requirements.txt', 'setup.py',
        'pyproject.toml', 'composer.json', 'pom.xml', 'build.gradle'
    }
    
    for file_path in folder_path.iterdir():
        if file_path.is_file():
            if (file_path.suffix.lower() in source_extensions or 
                file_path.name.lower() in source_filenames):
                return True
    return False


def get_source_files(folder_path: Path) -> List[str]:
    """Get list of source files in a folder (non-recursive)."""
    source_extensions = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', '.cs', 
        '.rb', '.go', '.rs', '.php', '.swift', '.kt', '.scala', '.clj', '.hs',
        '.ml', '.fs', '.vb', '.dart', '.lua', '.r', '.jl', '.nim', '.zig',
        '.toml', '.yaml', '.yml', '.json', '.xml', '.sql', '.sh', '.bash',
        '.dockerfile', '.makefile', '.cmake', '.gradle'
    }
    
    source_filenames = {
        'makefile', 'dockerfile', 'pipfile', 'gemfile', 'rakefile',
        'cargo.toml', 'package.json', 'requirements.txt', 'setup.py',
        'pyproject.toml', 'composer.json', 'pom.xml', 'build.gradle'
    }
    
    files = []
    for file_path in folder_path.iterdir():
        if file_path.is_file() and not file_path.name.startswith('.'):
            if (file_path.suffix.lower() in source_extensions or 
                file_path.name.lower() in source_filenames):
                files.append(file_path.name)
    
    return sorted(files)


def find_source_folders(root_path: Path) -> List[Path]:
    """Find all folders that contain source code, ordered for bottom-up processing."""
    source_folders = []
    
    def scan_directory(path: Path, depth: int = 0):
        if not path.is_dir() or path.name.startswith('.'):
            return
        
        # Skip common non-source directories
        skip_dirs = {
            'node_modules', '__pycache__', '.git', '.svn', '.hg',
            'build', 'dist', 'target', 'bin', 'obj', '.venv', 'venv',
            '.tox', '.pytest_cache', '.mypy_cache', 'coverage',
            'logs', 'temp', 'tmp', 'cache'
        }
        
        if path.name in skip_dirs:
            return
        
        # Recursively scan subdirectories first (for bottom-up order)
        subdirs = [p for p in path.iterdir() if p.is_dir()]
        for subdir in sorted(subdirs):
            scan_directory(subdir, depth + 1)
        
        # Check if this directory contains source files
        if is_source_folder(path):
            source_folders.append(path)
    
    scan_directory(root_path)
    return source_folders


def load_existing_readmes(folder_path: Path) -> Dict[str, str]:
    """Load README content from immediate subfolders."""
    readmes = {}
    
    for item in folder_path.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            readme_path = item / "README.md"
            if readme_path.exists():
                try:
                    content = readme_path.read_text(encoding='utf-8')
                    # Extract just the main content, skip the title
                    lines = content.split('\n')
                    if lines and lines[0].startswith('# '):
                        content = '\n'.join(lines[1:]).strip()
                    readmes[item.name] = content
                except Exception as e:
                    print(f"Warning: Could not read {readme_path}: {e}")
    
    return readmes


def main():
    parser = argparse.ArgumentParser(description="Generate README.md files for source folders using DSPy")
    parser.add_argument("folder", help="Root folder to process")
    parser.add_argument("--model", default="gpt-3.5-turbo", help="LLM model to use")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without writing files")
    
    args = parser.parse_args()
    
    root_path = Path(args.folder).resolve()
    if not root_path.exists():
        print(f"Error: Folder {root_path} does not exist")
        sys.exit(1)
    
    if not root_path.is_dir():
        print(f"Error: {root_path} is not a directory")
        sys.exit(1)
    
    # Configure DSPy
    try:
        lm = dspy.LM(model=args.model)
        dspy.configure(lm=lm)
    except Exception as e:
        print(f"Error configuring DSPy: {e}")
        print("Make sure you have OPENAI_API_KEY set in your environment")
        sys.exit(1)
    
    # Initialize the README generator module
    readme_module = READMEModule()
    
    # Find all source folders (bottom-up order)
    source_folders = find_source_folders(root_path)
    
    if not source_folders:
        print(f"No source folders found in {root_path}")
        sys.exit(0)
    
    print(f"Found {len(source_folders)} source folders to process")
    
    # Process folders bottom-up
    for folder_path in source_folders:
        print(f"Processing: {folder_path}")
        
        # Load existing README files from subfolders
        subfolder_readmes = load_existing_readmes(folder_path)
        
        try:
            # Generate README content
            readme_content = readme_module.forward(
                folder_path=folder_path,
                subfolder_readmes=subfolder_readmes
            )
            
            # Write README file
            readme_path = folder_path / "README.md"
            
            if args.dry_run:
                print(f"  Would write: {readme_path}")
                print(f"  Content preview: {readme_content[:100]}...")
            else:
                readme_path.write_text(readme_content, encoding='utf-8')
                print(f"  Generated: {readme_path}")
                
        except Exception as e:
            print(f"  Error processing {folder_path}: {e}")
            continue
    
    print("README generation complete!")


if __name__ == "__main__":
    main()