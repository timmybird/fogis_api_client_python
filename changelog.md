# Changelog

## [0.0.11] - 2025-04-11

### Changed
- Reverted to v0.0.5 codebase due to critical issues in later versions
- Created CHANGES_SINCE_V0.0.5.md to document features that need to be re-implemented


## [0.0.5] - 2025-03-14

### Fixed
- Completely revamped the entire filtering logic to use the `MatchListFilter` class for both server side and local filtering.

### Added
- `MatchListFilter` class for that passes a date filter to the API client and then does client-side filtering on the returned data.
- Filtering for status, age category, gender, and football type.

## [0.0.4] - 2025-03-05

### Added
- Added optional filter parameter for `fetch_matches_list_json`
- Added FilterBuilder class for creating filter parameters for `fetch_matches_list_json`
- Added `FogisFilterValidationError` exception class for handling invalid filter parameters.

## [0.0.3] - 2025-02-28

### Fixed
- Fixed file structure to allow proper installation and test execution.

## [0.0.2] - 2025-02-21

### Fixed
- Corrected package structure to allow proper installation and test execution.
- Added `pytest`, `pytest-mock`, `pytest-cov`, `flake8` as development dependencies.

### Added
- Changelog file to document releases.