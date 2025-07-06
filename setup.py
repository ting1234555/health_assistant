from setuptools import setup, find_packages

setup(
    name="health_assistant",
    version="0.1.0",
    packages=find_packages(where="backend"),
    package_dir={"": "backend"},
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "python-multipart>=0.0.5",
        "Pillow>=8.3.1",
        "transformers>=4.11.3",
        "torch>=1.9.0",
        "python-dotenv>=0.19.0",
        "httpx>=0.19.0",
        "pydantic>=1.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.2.5",
            "pytest-cov>=2.12.1",
            "pytest-asyncio>=0.15.1",
            "black>=21.7b0",
            "isort>=5.9.3",
            "mypy>=0.910",
        ],
    },
    python_requires=">=3.8",
)
