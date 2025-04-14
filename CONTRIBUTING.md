# Contributing to Agent Swarm System

First off, thank you for considering contributing to Agent Swarm System! It's people like you that make this system such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* Use a clear and descriptive title
* Describe the exact steps which reproduce the problem
* Provide specific examples to demonstrate the steps
* Describe the behavior you observed after following the steps
* Explain which behavior you expected to see instead and why
* Include screenshots if relevant

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* Use a clear and descriptive title
* Provide a step-by-step description of the suggested enhancement
* Provide specific examples to demonstrate the steps
* Describe the current behavior and explain which behavior you expected to see instead
* Explain why this enhancement would be useful

### Pull Requests

* Fill in the required template
* Do not include issue numbers in the PR title
* Include screenshots and animated GIFs in your pull request whenever possible
* Follow the Python style guides
* Include thoughtfully-worded, well-structured tests
* Document new code based on the Documentation Styleguide
* End all files with a newline

## Development Process

1. Fork the repo
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Make changes
4. Run tests
5. Commit changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Git Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line

### Python Styleguide

* Follow PEP 8
* Use type hints
* Write docstrings for all public methods
* Keep functions focused and single-purpose

### Documentation Styleguide

* Use Markdown
* Reference functions and classes appropriately
* Include code examples when relevant
* Keep explanations clear and concise

## Project Structure

```
agent-swarm-system/
├── docs/                  # Documentation
├── src/                  # Source code
│   ├── agents/          # Specialized agents
│   ├── core/            # Core system components
│   └── main.py          # Application entry point
├── tests/               # Test suite
└── requirements.txt     # Python dependencies
```

## Testing

* Write tests for all new features
* Maintain high test coverage
* Run the full test suite before submitting PRs
* Include both unit and integration tests

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_specific.py

# Run with coverage report
pytest --cov=src tests/
```

## Additional Notes

### Issue and Pull Request Labels

* bug: Something isn't working
* documentation: Improvements or additions to documentation
* enhancement: New feature or request
* good first issue: Good for newcomers
* help wanted: Extra attention is needed
* invalid: This doesn't seem right
* question: Further information is requested
* wontfix: This will not be worked on

## Recognition

Contributors who have made significant improvements will be recognized in the README.md file.

## Questions?

Don't hesitate to ask questions in the issues section or contact the maintainers directly.

Thank you for contributing to Agent Swarm System! 🚀
