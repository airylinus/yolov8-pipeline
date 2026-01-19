# AGENTS.md - Coding Guidelines for YOLOv8 Pipeline Project

This document provides coding standards and operational guidelines for AI coding agents working on the yolov8-pipeline repository.

## Build/Lint/Test Commands

### Build Commands
No build system is used. Python scripts are executed directly:
```bash
python split_dataset.py <dataset_dir>
python label_converter.py --mode <mode> --src_path <src> --dst_path <dst> --classes <classes_file>
python generate_yaml.py <dataset_dir>
```

### Test Commands
No dedicated testing framework is configured. Manual testing is performed by running the data preparation pipeline:

```bash
# Test the full data preparation pipeline
.\data-prepare.bat D:\path\to\labeled\images

# Test individual components
python split_dataset.py <dataset_dir>
python -c "import label_converter; print('Import successful')"
```

### Single Test Execution
Since there are no unit tests, individual functionality is tested by running specific scripts with sample data or by importing modules:

```bash
# Test label converter import
python -c "from label_converter import RectLabelConverter; print('RectLabelConverter imported successfully')"

# Test with small dataset sample
python split_dataset.py small_test_dataset/
```

## Code Style Guidelines

### Python Version
- Target Python 3.7+ (based on imports and syntax used)
- Compatible with Windows and cross-platform execution

### Imports
- Standard library imports first, grouped alphabetically
- Third-party imports second (PIL, tqdm, numpy, etc.)
- Relative imports not used (all absolute imports)
- Import order:
  ```python
  import os
  import sys
  import json

  import numpy as np
  from PIL import Image
  from tqdm import tqdm
  ```

### Naming Conventions
- **Functions**: snake_case (`split_dataset`, `get_image_size`, `custom_to_yolov5`)
- **Classes**: PascalCase (`BaseLabelConverter`, `RectLabelConverter`, `JsonEncoder`)
- **Variables**: snake_case (`dataset_dir`, `image_width`, `output_file`)
- **Constants**: UPPER_CASE (not extensively used, but follow this pattern)
- **File names**: snake_case with hyphens for multi-word (`split_dataset.py`, `label_converter.py`)

### Code Formatting
- **Indentation**: 4 spaces (standard Python)
- **Line length**: No strict limit, but keep lines readable (typically < 100 chars)
- **String quotes**: Double quotes preferred for consistency
- **Trailing commas**: Not used consistently, but acceptable in multi-line structures
- **Blank lines**: 2 blank lines between top-level functions/classes, 1 blank line between methods

### Type Hints
- Used sparingly but consistently in some files
- Function parameters should include type hints when possible:
  ```python
  def split_dataset(dataset_dir: str):
  def list_labels(raw_labels_dir: str) -> List[str]:
  ```

### Comments and Documentation
- **Comments**: Minimal comments, mostly in Chinese for Chinese developers
- **Docstrings**: Not used (functions are self-documenting)
- **Inline comments**: Only when code is not obvious
- **File headers**: No standard headers

### Error Handling
- Basic error handling with `exit(1)` for critical failures
- Print error messages to console
- Use `os.path.exists()` checks before file operations
- Handle missing files gracefully

### File I/O
- Use `encoding="utf-8"` for all text file operations
- Use context managers (`with open()`) for file operations
- Check file existence before operations
- Use `os.path.join()` for cross-platform path construction
- Use `os.path.splitext()` for file extension handling

### Data Structures
- Use dictionaries for configuration and metadata
- Use lists for collections of items
- Use numpy arrays for numerical data processing
- JSON format for label data interchange

### Command Line Interface
- Use `argparse` for complex scripts (`label_converter.py`)
- Use `sys.argv` for simple scripts with few parameters
- Provide usage messages and help text
- Validate input parameters

### Logging and Output
- Use `print()` for user feedback and progress messages
- Use `tqdm` for progress bars in long-running operations
- Print success/failure messages
- Include timing information for performance-critical operations

### Dependencies
- Core dependencies: PIL, tqdm, numpy, requests
- Avoid adding new dependencies unless absolutely necessary
- Import checking not implemented - ensure dependencies are available

### Project Structure
- Flat structure with all scripts in root directory
- No package structure (`__init__.py` files)
- Shared utilities in base classes (`BaseLabelConverter`)
- Batch files for Windows automation

### Security Considerations
- No sensitive data handling
- File paths from user input - validate and sanitize
- Network operations in `download.py` - use appropriate timeouts
- No secrets or credentials in code

### Performance
- Use numpy for numerical computations
- Use tqdm for long-running loops
- Process files in batches where possible
- Consider memory usage for large datasets

### Windows Compatibility
- Use `os.path.join()` for paths (not forward slashes)
- Batch files for automation
- Handle Windows path separators correctly
- Test on Windows platform

### Code Quality Checks
- No automated linting configured
- Manual code review recommended
- Test imports and basic functionality
- Validate JSON/YAML output formats

### Commit Message Style
- Not standardized, but follow conventional commits when possible:
  - `feat: add new conversion format`
  - `fix: handle missing image files`
  - `refactor: simplify label processing logic`

### Git Workflow
- No specific workflow defined
- Direct commits to main branch
- Include related files in commits
- Test changes before committing