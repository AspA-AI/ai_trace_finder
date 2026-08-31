from datetime import datetime, timezone
from time import perf_counter
from uuid import uuid4
import logging

from app.evidence_pipeline.contracts.inputs import PersonClues
from app.evidence_pipeline.discovery.query_planner import QueryPlanner
from app.evidence_pipeline.discovery.url_utils import canonicalize_url
from app.evidence_pipeline.persistence.in_memory import InMemoryEvidenceRepository
from app.evidence_pipeline.providers.protocols import DiscoveryProvider, SourceRetriever
from app.evidence_pipeline.retrieval.relevance import assess_relevance, matches_identity
from app.evidence_pipeline.extraction.normalization import normalize_observations
from app.evidence_pipeline.orchestration.artifacts import save_run_artifact


log = logging.getLogger("trace.pipeline")


class EvidencePipelineService:
    def __init__(
        self,
        discovery: DiscoveryProvider,
        retrievers: list[SourceRetriever],
        repository: InMemoryEvidenceRepository,
        planner: QueryPlanner | None = None,
        max_rounds: int = 2,
        max_queries_per_round: int = 5,
        max_results_per_query: int = 10,
        retry_attempts: int = 2,
        extractor=None,
        run_repository=None,
        source_cache_ttl_hours: int = 24,
    ) -> None:
        self.discovery = discovery
        self.retrievers = retrievers
        self.repository = repository
        self.planner = planner or QueryPlanner()
        self.max_rounds = max_rounds
        self.max_queries_per_round = max_queries_per_round
        self.max_results_per_query = max_results_per_query
        self.retry_attempts = max(1, retry_attempts)
        self.extractor = extractor
        self.run_repository = run_repository
        self.source_cache_ttl_hours = source_cache_ttl_hours

    async def _search_with_retries(self, query: str):
        last_error: Exception | None = None
        for attempt in range(1, self.retry_attempts + 1):
            try:
                log.info("discovery search started query=%r attempt=%d/%d", query, attempt, self.retry_attempts)
                return await self.discovery.search(query, self.max_results_per_query)
            except Exception as exc:
                last_error = exc
                log.warning("discovery search failed query=%r attempt=%d/%d error=%s", query, attempt, self.retry_attempts, exc)
        raise last_error or RuntimeError("discovery failed")

    async def run(self, clues: PersonClues, investigation_id: str | None = None, force_refresh: bool = False) -> dict:
        started_at = datetime.now(timezone.utc)
        started_clock = perf_counter()
        investigation_id = investigation_id or f"inv_{uuid4().hex[:12]}"
        queries = self.planner.plan(clues)
        run_id = f"run_{uuid4().hex[:12]}"
        trajectory = []
        log.info("investigation started investigation_id=%s run_id=%s query_count=%d force_refresh=%s", investigation_id, run_id, len(queries), force_refresh)

        def event(stage: str, action: str, status: str, details: dict | None = None) -> None:
            trajectory.append({
                "sequence": len(trajectory) + 1,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "stage": stage,
                "action": action,
                "status": status,
                "details": details or {},
            })

        event("planning", "planned_search", "completed", {
            "query_count": len(queries),
            "queries": [item.query for item in queries],
            "reason": "Expand the supplied clues into bounded search formulations.",
        })
        results = []
        errors = []
        attempted: set[str] = set()
        await self._create_investigation(investigation_id, clues, started_at)
        event("orchestration", "created_run", "completed", {"investigation_id": investigation_id, "run_id": run_id})

        for round_number in range(self.max_rounds):
            current = [query for query in queries if query.query not in attempted]
            current = current[: self.max_queries_per_round]
            if not current:
                event("discovery", "stopped", "completed", {"reason": "No unattempted queries remain."})
                break
            event("discovery", "started_round", "started", {"round": round_number + 1, "query_count": len(current)})
            log.info("discovery round started investigation_id=%s round=%d/%d query_count=%d", investigation_id, round_number + 1, self.max_rounds, len(current))
            for query in current:
                attempted.add(query.query)
                event("discovery", "search_query", "started", {"round": round_number + 1, "query": query.query})
                try:
                    found = await self._search_with_retries(query.query)
                    results.extend(found)
                    log.info("discovery search completed investigation_id=%s query=%r result_count=%d", investigation_id, query.query, len(found))
                    event("discovery", "search_query", "completed", {"query": query.query, "result_count": len(found), "retry_limit": self.retry_attempts})
                except Exception as exc:  # record provider errors; do not hide them
                    errors.append({"stage": "discovery", "query": query.query, "error": str(exc)})
                    event("discovery", "search_query", "failed", {"query": query.query, "error": str(exc), "retry_limit": self.retry_attempts})
            unique_count_before = len({canonicalize_url(str(result.url)) for result in results})
            if unique_count_before or round_number == self.max_rounds - 1:
                event("discovery", "stopped", "completed", {"reason": "Search produced discoverable URLs or the search budget was exhausted.", "unique_url_count": unique_count_before})
                break
            queries.extend(self.planner.follow_up(clues, attempted))
            event("discovery", "planned_follow_up", "completed", {"reason": "No unique URL was found; planner generated follow-up queries.", "query_count": len(queries)})

        unique_results = {}
        for result in results:
            unique_results[canonicalize_url(str(result.url))] = result
        log.info("discovery completed investigation_id=%s unique_url_count=%d", investigation_id, len(unique_results))

        observations = []
        cache_hits = 0
        cache_misses = 0
        for result in unique_results.values():
            url = str(result.url)
            retriever = next((item for item in self.retrievers if item.supports(url)), None)
            if retriever is None:
                errors.append({"stage": "retrieval", "url": url, "error": "no supported retriever"})
                event("retrieval", "skipped_source", "failed", {"url": url, "reason": "No provider adapter supports this URL."})
                continue
            try:
                source = None if force_refresh else await self.repository.get_cached(canonicalize_url(url), self.source_cache_ttl_hours)
                cache_hit = source is not None
                cache_hits += int(cache_hit)
                cache_misses += int(not cache_hit)
                if source is None:
                    source = await retriever.fetch(url, investigation_id)
                else:
                    source = source.model_copy(update={"investigation_id": investigation_id})
                relevance = assess_relevance(
                    clues,
                    url=url,
                    title=result.title,
                    text=source.content,
                )
                source = source.model_copy(
                    update={
                        "relevance_score": relevance.score,
                        "relevance_reasons": relevance.reasons,
                        "is_relevant": relevance.relevant,
                    }
                )
                if hasattr(self.repository, "sources"):
                    self.repository.sources[source.source_id] = source
                await self.repository.link_source(investigation_id, source, relevance.score, relevance.relevant, relevance.reasons)
                if not cache_hit:
                    await self.repository.save(source)
                event("retrieval", "evaluated_source", "completed", {"url": url, "source_id": source.source_id, "cache_hit": cache_hit, "relevance_score": relevance.score, "is_relevant": relevance.relevant, "relevance_reasons": relevance.reasons})
                log.info("retrieval completed investigation_id=%s source_id=%s cache_hit=%s relevant=%s score=%.3f", investigation_id, source.source_id, cache_hit, relevance.relevant, relevance.score)
                if self.extractor and relevance.relevant:
                    try:
                        extracted = normalize_observations(await self.extractor.extract(source, clues))
                        matched = [item for item in extracted if matches_identity(item.subject_text, clues) or matches_identity(item.quote, clues)]
                        observations.extend(matched)
                        event("extraction", "extracted_observations", "completed", {"source_id": source.source_id, "candidate_observation_count": len(extracted), "accepted_observation_count": len(matched)})
                        log.info("extraction completed investigation_id=%s source_id=%s extracted=%d accepted=%d", investigation_id, source.source_id, len(extracted), len(matched))
                    except Exception as exc:
                        errors.append({"stage": "extraction", "url": url, "error": str(exc)})
                        event("extraction", "extracted_observations", "failed", {"source_id": source.source_id, "error": str(exc)})
                elif not relevance.relevant:
                    event("extraction", "skipped_source", "completed", {"source_id": source.source_id, "reason": "Relevance gate rejected the source."})
            except Exception as exc:
                errors.append({"stage": "retrieval", "url": url, "error": str(exc)})
                event("retrieval", "evaluated_source", "failed", {"url": url, "error": str(exc)})

        if observations and hasattr(self.repository, "save_many"):
            log.info("persistence observations saving investigation_id=%s count=%d", investigation_id, len(observations))
            if hasattr(self.repository, "save_investigation_observations"):
                await self.repository.save_investigation_observations(investigation_id, observations)
            else:
                await self.repository.save_many(observations)
        completed_at = datetime.now(timezone.utc)
        event("orchestration", "completed_run", "completed", {"observation_count": len(observations), "retrieved_source_count": len(self._stored_sources(investigation_id)), "error_count": len(errors), "decision": "completed_with_errors" if errors else "completed"})
        result = {
            "investigation_id": investigation_id,
            "run_id": run_id,
            "status": "completed" if not errors else "completed_with_errors",
            "started_at": started_at.isoformat(),
            "completed_at": completed_at.isoformat(),
            "duration_ms": round((perf_counter() - started_clock) * 1000, 2),
            "queries_attempted": sorted(attempted),
            "query_count": len(attempted),
            "discovered_sources": [result.model_dump(mode="json") for result in unique_results.values()],
            "discovered_source_count": len(unique_results),
            "retrieved_sources": [
                {
                    "source_id": source.source_id,
                    "url": str(source.url),
                    "domain": source.domain,
                    "source_type": source.source_type,
                    "retrieval_method": source.retrieval_method,
                    "http_status": source.http_status,
                    "content_length": len(source.content),
                    "content_hash": source.content_hash,
                    "relevance_score": source.relevance_score,
                    "is_relevant": source.is_relevant,
                    "relevance_reasons": source.relevance_reasons,
                }
                for source in self._stored_sources(investigation_id)
            ],
            "retrieved_source_ids": [source.source_id for source in self._stored_sources(investigation_id)],
            "retrieved_source_count": len(self._stored_sources(investigation_id)),
            "cache_hits": cache_hits,
            "cache_misses": cache_misses,
            "force_refresh": force_refresh,
            "observation_count": len(observations),
            "errors": errors,
            "trajectory": trajectory,
        }
        trajectory_artifact = save_run_artifact(investigation_id, run_id, {
            "artifact_type": "investigation_trajectory",
            "schema_version": "1.0",
            "investigation_id": investigation_id,
            "run_id": run_id,
            "started_at": started_at.isoformat(),
            "completed_at": completed_at.isoformat(),
            "clues": clues.model_dump(mode="json"),
            "trajectory": trajectory,
            "summary": {"status": result["status"], "query_count": result["query_count"], "discovered_source_count": result["discovered_source_count"], "retrieved_source_count": result["retrieved_source_count"], "observation_count": result["observation_count"], "error_count": len(errors)},
        })
        result["trajectory_artifact"] = trajectory_artifact
        if self.run_repository:
            await self.run_repository.save_run(run_id, investigation_id, result, completed_at.isoformat())
        log.info("investigation completed investigation_id=%s run_id=%s sources=%d observations=%d errors=%d elapsed_ms=%.2f", investigation_id, run_id, result["retrieved_source_count"], result["observation_count"], len(errors), result["duration_ms"])
        return result

    def _stored_sources(self, investigation_id: str):
        if hasattr(self.repository, "sources"):
            return [source for source in self.repository.sources.values() if source.investigation_id == investigation_id]
        return []

    async def _create_investigation(self, investigation_id: str, clues: PersonClues, created_at: datetime) -> None:
        if self.run_repository and hasattr(self.run_repository, "create_investigation"):
            await self.run_repository.create_investigation(
                investigation_id, clues.model_dump_json(), created_at.isoformat()
            )
