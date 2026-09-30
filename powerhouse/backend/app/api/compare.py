from typing import Optional
from fastapi import APIRouter, Query
from app.engine.business_analyzer import compare_business_categories

router = APIRouter(prefix="/business-compare", tags=["Business Category Comparison"])


@router.get("")
def compare_categories(
    category_a: str = Query("clothing_textile", description="First business category"),
    category_b: str = Query("restaurant", description="Second business category"),
    city: str = Query("Tiruppur", description="Operational city"),
    state: str = Query("Tamil Nadu", description="Operational state")
):
    """
    Returns side-by-side compliance comparison between two business categories
    in the same geographic location, demonstrating deterministic context-dependence.
    """
    return compare_business_categories(
        category_a=category_a,
        category_b=category_b,
        city=city,
        state=state
    )
