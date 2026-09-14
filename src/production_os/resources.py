from __future__ import annotations


def allocate_resources(schedule: dict, total_slots: int = 3) -> dict:
    if total_slots < 1:
        raise ValueError("total_slots must be >= 1")

    active = [
        item for item in schedule.get("work", [])
        if item.get("lane") in {"NOW", "PARALLEL"}
    ]
    active.sort(key=lambda item: (-float(item.get("score", 0)), int(item.get("effort", 1))))

    allocations: list[dict] = []
    remaining = total_slots
    for item in active:
        if remaining <= 0:
            break
        slots = 1
        allocations.append({
            "repository": item["repository"],
            "task": item["task"],
            "slots": slots,
            "lane": item["lane"],
            "score": item["score"],
        })
        remaining -= slots

    if remaining and allocations:
        allocations[0]["slots"] += remaining
        remaining = 0

    return {
        "schema_version": "production-os/resource-allocation/v1",
        "total_slots": total_slots,
        "allocated_slots": sum(item["slots"] for item in allocations),
        "allocations": allocations,
    }
