import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException

from app.clients import AzureClients
from app.models import (
    CandidateProfile,
    ExtractSkillsRequest,
    ExtractSkillsResponse,
)
from app.pipeline.extract import extract_and_ground_cv

router = APIRouter(prefix="/api/v1", tags=["Matching & Pipeline"])


@router.post("/extract-skills", response_model=ExtractSkillsResponse)
def extract_skills_endpoint(req: ExtractSkillsRequest):
    """
    Stage 1: Extract candidate skills from CV and ground against JobTech taxonomy.
    """
    if not req.cv_text or len(req.cv_text.strip()) < 10:
        raise HTTPException(status_code=422, detail="CV text must be at least 10 characters long.")

    if len(req.cv_text) > 20000:
        raise HTTPException(status_code=413, detail="CV text exceeds maximum allowed limit (20,000 characters).")

    candidate_id = req.candidate_id or f"cand-{uuid.uuid4().hex[:6]}"
    display_name = req.display_name or f"Candidate {candidate_id.split('-')[-1]}"

    graph, profile_vector, warnings = extract_and_ground_cv(req.cv_text)

    # Persist / Upsert into Cosmos DB
    profile = CandidateProfile(
        id=candidate_id,
        partition_key="synthetic-candidates",
        candidate_id=candidate_id,
        display_name=display_name,
        source="pasted",
        cv_text=req.cv_text,
        competency_graph=graph,
        profile_vector=profile_vector,
        created_at=datetime.utcnow()
    )

    try:
        clients = AzureClients.get()
        clients.container_candidates.upsert_item(profile.model_dump(mode="json"))
    except Exception as e:
        warnings.append(f"Cosmos DB persistence notice: {str(e)}")

    return ExtractSkillsResponse(
        candidate_id=candidate_id,
        display_name=display_name,
        competency_graph=graph,
        warnings=warnings
    )


@router.get("/candidates")
def list_candidates():
    """List up to 50 candidate profiles from Cosmos DB."""
    try:
        clients = AzureClients.get()
        query = "SELECT c.id, c.display_name, c.background_text, c.competency_graph FROM c OFFSET 0 LIMIT 50"
        items = list(clients.container_candidates.query_items(query=query, enable_cross_partition_query=True))
        return {"total": len(items), "candidates": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to query Cosmos DB: {str(e)}")


@router.get("/candidates/{candidate_id}")
def get_candidate(candidate_id: str):
    """Fetch a single candidate profile."""
    try:
        clients = AzureClients.get()
        query = "SELECT * FROM c WHERE c.id = @id"
        params = [{"name": "@id", "value": candidate_id}]
        items = list(clients.container_candidates.query_items(
            query=query, parameters=params, enable_cross_partition_query=True
        ))
        if not items:
            raise HTTPException(status_code=404, detail="Candidate not found")
        return items[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs")
def list_jobs(limit: int = 25):
    """List job postings from Azure AI Search jobs index."""
    try:
        clients = AzureClients.get()
        results = list(clients.search_jobs.search(
            search_text="*",
            select=["id", "title", "sector", "municipality", "taxonomy_ids", "source_url"],
            top=limit
        ))
        return {"total": len(results), "jobs": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to query AI Search jobs: {str(e)}")


@router.get("/jobs/{job_id}")
def get_job(job_id: str):
    """Retrieve full details for a job description."""
    try:
        clients = AzureClients.get()
        doc = clients.search_jobs.get_document(key=job_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Job not found")
        # Remove raw vector from response for cleanliness
        doc.pop("vector", None)
        return doc
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Job not found: {str(e)}")
