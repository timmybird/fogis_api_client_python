# Contributing to fogis_api_client

Thank you for your interest in contributing to fogis_api_client! This document outlines the process and guidelines for contributing to this project.

## Git Workflow

### 1. Never Push Directly to Main
- All changes must go through pull requests
- The main branch is protected and requires PR review
- This ensures code quality and prevents accidental breaking changes

### 2. Branch Naming Convention
- `feature/descriptive-name` for new features
- `fix/issue-description` for bug fixes
- `docs/what-is-documented` for documentation changes
- `refactor/what-is-refactored` for code refactoring
- `test/what-is-tested` for adding or updating tests

### 3. Pull Request Process
1. Create a branch from main: `git checkout -b branch-name main`
2. Make your changes
3. Write or update tests for your changes
4. Run all tests locally: `python -m unittest discover tests`
5. Push your branch: `git push -u origin branch-name`
6. Create a PR through GitHub
7. Wait for CI/CD to pass
8. Get at least one review
9. Squash-merge to main
10. Delete the branch after merging

### 4. Commit Message Guidelines
- Use the format: `Type: Short description`
- Types: `Fix`, `Feature`, `Docs`, `Style`, `Refactor`, `Test`, `Chore`
- Example: `Fix: Ensure proper payload structure in fetch_matches_list_json`
- Keep messages clear, concise, and descriptive
- Reference issue numbers when applicable: `Fix #123: Add error handling`

## Code Standards

### Python Style
- Follow PEP 8 style guidelines
- Use 4 spaces for indentation (no tabs)
- Maximum line length of 100 characters
- Use meaningful variable and function names
- Add docstrings to all public methods and classes

### Type Hints
- Use type hints for all function parameters and return values
- Ensure proper conversion of types (e.g., string IDs to integers)
- Example:
  ```python
  def fetch_match_json(self, match_id: int) -> dict:
      """
      Fetches match information.
      
      Args:
          match_id (int): The ID of the match
          
      Returns:
          dict: Match information
      """
      payload = {"matchid": int(match_id)}
      return self._api_request(url, payload)
  ```

### Documentation
- All public methods must have docstrings
- Include parameter descriptions, return values, and exceptions
- Add examples for complex methods
- Keep documentation up-to-date with code changes

## Testing

### Test Requirements
- All new features must include tests
- Bug fixes should include regression tests
- Aim for high test coverage of critical functionality
- Tests should be independent and repeatable

### Running Tests
- Run all tests before submitting a PR: `python -m unittest discover tests`
- Ensure all tests pass in your local environment
- Fix any failing tests before submitting your PR

### Test Structure
- Unit tests for individual functions and methods
- Integration tests for API endpoints
- Regression tests for critical functionality
- Mock external dependencies when appropriate

## API Changes

### Backward Compatibility
- Maintain backward compatibility when possible
- If breaking changes are necessary, document them clearly
- Consider deprecation warnings before removing functionality

### API Documentation
- Document all API endpoints and methods
- Include parameter descriptions, types, and examples
- Note any rate limits or usage restrictions
- Update documentation when API changes

## Versioning and Releases

### Semantic Versioning
- Follow [Semantic Versioning](https://semver.org/) (MAJOR.MINOR.PATCH)
- MAJOR: Incompatible API changes
- MINOR: Add functionality in a backward-compatible manner
- PATCH: Backward-compatible bug fixes

### Changelog
- Update the changelog for each release
- Group changes by type: Added, Changed, Deprecated, Removed, Fixed, Security
- Reference PR numbers and contributors

## Getting Help

If you have questions or need help with the contribution process:
- Open an issue on GitHub
- Ask for clarification in your PR
- Reach out to the maintainers

Thank you for contributing to fogis_api_client!
