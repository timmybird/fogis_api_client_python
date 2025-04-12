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
4. Run all tests locally:
   ```bash
   python -m unittest discover tests
   python -m pytest integration_tests
   ```
5. Ensure pre-commit hooks pass: `pre-commit run --all-files`
6. Push your branch: `git push -u origin feature/name`
7. Create a PR to merge into develop
8. After review and approval, squash-merge into develop
9. Delete the feature branch

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

### 5. Issue Management

1. **Creating Issues**:
   - Use descriptive titles that clearly state the problem or feature
   - Include detailed descriptions with context and requirements
   - Add appropriate labels (enhancement, bug, documentation, etc.)
   - Add screenshots or examples when relevant
   - Reference related issues or PRs

2. **Issue Template**:
   ```markdown
   ## Description
   [Clear description of the issue or feature request]

   ## Current Behavior
   [What currently happens, if applicable]

   ## Expected Behavior
   [What should happen instead]

   ## Steps to Reproduce (for bugs)
   1. [First Step]
   2. [Second Step]
   3. [and so on...]

   ## Possible Solution (optional)
   [Any ideas for how to implement or fix]

   ## Context
   [Any relevant context, environment details, etc.]
   ```

3. **Closing Issues**:
   - Issues should be closed when the corresponding PR is merged
   - Use closing keywords in PR descriptions (e.g., "Closes #123")
   - If an issue is invalid or duplicate, close with a clear explanation
   - Check if there are duplicate issues before creating new ones

### 6. Pull Request Process

1. **Creating PRs**:
   - Create a PR through GitHub
   - Use descriptive titles that clearly state the changes
   - Fill out the PR template completely
   - Reference related issues (e.g., "Closes #123")
   - Add screenshots or examples when relevant

2. **PR Template**:
   ```markdown
   ## Description
   [Clear description of the changes made]

   ## Related Issue
   Closes #[issue number]

   ## Type of Change
   - [ ] Bug fix (non-breaking change that fixes an issue)
   - [ ] New feature (non-breaking change that adds functionality)
   - [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
   - [ ] Documentation update

   ## How Has This Been Tested?
   [Describe the tests that you ran to verify your changes]

   ## Checklist:
   - [ ] My code follows the style guidelines of this project
   - [ ] I have added tests that prove my fix is effective or that my feature works
   - [ ] New and existing unit tests pass locally with my changes
   - [ ] I have updated the documentation accordingly
   ```

3. **PR Review Process**:
   - Wait for CI/CD to pass
   - Get at least one review
   - Address any feedback
   - Merge according to the branch type (squash for features/fixes, no squash for releases/hotfixes)
   - Delete the branch after merging

### 7. Commit Message Guidelines
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

Before submitting a pull request, please ensure all tests pass:

1. **Run unit tests**:
   ```bash
   python -m unittest discover tests
   ```

2. **Run integration tests**:
   ```bash
   python -m pytest integration_tests
   ```

3. **When adding new features or modifying existing ones**:
   - Add or update unit tests in the `tests/` directory
   - Add or update integration tests in the `integration_tests/` directory
   - Ensure test coverage for both success and error cases

### Test Coverage Guidelines

- **Endpoint Changes**: If you add, modify, or remove an API endpoint, update all corresponding tests
- **Feature Changes**: Add tests for new features and update tests for modified features
- **Bug Fixes**: Add a test that reproduces the bug and verifies the fix

### Test Structure
- Unit tests for individual functions and methods
- Integration tests for API endpoints
- Regression tests for critical functionality
- Mock external dependencies when appropriate

### Pre-commit Hooks

We use pre-commit hooks to automate testing and code quality checks. This helps catch issues early and ensures consistent code quality.

1. Install pre-commit:
   ```bash
   pip install pre-commit
   ```

2. Install the hooks:
   ```bash
   pre-commit install
   ```

3. The hooks will now run automatically before each commit

Pre-commit hooks will:
- Format your code with Black and isort
- Check for common issues with flake8
- Verify type hints with mypy
- Run unit tests to ensure they pass

If any checks fail, the commit will be blocked until you fix the issues.

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

## Working with AI Assistants

When using AI assistants (like GitHub Copilot, Claude, ChatGPT, etc.) to help with development:

### For Human Developers

1. **Explicitly Instruct the AI**:
   - Ask the AI to read and follow the CONTRIBUTING.md guidelines
   - Provide the repository URL or paste relevant sections of the guidelines
   - Specify which branch to use as the base (usually develop, not main)

2. **Review AI-Generated Code Carefully**:
   - Ensure it follows the project's coding standards
   - Verify it includes appropriate tests
   - Check that it maintains backward compatibility
   - Look for potential edge cases the AI might have missed

3. **Follow the Same Process**:
   - AI-assisted code should go through the same PR process
   - Don't use AI to bypass code review or testing

### For AI Assistants

If you are an AI assistant reading this:

1. **Follow the GitFlow Process**:
   - Create branches from develop, not main
   - Use the correct branch naming conventions
   - Suggest squash merging for feature/fix branches
   - Recommend running pre-commit hooks before pushing changes

2. **Maintain Code Quality**:
   - Add comprehensive tests for all new code (both unit and integration tests)
   - Include proper type hints
   - Follow the project's coding style
   - Document all public methods and functions
   - Ensure code passes all pre-commit hooks

3. **Preserve Critical Functionality**:
   - Be cautious when modifying existing code
   - Ensure backward compatibility
   - Add regression tests for modified functionality
   - Verify that API endpoints still work as expected

4. **Proper Issue Management**:
   - Create well-structured issues with clear descriptions
   - Add appropriate labels to issues
   - Close issues when the corresponding PR is merged
   - Use closing keywords in PR descriptions (e.g., "Closes #123")
   - Check for duplicate issues before creating new ones
   - Update issue status when working on it

5. **Branch Cleanup**:
   - Always delete branches after merging
   - Remind users to delete branches after PRs are merged
   - Don't leave stale branches in the repository
   - Check if branches can be deleted when PRs are closed without merging

6. **PR Best Practices**:
   - Create descriptive PR titles
   - Include detailed descriptions of changes
   - Reference related issues
   - Add screenshots or examples when relevant
   - Respond to review comments

7. **Remind Users of the Process**:
   - If a user asks you to push directly to main, remind them of the GitFlow process
   - Suggest creating a proper branch and PR instead
   - Reference this document when explaining the process

## Getting Help

If you have questions or need help with the contribution process:
- Open an issue on GitHub
- Ask for clarification in your PR
- Reach out to the maintainers

Thank you for contributing to fogis_api_client!
