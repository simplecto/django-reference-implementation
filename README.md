# Project Purpose
This project is a reference implementation for a production-ready Django
application with common use cases baked in. It is the base application that
Simple CTO uses for its projects, and we hope that it can be helpful to you.
It is quite opinionated as to its patterns, conventions, and library choices.

This is not prescriptive. That is to say that there are many ways to do
build applications, and this is ours. You are welcome to fork, copy, and
imitate. We stand on the shoulders of giants, and you are welcome to as
well.

# Use cases covered
You will see a number of use cases covered:

  * Async tasks (sending email and sms, health-check PUSH)
  * Sending e-mail (with SMTP)
  * User Login, Logout, Registration, password reset (email, social)
  * Admin interface customization
  * Health-check (HEAD/GET used by Load Balancers)
  * Simple template tags (quick image thumbnails)
  * Serving static assets from Django vs. needing nginx/apache


# Project Principles

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
  * Python 3.6 or later
  * SMTP Credentials
  * S3 Credentials (optional)

# Developing locally
PyCharm's integration with the debugger and Docker leaves some things to be desired.
This has changed how I work on the desktop. In short, I don't use docker for the django
part of development. I use the local development environment provided by MacOS.


# Customizing the docker-compose.yml

## Adding more workers

Below is the text used for adding a worker that sends SMS messages.

These workers are actually Django management commands that are run in a loop.

```
  simple_async_worker:
    build: .
    command: ./manage.py simple_async_worker
    restart: always
    env_file: env
```

# My Preferred developer stack

  * [PyCharm](https://jetbrains.com/pycharm/) (paid but community version is good, too)
  * [Postgres](https://postgresql.org) installed via homebrew or docker
  * [Mailpit](https://mailpit.axllent.org/) for SMTP testing *Installed via Homebrew or docker).
  * Virtual environment


# Other Django Template Projects
Thankfully there are many other Django template projects that you can use.
We all take inspiration from each other and build upon the work of others.
If this one is not to your taste, then there are others to consider:

  * [cookiecutter-django](https://github.com/cookiecutter/cookiecutter-django)
  * [django-superapp](https://github.com/django-superapp/django-superapp)
  * [SaaS Pegasus](https://www.saaspegasus.com/)
  * [SaaS Boilerplate](https://github.com/apptension/saas-boilerplate)

*NOTE: These are not endorsements of these projects. Just examples of other
ways to get started with Django.*


# Related projects (my own)

This project is tightly scoped to Django, but if you are interested
to learn more about a full production environment, then please refer
to this repo:

  * [simplecto/production-stack-template](https://github.com/simplecto/production-stack-template)

# Contributing

Contributions are welcome. Simply fork, submit a pull request, and explain
what you would like to fix/improve.

# License

This code is uner the MIT License. See LICENSE.txt
