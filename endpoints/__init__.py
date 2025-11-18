from .agent_endpoints import router as agent_router
from .test_endpoints import router as test_router
from .health_endpoints import router as health_router
from .data_collection_endpoints import router as data_router
from .workflow_endpoints import router as workflow_router

__all__ = ["agent_router", "test_router", "health_router", "data_router", "workflow_router"]
