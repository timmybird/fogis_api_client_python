# Changes Since v0.0.5

This document lists all the changes that have been made since v0.0.5, which will need to be re-implemented after reverting to v0.0.5.

## Closed Issues

1. **#25** - Add more endpoints to the HTTP wrapper
2. **#16** - Improve documentation for editing existing events
3. **#14** - Support cookie-based authentication
4. **#12** - Implement lazy login in FogisApiClient
5. **#9** - Implement mark as done

## Merged Pull Requests

1. **#41** - Fix: Add report_team_official_action method
2. **#40** - Add tests for report_team_official_action method
3. **#39** - Fix: Restore event_types dictionary that was accidentally removed
4. **#38** - Fix: Ensure all IDs are handled as integers throughout the codebase
5. **#37** - Improve CI/CD pipeline and Docker setup
6. **#31** - Add more endpoints to the HTTP wrapper (Issue #25)
7. **#30** - Rename HTTP wrapper to API Gateway
8. **#29** - Add OpenAPI/Swagger documentation
9. **#26** - Add query parameters support to HTTP wrapper
10. **#24** - Fix test issues and improve CI/CD pipeline
11. **#23** - Fix test issues
12. **#22** - Add pre-merge check script
13. **#21** - Fix Docker build issues
14. **#20** - Fix issues with Docker setup merge

## Commit History

1. **9a94ab3** - Bump version to 0.0.10
2. **bc521bf** - Add report_team_official_action method (#41)
3. **0931cc7** - Bump version to 0.0.9
4. **f10079e** - Add tests for report_team_official_action method (#40)
5. **2440065** - Bump version to 0.0.8
6. **4323f0e** - Fix: Restore event_types dictionary that was accidentally removed (#39)
7. **b5c3f4f** - Add GitHub Actions workflow for PyPI publishing
8. **e3d09f5** - Bump version to 0.0.7
9. **127ae65** - Fix: Ensure all IDs are handled as integers throughout the codebase (#38)
10. **4299226** - Revert changes pushed directly to main
11. **7dcc020** - Fix: Restore original report_match_result function and update fetch_match_result_json to match v0.0.5
12. **71b8b9c** - Fix: Add report_match_result function and ensure all match IDs are handled as integers
13. **80f68fd** - Bump version to 0.0.6 and update changelog
14. **6a95199** - Fix: Improve CI/CD pipeline and Docker setup, fix health check issues
15. **d820ec8** - Fix Swagger integration with API Gateway
16. **89e028a** - Rename HTTP wrapper to API Gateway (PR #30)
17. **af52879** - Add OpenAPI/Swagger documentation (PR #29)
18. **4ca2c4a** - Add query parameters support to HTTP wrapper (PR #26)
19. **135de3a** - Add more endpoints to the HTTP wrapper (Issue #25) (#31)
20. **e7decf7** - Fix test issues and improve CI/CD pipeline (#24)
21. **a37ee2f** - Fix test issues (#23)
22. **a0d1d30** - Add pre-merge check script (#22)
23. **9ce040d** - Fix Docker build issues (#21)
24. **276298e** - Fix issues with Docker setup merge (#20)

## Features to Re-implement

1. **Lazy Login** - Implement lazy login in FogisApiClient (Issue #12)
2. **Mark as Done** - Implement functionality to mark matches as done (Issue #9)
3. **Type Hints** - Ensure all IDs are handled as integers throughout the codebase (PR #38)
4. **API Gateway** - Rename HTTP wrapper to API Gateway and add more endpoints (PR #30, Issue #25)
5. **OpenAPI/Swagger Documentation** - Add OpenAPI/Swagger documentation (PR #29)
6. **Query Parameters Support** - Add query parameters support to HTTP wrapper (PR #26)
7. **CI/CD Pipeline** - Improve CI/CD pipeline and Docker setup (PR #37, PR #24)
8. **Pre-merge Check Script** - Add pre-merge check script (PR #22)
9. **Docker Setup** - Fix Docker build issues and setup (PR #21, PR #20)
10. **Tests** - Add tests for report_team_official_action method (PR #40)
11. **GitHub Actions Workflow** - Add GitHub Actions workflow for PyPI publishing

## Important Bug Fixes

1. **report_team_official_action Method** - Add the report_team_official_action method (PR #41)
2. **event_types Dictionary** - Restore event_types dictionary that was accidentally removed (PR #39)
3. **report_match_result Function** - Restore original report_match_result function (Commit 7dcc020)

## Notes

When re-implementing these features, it's important to:
1. Ensure that the core functionality of the API client remains stable and reliable
2. Add comprehensive tests for all new features
3. Maintain proper type hints and documentation
4. Ensure that the API client works correctly with the FOGIS API
5. Carefully review all changes to avoid introducing regressions
