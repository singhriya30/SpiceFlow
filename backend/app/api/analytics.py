from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.analytics import SummaryResponse
from app.services.analytics_service import get_summary
from app.core.dependencies import require_role
from app.models.user import User

from app.schemas.analytics import SummaryResponse, TopProductResponse
from app.services.analytics_service import get_summary, get_top_products


from app.schemas.analytics import TopCategoryResponse
from app.services.analytics_service import get_top_categories

from app.schemas.analytics import SalesOverTimeResponse
from app.services.analytics_service import get_sales_over_time


from app.schemas.analytics import CustomerStatsResponse
from app.services.analytics_service import get_customer_stats


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


@router.get("/summary", response_model=SummaryResponse)
def summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Owner", "Employee"))
):
    return get_summary(db)



@router.get("/top-products", response_model=list[TopProductResponse])
def top_products(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Owner", "Employee"))
):
    return get_top_products(db, limit)


@router.get("/top-categories", response_model=list[TopCategoryResponse])
def top_categories(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Owner", "Employee"))
):
    return get_top_categories(db, limit)


@router.get("/sales-over-time", response_model=list[SalesOverTimeResponse])
def sales_over_time(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Owner", "Employee"))
):
    return get_sales_over_time(db)


@router.get("/customers", response_model=CustomerStatsResponse)
def customer_stats(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Owner", "Employee"))
):
    return get_customer_stats(db, limit)