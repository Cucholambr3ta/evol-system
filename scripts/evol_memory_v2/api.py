"""
Integration API for EDMS Memory v2.0.

REST API for external ecosystem (plugins, tools).
Provides read/write access to memory via HTTP endpoints.

Part of EDMS Memory v2.0 Phase 4 - Portability and Ecosystem.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Any
from urllib.parse import urlparse, parse_qs


@dataclass
class APIConfig:
    """API server configuration."""
    host: str = "127.0.0.1"
    port: int = 8766
    version: str = "v1"
    cors_origin: str = "*"
    auth_token: str = ""  # Empty = no auth required


class MemoryAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Memory API."""

    # Will be set by MemoryAPI class
    _memory_store: Any = None
    _api_config: APIConfig = None

    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        # Route requests
        if path == f"/api/{self._api_config.version}/health":
            self._send_json({"status": "ok", "timestamp": datetime.now().isoformat()})
        elif path == f"/api/{self._api_config.version}/memories":
            self._handle_list_memories(params)
        elif path.startswith(f"/api/{self._api_config.version}/memories/"):
            mem_id = path.split("/")[-1]
            self._handle_get_memory(mem_id)
        elif path == f"/api/{self._api_config.version}/entities":
            self._handle_list_entities(params)
        elif path.startswith(f"/api/{self._api_config.version}/entities/"):
            entity_name = path.split("/")[-1]
            self._handle_get_entity(entity_name)
        elif path == f"/api/{self._api_config.version}/search":
            self._handle_search(params)
        elif path == f"/api/{self._api_config.version}/stats":
            self._handle_stats()
        else:
            self._send_error(404, "Endpoint not found")

    def do_POST(self):
        """Handle POST requests."""
        parsed = urlparse(self.path)
        path = parsed.path

        # Read request body
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b""

        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self._send_error(400, "Invalid JSON")
            return

        # Route requests
        if path == f"/api/{self._api_config.version}/memories":
            self._handle_create_memory(data)
        elif path == f"/api/{self._api_config.version}/search":
            self._handle_search_post(data)
        else:
            self._send_error(404, "Endpoint not found")

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def _set_cors_headers(self):
        """Set CORS headers."""
        self.send_header("Access-Control-Allow-Origin", self._api_config.cors_origin)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def _send_json(self, data: dict[str, Any], status: int = 200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self._set_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def _send_error(self, status: int, message: str):
        """Send error response."""
        self._send_json({"error": message}, status)

    def _handle_list_memories(self, params: dict):
        """Handle list memories request."""
        limit = int(params.get("limit", [100])[0])
        memories = self._memory_store.get_all_memories(limit=limit)
        self._send_json({"memories": memories, "count": len(memories)})

    def _handle_get_memory(self, mem_id: str):
        """Handle get memory request."""
        memory = self._memory_store.get_memory(mem_id)
        if memory:
            self._send_json({"memory": memory})
        else:
            self._send_error(404, f"Memory not found: {mem_id}")

    def _handle_list_entities(self, params: dict):
        """Handle list entities request."""
        entity_type = params.get("type", [None])[0]
        entities = self._memory_store.get_all_entities(entity_type=entity_type)
        self._send_json({"entities": entities, "count": len(entities)})

    def _handle_get_entity(self, entity_name: str):
        """Handle get entity request."""
        entity = self._memory_store.get_entity(entity_name)
        if entity:
            self._send_json({"entity": entity})
        else:
            self._send_error(404, f"Entity not found: {entity_name}")

    def _handle_search(self, params: dict):
        """Handle search request."""
        query = params.get("q", [""])[0]
        limit = int(params.get("limit", [10])[0])

        if not query:
            self._send_error(400, "Query parameter 'q' required")
            return

        results = self._memory_store.search(query, limit=limit)
        self._send_json({"results": results, "count": len(results)})

    def _handle_search_post(self, data: dict):
        """Handle search POST request."""
        query = data.get("query", "")
        limit = data.get("limit", 10)

        if not query:
            self._send_error(400, "Query field required")
            return

        results = self._memory_store.search(query, limit=limit)
        self._send_json({"results": results, "count": len(results)})

    def _handle_create_memory(self, data: dict):
        """Handle create memory request."""
        text = data.get("text", "")
        metadata = data.get("metadata", {})

        if not text:
            self._send_error(400, "Text field required")
            return

        memory_id = self._memory_store.index(text, metadata)
        self._send_json({"id": memory_id, "created": True}, 201)

    def _handle_stats(self):
        """Handle stats request."""
        stats = self._memory_store.stats()
        self._send_json({"stats": stats})

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


class MemoryAPI:
    """
    Memory API server.

    Provides REST API for external ecosystem (plugins, tools).

    Usage:
        from evol_memory_v2.compat import MemoryV2
        mem = MemoryV2()

        api = MemoryAPI(mem)
        api.start()  # Runs in background thread

        # Or run in foreground
        api.run()
    """

    def __init__(
        self,
        memory_store: Any,
        config: APIConfig | None = None,
    ):
        self._memory_store = memory_store
        self._config = config or APIConfig()
        self._server: HTTPServer | None = None

    def _create_handler(self):
        """Create request handler with injected dependencies."""
        handler = MemoryAPIHandler
        handler._memory_store = self._memory_store
        handler._api_config = self._config
        return handler

    def start(self) -> dict[str, Any]:
        """
        Start API server in background thread.

        Returns:
            Dict with server info
        """
        import threading

        handler = self._create_handler()
        self._server = HTTPServer(
            (self._config.host, self._config.port),
            handler,
        )

        thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        thread.start()

        return {
            "status": "started",
            "host": self._config.host,
            "port": self._config.port,
            "version": self._config.version,
            "endpoints": self._get_endpoints(),
        }

    def stop(self):
        """Stop API server."""
        if self._server:
            self._server.shutdown()
            self._server = None

    def run(self):
        """Run API server in foreground."""
        handler = self._create_handler()
        self._server = HTTPServer(
            (self._config.host, self._config.port),
            handler,
        )

        print(f"Memory API running on http://{self._config.host}:{self._config.port}")
        print(f"Endpoints: {', '.join(self._get_endpoints())}")

        try:
            self._server.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down...")
            self.stop()

    def _get_endpoints(self) -> list[str]:
        """Get list of available endpoints."""
        v = self._config.version
        return [
            f"GET  /api/{v}/health",
            f"GET  /api/{v}/memories",
            f"GET  /api/{v}/memories/:id",
            f"POST /api/{v}/memories",
            f"GET  /api/{v}/entities",
            f"GET  /api/{v}/entities/:name",
            f"GET  /api/{v}/search?q=query",
            f"POST /api/{v}/search",
            f"GET  /api/{v}/stats",
        ]

    def stats(self) -> dict[str, Any]:
        """Get API server statistics."""
        return {
            "status": "running" if self._server else "stopped",
            "host": self._config.host,
            "port": self._config.port,
            "version": self._config.version,
            "endpoints": len(self._get_endpoints()),
        }
