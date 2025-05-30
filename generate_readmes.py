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

**CRITICAL REQUIREMENT - PRESERVE EXISTING CONTENT**
If an existing README is provided, you MUST:
- PRESERVE ALL existing information, details, explanations, and content
- NEVER remove, omit, or lose any information from the existing README
- You may reorganize, reformat, and improve the structure and clarity
- You may add new sections and information based on code analysis
- Merge existing content with new analysis seamlessly
- If existing content conflicts with code analysis, include both perspectives

**What to include**

1. **Project title & one-sentence tagline** – infer from folder name, main file, or existing README.  
2. **Overview** – 1-2 short paragraphs explaining what the project is, why it exists, and the core problem it solves. MERGE with existing overview if present.  
3. **Badges** – preserve existing badges and add placeholders for missing ones.  
4. **Table of Contents** – generate only if the README will have four or more second-level headings.  
5. **Features / key components** – 3-7 concise bullet points. MERGE with existing features.  
6. **Quick start**  
   * *Prerequisites* (languages, runtimes, package managers). PRESERVE existing prerequisites.  
   * *Installation* (clone, install, build/run). PRESERVE existing installation steps.  
7. **Usage examples** – at least one minimal CLI or code snippet. PRESERVE all existing examples.  
8. **Folder / file overview** – one-line purpose for each top-level item. MERGE with existing descriptions.  
9. **Contributing** – standard fork/branch/PR flow. PRESERVE existing contribution guidelines.  
10. **License** – detect license file or PRESERVE existing license information.  
11. **Acknowledgements / references** – PRESERVE all existing acknowledgements and references.  
12. **Any existing sections** – PRESERVE all custom sections, configuration details, deployment instructions, etc.

**Formatting rules**

* Use GitHub-flavored Markdown.  
* Code blocks wrapped in triple backticks with language tags.  
* Consistent heading levels (`#`, `##`, `###`).  
* Wrap lines at ≤ 100 chars.  
* Be succinct; avoid filler words.
* PRESERVE formatting of existing code examples and structured content.

**Output**  
Return only the completed `README.md` content—no extra commentary, no outer markdown fences."""
    
    folder_tree: str = dspy.InputField(desc="Complete folder structure showing all files and subfolders")
    folder_name: str = dspy.InputField(desc="Name of the folder being analyzed")
    existing_readme: str = dspy.InputField(desc="Existing README content to preserve and incorporate (empty if no existing README)")
    subfolder_readmes: str = dspy.InputField(desc="Content from README files of subfolders for context")
    
    readme_content: str = dspy.OutputField(desc="Complete README.md content preserving all existing information while adding new insights")


class AppendOnlyREADMEGenerator(dspy.Signature):
    """You are an expert technical writer specializing in clear, comprehensive documentation.

**Task**  
Generate ONLY NEW SECTIONS to append to an existing README.md file.

**CRITICAL REQUIREMENT - APPEND-ONLY MODE**
You must ONLY generate new content to be appended to the existing README.
- DO NOT modify, rewrite, or reorganize any existing content
- DO NOT repeat any information already present in the existing README
- ONLY create new sections that add value and don't duplicate existing information
- Focus on gaps in the existing documentation based on the code analysis

**What to generate (only if missing from existing README)**

1. **Code Analysis Section** – if the existing README lacks technical details about the codebase
2. **API Documentation** – if there are public APIs not documented
3. **Architecture Overview** – if the code structure isn't explained
4. **Dependencies & Requirements** – if missing or incomplete
5. **Development Setup** – if build/dev instructions are missing
6. **Testing Instructions** – if test guidance is absent
7. **Deployment Notes** – if deployment info is missing
8. **Performance Notes** – if there are performance considerations
9. **Security Considerations** – if relevant security info is missing
10. **Troubleshooting** – if common issues aren't documented
11. **File Structure Analysis** – detailed breakdown of what each file/folder does

**Formatting rules**

* Use GitHub-flavored Markdown
* Start each new section with ## (second-level heading)
* Add clear separation between sections
* Use consistent formatting with existing README style
* Include proper code blocks with language tags

**Output**  
Return only the NEW content to be appended—no existing content, no modifications to existing sections."""
    
    folder_tree: str = dspy.InputField(desc="Complete folder structure showing all files and subfolders")
    folder_name: str = dspy.InputField(desc="Name of the folder being analyzed")
    existing_readme: str = dspy.InputField(desc="Existing README content that must not be modified")
    subfolder_readmes: str = dspy.InputField(desc="Content from README files of subfolders for context")
    
    new_content: str = dspy.OutputField(desc="Only new sections to append to the existing README")


class READMEModule(dspy.Module):
    """DSPy module for generating README files using expert technical writing."""
    
    def __init__(self, append_only: bool = False):
        super().__init__()
        self.append_only = append_only
        if append_only:
            self.generate_readme = dspy.ChainOfThought(AppendOnlyREADMEGenerator)
        else:
            self.generate_readme = dspy.ChainOfThought(EnhancedREADMEGenerator)
    
    def forward(self, folder_path: Path, subfolder_readmes: Dict[str, str]) -> str:
        # Generate folder tree structure
        folder_tree = self._generate_folder_tree(folder_path)
        
        # Read existing README if it exists
        existing_readme = ""
        readme_path = folder_path / "README.md"
        if readme_path.exists():
            try:
                existing_readme = readme_path.read_text(encoding='utf-8')
                mode_text = "appending to" if self.append_only else "preserving"
                print(f"  Found existing README, {mode_text} {len(existing_readme)} characters of content")
            except Exception as e:
                print(f"  Warning: Could not read existing README: {e}")
        
        # Prepare subfolder README content for context
        subfolder_content = ""
        if subfolder_readmes:
            subfolder_content = "\n\n".join([
                f"## {subfolder} (subfolder context)\n{content[:500]}..." 
                for subfolder, content in subfolder_readmes.items()
            ])
        
        if self.append_only and existing_readme:
            # Generate only new content to append
            result = self.generate_readme(
                folder_tree=folder_tree,
                folder_name=folder_path.name,
                existing_readme=existing_readme,
                subfolder_readmes=subfolder_content
            )
            
            # Combine existing README with new content
            new_content = result.new_content.strip()
            if new_content:
                # Add proper separation
                return existing_readme.rstrip() + "\n\n" + new_content
            else:
                return existing_readme
        else:
            # Generate complete README (existing behavior)
            readme = self.generate_readme(
                folder_tree=folder_tree,
                folder_name=folder_path.name,
                existing_readme=existing_readme,
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
    parser = argparse.ArgumentParser(
        description="Generate README.md files for source folders using DSPy",
        epilog="""
Behavior with existing READMEs:
- Default: Existing content is preserved and enhanced (may reorganize)
- --append-only: Only adds new sections, never modifies existing content
- Backup files (README.md.backup) are created before updates
- Use --append-only for maximum safety when updating existing documentation
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("folder", help="Root folder to process")
    parser.add_argument("--model", default="gpt-3.5-turbo", help="LLM model to use")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without writing files")
    parser.add_argument("--no-backup", action="store_true", help="Skip creating backup files when updating existing READMEs")
    parser.add_argument("--append-only", action="store_true", help="Only append new sections to existing READMEs, never modify existing content")
    
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
    readme_module = READMEModule(append_only=args.append_only)
    
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
                if readme_path.exists():
                    action = "append to" if args.append_only else "update"
                else:
                    action = "create"
                print(f"  Would {action}: {readme_path}")
                print(f"  Content preview: {readme_content[:100]}...")
            else:
                # Create backup of existing README if it exists
                is_update = readme_path.exists()
                if is_update and not args.no_backup:
                    backup_path = folder_path / "README.md.backup"
                    try:
                        import shutil
                        shutil.copy2(readme_path, backup_path)
                        print(f"  Created backup: {backup_path}")
                    except Exception as e:
                        print(f"  Warning: Could not create backup: {e}")
                
                readme_path.write_text(readme_content, encoding='utf-8')
                if is_update:
                    action = "Appended to" if args.append_only else "Updated"
                else:
                    action = "Generated"
                print(f"  {action}: {readme_path}")
                
        except Exception as e:
            print(f"  Error processing {folder_path}: {e}")
            continue
    
    print("README generation complete!")


if __name__ == "__main__":
    main()