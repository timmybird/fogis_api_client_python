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
   - Assign to a specific milestone when applicable
   - Set priority using labels (high, medium, low)

2. **Issue Tracking**:
   - Use GitHub Projects for tracking issue status
   - Update issue status when you start working on it
   - Add the "in progress" label when actively working on an issue
   - If you stop working on an issue, remove the "in progress" label and add a comment explaining why
   - Mention blockers or dependencies in comments
   - Regularly update long-running issues with progress reports

3. **Closing Issues**:
   - Issues should be closed when the corresponding PR is merged
   - Use closing keywords in PR descriptions (e.g., "Closes #123")
   - If an issue is invalid or duplicate, close with a clear explanation
   - Check if there are duplicate issues before creating new ones
   - When closing without fixing, provide a clear reason in a comment
   - For "won't fix" decisions, explain the rationale

### 6. Branch Cleanup

1. **After Merging**:
   - Always delete branches after merging
   - Use `git branch -d branch-name` for local branch deletion
   - Use `git push origin --delete branch-name` for remote branch deletion

2. **Stale Branches**:
   - Periodically review and clean up old branches
   - Consider deleting branches that haven't been updated in 3+ months
   - Before deleting, check if the branch contains unique work
   - If a branch contains valuable work, create an issue to track it

3. **Abandoned PRs**:
   - If a PR is abandoned, comment asking for status
   - After 2 weeks without response, consider closing the PR
   - Mention that the work can be continued in a new PR if needed

### 7. Pull Request Process
1. Create a PR through GitHub
2. Fill out the PR template completely
3. Wait for CI/CD to pass
4. Get at least one review
5. Address any feedback
6. Merge according to the branch type (squash for features/fixes, no squash for releases/hotfixes)
7. Delete the branch after merging

### 8. Commit Message Guidelines
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

#### Quick Setup (Recommended)

Use our setup script to install and configure pre-commit hooks with all necessary dependencies:

```bash
./setup_precommit.sh
```

This script will:
- Install pre-commit and all required dependencies
- Set up the hooks
- Verify the installation works correctly
- Provide troubleshooting guidance

#### Manual Setup

If you prefer to set up manually:

1. Install pre-commit:
   ```bash
   pip install pre-commit
   ```

2. Install the hooks:
   ```bash
   pre-commit install
   ```

3. Install additional dependencies required by hooks:
   ```bash
   pip install pytest pytest-cov types-requests
   ```

#### What the Hooks Do

Pre-commit hooks will:
- Format your code with Black and isort (line length 127 to match CI/CD)
- Check for common issues with flake8
  - Note: We ignore whitespace before ':' (E203) for Black compatibility
  - Note: We ignore lazy string interpolation (F541) as it's not a significant gain for this project
- Verify type hints with mypy
- Run unittest tests to ensure they pass (compatible with the project's test suite)
- Optionally run pytest tests (disabled by default)
- Optionally check documentation freshness (disabled by default)

#### Running Hooks Manually

To run all hooks on all files:
```bash
pre-commit run --all-files
```

To run a specific hook:
```bash
pre-commit run black --all-files
```

#### Troubleshooting Common Issues

1. **Black/isort formatting issues**:
   - These hooks will automatically fix formatting
   - After they run, add the changes and commit again

2. **Flake8 linting issues**:
   - Follow the error messages to fix style issues
   - Common fixes: remove unused imports, fix line length, add docstrings

3. **Mypy type checking issues**:
   - Add proper type hints to function parameters and return values
   - For third-party libraries without type hints, use `# type: ignore` comments

4. **Test failures**:
   - Run the failing test individually to debug: `pytest tests/test_file.py::test_function -v`
   - Fix the failing tests before committing

5. **Hook dependencies**:
   - If you get "command not found" errors, install the missing dependency
   - Run `./setup_precommit.sh` to install all required dependencies

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

4. **Using Markdown Files with GitHub CLI**:
   - Use markdown files for any complex GitHub content instead of inline text
   - This applies to PR descriptions, issue templates, comments, and more
   - Create markdown files with proper formatting, headings, lists, and code blocks
   - Use the GitHub CLI with the appropriate file option for different commands
   - Example workflows:

     **For PR descriptions:**
     ```bash
     # Create a markdown file with your PR description
     cat > pr_description.md << 'EOL'
     # PR Title

     ## Description
     This PR adds feature X which does Y.

     ## Changes
     - Added new class for X
     - Updated tests
     - Documentation updates

     ## Related Issue
     Fixes #123

     ## Type of Change
     - [x] New feature
     - [ ] Bug fix
     EOL

     # Create the PR using the file
     gh pr create --base develop --head your-branch --title "Add feature X" --body-file pr_description.md

     # Or update an existing PR
     gh pr edit 123 --body-file pr_description.md
     ```

     **For issue descriptions:**
     ```bash
     # Create a markdown file with your issue description
     cat > issue_description.md << 'EOL'
     ## Description
     Detailed description of the issue...

     ## Steps to Reproduce
     1. Step one
     2. Step two
     3. Step three

     ## Expected Behavior
     What should happen...

     ## Actual Behavior
     What actually happens...
     EOL

     # Create the issue using the file
     gh issue create --title "Bug: Something is broken" --body-file issue_description.md
     ```

     **For comments:**
     ```bash
     # Create a markdown file with your comment
     cat > comment.md << 'EOL'
     I've reviewed this PR and have the following feedback:

     ## Code Quality
     - The function on line 42 could be simplified
     - Good test coverage overall

     ## Suggestions
     ```python
     # Instead of this:
     def complex_function(x, y):
         return x * 2 + y * 3

     # Consider this:
     def complex_function(x, y):
         return 2*x + 3*y
     ```
     EOL

     # Add a comment to a PR
     gh pr comment 123 --body-file comment.md

     # Or add a comment to an issue
     gh issue comment 456 --body-file comment.md
     ```

   - Benefits of this approach:
     - Produces cleaner, better-formatted content
     - Allows you to version control your content
     - Makes it easier to reuse templates
     - Simplifies editing and reviewing before submission
     - Works better with AI-generated content

5. **Proper Issue Management**:
   - Create well-structured issues with clear descriptions
   - Add appropriate labels to issues (bug, enhancement, documentation, etc.)
   - Close issues when the corresponding PR is merged
   - Use closing keywords in PR descriptions (e.g., "Closes #123")
   - Check for duplicate issues before creating new ones
   - Update issue status when working on it
   - Add the "in progress" label when actively working on an issue
   - If you stop working on an issue, remove the "in progress" label and add a comment explaining why
   - Mention blockers or dependencies in comments
   - For "won't fix" decisions, explain the rationale

6. **Branch Cleanup**:
   - Always delete branches after merging
   - Remind users to delete branches after PRs are merged
   - Don't leave stale branches in the repository
   - Check if branches can be deleted when PRs are closed without merging
   - Use `git branch -d branch-name` for local branch deletion
   - Use `git push origin --delete branch-name` for remote branch deletion
   - Periodically review and clean up old branches

6. **PR Best Practices**:
   - Create descriptive PR titles
   - Include detailed descriptions of changes
   - Reference related issues
   - Add screenshots or examples when relevant
   - Respond to review comments promptly
   - Update PRs based on feedback
   - Rebase or merge with the target branch if conflicts arise
   - For complex PR descriptions, use a markdown file with the GitHub CLI:
     ```bash
     # Create a markdown file with your PR description
     echo "# PR Title\n\n## Description\nDetailed description here..." > pr_description.md

     # Create a PR using the file
     gh pr create --base develop --head your-branch --title "Your PR Title" --body-file pr_description.md

     # Or update an existing PR
     gh pr edit 123 --body-file pr_description.md
     ```

7. **Guidelines for AI Agents**:
   - Follow all the same guidelines as human contributors
   - Always use the markdown file approach for complex GitHub content (as described in section 4)
   - This is especially important for AI-generated content, which can be lengthy and complex
   - Generate well-structured, properly formatted code that follows the project's style guidelines
   - Provide detailed explanations of your changes in PR descriptions
   - Break down complex tasks into smaller, manageable PRs
   - Always run tests locally before submitting PRs
   - Be explicit about any limitations or potential issues in your implementation
   - When in doubt, ask for clarification rather than making assumptions
   - Consider creating templates for common tasks to ensure consistency

8. **Include Reminders in Issues and PRs**:
   - All issues and pull requests should include a reminder about following these guidelines
   - Issue templates and PR templates have checkboxes to confirm reading this document
   - When creating issues or PRs manually, include a link to this document
   - This ensures consistency across all contributions, regardless of who handles them

9. **Remind Users of the Process**:
   - If a user asks you to push directly to main, remind them of the GitFlow process
   - Suggest creating a proper branch and PR instead
   - Reference this document when explaining the process

## Getting Help

If you have questions or need help with the contribution process:
- Open an issue on GitHub
- Ask for clarification in your PR
- Reach out to the maintainers

Thank you for contributing to fogis_api_client!
