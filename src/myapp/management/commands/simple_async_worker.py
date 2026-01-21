from ._base import BaseWorkerCommand


class Command(BaseWorkerCommand):
    """Simple Async Worker."""

    help = "Simple Async Worker"
    NAME = "simple_async_worker"

    def run(self) -> None:
        """Run the worker."""
        self.logger.debug("I'm here, running things...")
