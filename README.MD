# FurniFindr — Furniture Recommendation & Analytics App

Welcome to FurniFindr, a complete AI/ML-driven web application for furniture product recommendations and analytics. This project was built to satisfy the requirements of the AI/ML Internship Assignment.

## Architecture Overview

The project follows a simple monorepo structure:

* **`backend/`**: A Python **FastAPI** application that serves the API. It handles:
    * Data ingestion and embedding generation.
    * Connecting to a Vector DB (**Pinecone** or **FAISS**).
    * Semantic search for recommendations.
    * **LangChain** orchestration for generating creative descriptions.
    * Analytics data endpoints.
* **`frontend/`**: A JavaScript **React** (Vite) application that provides the user interface. It includes:
    * A chat-based recommendation page.
    * An analytics dashboard page with charts.
    * Routing via `react-router-dom`.
* **`notebooks/`**: A set of **Jupyter Notebooks** demonstrating the core ML, NLP, and CV tasks:
    * `1_Data_Analytics_EDA.ipynb`: Exploratory Data Analysis.
    * `2_ML_Clustering_Recommendations.ipynb`: Content-based filtering (TF-IDF) and K-Means clustering.
    * `3_CV_Category_Classification.ipynb`: A simple image classification model.



## Features

* **Conversational Recommendations**: Users can type prompts (e.g., "a comfy sofa for a small apartment") into a chat UI.
* **GenAI Descriptions**: The backend uses a Generative AI model (via LangChain) to write a unique, creative description for each recommended item.
* **Vector Search**: Uses `sentence-transformers` embeddings stored in a vector DB (FAISS locally, or Pinecone) for fast semantic search.
* **Data Analytics**: A separate page displays interactive charts for price distribution, category counts, and top brands.
* **ML/NLP Pipelines**: Notebooks demonstrate content-based filtering (TF-IDF) and item clustering (K-Means).
* **CV Pipeline**: A notebook shows how to train a simple CNN/ResNet to classify product images by category.

## Tech Stack

* **Backend**: FastAPI, Uvicorn, Python 3.10+
* **Frontend**: React 18, Vite, Material-UI (MUI), Recharts, Axios
* **Vector DB**: FAISS (local, default) or Pinecone (cloud)
* **Embeddings**: Hugging Face `sentence-transformers` (`all-MiniLM-L6-v2`)
* **GenAI & Orchestration**: LangChain, OpenAI (default, can be swapped)
* **ML/Notebooks**: Scikit-learn, Pandas, Matplotlib, Seaborn, PyTorch (for CV)

---

## Setup & Installation (Local Demo)

Follow these steps to run the entire application locally.

### Prerequisites

* Python 3.10+ and `pip`
* Node.js 18+ and `npm`

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd FurniFindr