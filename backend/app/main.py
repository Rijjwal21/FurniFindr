from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import pandas as pd
import warnings

from app.models.schemas import (
    RecommendationRequest, 
    RecommendationResponse,
    AnalyticsData,
    Product
)
from app.services import recommendations, vector_store
from app.core.config import settings

# --- Application Lifespan (Startup/Shutdown) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages application startup and shutdown events.
    """
    # Startup:
    print("Application startup...")
    # Suppress a specific pandas warning
    warnings.simplefilter(action='ignore', category=UserWarning)
    
    # Load the vector store into memory
    try:
        vector_store.get_vector_store()
        print("Vector store initialized.")
    except Exception as e:
        print(f"CRITICAL: Failed to initialize vector store: {e}")
        # In a real app, you might want to prevent startup
    
    yield
    
    # Shutdown:
    print("Application shutdown...")
    # Any cleanup code would go here

# --- FastAPI App Initialization ---
app = FastAPI(
    title="FurniFindr API",
    description="API for furniture recommendations and analytics.",
    version="0.1.0",
    lifespan=lifespan
)

# --- CORS Middleware ---
# Allow requests from our frontend (localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Cached Data for Analytics ---
# For a simple demo, we load the CSV into pandas once for analytics.
# In a real app, this would come from a proper database.
try:
    analytics_df = pd.read_csv(settings.DATA_FILE_PATH)
    analytics_df = analytics_df.fillna("")
    analytics_df['price_clean'] = analytics_df['price'].apply(
        lambda x: float(re.sub(r"[$,]", "", str(x))) if isinstance(x, str) and re.sub(r"[$,]", "", str(x)) else 0.0
    )
    analytics_df['has_image'] = analytics_df['images'].apply(lambda x: isinstance(x, str) and len(x) > 5)
except FileNotFoundError:
    print(f"Warning: Analytics data file not found at {settings.DATA_FILE_PATH}")
    analytics_df = pd.DataFrame() # Empty dataframe

# --- API Endpoints ---

@app.get("/health", tags=["General"])
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "vector_db": settings.VECTOR_DB}

@app.post("/recommend", 
          response_model=RecommendationResponse, 
          tags=["Recommendations"])
async def recommend_products(request: RecommendationRequest):
    """
    Main conversational recommendation endpoint.
    Receives a user prompt and returns ranked recommendations
    with generated descriptions.
    """
    return await recommendations.get_recommendations(request)

@app.get("/analytics-data", 
         response_model=AnalyticsData, 
         tags=["Analytics"])
async def get_analytics_data():
    """
    Endpoint to feed the analytics dashboard.
    Computes stats from the loaded CSV.
    """
    if analytics_df.empty:
        return {"total_products": 0, "price_distribution": {}, "category_counts": {}, "brand_counts": {}, "image_coverage_percent": 0}

    # 1. Price Distribution (Histogram)
    price_hist = pd.cut(analytics_df['price_clean'], bins=[0, 50, 100, 200, 500, 10000]).value_counts().sort_index()
    price_dist_data = [{"name": str(k), "count": int(v)} for k, v in price_hist.to_dict().items()]

    # 2. Category Counts (Top 5)
    # Needs exploding the list
    try:
        categories_s = analytics_df['categories'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) and x.startswith('[') else ['Other'])
        all_categories = categories_s.explode().str.strip()
        cat_counts = all_categories.value_counts().head(10).to_dict()
    except:
        cat_counts = {"Error": "Could not parse categories"}

    # 3. Brand Counts (Top 10)
    brand_counts = analytics_df['brand'].value_counts().head(10).to_dict()

    # 4. Image Coverage
    image_coverage = (analytics_df['has_image'].sum() / len(analytics_df)) * 100

    return AnalyticsData(
        total_products=int(len(analytics_df)),
        price_distribution=price_dist_data,
        category_counts=cat_counts,
        brand_counts=brand_counts,
        image_coverage_percent=round(image_coverage, 2)
    )

@app.get("/products", 
         response_model=List[Product], 
         tags=["Products"])
async def get_all_products():
    """
    Get all product metadata. Used by analytics page for filtering.
    (Note: In a real app, this should be paginated)
    """
    if analytics_df.empty:
        return []
    
    products = [
        Product(
            uniq_id=row.get("uniq_id"),
            title=row.get("title"),
            brand=row.get("brand"),
            price=row.get("price"),
            images=ast.literal_eval(row.get("images", "[]")) if isinstance(row.get("images"), str) and row.get("images").startswith('[') else [],
            categories=ast.literal_eval(row.get("categories", "[]")) if isinstance(row.get("categories"), str) and row.get("categories").startswith('[') else [],
            # Add other fields as needed
        ) for _, row in analytics_df.head(50).iterrows() # Limit to 50 for demo
    ]
    return products