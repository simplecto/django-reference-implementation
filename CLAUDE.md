# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Data Room Application** - a secure file upload and management system for collecting customer data files for proof-of-concept development. Built on Django with django-allauth (2FA + SSO support), it enables internal teams to provision UUID-based upload endpoints for customers while maintaining complete privacy and audit trails.

## Architecture

### Core Apps Structure
- **config/**: Django project configuration (settings, URLs, WSGI/ASGI)
- **myapp/**: Base application with site configuration models and templates
- **dataroom/**: File upload system with customers, endpoints, and audit logging
- **require2fa/**: Two-factor authentication enforcement middleware

### Key Components
- **Authentication**: Uses django-allauth with 2FA support and SSO-ready (Okta)
- **File Management**: Local filesystem storage with UUID-based endpoint privacy
- **Admin Interface**: Django admin for internal team management of customers and endpoints
- **Audit Logging**: Complete tracking of file uploads, deletions, and staff downloads
- **UI Framework**: Tailwind CSS via Play CDN with dark mode support and Heroicons
- **Templates**: Minimal, professional upload interface with responsive design

## Data Room Features

### Customer & Endpoint Management
- **Customers**: Internal tracking of companies/projects receiving upload endpoints
- **Data Endpoints**: UUID-based upload URLs that don't expose customer information
- **Multiple Endpoints**: Each customer can have multiple endpoints for different POCs
- **Status Control**: Endpoints can be active, disabled, or archived

### File Upload System
- **Anonymous Upload**: Customers upload via UUID URL (no authentication required)
- **Security**: Filename sanitization, path traversal prevention, duplicate handling
- **Soft Delete**: Customers can request deletion (immediate with audit trail)
- **File Listing**: Customers can view all files uploaded to their endpoint

### Staff Features (Django Admin)
- **Customer Management**: Create customers with freeform notes
- **Endpoint Creation**: Generate new upload endpoints with one-click URL copying
- **File Downloads**: Secure download with automatic audit logging
- **Audit Dashboard**: View all file downloads and deletion activity

## Git Workflow for Claude Code

### Commit and Push Process
**IMPORTANT**: Always run pre-commit checks before committing to avoid sync issues.

```bash
# 1. Stage changes
git add .

# 2. Run pre-commit checks manually (prevents hook conflicts)
pre-commit run --all-files

# 3. Stage any fixes made by pre-commit
git add .

# 4. Commit and push atomically (prevents race conditions)
git commit -m "message" && git push origin master
```

**Why this matters:**
- Pre-commit hooks modify files AFTER commit creation
- This creates mismatches between local commit and working directory
- Leads to push rejections and rebase issues
- Running checks first eliminates these problems

**For documentation-only changes (optional):**
```bash
git commit -m "docs: message" --no-verify && git push origin master
```

## Common Commands

### Development Environment
```bash
# Bootstrap development environment
make dev-bootstrap

# Start development services
make dev-start

# Stop development services
make dev-stop

# Restart Django service
make dev-restart-django
```

### Database Operations
```bash
# Run migrations
make migrate

# Create superuser
make superuser

# Database snapshot and restore
make snapshot-local-db
make restore-local-db
```

### Django Management Commands
```bash
# Run with uv (uses local virtual environment)
uv run src/manage.py <command>

# Key management commands:
uv run src/manage.py migrate
uv run src/manage.py createsuperuser
uv run src/manage.py test
```

### Code Quality
```bash
# Run linting (uses ruff)
uv run ruff check .

# Run formatting
uv run ruff format .

# Run tests
uv run src/manage.py test

# Security scanning
uv run bandit -r src/

# Code complexity analysis
uv run radon cc src/ --show-complexity  # Cyclomatic complexity
uv run radon mi src/                     # Maintainability index
uv run radon raw src/                    # Raw metrics (SLOC, comments, etc.)

# Dead code detection
uv run vulture src/ --min-confidence 80  # Find unused code (high confidence)
uv run vulture src/ --min-confidence 60  # Find unused code (medium confidence)

# Type checking
cd src && DJANGO_SETTINGS_MODULE=config.settings uv run mypy dataroom/ myapp/ config/ --ignore-missing-imports --disable-error-code=var-annotated
```

## Development Workflow

### Local Development
- Uses Docker Compose for PostgreSQL and Mailpit
- Django runs locally or in Docker
- Environment variables configured in `env` file (copy from `env.sample`)
- File uploads stored in `src/media/uploads/{endpoint-uuid}/`

### Testing
- Tests located in `*/tests.py` or `*/tests/` directories
- Run with `uv run src/manage.py test`
- Covers models, views, upload/download functionality, and security

### URL Structure
- **Public (No Auth)**: `/upload/{uuid}/` - Customer upload page
- **Admin Only**: `/admin/` - Django admin interface
- **Staff Downloads**: Via Django admin actions (with audit logging)

## Important Files

### Configuration
- `src/config/settings.py`: Main Django settings
- `pyproject.toml`: Project metadata and tool configuration (ruff, bandit)
- `docker-compose.yml`: Development services (PostgreSQL, Mailpit)
- `Makefile`: Development automation commands
- `env`: Environment variables (copy from `env.sample`)

### Models
- `dataroom/models.py`: Customer, DataEndpoint, UploadedFile, FileDownload
- `myapp/models/`: Site configuration model
- `require2fa/models.py`: Two-factor configuration model

### Views & Templates
- `dataroom/views.py`: Upload page, file upload handler, delete handler
- `dataroom/templates/dataroom/`: Upload page, disabled/archived templates
- `dataroom/admin.py`: Complete admin configuration with download actions

### Tests
- `dataroom/tests.py`: Comprehensive model and view tests

## Code Standards

### Linting
- Uses ruff with strict settings (line length: 120)
- Excludes tests and migrations from most checks
- Full rule set in `pyproject.toml`

### File Organization
- Apps follow Django conventions
- Models in `models.py` or `models/` directory
- Views in `views.py` or `views/` directory
- Templates in `templates/` with app namespacing
- Admin configurations in `admin.py`

### Security
- **Filename Sanitization**: `sanitize_filename()` prevents path traversal
- **UUID Endpoints**: No customer information exposed in URLs
- **IP Tracking**: All uploads, deletes, and downloads log IP addresses
- **Soft Deletes**: Files marked deleted but retained for audit
- **Staff-Only Downloads**: File downloads only via authenticated admin

## Dependencies

### Dependency Management
- Uses `pyproject.toml` for dependency specification
- Production dependencies in `[project.dependencies]`
- Development dependencies in `[project.optional-dependencies.dev]`
- Install with `uv sync` or `uv sync --extra dev`

### Core Dependencies
- Django 5.2.5
- Python 3.12
- PostgreSQL 16
- django-allauth (authentication with MFA and SSO support)
- django-allauth-require2fa (2FA enforcement)
- django-solo (singleton models)
- Tailwind CSS (via Play CDN - no build process required)
- Heroicons (SVG icon library)

### Development Dependencies
- ruff (linting/formatting)
- pre-commit (hooks)
- mypy + django-stubs (type checking)
- bandit (security scanning)
- radon (complexity analysis)
- vulture (dead code detection)

## Environment Variables

Key environment variables (defined in `env` file):
- `DEBUG`: Development mode flag
- `SECRET_KEY`: Django secret key
- `BASE_URL`: Application base URL (used for upload URL generation)
- `DATABASE_URL`: PostgreSQL connection string
- `EMAIL_URL`: Email backend configuration (console, SMTP, etc.)

## File Storage

### Structure
```
src/media/
  uploads/
    {endpoint-uuid}/
      filename.ext
      filename-20250117143022-1.ext  # Duplicate with timestamp
```

### Handling
- Files stored in MEDIA_ROOT (`src/media/`)
- Organized by endpoint UUID for isolation
- Duplicate filenames auto-renamed with timestamp
- Soft deletes keep files on disk for audit/recovery

## Deployment

- Docker-based deployment ready
- Heroku/Dokku compatible with `Procfile`
- Static files served via WhiteNoise
- File uploads served securely via Django (for staff only)
- Uses environment variables for all configuration
- Database migrations handled via release phase

## Future Enhancements

- SSO integration with Okta (django-allauth is already SSO-ready)
- File size limits and validation
- Virus scanning integration
- Automated file expiration/archival
- Email notifications for uploads
- Download links for customers (with expiration)
