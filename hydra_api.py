"""
hydra_api.py  —  Hydra Node API Extension
Project Hydra  ·  DATA-RELAY (Futro S930)

Stellt folgende Endpunkte bereit:
  GET  /hydra/status      — Systemstatus des Futro, bekannte Nodes
  POST /hydra/heartbeat   — Heartbeat-Empfang von Nodes
  GET  /hydra/nodes       — Liste aller registrierten Nodes (JSON)

Einbinden in routes.py:
  from hydra_api import *
"""

import time
import platform
import socket
from datetime import datetime
from flask import jsonify, request
from app import app

# ─────────────────────────────────────────────────────────────────────────────
# In-Memory Node-Registry
# (wird bei Neustart zurückgesetzt – reicht für den Betrieb)
# ─────────────────────────────────────────────────────────────────────────────

_node_registry: dict[str, dict] = {}
_server_start = time.time()


def _uptime_str(seconds: float) -> str:
    seconds = int(seconds)
    d, r = divmod(seconds, 86400)
    h, r = divmod(r, 3600)
    m, s = divmod(r, 60)
    parts = []
    if d: parts.append(f"{d}d")
    if h: parts.append(f"{h}h")
    if m: parts.append(f"{m}m")
    parts.append(f"{s}s")
    return " ".join(parts)


# ─────────────────────────────────────────────────────────────────────────────
# Endpunkte
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/hydra/status", methods=["GET"])
def hydra_status():
    """
    Gibt den aktuellen Status des Futro-Backends zurück.
    Wird von der MOTD und dem hydra-menu auf dem Pi abgefragt.
    """
    uptime = time.time() - _server_start
    active_nodes = [
        nid for nid, info in _node_registry.items()
        if time.time() - info.get("last_seen", 0) < 120   # aktiv = Heartbeat < 2 min
    ]

    return jsonify({
        "node":        "DATA-RELAY",
        "role":        "backend",
        "host":        socket.gethostname(),
        "platform":    platform.system(),
        "uptime":      _uptime_str(uptime),
        "uptime_sec":  int(uptime),
        "timestamp":   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "known_nodes": len(_node_registry),
        "active_nodes": len(active_nodes),
        "nodes":       active_nodes,
        "status":      "online",
    })


@app.route("/hydra/heartbeat", methods=["POST"])
def hydra_heartbeat():
    """
    Empfängt Heartbeats von Hydra-Nodes.
    Erwartet JSON: { "node_id": "...", "role": "...", "ip": "...", "uptime": "..." }
    """
    data = request.get_json(silent=True) or {}
    node_id = data.get("node_id", "UNKNOWN")

    _node_registry[node_id] = {
        "node_id":   node_id,
        "role":      data.get("role", "unknown"),
        "ip":        data.get("ip", request.remote_addr),
        "uptime":    data.get("uptime", "?"),
        "last_seen": time.time(),
        "last_seen_str": datetime.now().strftime("%H:%M:%S"),
        "events":    _node_registry.get(node_id, {}).get("events", 0) + 1,
    }

    return jsonify({"status": "ok", "registered": node_id})


@app.route("/hydra/nodes", methods=["GET"])
def hydra_nodes():
    """
    Gibt alle registrierten Nodes mit Status zurück.
    """
    now = time.time()
    result = []
    for nid, info in _node_registry.items():
        age = now - info.get("last_seen", 0)
        result.append({
            **info,
            "online": age < 120,
            "last_seen_ago": f"{int(age)}s ago",
        })
    result.sort(key=lambda x: x.get("last_seen", 0), reverse=True)
    return jsonify({"nodes": result, "count": len(result)})
