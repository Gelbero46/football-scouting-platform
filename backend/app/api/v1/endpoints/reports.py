from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import Any, Optional
import uuid
from datetime import datetime, timedelta

from app.core.database import get_db
from app.schemas.report import ReportResponse, ReportCreate
from app.schemas.common import StandardResponse, PaginatedResponse
from app.models import Report

router = APIRouter()

@router.get("", response_model=PaginatedResponse[ReportResponse])
async def get_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    type: Optional[str] = Query(None, description="Filter by report type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db)
) -> Any:
    """Get user's reports with filtering"""
    
    query = db.query(Report)
    
    # Apply filters
    if type:
        query = query.filter(Report.type == type)
    
    if status:
        query = query.filter(Report.status == status)
    
    # Order by creation date (newest first)
    query = query.order_by(desc(Report.created_at))
    
    # Pagination
    total = query.count()
    reports = query.offset(skip).limit(limit).all()
    
    return {
        "success": True,
        "data": reports,
        "meta": {
            "pagination": {
                "page": (skip // limit) + 1,
                "per_page": limit,
                "total": total,
                "total_pages": (total + limit - 1) // limit
            }
        }
    }

@router.post("", response_model=StandardResponse[ReportResponse])
async def generate_report(
    report_data: ReportCreate,
    db: Session = Depends(get_db)
) -> Any:
    """Generate new report (async processing)"""
    
    # Create report record
    report = Report(
        title=report_data.title,
        type=report_data.type,
        parameters=report_data.parameters,
        filters=report_data.filters,
        status="pending",
        # generated_by=current_user.id,  # Add when auth is ready
        expires_at=(datetime.utcnow() + timedelta(days=30)).isoformat()  # 30 days expiry
    )
    
    db.add(report)
    db.commit()
    db.refresh(report)
    
    # TODO: Queue background task for actual report generation
    # For now, we'll just mark as generating
    report.status = "generating"
    db.commit()
    
    return {
        "success": True,
        "data": report
    }

@router.get("/{report_id}", response_model=StandardResponse[ReportResponse])
async def get_report(
    report_id: str,
    db: Session = Depends(get_db)
) -> Any:
    """Get report details"""
    
    try:
        report_uuid = uuid.UUID(report_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid report ID format"
        )
    
    report = db.query(Report).filter(Report.id == report_uuid).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Check if report has expired
    if report.is_expired:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Report has expired"
        )
    
    return {
        "success": True,
        "data": report
    }

@router.get("/{report_id}/download")
async def download_report(
    report_id: str,
    db: Session = Depends(get_db)
) -> Any:
    """Download report file"""
    
    try:
        report_uuid = uuid.UUID(report_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid report ID format"
        )
    
    report = db.query(Report).filter(Report.id == report_uuid).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    if report.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Report is not ready. Current status: {report.status}"
        )
    
    if report.is_expired:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Report has expired"
        )
    
    # Update download count
    report.increment_download_count()
    db.commit()
    
    # TODO: Return actual file or signed URL
    # For now, return download info
    return {
        "success": True,
        "data": {
            "download_url": f"/files/reports/{report.file_name}",
            "file_name": report.file_name,
            "file_size": report.file_size,
            "expires_in": "24 hours"
        }
    }

@router.delete("/{report_id}")
async def delete_report(
    report_id: str,
    db: Session = Depends(get_db)
) -> Any:
    """Delete report"""
    
    try:
        report_uuid = uuid.UUID(report_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid report ID format"
        )
    
    report = db.query(Report).filter(Report.id == report_uuid).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # TODO: Delete actual file from storage
    
    db.delete(report)
    db.commit()
    
    return {
        "success": True,
        "data": {"message": "Report deleted successfully"}
    }