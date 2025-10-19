from app.models.schemas import Product, RecommendationResponse, RecommendationRequest
from app.services.vector_store import get_retriever
from app.services.generative import generate_creative_description
from typing import List
import ast
import asyncio

def _parse_metadata_to_product(metadata: dict) -> Product:
    """Converts a Document's metadata dict into a Product schema."""
    
    # Safely parse list-like strings from metadata
    try:
        images = ast.literal_eval(metadata.get("images", "[]"))
    except:
        images = []
        
    try:
        categories = ast.literal_eval(metadata.get("categories", "[]"))
    except:
        categories = []

    return Product(
        uniq_id=metadata.get("uniq_id"),
        title=metadata.get("title"),
        brand=metadata.get("brand"),
        description=metadata.get("description"),
        price=metadata.get("price"),
        manufacturer=metadata.get("manufacturer"),
        package_dimensions=metadata.get("package_dimensions"),
        country_of_origin=metadata.get("country_of_origin"),
        material=metadata.get("material"),
        color=metadata.get("color"),
        images=images,
        categories=categories
    )


async def get_recommendations(request: RecommendationRequest) -> RecommendationResponse:
    """
    Main recommendation logic.
    1. Retrieves similar documents from the vector store.
    2. Enriches them with generated descriptions.
    """
    print(f"Received recommendation request: {request.prompt}")
    
    # 1. Get the retriever
    retriever = get_retriever(top_k=request.top_k)
    
    # 2. Retrieve relevant documents (asynchronous)
    # .ainvoke() is the async version of .invoke()
    relevant_docs = await retriever.ainvoke(request.prompt)
    
    # 3. Convert docs to Product models
    products = [_parse_metadata_to_product(doc.metadata) for doc in relevant_docs]
    
    # 4. Generate creative descriptions for each product *in parallel*
    generation_tasks = [
        generate_creative_description(product) for product in products
    ]
    generated_descriptions = await asyncio.gather(*generation_tasks)
    
    # 5. Add the generated descriptions to the product objects
    for product, gen_desc in zip(products, generated_descriptions):
        product.generated_description = gen_desc
        
    return RecommendationResponse(recommendations=products)