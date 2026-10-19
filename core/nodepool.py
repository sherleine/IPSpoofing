"""Node pool for the in-house mobile-proxy prototype.

Each exit node (a phone or PC on its OWN mobile-data connection) opens a reverse
SOCKS tunnel into the controller via chisel, which gives the controller a local
SOCKS5 port that exits through that node's cellular IP. This pool rotates
requests across those local ports and, on a block, rests a node for a cooldown
(default 10 seconds) before it is eligible again.

Run this on the controller (the public-IP VPS), where chisel puts each node's
reverse SOCKS proxy at 127.0.0.1:<port>.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from threading import Lock
from typing import List, Optional


@dataclass
class Node:
    name: str
    port: int                  # local SOCKS5 port on the controller (chisel reverse)
    resting_until: float = 0.0
    successes: int = 0
    failures: int = 0

    @property
    def proxy_url(self) -> str:
        return f"socks5://127.0.0.1:{self.port}"

    def resting(self, now: float) -> bool:
        return now < self.resting_until


class NodePool:
    def __init__(self, nodes: List[Node], *, cooldown_seconds: float = 10.0):
        self._nodes = list(nodes)
        self.cooldown = cooldown_seconds
        self._i = 0
        self._lock = Lock()

    def acquire(self) -> Optional[Node]:
        """Next node that isn't resting, round-robin. None if all are cooling down."""
        with self._lock:
            now = time.time()
            n = len(self._nodes)
            for _ in range(n):
                node = self._nodes[self._i % n]
                self._i += 1
                if not node.resting(now):
                    return node
            return None

    def report(self, node: Node, ok: bool) -> None:
        """Record the outcome. A failure rests the node for the cooldown (the 10s rule)."""
        with self._lock:
            if ok:
                node.successes += 1
            else:
                node.failures += 1
                node.resting_until = time.time() + self.cooldown

    def status(self) -> List[dict]:
        now = time.time()
        return [
            {
                "name": nd.name,
                "port": nd.port,
                "resting_for": round(max(0.0, nd.resting_until - now), 1),
                "ok": nd.successes,
                "fail": nd.failures,
            }
            for nd in self._nodes
        ]
