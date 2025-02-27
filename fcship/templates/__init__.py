"""Templates package."""

from .api_templates import get_api_templates
from .domain_templates import get_domain_templates
from .project_templates import get_project_templates
from .repo_templates import get_repo_templates
from .service_templates import get_service_templates
from .test_templates import get_test_template

__all__ = [
    "get_api_templates",
    "get_domain_templates",
    "get_project_templates",
    "get_repo_templates",
    "get_service_templates",
    "get_test_template",
]
