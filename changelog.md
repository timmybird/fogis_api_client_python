# Changelog

## [0.0.11] - 2025-04-11

### Changed
- Reverted to v0.0.5 codebase due to critical issues in later versions
- Created CHANGES_SINCE_V0.0.5.md to document features that need to be re-implemented

## [0.0.10] - 2025-04-08

### Added
- Added the report_team_official_action method
- Fixed the CI/CD pipeline tests

## [0.0.9] - 2025-04-08

### Added
- Added tests for report_team_official_action method

## [0.0.8] - 2025-04-08

### Fixed
- Restored event_types dictionary that was accidentally removed

## [0.0.7] - 2025-04-08

### Fixed
- Ensure all IDs are handled as integers throughout the codebase

## [0.0.6] - 2025-04-08

### Added
- Implemented lazy login in FogisApiClient - now the client only logs in when needed, improving performance and reliability
- Added functionality to mark matches as done (mark_reporting_finished method)

### Improved
- Various improvements to the development environment (Docker setup, API Gateway, Swagger UI)
- Enhanced CI/CD pipeline and testing infrastructure

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
