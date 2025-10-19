from pydantic import BaseModel, Field
from typing import List, Optional, Any

class Product(BaseModel):
    """
    Pydantic model representing a product's metadata.
    This is what the API will return.
    """
    uniq_id: str
    title: str
    brand: Optional[str] = None
    description: Optional[str] = None
    price: Optional[str] = None
    categories: Optional[List[str]] = Field(default_factory=list)
    images: Optional[List[str]] = Field(default_factory=list)
    manufacturer: Optional[str] = None
    package_dimensions: Optional[str] = None
    country_of_origin: Optional[str] = None
    material: Optional[str] = None
    color: Optional[str] = None
    
    # This field will be added by our GenAI service
    generated_description: Optional[str] = None

class RecommendationRequest(BaseModel):
    """
    The shape of the request body for the /recommend endpoint.
    """
    prompt: str
    top_k: int = 3

class RecommendationResponse(BaseModel):
    """
    The shape of the response from the /recommend endpoint.
    """
    recommendations: List[Product]

class AnalyticsData(BaseModel):
    """
    The shape of the response from the /analytics-data endpoint.
    """
    total_products: int
    price_distribution: dict
    category_counts: dict
    brand_counts: dict
    image_coverage_percent: float