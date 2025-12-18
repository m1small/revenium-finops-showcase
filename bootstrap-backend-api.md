# Meta-Specification: Modular Specification-Driven Backend API Development Framework

## Purpose

This specification teaches AI coding agents how to create backend APIs using modular, specification-driven development that enables humans to easily author and maintain specifications that generate production-quality API code.

---

## Core Principles

### 1. Human-Centric Design
- Specifications should be easy for humans to write, read, and modify
- Use natural language with structured formatting
- Minimize cognitive load through clear organization
- Enable rapid iteration without breaking existing specs

### 2. Single Source of Truth
- Each concept defined once, referenced everywhere
- Changes propagate automatically through the system
- No duplication, no inconsistencies
- Clear ownership of each specification file

### 3. Modular Architecture
- Separation of concerns (data models, endpoints, business logic, infrastructure)
- Reusable building blocks
- Independent versioning of modules
- Easy to add, modify, or remove components

### 4. Agent-Friendly Format
- Unambiguous specifications
- Clear implementation order
- Parseable formats (key-value, structured data)
- Explicit cross-references

### 5. Production Quality
- Complete specifications leave no ambiguity
- Built-in quality standards (security, performance, reliability)
- Validation and testing protocols
- Professional output by default

---

## Project Structure Template

```
api-project-name/
├── README.md                          # Project overview and methodology
├── SAFETY.md                          # Agent safety guidelines
├── plans/                             # Planning documents (optional)
│   └── architecture.md                # Architecture decisions
├── specs/                             # Specifications (READ-ONLY for agents)
│   ├── README.md                      # Navigation and implementation order
│   ├── project.md                     # Project metadata
│   ├── api-standards/                 # API design standards (reusable)
│   │   ├── response-formats.md
│   │   ├── error-codes.md
│   │   ├── authentication.md
│   │   ├── rate-limiting.md
│   │   └── versioning.md
│   ├── data-models/                   # Data model specifications
│   │   ├── model-1.md
│   │   ├── model-2.md
│   │   └── model-n.md
│   ├── endpoints/                     # API endpoint specifications
│   │   ├── endpoint-group-1/
│   │   │   ├── get-resource.md
│   │   │   ├── create-resource.md
│   │   │   └── update-resource.md
│   │   └── endpoint-group-n/
│   │       └── [endpoint-files].md
│   ├── business-logic/                # Business rules and workflows
│   │   ├── validation-rules.md
│   │   ├── workflow-1.md
│   │   └── workflow-n.md
│   └── requirements/                  # Cross-cutting concerns
│       ├── technical.md
│       ├── security.md
│       ├── performance.md
│       ├── monitoring.md
│       └── deployment.md
├── src/                               # Source code (agent workspace)
│   ├── README.md
│   ├── models/
│   ├── controllers/
│   ├── services/
│   ├── middleware/
│   ├── utils/
│   └── [generated-files]
├── tests/                             # Testing specifications and code
│   ├── validation.md
│   ├── unit/
│   ├── integration/
│   └── e2e/
└── docs/                              # API documentation
    ├── openapi.yaml (generated)
    └── deployment.md
```

---

## Specification File Templates

### Template 1: `README.md` (Root)

```markdown
# [API Project Name]

> [One-line description of what this API provides]

[Brief explanation of the API's purpose, domain, and approach]

## What This Demonstrates

- **[Key Feature 1]**: Description (e.g., RESTful resource management)
- **[Key Feature 2]**: Description (e.g., Authentication & authorization)
- **[Key Feature 3]**: Description (e.g., Data validation & error handling)

## The Workflow

📝 Specification → 🤖 Agent Generation → 👤 Human Review → ✅ Production

1. Write detailed requirements in `specs/`
2. AI agent generates API code matching specifications
3. Human verifies output quality and accuracy
4. Approved code tested and deployed

## Technical Stack

**Development Tools**
- AI Agent: Claude.ai (Sonnet 4.5)
- Version Control: [Git platform]
- Testing: [Testing framework]
- Deployment: [Deployment platform]

**Technology**
- Language: [Programming language]
- Framework: [API framework]
- Database: [Database system]
- Authentication: [Auth method]

**Approach**
- Methodology: Specification-driven development
- Human Role: Supervisor, reviewer, quality control
- Agent Role: Code generation, implementation
- Safety Model: Human-in-the-loop (HITL)

## Project Structure

[ASCII tree of directory structure]

## How to Use

1. **Write Specification** in `specs/` with clear requirements
2. **Generate Code** using AI agent with system prompt
3. **Review Output** for accuracy and quality
4. **Test** using automated test suites
5. **Deploy** and commit changes

## Key Learnings

- [Learning 1]
- [Learning 2]
- [Learning 3]

## Safety Features

✅ Human approval required for all changes  
✅ Agent scope bounded to specific folders  
✅ Full Git history for rollback capability  
✅ Documented procedures in SAFETY.md

---

**Project**: [Attribution]  
**Creators**: [Names]  
**Completed**: [Date]

*Built with AI assistance, supervised by humans.*
```

---

### Template 2: `SAFETY.md`

```markdown
# Agent Safety Guidelines 🛡️

## Purpose

This AI agent converts API specifications into code with human oversight.

## The Three Laws

1. **Human Approval Required**: Every change needs explicit review
2. **Bounded Scope**: Agent only modifies files in `src/` and `tests/`
3. **Read Before Write**: Agent must see current code before changes

## Approved Actions

✅ Read any file in `specs/`  
✅ Generate [language] code  
✅ Create/update API endpoints  
✅ Create/update data models  
✅ Create/update tests  
✅ Suggest improvements  
✅ Update files in `src/` and `tests/`

## Forbidden Actions

❌ Delete files without explicit permission  
❌ Modify `specs/` folder (read-only)  
❌ Modify `.git` configurations  
❌ Make changes without showing code first  
❌ Modify database schemas without approval  
❌ Change authentication/security logic without review  
❌ Deploy to production environments  
❌ Modify environment variables or secrets

## Human Responsibilities

- Review every line of generated code
- Test API endpoints before committing
- Verify security implementations
- Keep specifications clear and detailed
- Commit frequently to create rollback points
- Review database migrations carefully
- Validate authentication and authorization logic

## Emergency Recovery

If agent generates bad code:

1. Do NOT commit the changes
2. Do NOT deploy to any environment
3. If already committed, use Git history to restore previous version
4. Clarify the specification and regenerate
5. Document what went wrong to prevent recurrence
6. If database changes were made, restore from backup
```

---

### Template 3: `specs/README.md`

```markdown
# API Specifications

[Brief description of what this API provides]

## Structure

```
specs/
├── project.md              # Project overview
├── api-standards/          # API design standards
│   ├── response-formats.md
│   ├── error-codes.md
│   ├── authentication.md
│   └── [other-standards].md
├── data-models/            # Data model specs
│   ├── [model-files].md
├── endpoints/              # Endpoint specs
│   ├── [endpoint-groups]/
│   │   └── [endpoint-files].md
├── business-logic/         # Business rules
│   └── [logic-files].md
└── requirements/           # Requirements
    ├── technical.md
    ├── security.md
    └── performance.md
```

## Implementation Order

1. Read [`project.md`](project.md) for context
2. Read [`api-standards/`](api-standards/) for design standards
3. Read [`data-models/`](data-models/) for data structures
4. Read [`business-logic/`](business-logic/) for validation rules
5. Read [`endpoints/`](endpoints/) for API endpoints
6. Read [`requirements/`](requirements/) for constraints

## Testing

See [`../tests/validation.md`](../tests/validation.md) for testing criteria.

## Related

- Main: [`../README.md`](../README.md)
- Safety: [`../SAFETY.md`](../SAFETY.md)
- Source: [`../src/`](../src/)
```

---

### Template 4: `specs/project.md`

```markdown
# Project: [API Project Name]

## Overview
[2-3 sentence description of what this API provides and why it exists]

## Goals
1. [Primary goal - e.g., Provide secure access to user data]
2. [Secondary goal - e.g., Enable third-party integrations]
3. [Tertiary goal - e.g., Support high-volume transactions]

## Target Audience
- [Audience segment 1 - e.g., Mobile app developers]
- [Audience segment 2 - e.g., Web application clients]
- [Audience segment 3 - e.g., Internal microservices]

## Value Proposition
"[One sentence capturing the core value delivered]"

## Scope

**In Scope**:
- [Feature 1 - e.g., User authentication and authorization]
- [Feature 2 - e.g., CRUD operations for core resources]
- [Feature 3 - e.g., Real-time notifications]

**Out of Scope**:
- [Non-feature 1 - e.g., Payment processing]
- [Non-feature 2 - e.g., Email delivery]
- [Non-feature 3 - e.g., File storage]

## Technical Stack
- Language: [Programming language]
- Framework: [API framework]
- Database: [Database system]
- Cache: [Caching system]
- Message Queue: [Queue system if applicable]
- Authentication: [Auth method]

## API Design Philosophy
- RESTful principles
- Resource-oriented URLs
- Standard HTTP methods
- JSON request/response bodies
- Consistent error handling
- Versioned endpoints

## Contact
[Name] - [Email] - [Website]
```

---

### Template 5: API Standards Files

#### `specs/api-standards/response-formats.md`

```markdown
# Response Formats

## Success Response Structure

### Single Resource
```json
{
  "data": {
    "id": "string",
    "type": "string",
    "attributes": { ... }
  },
  "meta": {
    "timestamp": "ISO-8601 datetime"
  }
}
```

### Collection Response
```json
{
  "data": [
    {
      "id": "string",
      "type": "string",
      "attributes": { ... }
    }
  ],
  "meta": {
    "total": "integer",
    "page": "integer",
    "per_page": "integer",
    "timestamp": "ISO-8601 datetime"
  },
  "links": {
    "self": "string",
    "next": "string|null",
    "prev": "string|null"
  }
}
```

## Error Response Structure

```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": [ ... ],
    "timestamp": "ISO-8601 datetime"
  }
}
```

## HTTP Status Codes

### Success Codes
- 200: OK (successful GET, PUT, PATCH)
- 201: Created (successful POST)
- 204: No Content (successful DELETE)

### Client Error Codes
- 400: Bad Request (validation error)
- 401: Unauthorized (authentication required)
- 403: Forbidden (insufficient permissions)
- 404: Not Found (resource doesn't exist)
- 409: Conflict (resource conflict)
- 422: Unprocessable Entity (semantic error)
- 429: Too Many Requests (rate limit exceeded)

### Server Error Codes
- 500: Internal Server Error
- 502: Bad Gateway
- 503: Service Unavailable
- 504: Gateway Timeout

## Content Type
- Request: `application/json`
- Response: `application/json`
- Character encoding: UTF-8

## Pagination

### Query Parameters
- page: Page number (default: 1)
- per_page: Items per page (default: 20, max: 100)
- sort: Sort field (prefix with - for descending)

### Example
```
GET /api/v1/users?page=2&per_page=50&sort=-created_at
```

## Filtering

### Query Parameters
- filter[field]: Filter by field value
- search: Full-text search

### Example
```
GET /api/v1/users?filter[status]=active&search=john
```
```

#### `specs/api-standards/error-codes.md`

```markdown
# Error Codes

## Format
error-code: [DOMAIN]_[CATEGORY]_[SPECIFIC_ERROR]

## Authentication Errors (AUTH_*)
AUTH_MISSING_TOKEN: Authentication token not provided
AUTH_INVALID_TOKEN: Authentication token is invalid or expired
AUTH_INSUFFICIENT_PERMISSIONS: User lacks required permissions
AUTH_ACCOUNT_LOCKED: User account is locked
AUTH_ACCOUNT_DISABLED: User account is disabled

## Validation Errors (VAL_*)
VAL_REQUIRED_FIELD: Required field is missing
VAL_INVALID_FORMAT: Field format is invalid
VAL_OUT_OF_RANGE: Value is out of acceptable range
VAL_INVALID_TYPE: Field type is incorrect
VAL_DUPLICATE_VALUE: Value must be unique

## Resource Errors (RES_*)
RES_NOT_FOUND: Requested resource not found
RES_ALREADY_EXISTS: Resource already exists
RES_CONFLICT: Resource state conflict
RES_LOCKED: Resource is locked for editing
RES_DELETED: Resource has been deleted

## Business Logic Errors (BIZ_*)
BIZ_INSUFFICIENT_BALANCE: Insufficient account balance
BIZ_QUOTA_EXCEEDED: Usage quota exceeded
BIZ_INVALID_STATE: Operation not allowed in current state
BIZ_DEPENDENCY_MISSING: Required dependency not met

## System Errors (SYS_*)
SYS_INTERNAL_ERROR: Internal server error
SYS_DATABASE_ERROR: Database operation failed
SYS_EXTERNAL_SERVICE_ERROR: External service unavailable
SYS_TIMEOUT: Operation timed out

## Rate Limiting Errors (RATE_*)
RATE_LIMIT_EXCEEDED: Rate limit exceeded
RATE_QUOTA_EXCEEDED: Daily/monthly quota exceeded

## Error Response Example
```json
{
  "error": {
    "code": "VAL_REQUIRED_FIELD",
    "message": "Email address is required",
    "details": [
      {
        "field": "email",
        "issue": "missing"
      }
    ],
    "timestamp": "2024-12-18T07:00:00Z"
  }
}
```
```

#### `specs/api-standards/authentication.md`

```markdown
# Authentication

## Method
type: [Bearer Token / API Key / OAuth 2.0 / JWT]

## Header Format
```
Authorization: Bearer <token>
```

## Token Lifecycle
- Expiration: [duration, e.g., 1 hour]
- Refresh: [method, e.g., refresh token endpoint]
- Revocation: [method, e.g., logout endpoint]

## Authentication Endpoints

### Login
endpoint: POST /api/v1/auth/login
request-body:
```json
{
  "email": "string",
  "password": "string"
}
```
response-body:
```json
{
  "data": {
    "access_token": "string",
    "refresh_token": "string",
    "expires_in": "integer",
    "token_type": "Bearer"
  }
}
```

### Refresh Token
endpoint: POST /api/v1/auth/refresh
request-body:
```json
{
  "refresh_token": "string"
}
```

### Logout
endpoint: POST /api/v1/auth/logout
headers: Authorization: Bearer <token>

## Authorization

### Permission Model
- Role-based access control (RBAC)
- Resource-level permissions
- Action-based permissions (read, write, delete)

### Permission Check
- Verify authentication (valid token)
- Verify authorization (user has permission)
- Return 401 if not authenticated
- Return 403 if not authorized

## Security Requirements
- Passwords hashed with [algorithm, e.g., bcrypt]
- Tokens signed with [algorithm, e.g., HS256]
- HTTPS required for all endpoints
- Token stored securely (not in localStorage)
- Rate limiting on auth endpoints
```

#### `specs/api-standards/rate-limiting.md`

```markdown
# Rate Limiting

## Strategy
type: [Token bucket / Sliding window / Fixed window]

## Limits

### By Authentication Status
unauthenticated: [requests] per [time period]
authenticated: [requests] per [time period]
premium: [requests] per [time period]

### By Endpoint Type
read-operations: [requests] per [time period]
write-operations: [requests] per [time period]
expensive-operations: [requests] per [time period]

## Response Headers
```
X-RateLimit-Limit: [maximum requests]
X-RateLimit-Remaining: [remaining requests]
X-RateLimit-Reset: [unix timestamp]
```

## Rate Limit Exceeded Response
status-code: 429
response-body:
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again in [seconds] seconds.",
    "details": {
      "limit": "integer",
      "remaining": 0,
      "reset_at": "ISO-8601 datetime"
    }
  }
}
```

## Retry Strategy
- Client should respect Retry-After header
- Exponential backoff recommended
- Maximum retry attempts: [number]
```

#### `specs/api-standards/versioning.md`

```markdown
# API Versioning

## Strategy
type: URL path versioning

## Format
```
/api/v{major}/[resource]
```

## Examples
```
/api/v1/users
/api/v2/users
```

## Version Lifecycle

### Current Version
version: v1
status: stable
support-until: [date]

### Deprecated Versions
[version]: deprecated on [date], sunset on [date]

## Breaking Changes
- Changes to response structure
- Removal of fields
- Changes to authentication
- Changes to error codes

## Non-Breaking Changes
- Adding new endpoints
- Adding optional fields
- Adding new error codes
- Performance improvements

## Deprecation Process
1. Announce deprecation [timeframe] in advance
2. Add deprecation headers to responses
3. Update documentation
4. Provide migration guide
5. Sunset old version after [timeframe]

## Deprecation Headers
```
Deprecation: true
Sunset: [HTTP date]
Link: <[migration-guide-url]>; rel="deprecation"
```
```

---

### Template 6: Data Model Specification

#### `specs/data-models/[model-name].md`

```markdown
# [Model Name]

## Purpose
[One sentence: what this model represents]

## Schema

### Fields

#### id
type: [string/integer/uuid]
required: true
unique: true
description: Unique identifier

#### [field-name]
type: [string/integer/boolean/datetime/etc.]
required: [true/false]
unique: [true/false]
default: [value or null]
min-length: [value] (for strings)
max-length: [value] (for strings)
min-value: [value] (for numbers)
max-value: [value] (for numbers)
format: [email/url/uuid/etc.]
description: [Field description]

#### created_at
type: datetime
required: true
auto-generated: true
description: Timestamp of creation

#### updated_at
type: datetime
required: true
auto-generated: true
description: Timestamp of last update

## Relationships

### [relationship-name]
type: [one-to-one/one-to-many/many-to-many]
related-model: [model-name.md](model-name.md)
foreign-key: [field-name]
cascade-delete: [true/false]
description: [Relationship description]

## Indexes
- [field-name]: [unique/non-unique] index
- [field1, field2]: composite index

## Validation Rules

### Field-Level Validation
- [field-name]: [validation rule]
- [field-name]: [validation rule]

### Model-Level Validation
- [cross-field validation rule]
- [business logic validation rule]

## Example Instance

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "field_name": "value",
  "created_at": "2024-12-18T07:00:00Z",
  "updated_at": "2024-12-18T07:00:00Z"
}
```

## Database Considerations
- Table name: [table_name]
- Primary key: [field_name]
- Soft delete: [true/false]
- Audit trail: [true/false]

## Notes
[Any special considerations or implementation notes]
```

---

### Template 7: Endpoint Specification

#### `specs/endpoints/[group]/[operation]-[resource].md`

```markdown
# [Operation] [Resource]

## Endpoint
method: [GET/POST/PUT/PATCH/DELETE]
path: /api/v1/[resource-path]

## Purpose
[One sentence: what this endpoint does]

## Authentication
required: [true/false]
permissions: [list of required permissions]

## Rate Limiting
limit: [requests] per [time period]
scope: [per-user/per-ip/global]

## Request

### Path Parameters
#### [parameter-name]
type: [string/integer/uuid]
required: true
description: [Parameter description]
example: [example value]

### Query Parameters
#### [parameter-name]
type: [string/integer/boolean]
required: [true/false]
default: [value]
description: [Parameter description]
example: [example value]

### Request Headers
```
Content-Type: application/json
Authorization: Bearer <token>
```

### Request Body
```json
{
  "field_name": "type (description)",
  "field_name": "type (description)"
}
```

### Request Body Schema
#### [field-name]
type: [string/integer/boolean/object/array]
required: [true/false]
validation: [validation rules]
description: [Field description]

### Request Example
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "age": 30
}
```

## Response

### Success Response (200/201/204)
status-code: [200/201/204]

#### Response Headers
```
Content-Type: application/json
X-RateLimit-Limit: [value]
X-RateLimit-Remaining: [value]
```

#### Response Body
```json
{
  "data": {
    "id": "string",
    "type": "string",
    "attributes": { ... }
  },
  "meta": {
    "timestamp": "ISO-8601 datetime"
  }
}
```

#### Response Example
```json
{
  "data": {
    "id": "123",
    "type": "user",
    "attributes": {
      "name": "John Doe",
      "email": "john@example.com",
      "age": 30
    }
  },
  "meta": {
    "timestamp": "2024-12-18T07:00:00Z"
  }
}
```

### Error Responses

#### 400 Bad Request
```json
{
  "error": {
    "code": "VAL_REQUIRED_FIELD",
    "message": "Email address is required",
    "details": [
      {
        "field": "email",
        "issue": "missing"
      }
    ]
  }
}
```

#### 401 Unauthorized
```json
{
  "error": {
    "code": "AUTH_INVALID_TOKEN",
    "message": "Authentication token is invalid or expired"
  }
}
```

#### 404 Not Found
```json
{
  "error": {
    "code": "RES_NOT_FOUND",
    "message": "Resource not found"
  }
}
```

## Business Logic

### Validation
- [Validation rule 1]
- [Validation rule 2]
- [Validation rule 3]

### Processing Steps
1. [Step 1]
2. [Step 2]
3. [Step 3]

### Side Effects
- [Side effect 1 - e.g., Send notification email]
- [Side effect 2 - e.g., Update cache]
- [Side effect 3 - e.g., Log audit trail]

## Database Operations
- [Operation 1 - e.g., INSERT into users table]
- [Operation 2 - e.g., UPDATE user_stats table]

## Dependencies
- Data Models: [model-1.md](../../data-models/model-1.md)
- External Services: [service name]
- Other Endpoints: [endpoint.md](../other/endpoint.md)

## Testing Considerations
- [Test case 1]
- [Test case 2]
- [Test case 3]

## Performance Considerations
- Expected response time: <[value]ms
- Database query optimization: [notes]
- Caching strategy: [notes]

## Notes
[Any special considerations or implementation notes]
```

---

### Template 8: Business Logic Specification

#### `specs/business-logic/validation-rules.md`

```markdown
# Validation Rules

## Global Validation Rules

### String Fields
- Trim whitespace before validation
- Reject empty strings for required fields
- Maximum length: [value] characters (unless specified)
- Sanitize HTML/script tags

### Email Fields
- Format: RFC 5322 compliant
- Lowercase normalization
- Domain validation
- Disposable email detection: [enabled/disabled]

### Password Fields
- Minimum length: [value] characters
- Require uppercase: [true/false]
- Require lowercase: [true/false]
- Require numbers: [true/false]
- Require special characters: [true/false]
- Reject common passwords: [true/false]

### Numeric Fields
- Type validation (integer/float)
- Range validation
- Precision validation (for decimals)

### Date/Time Fields
- Format: ISO 8601
- Timezone handling: [UTC/local/specified]
- Future date validation: [allowed/not allowed]
- Past date validation: [allowed/not allowed]

## Model-Specific Validation

### [Model Name]
- [Field name]: [Validation rule]
- [Field name]: [Validation rule]
- Cross-field validation: [Rule]

## Business Rule Validation

### [Rule Name]
condition: [When this rule applies]
validation: [What to validate]
error-code: [Error code if validation fails]
error-message: [Error message]

## Validation Error Response Format
```json
{
  "error": {
    "code": "VAL_INVALID_FORMAT",
    "message": "Validation failed",
    "details": [
      {
        "field": "email",
        "issue": "invalid_format",
        "message": "Email address format is invalid"
      }
    ]
  }
}
```
```

#### `specs/business-logic/[workflow-name].md`

```markdown
# [Workflow Name]

## Purpose
[Description of what this workflow accomplishes]

## Trigger
[What initiates this workflow]

## Preconditions
- [Condition 1]
- [Condition 2]
- [Condition 3]

## Steps

### Step 1: [Step Name]
action: [What happens]
validation: [What to validate]
on-success: [Next step]
on-failure: [Error handling]

### Step 2: [Step Name]
action: [What happens]
validation: [What to validate]
on-success: [Next step]
on-failure: [Error handling]

### Step N: [Step Name]
action: [What happens]
validation: [What to validate]
on-success: [Complete]
on-failure: [Error handling]

## Postconditions
- [Condition 1]
- [Condition 2]
- [Condition 3]

## Side Effects
- [Side effect 1]
- [Side effect 2]
- [Side effect 3]

## Error Handling
- [Error scenario 1]: [How to handle]
- [Error scenario 2]: [How to handle]
- [Error scenario 3]: [How to handle]

## Rollback Strategy
[How to rollback if workflow fails midway]

## Notifications
- [Who to notify]
- [When to notify]
- [What to include]

## Audit Trail
- [What to log]
- [Where to log]
- [Retention period]

## Performance Considerations
- Expected duration: [timeframe]
- Async processing: [true/false]
- Queue usage: [true/false]

## Dependencies
- Data Models: [model references]
- Endpoints: [endpoint references]
- External Services: [service names]
```

---

### Template 9: Requirements Specifications

#### `specs/requirements/technical.md`

```markdown
# Technical Requirements

## Technology Stack
language: [Programming language and version]
framework: [API framework and version]
database: [Database system and version]
cache: [Caching system and version]
message-queue: [Queue system if applicable]

## Project Structure
```
src/
├── models/          # Data models
├── controllers/     # Request handlers
├── services/        # Business logic
├── middleware/      # Middleware functions
├── utils/           # Utility functions
├── config/          # Configuration
└── app.js           # Application entry point
```

## Code Standards
- Follow [style guide name] style guide
- Use [linter name] for code linting
- Use [formatter name] for code formatting
- Maximum function length: [lines]
- Maximum file length: [lines]
- Comment complex logic
- Use meaningful variable names

## Dependency Management
- Lock file required: [true/false]
- Dependency audit: [frequency]
- Update strategy: [conservative/moderate/aggressive]

## Environment Configuration
- Use environment variables for configuration
- Never commit secrets to version control
- Support multiple environments (dev, staging, prod)
- Configuration validation on startup

## Logging
- Log level: [debug/info/warn/error]
- Log format: [JSON/text]
- Log destination: [console/file/service]
- Include request ID in all logs
- Log all errors with stack traces
- Log authentication attempts
- Log slow queries (>[value]ms)

## Error Handling
- Catch all errors at top level
- Return consistent error format
- Never expose internal errors to clients
- Log all errors with context
- Use custom error classes

## Database
- Use migrations for schema changes
- Use connection pooling
- Use prepared statements (prevent SQL injection)
- Index frequently queried fields
- Implement soft deletes where appropriate

## API Documentation
- Generate OpenAPI/Swagger documentation
- Keep documentation in sync with code
- Include request/response examples
- Document all error codes

## Version Control
- Use semantic versioning
- Write meaningful commit messages
- Use feature branches
- Require code review before merge
- Tag releases

## Testing Requirements
- Unit test coverage: >[percentage]%
- Integration tests for all endpoints
- End-to-end tests for critical workflows
- Test error scenarios
- Test authentication/authorization
```

#### `specs/requirements/security.md`

```markdown
# Security Requirements

## Authentication & Authorization
- Implement secure authentication (see [authentication.md](../api-standards/authentication.md))
- Use strong password hashing ([algorithm])
- Implement token expiration
- Support token