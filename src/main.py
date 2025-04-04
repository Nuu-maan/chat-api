from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from contextlib import asynccontextmanager
from src.config.settings import get_settings
from src.api.v1.router import api_router
from src.dependencies import get_database
import logging
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for the application."""
    try:
        await get_database().connect()
        logger.info("Connected to Redis")
        yield
    finally:
        await get_database().disconnect()
        logger.info("Disconnected from Redis")

app = FastAPI(
    title="Chat API",
    description="""
    A real-time chat API with WebSocket support.
    
    ## Features
    
    * Create and manage chat rooms
    * User registration and management
    * Real-time messaging using WebSocket
    * Message history and retrieval
    * Room-based chat organization
    
    ## Authentication
    
    This API uses token-based authentication. Include the token in the Authorization header:
    
    ```
    Authorization: Bearer <your_token>
    ```
    
    ## WebSocket
    
    Connect to the WebSocket endpoint at:
    ```
    ws://localhost:8000/api/v1/ws/{room_id}/{user_id}
    ```
    """,
    version="1.0.0",
    docs_url=None,  # Disable default docs
    redoc_url=None,  # Disable default redoc
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Customize OpenAPI schema
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }

    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    # Apply security globally
    openapi_schema["security"] = [{"bearerAuth": []}]

    # Add tags metadata
    openapi_schema["tags"] = [
        {
            "name": "chat",
            "description": "Operations related to chat rooms and messages",
        },
        {
            "name": "users",
            "description": "User management operations",
        },
        {
            "name": "websocket",
            "description": "WebSocket operations for real-time messaging",
        },
    ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.get("/", include_in_schema=False)
async def custom_swagger_ui_html():
    """Main documentation endpoint with dark mode Swagger UI"""
    return get_swagger_ui_html(
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        title="Chat API Documentation",
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
        swagger_favicon_url="/static/favicon.png",
        custom_css_url="/static/css/custom.css",
        custom_js_url="/static/custom.js",
        swagger_ui_parameters={
            "docExpansion": "none",
            "defaultModelsExpandDepth": -1,
            "theme": "dark",
            "syntaxHighlight.theme": "monokai",
        }
    )

@app.get("/docs", include_in_schema=False)
async def docs_redirect():
    """Redirect /docs to root path"""
    return RedirectResponse(url="/")

@app.get("/redoc", include_in_schema=False)
async def custom_redoc_html():
    """Alternative documentation using ReDoc"""
    return HTMLResponse(
        f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Chat API Documentation</title>
            <meta charset="utf-8"/>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link rel="stylesheet" href="/static/css/custom.css">
            <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                }}
            </style>
        </head>
        <body>
            <redoc spec-url="{settings.API_V1_STR}/openapi.json"></redoc>
            <script src="https://cdn.jsdelivr.net/npm/redoc@latest/bundles/redoc.standalone.js"></script>
        </body>
        </html>
        """
    )

@app.get("/")
async def root():
    """Redirect to API documentation"""
    return HTMLResponse(
        """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Chat API</title>
            <meta http-equiv="refresh" content="0; url=/docs">
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background-color: #1a1a1a;
                    color: #e0e0e0;
                }
                .container {
                    text-align: center;
                }
                a {
                    color: #00b4d8;
                    text-decoration: none;
                }
                a:hover {
                    text-decoration: underline;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Welcome to Chat API</h1>
                <p>Redirecting to <a href="/docs">API documentation</a>...</p>
            </div>
        </body>
        </html>
        """
    ) 