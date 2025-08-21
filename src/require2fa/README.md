# Django Require 2FA

A production-ready Django app that enforces Two-Factor Authentication (2FA) across your entire application.

## Why This Exists

### The Django-Allauth Gap

Django-allauth provides excellent 2FA functionality, but **intentionally does not include** site-wide 2FA enforcement. This decision was made explicit in:

- **[PR #3710](https://github.com/pennersr/django-allauth/pull/3710)** - A middleware approach was proposed but **rejected** by the maintainer
- **[Issue #3649](https://github.com/pennersr/django-allauth/issues/3649)** - Community discussed various enforcement strategies, issue was **closed without implementation**

The django-allauth maintainer's position:
> "leave such functionality for individual projects to implement"

### The Enterprise Need

Many organizations need to:
- Enforce 2FA for **all users** (not optional)
- Configure 2FA requirements **at runtime** (not hardcoded)
- Support **SaaS/multi-tenant** scenarios with organization-level policies
- Maintain **audit trails** of security configuration changes

Since django-allauth won't provide this, there's a clear market need for a standalone solution.

## Our Solution

### What We Built

This app provides what the **rejected django-allauth PR attempted**, but with significant improvements:

| Feature | Rejected PR #3710 | Our Implementation |
|---------|------------------|-------------------|
| URL Matching | String prefix matching (vulnerable) | Proper Django URL resolution |
| Configuration | Hardcoded settings | Runtime admin configuration |
| Testing | Basic tests | 15 comprehensive security tests |
| Security | Known vulnerabilities | Production-hardened |
| Admin Protection | Exempt admin login | Proper 2FA for admin access |

### Key Security Features

- **Vulnerability Protection**: Fixed Issue #173 path traversal attacks
- **URL Resolution**: Uses Django's proper URL resolution instead of dangerous string matching
- **Configuration Validation**: Prevents dangerous Django settings misconfigurations
- **Comprehensive Testing**: 15 security tests covering edge cases, malformed URLs, and regression scenarios
- **Admin Security**: Removed admin login exemption (admins now require 2FA)

### Architecture

- **Django-Solo Pattern**: Runtime configuration via admin interface
- **Middleware Approach**: Site-wide enforcement without code changes
- **Allauth Integration**: Works seamlessly with django-allauth's MFA system
- **Production Ready**: Data migrations, backward compatibility, zero downtime

## Usage

### Installation (Internal)

1. Add to `INSTALLED_APPS`:
   ```python
   INSTALLED_APPS = [
       # ...
       'require2fa',
       # ...
   ]
   ```

2. Add to `MIDDLEWARE`:
   ```python
   MIDDLEWARE = [
       # ...
       'require2fa.middleware.Require2FAMiddleware',
   ]
   ```

3. Run migrations:
   ```bash
   python manage.py migrate require2fa
   ```

### Configuration

Visit Django Admin → Two-Factor Authentication Configuration:
- **Require Two-Factor Authentication**: Toggle 2FA enforcement site-wide
- Changes take effect immediately (no restart required)

### How It Works

1. **Authenticated users** without 2FA are redirected to `/accounts/2fa/`
2. **Exempt URLs** (login, logout, 2FA setup) remain accessible
3. **Static/media files** are automatically detected and exempted
4. **Admin access** requires 2FA verification (security improvement)

## Testing

Run the comprehensive test suite:
```bash
python manage.py test require2fa
```

**15 security tests** covering:
- URL resolution edge cases
- Malformed URL handling
- Static file exemptions
- Admin protection
- Configuration security
- Regression tests for known vulnerabilities

## Future: Package Extraction

This app is designed to be **extracted into a standalone Django package**:

### Target Package Structure
```
django-require2fa/
├── pyproject.toml       # Modern Python packaging
├── README.md           # Installation & usage docs
├── LICENSE             # Open source license
├── CHANGELOG.md        # Version history
├── .github/workflows/  # CI/CD pipeline
└── require2fa/         # This app (copy-paste ready)
```

### Market Positioning
- **Fills django-allauth gap**: Provides what they explicitly won't
- **Enterprise-ready**: SaaS/multi-tenant 2FA enforcement
- **Security-first**: Production-hardened with comprehensive testing
- **Community need**: Addresses requests from Issues #3649 and PR #3710

## Contributing

When making changes:
1. **Security first** - any middleware changes need security review
2. **Comprehensive testing** - maintain the 15-test security suite
3. **Backward compatibility** - consider migration paths
4. **Documentation** - update this README with architectural decisions

## License

MIT License - ready for open source packaging and community adoption.
