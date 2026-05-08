import os
import time
from typing import Dict, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Orders API", version="1.0.0")

_REQUEST_COUNT = 0
_ERROR_COUNT = 0
_LAST_LATENCY_MS = 0.0


class Order(BaseModel):
    customer_id: str
    amount: float


ORDERS: List[Dict[str, object]] = [
    {"id": "ord-001", "customer_id": "cust-001", "amount": 120.5, "status": "created"},
    {"id": "ord-002", "customer_id": "cust-002", "amount": 89.9, "status": "created"},
]


def _bug_mode() -> str:
    return os.getenv("BUG_MODE", "off").lower().strip()


def _record(start: float, error: bool = False) -> None:
    global _REQUEST_COUNT, _ERROR_COUNT, _LAST_LATENCY_MS
    _REQUEST_COUNT += 1
    if error:
        _ERROR_COUNT += 1
    _LAST_LATENCY_MS = round((time.time() - start) * 1000, 2)


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok", "service": "orders-api"}


@app.get("/orders")
def list_orders() -> Dict[str, object]:
    start = time.time()
    mode = _bug_mode()
    try:
        if mode == "latency":
            time.sleep(3)
        if mode == "error":
            raise HTTPException(status_code=500, detail="Simulated production bug")
        return {"orders": ORDERS, "count": len(ORDERS)}
    except Exception:
        _record(start, error=True)
        raise
    finally:
        if mode != "error":
            _record(start, error=False)


@app.post("/orders")
def create_order(order: Order) -> Dict[str, object]:
    start = time.time()
    new_order = {
        "id": f"ord-{len(ORDERS) + 1:03d}",
        "customer_id": order.customer_id,
        "amount": order.amount,
        "status": "created",
    }
    ORDERS.append(new_order)
    _record(start)
    return new_order


@app.get("/metrics")
def metrics() -> Dict[str, object]:
    error_rate = 0.0 if _REQUEST_COUNT == 0 else round(_ERROR_COUNT / _REQUEST_COUNT, 4)
    return {
        "request_count": _REQUEST_COUNT,
        "error_count": _ERROR_COUNT,
        "error_rate": error_rate,
        "last_latency_ms": _LAST_LATENCY_MS,
        "bug_mode": _bug_mode(),
    }
