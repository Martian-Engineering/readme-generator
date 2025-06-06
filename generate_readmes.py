#!/usr/bin/env python3
"""
DSPy-powered README generator that creates README.md files for all source folders
in a directory tree, working bottom-up to ensure subfolders are processed first.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List, Dict, Set, Optional
import dspy


class READMEGenerator(dspy.Signature):
    """Generate structured README sections for a source code folder."""
    folder_tree: str = dspy.InputField(desc="Complete folder structure showing all files and subfolders")
    folder_name: str = dspy.InputField(desc="Name of the folder being analyzed")
    existing_readme: str = dspy.InputField(desc="Existing README content to preserve and incorporate (empty if no existing README)")
    subfolder_readmes: str = dspy.InputField(desc="Content from README files of subfolders for context")
    
    title: str = dspy.OutputField(desc="Project title and one-sentence tagline")
    overview: str = dspy.OutputField(desc="1-2 paragraph overview explaining what the project is and why it exists")
    badges: Optional[str] = dspy.OutputField(desc="Relevant badges for the project (can be empty if none needed)")
    features: str = dspy.OutputField(desc="3-7 bullet points of key features or components")
    prerequisites: str = dspy.OutputField(desc="Required languages, runtimes, and package managers")
    installation: str = dspy.OutputField(desc="Step-by-step installation instructions")
    usage: str = dspy.OutputField(desc="Usage examples with code snippets")
    file_structure: Optional[str] = dspy.OutputField(desc="Overview of important files and folders")
    contributing: Optional[str] = dspy.OutputField(desc="Contributing guidelines and process")
    license_info: str = dspy.OutputField(desc="License information")
    acknowledgments: Optional[str] = dspy.OutputField(desc="Acknowledgments and references (can be empty)")


class AppendOnlyREADMEGenerator(dspy.Signature):
    """Generate additional README sections to append to existing content."""
    folder_tree: str = dspy.InputField(desc="Complete folder structure showing all files and subfolders")
    folder_name: str = dspy.InputField(desc="Name of the folder being analyzed")
    existing_readme: str = dspy.InputField(desc="Existing README content that must not be modified")
    subfolder_readmes: str = dspy.InputField(desc="Content from README files of subfolders for context")
    
    api_docs: Optional[str] = dspy.OutputField(desc="API documentation if public APIs exist (empty if not needed)")
    architecture: Optional[str] = dspy.OutputField(desc="Architecture overview if code structure needs explanation (empty if not needed)")
    development: Optional[str] = dspy.OutputField(desc="Development setup instructions if missing (empty if not needed)")
    testing: Optional[str] = dspy.OutputField(desc="Testing instructions if absent (empty if not needed)")
    deployment: Optional[str] = dspy.OutputField(desc="Deployment notes if missing (empty if not needed)")
    performance: Optional[str] = dspy.OutputField(desc="Performance considerations if relevant (empty if not needed)")
    security: Optional[str] = dspy.OutputField(desc="Security considerations if relevant (empty if not needed)")
    troubleshooting: Optional[str] = dspy.OutputField(desc="Troubleshooting guide if needed (empty if not needed)")


class READMEModule(dspy.Module):
    """DSPy module for generating README files with structured output fields."""
    
    def __init__(self, append_only: bool = False):
        super().__init__()
        self.append_only = append_only
        if append_only:
            self.generate_readme = dspy.ChainOfThought(AppendOnlyREADMEGenerator)
        else:
            self.generate_readme = dspy.ChainOfThought(READMEGenerator)
    
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
            # In append-only mode with existing README, generate additional sections
            result = self.generate_readme(
                folder_tree=folder_tree,
                folder_name=folder_path.name,
                existing_readme=existing_readme,
                subfolder_readmes=subfolder_content
            )
            
            # Collect non-empty additional sections
            additional_sections = []
            sections = {
                "API Documentation": result.api_docs,
                "Architecture": result.architecture,
                "Development Setup": result.development,
                "Testing": result.testing,
                "Deployment": result.deployment,
                "Performance": result.performance,
                "Security": result.security,
                "Troubleshooting": result.troubleshooting
            }
            
            for title, content in sections.items():
                if content and content.strip():
                    additional_sections.append(f"## {title}\n\n{content.strip()}")
            
            # Combine existing README with new sections
            if additional_sections:
                new_content = "\n\n".join(additional_sections)
                return existing_readme.rstrip() + "\n\n" + new_content
            else:
                return existing_readme
        else:
            # Generate complete README using structured approach
            result = self.generate_readme(
                folder_tree=folder_tree,
                folder_name=folder_path.name,
                existing_readme=existing_readme,
                subfolder_readmes=subfolder_content
            )
            
            # Assemble complete README from structured fields
            return self._assemble_readme(result)
    
    def _assemble_readme(self, result) -> str:
        """Assemble a complete README from structured output fields."""
        sections = []
        
        # Title (always first)
        if result.title.strip():
            sections.append(f"# {result.title.strip()}")
        
        # Badges (if present)
        if result.badges and result.badges.strip():
            sections.append(result.badges.strip())
        
        # Overview
        if result.overview.strip():
            sections.append(f"## Overview\n\n{result.overview.strip()}")
        
        # Features
        if result.features.strip():
            sections.append(f"## Features\n\n{result.features.strip()}")
        
        # Prerequisites
        if result.prerequisites.strip():
            sections.append(f"## Prerequisites\n\n{result.prerequisites.strip()}")
        
        # Installation
        if result.installation.strip():
            sections.append(f"## Installation\n\n{result.installation.strip()}")
        
        # Usage
        if result.usage.strip():
            sections.append(f"## Usage\n\n{result.usage.strip()}")
        
        # File Structure
        if result.file_structure and result.file_structure.strip():
            sections.append(f"## File Structure\n\n{result.file_structure.strip()}")
        
        # Contributing
        if result.contributing and result.contributing.strip():
            sections.append(f"## Contributing\n\n{result.contributing.strip()}")
        
        # License
        if result.license_info.strip():
            sections.append(f"## License\n\n{result.license_info.strip()}")
        
        # Acknowledgments
        if result.acknowledgments and result.acknowledgments.strip():
            sections.append(f"## Acknowledgments\n\n{result.acknowledgments.strip()}")
        
        return "\n\n".join(sections)
    
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