# Contributing to Centralized Metadata Management

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code:
- Be respectful and inclusive
- Be collaborative
- Be professional
- Focus on what is best for the community

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- Clear and descriptive title
- Steps to reproduce the problem
- Expected behavior
- Actual behavior
- Screenshots (if applicable)
- Environment details (OS, Python version, AWS region)
- Relevant logs

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- Clear and descriptive title
- Detailed description of the proposed functionality
- Why this enhancement would be useful
- Examples of how it would be used

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes**:
   - Write clear, commented code
   - Follow existing code style
   - Update documentation as needed
3. **Test your changes**:
   - Add unit tests for new functionality
   - Ensure all tests pass: `pytest`
   - Run linters: `black .` and `pylint src/`
4. **Commit your changes**:
   - Use clear, descriptive commit messages
   - Reference issues and pull requests liberally
5. **Push to your fork** and submit a pull request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/centralized-metadata-management-using-aws-glue-data-catalog-emr-athena.git
cd centralized-metadata-management-using-aws-glue-data-catalog-emr-athena

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
cd python && pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run linters
black src/
pylint src/
```

## Code Style

### Python

- Follow PEP 8 style guide
- Use Black for formatting
- Maximum line length: 100 characters
- Use type hints where appropriate
- Write docstrings for all public functions/classes

Example:
```python
def create_table(
    database: str,
    table: str,
    schema: List[Dict[str, str]],
    location: str
) -> Dict[str, Any]:
    """
    Create a new Glue table

    Args:
        database: Database name
        table: Table name
        schema: List of column definitions
        location: S3 location of data

    Returns:
        Response from create_table API

    Raises:
        CatalogException: If table creation fails
    """
    pass
```

### Terraform

- Use 2 spaces for indentation
- Use descriptive resource names
- Add comments for complex logic
- Use variables for configuration
- Include outputs for important values

### Documentation

- Use Markdown for documentation
- Keep lines under 100 characters
- Include code examples
- Update README.md if adding new features

## Testing

### Unit Tests

- Place tests in `python/tests/unit/`
- Name test files `test_*.py`
- Use pytest fixtures
- Mock external AWS calls

Example:
```python
def test_create_database(catalog_manager, mock_glue_client):
    """Test successful database creation"""
    mock_glue_client.create_database.return_value = {
        'ResponseMetadata': {'HTTPStatusCode': 200}
    }
    
    result = catalog_manager.create_database('test_db')
    
    assert result['ResponseMetadata']['HTTPStatusCode'] == 200
    mock_glue_client.create_database.assert_called_once()
```

### Integration Tests

- Place tests in `python/tests/integration/`
- Use `@pytest.mark.integration` decorator
- Clean up AWS resources after tests

## Documentation

When adding new features, update:

1. **README.md**: Add to features list
2. **INSTRUCTIONS.md**: Add relevant steps
3. **Code comments**: Explain complex logic
4. **Docstrings**: Document all public APIs
5. **Examples**: Add usage examples

## Commit Messages

Use conventional commit format:

- `feat: Add new crawler manager functionality`
- `fix: Resolve issue with partition handling`
- `docs: Update installation instructions`
- `test: Add tests for QueryRunner`
- `refactor: Simplify error handling logic`

## Review Process

1. All submissions require review
2. Maintainers will review for:
   - Code quality
   - Test coverage
   - Documentation
   - Adherence to guidelines
3. Address feedback from reviewers
4. Once approved, maintainer will merge

## Questions?

Feel free to open an issue for:
- Questions about contributing
- Clarifications on guidelines
- Feature discussions

Thank you for contributing! 🎉
