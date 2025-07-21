# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Django Reference Implementation - a production-ready Django SaaS template with organizations, invitations, and authentication. It follows a pragmatic approach to building multi-tenant applications with minimal dependencies.

## Architecture

### Core Apps Structure
- **config/**: Django project configuration (settings, URLs, WSGI/ASGI)
- **myapp/**: Base application with site configuration models, templates, and management commands
- **organizations/**: Complete multi-tenant organization system with invitations and user management

### Key Components
- **Authentication**: Uses django-allauth with 2FA support
- **Async Processing**: Custom worker pattern using Django management commands with PostgreSQL as task queue
- **Multi-tenancy**: Organization-based tenancy with invitation system
- **Templates**: Bootstrap 5 UI with dark mode support

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
uv run src/manage.py simple_async_worker
uv run src/manage.py send_email_confirmation
uv run src/manage.py send_email_invite
```

### Code Quality
```bash
# Run linting (uses ruff)
uv run ruff check .

# Run formatting
uv run ruff format .

# Run tests
uv run src/manage.py test
```

## Development Workflow

### Local Development
- Uses Docker Compose for services (PostgreSQL, Mailpit, S3Proxy)
- Django can run locally or in Docker
- Environment variables configured in `env` file (copy from `env.sample`)

### Testing
- Tests located in `*/tests/` directories
- Run with `uv run src/manage.py test`
- Covers models, views, and forms

### Worker System
- Custom async worker pattern using Django management commands
- Workers defined in `*/management/commands/`
- Uses PostgreSQL for task queue (no Redis/Celery required)
- Configure workers in `docker-compose.yml`

## Important Files

### Configuration
- `src/config/settings.py`: Main Django settings
- `pyproject.toml`: Project metadata and tool configuration (ruff, bandit)
- `docker-compose.yml`: Development services
- `Makefile`: Development automation commands

### Models
- `myapp/models/`: Site configuration and worker models
- `organizations/models.py`: Organization and invitation models

### Templates
- `templates/`: Global templates (base, auth, pages)
- `myapp/templates/`: App-specific templates
- `organizations/templates/`: Organization management templates

## Code Standards

### Linting
- Uses ruff with strict settings (line length: 120)
- Excludes tests and migrations from most checks
- Full rule set in `pyproject.toml`

### File Organization
- Apps follow Django conventions
- Models in `models/` directory (may be split into multiple files)
- Views in `views/` directory
- Management commands in `management/commands/`
- Templates in `templates/` with app namespacing

## Dependencies

### Dependency Management
- Uses `pyproject.toml` for dependency specification
- Production dependencies in `[project.dependencies]`
- Development dependencies in `[project.optional-dependencies.dev]`
- Install with `uv sync` or `uv sync --extra dev`

### Core Dependencies
- Django 5.2.3
- Python 3.12
- PostgreSQL 16
- django-allauth (authentication)
- django-bootstrap5 (UI)
- django-storages (S3 support)

### Development Dependencies
- ruff (linting/formatting)
- pre-commit (hooks)

## Environment Variables

Key environment variables (defined in `env` file):
- `DEBUG`: Development mode flag
- `SECRET_KEY`: Django secret key
- `BASE_URL`: Application base URL
- `DATABASE_URL`: PostgreSQL connection
- `AWS_*`: S3 configuration
- Email settings for django-allauth

## Deployment

- Docker-based deployment
- Heroku/Dokku ready with `Procfile`
- Static files served by Django or S3
- Uses environment variables for configuration
