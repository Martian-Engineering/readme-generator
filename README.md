# DSPy README Generator

A sophisticated README generation tool that automatically creates comprehensive documentation for source code repositories using DSPy (Declarative Self-improving Python) for AI-powered code analysis.

## Overview

This tool recursively scans directory trees to identify source code folders and generates tailored README.md files for each one. It employs a bottom-up processing approach, ensuring that subdirectory documentation is created first and can be referenced by parent directories.

## How It Works

### 1. Source Folder Discovery

The tool intelligently identifies source code folders by scanning for files with recognized extensions and patterns:

**Supported Programming Languages:**
- Python (`.py`)
- JavaScript/TypeScript (`.js`, `.ts`, `.jsx`, `.tsx`)
- Java (`.java`)
- C/C++ (`.c`, `.cpp`, `.h`)
- Rust (`.rs`)
- Go (`.go`)
- And 20+ other languages

**Configuration Files:**
- `package.json`, `pyproject.toml`, `Cargo.toml`
- `Makefile`, `Dockerfile`, `requirements.txt`
- `pom.xml`, `build.gradle`, `composer.json`

**Exclusions:**
The scanner automatically skips common non-source directories like `node_modules`, `__pycache__`, `.git`, `build`, `dist`, `.venv`, and others.

### 2. Bottom-Up Processing

The algorithm processes directories in dependency order:
1. **Leaf directories** (deepest folders) are processed first
2. **Parent directories** are processed after their children
3. **Root directory** is processed last

This ensures that when generating a README for a parent folder, it can intelligently reference and summarize the documentation already created for its subdirectories.

### Content Preservation

When updating existing READMEs, the tool:
- **Preserves all existing information** - no content is lost during updates
- **Reorganizes and enhances** - improves structure while maintaining all details
- **Merges seamlessly** - combines existing content with new code analysis
- **Creates backups** - saves original files as `README.md.backup` before updates
- **Handles conflicts** - includes both existing explanations and new analysis when they differ

### 3. DSPy-Powered Analysis

The tool leverages DSPy's declarative AI framework for sophisticated code analysis:

#### DSPy Signatures
- **`FileAnalyzer`**: Analyzes source files to extract key information about code structure, purpose, and components
- **`READMEGenerator`**: Synthesizes file analysis and subfolder context into comprehensive README content

#### DSPy Modules
- **`READMEModule`**: Orchestrates the analysis pipeline using `ChainOfThought` reasoning
- Combines file-level analysis with hierarchical context from subdirectories
- Generates contextually appropriate documentation based on folder structure and content

### 4. Intelligent Content Generation

For each source folder, the tool:
- Catalogs all source files and their types
- Analyzes code structure and identifies key components
- Incorporates README content from immediate subdirectories
- Generates comprehensive documentation including:
  - Project/folder purpose and overview
  - File descriptions and their roles
  - Code architecture insights
  - References to subdirectory documentation

## Installation

This project uses `uv` for fast, reliable dependency management:

```bash
git clone https://github.com/Martian-Engineering/readme-generator.git
cd readme-generator
uv sync
```

## Usage

### Basic Usage

Generate READMEs for all source folders in a project:

```bash
uv run generate_readmes.py /path/to/your/project
```

### Preview Mode

See what would be generated without writing files:

```bash
uv run generate_readmes.py /path/to/your/project --dry-run
```

### Custom AI Model

Specify a different language model:

```bash
uv run generate_readmes.py /path/to/your/project --model gpt-4
```

### Updating Existing READMEs

The tool automatically preserves existing README content when updating:

```bash
# Updates existing READMEs while preserving all content
uv run generate_readmes.py /path/to/existing/project

# Skip creating backup files
uv run generate_readmes.py /path/to/existing/project --no-backup
```

### Example Usage

```bash
# Generate READMEs for a Python project
uv run generate_readmes.py ~/my-python-app

# Preview generation for a JavaScript project
uv run generate_readmes.py ~/my-react-app --dry-run

# Use GPT-4 for higher quality analysis
uv run generate_readmes.py ~/my-complex-project --model gpt-4

# Update existing documentation without losing content
uv run generate_readmes.py ~/existing-project --model gpt-4
```

## Configuration

### Environment Variables

- **`OPENAI_API_KEY`**: Required for AI-powered analysis
- Model selection supports any model available through DSPy/LiteLLM

### Supported Models

The tool works with any language model supported by DSPy, including:
- OpenAI models (GPT-3.5, GPT-4, etc.)
- Anthropic Claude
- Local models via Ollama
- Azure OpenAI
- And more through LiteLLM integration

## Algorithm Details

### Directory Traversal

```python
def find_source_folders(root_path: Path) -> List[Path]:
    """
    Recursively finds source folders, returning them in bottom-up order
    for proper dependency-aware processing.
    """
```

The traversal algorithm:
1. Recursively scans all subdirectories first
2. Checks each directory for source code indicators
3. Returns folders in depth-first order (deepest first)
4. Skips common build/cache directories automatically

### AI Analysis Pipeline

```python
class READMEModule(dspy.Module):
    def __init__(self):
        self.analyze_files = dspy.ChainOfThought(FileAnalyzer)
        self.generate_readme = dspy.ChainOfThought(READMEGenerator)
```

The DSPy pipeline:
1. **File Analysis**: Examines source files to understand purpose and structure
2. **Context Integration**: Combines file analysis with existing subfolder READMEs
3. **Content Generation**: Uses chain-of-thought reasoning to produce comprehensive documentation

## Example Output Structure

Given a project structure like:
```
my-app/
├── src/
│   ├── components/
│   │   └── Button.tsx
│   ├── utils/
│   │   └── helpers.js
│   └── main.ts
└── tests/
    └── app.test.js
```

The tool generates:
```
my-app/
├── src/
│   ├── components/
│   │   ├── Button.tsx
│   │   └── README.md          # Documents Button component
│   ├── utils/
│   │   ├── helpers.js
│   │   └── README.md          # Documents utility functions
│   ├── main.ts
│   └── README.md              # References components/ and utils/
├── tests/
│   ├── app.test.js
│   └── README.md              # Documents test suite
└── README.md                  # Project overview referencing src/ and tests/
```

## Technical Architecture

- **Language**: Python 3.10+
- **AI Framework**: DSPy for declarative AI programming
- **LLM Integration**: LiteLLM for multi-provider model access
- **Dependency Management**: UV for fast package management
- **File Processing**: Pathlib for robust cross-platform file operations

## Requirements

- Python 3.10 or higher
- Valid API key for chosen language model provider
- UV package manager
- Internet connection for AI model access

## Contributing

Contributions are welcome! Areas for enhancement:
- Additional programming language support
- Custom README templates
- Integration with documentation generators
- Multi-language README generation
- Custom AI prompt engineering

## License

MIT License - see LICENSE file for details.

---

*Built with DSPy for intelligent, declarative AI programming*