
I stole this documentation from My Blog on SimpleCTO:
 - [Django Async Task Queue with Postgres](https://simplecto.com/djang-async-task-postgres-not-kafka-celery-redis/)

# Django Async Task Queue with Postgres (no Kafka, Rabbit MQ, Celery, or Redis)

Quickly develop async task queues with only django commands and postgresql. I dont need the complexity of Kafka, RabbitMQ, or Celery.

tldr; Let's talk about simple async task queues with Django Commands and PostgreSQL.

Simple Django Commands make excellent asynchronous workers that replace tasks otherwise done by Celery and other more complex methods. Minimal code samples are below.

I can run asynchronous tasks without adding Celery, Kafka, RabbitMQ, etc to my stack
Many projects use Celery successfully, but it is a lot to setup, manage, monitor, debug, and develop for. To send a few emails, push messages, or database cleanups feels like a long way to go for a ham sandwich.

Django gives us a very useful utility for running asynchronous tasks without the cognitive load and infrastructure overhead– namely, Commands.

I go a long way using only simple long-running Django Commands as the workers and Postgres as my queue. It means that in a simple Django, Postgres, Docker deployment I can run asynchronous tasks without adding more services to my stack.

The Django Command
In addition to serving web pages, Django Commands offer us a way to access the Django environment on the command line or a long-running process. Simply override a class, place your code inside, and you have bootstrapped your way to getting things done in a "side-car."

It is important to understand this is outside the processing context of the web application. It must therefore be managed separately as well. I like to use Docker and docker-compose for that.

sample docker-compose snipped of django task

```yaml
services:

  hello-world:
    image: hello-world-image
    name: hello-world
    restart: unless-stopped
    command: ./manage.py hello_world
```

The power and simplicity of a while loop and sleep function
Let's expand on the Command for a moment and explore the simple mechanism to keep this process long-lived.

A sample "hello world" Django Command

app/management/commands/hello_world.py

```python
from time import sleep
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Print Hello World every Hour'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting job..."))

        while True:
            self.stdout.write(self.style.SUCCESS(f"Hello, World."))
            do_the_work()
            sleep(3600) # sleep 1 hour
```

The command simply loops, executes commands, and sleeps for a number of seconds. For more frequent calls simply reduce the sleep time.

You should refer to the actual Django Docs here:

https://docs.djangoproject.com/en/3.1/howto/custom-management-commands/
Some more robust and deeper examples of the While/Do pattern
Yeah, I hate over-simplified examples, too. Here, have a look where I use this pattern in my open-source screenshot making application:

https://github.com/simplecto/screenshots/blob/master/src/shots/management/commands/screenshot_worker_ff.py
The Database-as-a-Queue
It is easy to track the state of your asynchronous tasks. Simply ask your database to manage it. On a high-level the process is something like this:

Query the database for a batch of tasks (1 to X at a time).
Of those tasks handed to the worker, update their status to "IN PROGRESS" and time stamp it.
Begin work on each task.
When task is finished, update the status of the task to "DONE".
If the task crashes then the database locks are released. The items are put back into the queue without changes. No harm, no foul.
The devil in the details, even in simple solutions (eg. Avoiding dead-locks)
If running multiple workers, it is possible that they pull the same tasks at the same time. In order to prevent this we ask the database to lock the rows when they are selected. This feature is not available on all databases.

I pretty much only use PostgreSQL, and doing so gives me access to some nice features like SKIP LOCKED when querying the database.

https://www.2ndquadrant.com/en/blog/what-is-select-skip-locked-for-in-postgresql-9-5/
However, we are not done yet. The smart and thoughtful Django devs brought this into the core:

https://docs.djangoproject.com/en/2.2/ref/models/querysets/#select-for-update
Make sure to read into the details on this. More devils inside.

Need more tasks? No problem.
Using skip-locked above, simply run more services with:

`docker-compose scale worker=3`

An exercise for the reader
There are a number of things left out of this article on purpose:

Exception handling
Retry failed tasks - what strategies (eg - exponential back-off)
Clean shutdown (handling SIGINT and friends)
Multi-threading (I don't prefer that, I just spin up more workers)
Monitoring / alerting
At-most-once / at-least-once semantics
Task idopentency
The Takeaway
This was a bit more to unpack than I thought. The takeaway here is that a While/Do loop can deliver a lot of value (at sufficient scale) before you have to start stacking more services, protocols, formats, and more.
