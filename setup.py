from setuptools import setup, find_packages

setup(
    name="chat-api",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.104.1",
        "uvicorn==0.24.0",
        "websockets==12.0",
        "redis[hiredis]==5.0.1",
        "pydantic==2.5.2",
        "pydantic-settings==2.1.0",
        "python-dotenv==1.0.0",
        "aiohttp==3.9.1",
        "pytest==7.4.3",
        "pytest-asyncio==0.23.2",
        "httpx==0.25.2",
        "pytest-cov==4.1.0",
        "black==23.11.0",
        "flake8==6.1.0"
    ],
    python_requires=">=3.8",
) 