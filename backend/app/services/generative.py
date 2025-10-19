from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_core.output_parsers import StrOutputParser
from app.core.config import settings
from app.models.schemas import Product
import os

# Set OpenAI API key
os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY

def get_generative_chain() -> RunnableSequence:
    """
    Initializes and returns a LangChain sequence for generating 
    creative product descriptions.
    """
    
    # 1. Define the LLM (Generative Model)
    # We use a simple, fast OpenAI model.
    # We set temperature to 0.7 for a bit of creativity.
    try:
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            openai_api_key=settings.OPENAI_API_KEY
        )
    except Exception as e:
        print(f"Error initializing OpenAI: {e}")
        # Fallback or error handling
        raise ConnectionError("Could not initialize Generative AI model. Check API key.")

    # 2. Define the Prompt Template
    template = """
    You are a witty and creative marketing assistant for a furniture store.
    Your job is to write a short, compelling, and slightly playful product description (2-3 sentences)
    for a customer based on its technical data.
    
    DO NOT just repeat the title or description. Be creative.
    
    Product Data:
    - Title: {title}
    - Brand: {brand}
    - Description: {description}
    - Material: {material}
    - Color: {color}

    Your Creative Description:
    """
    prompt = ChatPromptTemplate.from_template(template)
    
    # 3. Define the Output Parser
    output_parser = StrOutputParser()
    
    # 4. Create the Chain
    # This chain will:
    # 1. Take input variables (title, brand, etc.)
    # 2. Format them into the prompt
    # 3. Send the prompt to the LLM
    # 4. Parse the LLM's text output
    chain = prompt | llm | output_parser
    
    return chain

# Initialize the chain once to be reused
llm_chain = get_generative_chain()

async def generate_creative_description(product: Product) -> str:
    """
    Generates a creative description for a single product.
    """
    try:
        # Use .ainvoke() for an asynchronous call
        description = await llm_chain.ainvoke({
            "title": product.title,
            "brand": product.brand,
            "description": product.description,
            "material": product.material,
            "color": product.color
        })
        return description.strip()
    except Exception as e:
        print(f"Error generating description: {e}")
        return "A fantastic product you're sure to love!" # Fallback