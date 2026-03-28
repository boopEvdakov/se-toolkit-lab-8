"""MCP server exposing observability tools for logs and traces."""

from __future__ import annotations

import asyncio
import json
from typing import Any

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from pydantic import BaseModel, Field

from .settings import Settings


class LogsQuery(BaseModel):
    query: str = Field(default="_stream:{app=\"backend\"} | level=\"error\"", description="VictoriaLogs query string")
    time_range: str = Field(default="1h", description="Time range like '1h', '24h', '7d'")


class TracesQuery(BaseModel):
    service: str = Field(default="backend", description="Service name to filter traces")
    time_range: str = Field(default="1h", description="Time range like '1h', '24h', '7d'")
    limit: int = Field(default=10, ge=1, le=100, description="Max traces to return")


class HealthCheck(BaseModel):
    pass


ToolPayload = BaseModel


def _text(data: Any) -> list[TextContent]:
    if isinstance(data, BaseModel):
        payload = data.model_dump()
    else:
        payload = data
    return [TextContent(type="text", text=json.dumps(payload, ensure_ascii=False, default=str))]


def create_server(settings: Settings) -> Server:
    server = Server("observability")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="obs_logs",
                description="Query VictoriaLogs for log entries. Use level=\"error\" to find errors.",
                inputSchema=LogsQuery.model_json_schema(),
            ),
            Tool(
                name="obs_traces",
                description="Query VictoriaTraces for distributed traces of a service.",
                inputSchema=TracesQuery.model_json_schema(),
            ),
            Tool(
                name="obs_health",
                description="Check if VictoriaLogs and VictoriaTraces are healthy.",
                inputSchema=HealthCheck.model_json_schema(),
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
        try:
            async with httpx.AsyncClient() as client:
                if name == "obs_logs":
                    args = LogsQuery.model_validate(arguments or {})
                    result = await query_logs(client, settings.victorialogs_url, args.query, args.time_range)
                    return _text(result)

                elif name == "obs_traces":
                    args = TracesQuery.model_validate(arguments or {})
                    result = await query_traces(client, settings.victoriatraces_url, args.service, args.time_range, args.limit)
                    return _text(result)

                elif name == "obs_health":
                    result = await check_health(client, settings.victorialogs_url, settings.victoriatraces_url)
                    return _text(result)

                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]

        except Exception as exc:
            return [TextContent(type="text", text=f"Error: {type(exc).__name__}: {exc}")]

    _ = list_tools, call_tool
    return server


async def query_logs(client: httpx.AsyncClient, base_url: str, query: str, time_range: str) -> dict:
    """Query VictoriaLogs."""
    url = f"{base_url}/select/logsql/query"
    params = {"query": query, "time": time_range}
    response = await client.get(url, params=params, timeout=30.0)
    response.raise_for_status()
    return {"logs": response.text[:5000]}  # Limit response size


async def query_traces(client: httpx.AsyncClient, base_url: str, service: str, time_range: str, limit: int) -> dict:
    """Query VictoriaTraces."""
    url = f"{base_url}/api/search"
    params = {"service": service, "time": time_range, "limit": limit}
    response = await client.get(url, params=params, timeout=30.0)
    response.raise_for_status()
    return {"traces": response.json() if response.text else []}


async def check_health(client: httpx.AsyncClient, logs_url: str, traces_url: str) -> dict:
    """Check observability stack health."""
    result = {"victorialogs": "unknown", "victoriatraces": "unknown"}

    try:
        response = await client.get(f"{logs_url}/health", timeout=5.0)
        result["victorialogs"] = "healthy" if response.status_code == 200 else "unhealthy"
    except Exception:
        result["victorialogs"] = "unhealthy"

    try:
        response = await client.get(f"{traces_url}/health", timeout=5.0)
        result["victoriatraces"] = "healthy" if response.status_code == 200 else "unhealthy"
    except Exception:
        result["victoriatraces"] = "unhealthy"

    return result


async def main() -> None:
    settings = Settings()
    server = create_server(settings)
    async with stdio_server() as (read_stream, write_stream):
        init_options = server.create_initialization_options()
        await server.run(read_stream, write_stream, init_options)


if __name__ == "__main__":
    asyncio.run(main())
