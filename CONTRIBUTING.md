# Contributing to fogis_api_client

Thank you for your interest in contributing to fogis_api_client! This document outlines the process and guidelines for contributing to this project.

## Git Workflow

We follow a modified GitFlow workflow to ensure that the main branch is always in a releasable state.

### 1. Branch Structure

- **main**: Production-ready code. Always stable and releasable.
- **develop**: Integration branch for features. Contains code for the next release.
- **feature/***:  Feature branches for new functionality.
- **fix/***:  Bug fix branches for issues.
- **release/***:  Release preparation branches.
- **hotfix/***:  Emergency fixes for production issues.

### 2. Never Push Directly to Main or Develop
- All changes must go through pull requests
- The main and develop branches are protected and require PR review
- This ensures code quality and prevents accidental breaking changes

### 3. Branch Naming Convention
- `feature/descriptive-name` for new features (branch from develop)
- `fix/issue-description` for bug fixes (branch from develop)
- `docs/what-is-documented` for documentation changes (branch from develop)
- `refactor/what-is-refactored` for code refactoring (branch from develop)
- `test/what-is-tested` for adding or updating tests (branch from develop)
- `release/x.y.z` for release preparation (branch from develop)
- `hotfix/issue-description` for urgent production fixes (branch from main)

### 4. GitFlow Process

#### For Features and Bug Fixes:
1. Create a branch from develop: `git checkout -b feature/name develop`
2. Make your changes
3. Write or update tests for your changes
4. Run all tests locally: `python -m unittest discover tests`
5. Push your branch: `git push -u origin feature/name`
6. Create a PR to merge into develop
7. After review and approval, squash-merge into develop
8. Delete the feature branch

#### For Releases:
1. When develop has enough features for a release, create a release branch: `git checkout -b release/x.y.z develop`
2. Update version numbers and perform final testing
3. Create a PR to merge into main
4. After review and approval, merge into main (no squash)
5. Tag the release on main: `git tag -a vx.y.z -m "Version x.y.z"`
6. Merge the release branch back into develop: `git checkout develop && git merge release/x.y.z`
7. Delete the release branch

#### For Hotfixes:
1. Create a hotfix branch from main: `git checkout -b hotfix/issue main`
2. Fix the issue and update version number (patch increment)
3. Create a PR to merge into main
4. After review and approval, merge into main (no squash)
5. Tag the hotfix on main: `git tag -a vx.y.z -m "Hotfix x.y.z"`
6. Merge the hotfix into develop as well: `git checkout develop && git merge hotfix/issue`
7. Delete the hotfix branch

### 5. Pull Request Process
1. Create a PR through GitHub
2. Fill out the PR template completely
3. Wait for CI/CD to pass
4. Get at least one review
5. Address any feedback
6. Merge according to the branch type (squash for features/fixes, no squash for releases/hotfixes)
7. Delete the branch after merging

### 6. Commit Message Guidelines
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
