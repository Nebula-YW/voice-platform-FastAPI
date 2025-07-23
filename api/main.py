from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import router
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="FastAPI Vercel Template",
    description="A ready-to-deploy FastAPI template for Vercel with common patterns and examples",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {
        "message": "Welcome to the FastAPI Vercel Template",
        "description": "A ready-to-deploy FastAPI template with common patterns",
        "docs": "/api/v1/docs",
        "version": "1.0.0",
        "endpoints": {
            "/api/v1/health": "Health check endpoint",
            "/api/v1/echo": "Echo endpoint for testing",
            "/api/v1/items": "CRUD operations for items",
            "/api/v1/users": "User management endpoints",
        },
    }
