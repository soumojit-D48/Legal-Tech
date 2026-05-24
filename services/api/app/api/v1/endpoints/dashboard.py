"""
Dashboard Endpoint — GET /api/v1/dashboard
"""

import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_async_session
from app.core.security import get_current_user_id

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def get_dashboard(
    db: AsyncSession = Depends(get_async_session),
    user_id: str = Depends(get_current_user_id),
):
    """Real dashboard querying contracts for the user."""
    from app.repositories import contract_repo, user_repo
    
    user = await user_repo.get_user_by_clerk_id(db, user_id)
    if not user:
        return {
            "contracts": [],
            "power_trend": None,
            "critical_flags": 0,
            "active_scans": 0,
        }

    contracts = await contract_repo.get_all_contracts_by_user_id(db, user.id)
    
    # Calculate stats
    critical_flags = 0
    active_scans = 0
    power_scores = []
    
    contract_list = []
    for c in contracts:
        score = c.analysis_result.overall_risk_score if c.analysis_result else None
        power_score = c.analysis_result.power_score if c.analysis_result else None
        
        if score and score >= 80:  # arbitrary threshold for critical
            critical_flags += 1
            
        if power_score is not None:
            power_scores.append(power_score)
            
        status = "complete" if score is not None else "processing"
        latest_job_id = str(c.scan_jobs[0].id) if getattr(c, "scan_jobs", None) and len(c.scan_jobs) > 0 else None
            
        contract_list.append({
            "id": str(c.id),
            "file_name": c.original_filename,
            "contract_type": c.contract_type,
            "detected_language": c.detected_language,
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "overall_risk_score": score,
            "power_score": power_score,
            "should_sign": c.analysis_result.should_sign if c.analysis_result else "review",
            "status": status,
            "latest_job_id": latest_job_id
        })
        
    avg_power = sum(power_scores) / len(power_scores) if power_scores else 50
        
    return {
        "contracts": contract_list[:5],  # Only top 5 for recent analysis
        "power_trend": avg_power,
        "critical_flags": critical_flags,
        "active_scans": active_scans,
        "total_contracts": len(contracts)
    }