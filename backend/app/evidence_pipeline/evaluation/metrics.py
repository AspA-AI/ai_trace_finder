from collections import Counter


def summarize_run(result: dict) -> dict:
    errors = result.get("errors", [])
    error_stages = Counter(item.get("stage", "unknown") for item in errors)
    discovered = result.get("discovered_source_count", 0)
    retrieved = result.get("retrieved_source_count", 0)
    return {
        "investigation_id": result.get("investigation_id"),
        "duration_ms": result.get("duration_ms"),
        "query_count": result.get("query_count", 0),
        "discovered_source_count": discovered,
        "retrieved_source_count": retrieved,
        "retrieval_success_rate": round(retrieved / discovered, 4) if discovered else 0.0,
        "observation_count": result.get("observation_count", 0),
        "error_count": len(errors),
        "errors_by_stage": dict(error_stages),
    }
