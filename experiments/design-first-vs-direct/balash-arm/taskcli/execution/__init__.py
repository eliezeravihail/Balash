"""The execution layer -- the application-layer home of running agent-assigned tasks.

The domain stays free of providers and result storage; this package holds the provider
seam and the service that composes "gate -> run -> record". The provider port and its
one local implementation live here, not in the domain, because ExecutionRequest and
ExecutionOutcome must not be domain types -- the provider receives and returns no
domain ids.
"""

from .provider import ExecutionOutcome, ExecutionRequest, LocalProvider, Provider
from .service import ExecutionService

__all__ = [
    "ExecutionOutcome",
    "ExecutionRequest",
    "LocalProvider",
    "Provider",
    "ExecutionService",
]
