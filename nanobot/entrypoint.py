#!/usr/bin/env python3
"""
Entrypoint for nanobot gateway in Docker.

Resolves environment variables into config.json at runtime,
then execs into 'nanobot gateway'.
"""

import json
import os
from pathlib import Path


def main():
    # Paths
    app_dir = Path("/app")
    nanobot_dir = app_dir / "nanobot"
    config_path = nanobot_dir / "config.json"
    # Write resolved config to /tmp for write access
    resolved_path = Path("/tmp/config.resolved.json")
    workspace_dir = nanobot_dir / "workspace"

    # Read base config
    with open(config_path, "r") as f:
        config = json.load(f)

    # Override from environment variables
    # LLM provider settings
    if llm_api_key := os.environ.get("LLM_API_KEY"):
        config["providers"]["custom"]["apiKey"] = llm_api_key

    if llm_api_base := os.environ.get("LLM_API_BASE_URL"):
        config["providers"]["custom"]["apiBase"] = llm_api_base

    if llm_model := os.environ.get("LLM_API_MODEL"):
        config["agents"]["defaults"]["model"] = llm_model

    # Gateway settings
    if gateway_host := os.environ.get("NANOBOT_GATEWAY_CONTAINER_ADDRESS"):
        config.setdefault("gateway", {})["host"] = gateway_host

    if gateway_port := os.environ.get("NANOBOT_GATEWAY_CONTAINER_PORT"):
        config.setdefault("gateway", {})["port"] = int(gateway_port)

    # MCP LMS server settings
    if "mcpServers" in config.get("tools", {}):
        if "lms" in config["tools"]["mcpServers"]:
            if lms_backend := os.environ.get("NANOBOT_LMS_BACKEND_URL"):
                config["tools"]["mcpServers"]["lms"]["env"][
                    "NANOBOT_LMS_BACKEND_URL"
                ] = lms_backend

            if lms_api_key := os.environ.get("NANOBOT_LMS_API_KEY"):
                config["tools"]["mcpServers"]["lms"]["env"]["NANOBOT_LMS_API_KEY"] = (
                    lms_api_key
                )

        # MCP Observability server settings
        if "obs" in config["tools"]["mcpServers"]:
            if logs_url := os.environ.get("NANOBOT_VICTORIALOGS_URL"):
                config["tools"]["mcpServers"]["obs"]["env"][
                    "NANOBOT_VICTORIALOGS_URL"
                ] = logs_url

            if traces_url := os.environ.get("NANOBOT_VICTORIATRACES_URL"):
                config["tools"]["mcpServers"]["obs"]["env"][
                    "NANOBOT_VICTORIATRACES_URL"
                ] = traces_url

    # Write resolved config
    with open(resolved_path, "w") as f:
        json.dump(config, f, indent=2)

    print(f"Using config: {resolved_path}")

    # Exec into nanobot gateway
    os.execvp(
        "nanobot",
        [
            "nanobot",
            "gateway",
            "--config",
            str(resolved_path),
            "--workspace",
            str(workspace_dir),
        ],
    )


if __name__ == "__main__":
    main()
