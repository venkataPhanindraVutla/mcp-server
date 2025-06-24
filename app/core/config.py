from fastapi import FastAPI
from mcp.server.sse import SseServerTransport
from starlette.routing import Mount
from app.tools.tools import mcp
from app.api.routes import router
from app.dashboards.views import dashboard_router
from fastapi import Request as request
from app.core.database import create_db_and_tables


def create_app() -> FastAPI:
    app = FastAPI(
        title="Appointment MCP Server",
        description="Appointment booking system using FastAPI + MCP + SSE",
        version="0.1.0"
    )

    # Create tables
    create_db_and_tables()

    # Set up SSE
    sse = SseServerTransport("/messages/")
    app.router.routes.append(Mount("/messages", app=sse.handle_post_message))

    @app.get("/sse", tags=["MCP"])
    async def handle_sse(request: request):
        async with sse.connect_sse(request.scope, request.receive, request._send) as (
            read_stream,
            write_stream,
        ):
            await mcp._mcp_server.run(
                read_stream,
                write_stream,
                mcp._mcp_server.create_initialization_options(),
            )

    # Include routes
    app.include_router(router)
    app.include_router(dashboard_router)

    return app