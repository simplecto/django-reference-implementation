# Django Reference Implementation

<div style="text-align: center;">

![Django](https://img.shields.io/badge/Django-5.2.3-green.svg)
![Python](https://img.shields.io/badge/Python-3.12-blue.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)
![SQLite](https://img.shields.io/badge/SQLite-Testing-lightblue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen.svg)
![Ruff](https://img.shields.io/badge/Linting-Ruff-purple.svg)
![uv](https://img.shields.io/badge/Dependencies-uv-orange.svg)

**Production-ready Django SaaS template with organizations, invitations, and solid authentication built-in.**

[Features](#features) • [Quick Start](#quick-start) • [Architecture](#architecture) • [Why This Template?](#why-this-template) • [Documentation](#documentation) • [Contributing](#contributing) • [License](#license)

</div>

## Project Purpose
This project is a reference implementation for a production-ready Django
application with common use cases baked in. It is the base application that
Simple CTO uses for its projects, and we hope that it can be helpful to you.
It is quite opinionated as to its patterns, conventions, and library choices.

This is not prescriptive. That is to say that there are many ways to do
build applications, and this is ours. You are welcome to fork, copy, and
imitate. We stand on the shoulders of giants, and you are welcome to as
well.

## 🚀Quick Start

You are impatient, I get it. Here is the [quick start guide](docs/getting_started.md).

## 🌟 Features
You will see a number of use cases covered:

- **Organizations with Multi-tenancy** - Create, manage, and collaborate in organizations with fine-grained permissions
- **User Invitation System** - Complete invitation lifecycle with email notifications and secure onboarding
- **Modern Authentication** - Email verification, social logins, MFA/2FA support via django-allauth
- **Asynchronous Task Processing** - Simple worker pattern using PostgreSQL (no Celery/Redis/RabbitMQ required)
- **Docker-based Development** - Consistent development environment with Docker Compose
- **Production Ready** - Configured for deployment to Dokku or similar platforms
- **Strict Code Quality** - Ruff linting with strict settings, pre-commit hooks, GitHub Actions workflow
- **Comprehensive Testing** - Unit and integration tests covering critical functionality
- **Bootstrap 5 UI** - Clean, responsive interface with dark mode support
- **Admin interface customization** - Custom admin views for managing data
- **Health-check** - HEAD/GET used by Load Balancers and other services
- **Simple template tags** - Custom template tags for rendering common UI elements
- **Serving static assets** - from Django vs. needing nginx/apache
- **Storing assets in S3** - (optional)
- Local development using PyCharm and/or Docker
- Command line automation with `Makefile`
- Deployment with Docker and Docker Compose
- Deployment to Heroku, Dokku, etc using `Procfile`
- Opinionated linting and formatting with ruff
- Configuration and worker management inside the admin interface
- **Default pages** - for privacy policy, terms of service


## 🏗️ Architecture

This Django Reference Implementation follows a pragmatic approach to building SaaS applications:

- **Core Apps**:
  - `myapp`: Base application with site configuration models and templates
  - `organizations`: Complete multi-tenant organization system with invitations

- **Authentication**: Uses django-allauth for secure authentication with 2FA support

- **Async Processing**:
  - Custom worker pattern using Django management commands
  - Uses PostgreSQL as a task queue instead of complex message brokers
  - Simple to deploy, monitor, and maintain


## 🤔 Why This Template?

Unlike other Django templates that are either too simplistic or bloated with features, this reference implementation:

- **Solves Real Business Problems** - Built based on actual production experience, not theoretical patterns
- **Minimizes Dependencies** - No unnecessary packages that increase complexity and security risks
- **Focuses on Multi-tenancy** - Organizations and team collaboration are first-class citizens
- **Balances Structure and Flexibility** - Opinionated enough to get you started quickly, but not restrictive
- **Production Mindset** - Includes monitoring, error handling, and deployment configurations


## Project Principles

  * Use as little abstraction as possible. It should be easy to trace the code
    paths and see what is going on. Therefore, we will not be using too
    many advanced patterns, domains, and other things that create indirection.
  * [12-factor](https://12factor.net) ready
  * Simplicity, with a path forward for scaling the parts you need.
  * Single developer friendly
  * Single machine friendly
  * Optimize for developer speed

## Requirements

  * Docker
  * Python 3.12 or later
  * SMTP Credentials
  * S3 Credentials (optional)



## Customizing the docker-compose.yml

### Adding more workers

Below is the text used for adding a worker that sends SMS messages.

These workers are actually Django management commands that are run in a loop.

```
  simple_async_worker:
    build: .
    command: ./manage.py simple_async_worker
    restart: always
    env_file: env.sample
```


## Developing locally
PyCharm's integration with the debugger and Docker leaves some things to be desired.
This has changed how I work on the desktop. In short, I don't use docker for the django
part of development. I use the local development environment provided by MacOS.

### My Preferred developer stack

  * [PyCharm](https://jetbrains.com/pycharm/) (paid but community version is good, too)
  * [Postgres](https://postgresql.org) installed via homebrew or docker
  * [Mailpit](https://mailpit.axllent.org/) for SMTP testing *Installed via
    Homebrew or docker).
  * [s3proxy](https://github.com/andrewgaul/s3proxy) for S3 testing
    (installed via Homebrew or docker)
  * Virtual environment

---

## 🔄 Similar Projects
Thankfully there are many other Django template projects that you can use.
We all take inspiration from each other and build upon the work of others.
If this one is not to your taste, then there are others to consider:

### Free / OpenSource
  * [cookiecutter-django](https://github.com/cookiecutter/cookiecutter-django)
  * [django-superapp](https://github.com/django-superapp/django-superapp)
  * [SaaS Boilerplate](https://github.com/apptension/saas-boilerplate)
  * [Django Ship](https://www.djangoship.com)
  * [Djast](https://djast.dev/)
  * [Lithium](https://github.com/wsvincent/lithium)
  * [Django_Boilerplate_Free](https://github.com/cangeorgecode/Django_Boilerplate_Free)
  * [Quickscale](https://github.com/Experto-AI/quickscale)
  * [Hyperion](https://github.com/eriktaveras/django-saas-boilerplate)

### Paid
  * [SaaS Pegasus](https://www.saaspegasus.com/)
  * [SlimSaaS](https://slimsaas.com/)
  * [Sneat](https://themeselection.com/item/sneat-dashboard-pro-django/)

*NOTE: These are not endorsements of these projects. Just examples of other
ways to get started with Django.*

## 📚 Documentation

- [Getting Started Guide](docs/getting_started.md)
- [Manifesto](docs/manifesto.md)
- [Organizations](src/organizations/docs/README.md)
- [Asynchronous Tasks](docs/async_tasks.md)


## 🤝 Contributing

Contributions are welcome. Simply fork, submit a pull request, and explain
what you would like to fix/improve.

## 📜 License

[MIT License](LICENSE)

---

<div style="text-align: center; margin-top: 20px;">
  <p>If this project helps you, please consider giving it a star ⭐</p>
  <p>Developed and maintained by <a href="https://simplecto.com">SimpleCTO</a></p>
</div>
