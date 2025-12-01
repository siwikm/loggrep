# GitHub Copilot Instructions for Loggrep Project

## Core Principles

### Code Quality Standards
- **Readability First**: Write code that is self-documenting and easy to understand
- **Single Responsibility**: Each function should do one thing and do it well
- **Maximum Complexity Limits**:
  - Max 4 function parameters (use config objects for more)
  - Max 3-4 levels of nesting
  - Max 50 lines per function
  - No try/except blocks > 20 lines

### Testing Requirements
- **Test Coverage**: Every function MUST have accompanying tests
- **Test First Mindset**: Consider testability when designing functions
- **Test Organization**: 
  - Unit tests for individual functions in `tests/test_<function_name>.py`
  - Integration tests in `tests/test_loggrep.py`
  - Use descriptive test names: `test_<behavior>_when_<condition>`

### Function Design
```python
# GOOD: Small, focused, testable
def _validate_file_exists(file_path: str) -> bool:
    """Check if file exists and is readable."""
    path = Path(file_path)
    return path.exists() and path.is_file()

# BAD: Too many responsibilities, hard to test
def process_file(file, phrases, case, all_mode, window, output, 
                 verbose, count, files_only, show_nums, print_it):
    # 200 lines of mixed concerns...
```

## Coding Guidelines

### 1. Extract Complex Logic
When you see:
- Nested if/else blocks > 3 levels deep
- Loop with complex conditions inside
- Try/except spanning > 20 lines

**Action**: Extract to named helper function with early returns

### 2. Use Configuration Objects
When function has > 4 parameters:
```python
from dataclasses import dataclass

@dataclass
class SearchConfig:
    phrases: list[str]
    case_sensitive: bool = True
    match_all: bool = True
    window_size: int = 1
```

### 3. Early Returns Over Deep Nesting
```python
# GOOD
def process(data):
    if not data:
        return None
    if not data.is_valid():
        return None
    return data.process()

# BAD
def process(data):
    if data:
        if data.is_valid():
            return data.process()
    return None
```

### 4. Smart Logging
Use context-aware logger instead of scattered `if verbose:` checks:
```python
class VerboseLogger:
    def __init__(self, verbose: bool):
        self.verbose = verbose
    
    def info(self, msg: str):
        if self.verbose:
            logging.info(msg)
```

### 5. Type Hints
Always include type hints for function parameters and return values:
```python
def search_file(file_path: str, config: SearchConfig) -> int:
    """Search file and return match count."""
    ...
```

## Testing Standards

### Unit Test Template
```python
def test_<function>_<expected_behavior>_when_<condition>():
    """Test that <function> <expected_behavior> when <condition>."""
    # Arrange
    input_data = create_test_data()
    
    # Act
    result = function_under_test(input_data)
    
    # Assert
    assert result == expected_output, "Should return expected value"
```

### Test Coverage Requirements
- ✅ Happy path (normal usage)
- ✅ Edge cases (empty input, boundary values)
- ✅ Error cases (invalid input, missing files)
- ✅ Integration tests (full workflows)

### Use Pytest Features
```python
import pytest

@pytest.fixture
def temp_log_file(tmp_path):
    """Create temporary log file for testing."""
    log_file = tmp_path / "test.log"
    log_file.write_text("ERROR: something failed\n")
    return log_file

@pytest.mark.parametrize("input,expected", [
    ("error", True),
    ("ERROR", True),
    ("warning", False),
])
def test_line_matches(input, expected):
    assert line_matches(input, ["error"]) == expected
```

## File Organization

### When to Create New Functions
Create a new function when:
- Logic block is > 10 lines
- Code is duplicated in 2+ places
- Function has > 4 levels of nesting
- Function has multiple responsibilities
- Logic can be tested independently

### Naming Conventions
- Functions: `verb_noun()` - `search_file()`, `validate_input()`
- Private helpers: `_verb_noun()` - `_format_output()`, `_check_exists()`
- Tests: `test_<function>_<behavior>_when_<condition>()`
- Config classes: `<Purpose>Config` - `SearchConfig`, `OutputConfig`

## Error Handling

### Fail Fast with Clear Messages
```python
# GOOD
if not Path(file_path).exists():
    print(f"Error: File not found: {file_path}")
    return 0

# BAD
try:
    # 100 lines of code
    with open(file_path) as f:
        # ...
except FileNotFoundError:
    print("File not found")
```

### Specific Exception Handling
```python
# GOOD: Handle specific errors near their source
try:
    data = parse_json(content)
except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON in {file}: {e}")
    return None

# BAD: Catch-all that hides bugs
try:
    # Everything
except Exception:
    pass
```

## Documentation

### Docstring Format
```python
def search_phrases_in_file(file_path: str, config: SearchConfig) -> int:
    """
    Search file for phrases and return match count.
    
    Args:
        file_path: Absolute path to file to search
        config: Search configuration with phrases and options
    
    Returns:
        Number of matches found
    
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    ...
```

## Code Review Checklist

Before committing, verify:
- [ ] All new functions have tests
- [ ] No function has > 4 parameters
- [ ] No nesting deeper than 4 levels
- [ ] All tests pass
- [ ] Type hints on all functions
- [ ] Docstrings on public functions
- [ ] No `if verbose:` scattered in code
- [ ] Early returns instead of nested if/else
- [ ] Single responsibility per function

## Examples to Follow

### Good Patterns (from Priority 1.1 refactoring)
- `_validate_file_exists()` - Single responsibility, easy to test
- `_prepare_search_phrases()` - Pure function, no side effects
- `_line_matches_phrases()` - Clear logic, well-tested
- `_format_match_output()` - Focused on formatting only

### Patterns to Avoid
- Functions with 11 parameters
- Try/except blocks spanning 120 lines
- Nesting 9-10 levels deep
- 200+ line functions with mixed concerns

## When in Doubt
1. Can this be split into smaller functions? → **Do it**
2. Is this testable in isolation? → **If no, refactor**
3. Would I understand this in 6 months? → **If no, add comments**
4. Does this violate any limits above? → **Fix before committing**

---

**Remember**: Code is read 10x more than it's written. Optimize for readability and maintainability.
