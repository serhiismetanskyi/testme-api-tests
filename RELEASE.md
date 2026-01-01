## Release Notes

### 0.1.0 – Initial Version

**Overview**
- Initial release of the automated test suite for TestMe Test Case Management API.

**Features**
- Authentication tests with CSRF token handling and session management.
- Test case CRUD operations with status transitions (PASS/FAIL).
- Statistics endpoint validation and list operations with pagination.
- Modular API clients built on Playwright's APIRequestContext.
- Pydantic models for type-safe request/response validation.
- Faker-based test data generation.

**Observability**
- HTTP logging to files and HTML reports (pytest-html).

**Infrastructure**
- Docker containerization with Docker Compose.
- UV package manager and Ruff for code quality.

