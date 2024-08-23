# You made it this far, you must be serious.

Ok, lets get started. You're gonna need the usual things to get started:

# Requirements

  * Docker
  * Python 3.12
  * PostgreSQL
  * S3 Buckets (Provider of choice, we use Backblaze for production and
    S3Proxy[^1] for dev)
  * Domain with SSL certificate
  * `make` (seriously, you should have this)

[^1]: https://github.com/gaul/s3proxy


## Local development

  * PyCharm (not required but recommended)


## Before you get Started
If you are on x86 then you might need to edit the `docker-compose.yml`.

Remove the `platform: linux/arm64` from the `s3proxy` service.

---

# Wait, I'm a lazy bastard and just want to see it work.

I got you, Bae. But you really need to get the OpenAI API key. When you have
that come back.

Just run the following command:

```bash
make bootstrap-dev
```

It will :
- pull containers
- build the django container
- migrate the initial database
- prompt you to create a superuser.

_If you want to see all the things that does just peek at the `Makefile`._

NOTE: This does not start the crawlers. We will take that in the next step.

## Post bootstrap steps
Now we are ready to rock. Let's spin up the full dev environment.

```bash
make dev-start
```

Note, the workers will also start, but they do nothing. You will need to
activate them in the admin (See below).

When that is done point your browser to
[http://localhost:8000/admin](http://localhost:8000/admin), and you should
see the application running. Login as the superuser.

### Configure the site via the admin

1. [Site Name](http://localhost:8000/admin/sites/site/): Set up the name and
   domain in the admin.

2. [Global Site config](http://localhost:8000/admin/myapp/workerconfiguration/)
   Go to the "other" site configuration (yeah, yeah, I know) and check the
   following:
   1. `Worker Enabled` - This will enable the workers to run. Globally.
   2. `Worker sleep seconds` - This is the time in seconds that the workers
      will sleep between runs.
   3`JS Head`: Javascript to run in the head of every page. This will be
      where you will put analytics, for example.
   4`JS Body`: Javascript to run in the body of every page. This is the
      last tag in the body.
3. [Worker configs](http://localhost:8000/admin/myapp/workerconfiguration/):
   Manage the finer-grained settings for workers:
   1. `Is enabled`: Enable the worker.
   2. `Sleep seconds`: The time in seconds that the worker will sleep between
      runs.
   3. `Log Level`: The log level for the worker. (This is important for
      debugging in production)

---


## Production deployment

I currently use Dokku[^2] for deployment. It is a Heroku-like PaaS that you
can
run on your own servers. It is easy to use and has a lot of plugins.

Another option is Docker compose. You can use the `docker-compose.yml` file to
run the application locally or on a server.

  * Dokku (it should also work with Heroku)
  * Docker Compose
  * PostgreSQL
  * Domain with SSL certificate

 [^2]: https://dokku.com

---
