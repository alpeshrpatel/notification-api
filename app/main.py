from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import email_routes

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="A REST API for sending emails using AWS SES",
    version="1.0.0",
    debug=settings.DEBUG
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(email_routes.router, prefix="/api")

# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint that returns API information"""
    return {
        "app_name": settings.APP_NAME,
        "version": "1.0.0",
        "description": "API for sending emails through AWS SES"
    }

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)