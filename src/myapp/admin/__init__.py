"""Admin module for the myapp app."""

from .site_configuation import SiteConfigurationAdmin
from .worker_configurations import WorkerConfigurationAdmin
from .worker_errors import WorkerErrorAdmin

__all__ = [
    "SiteConfigurationAdmin",
    "WorkerConfigurationAdmin",
    "WorkerErrorAdmin",
]
