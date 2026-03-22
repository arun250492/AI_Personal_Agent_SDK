"""
Setup script for AI Personal Agent SDK
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ai-personal-agent-sdk",
    version="0.1.0",
    author="Arun Kumar Singh",
    author_email="arun250492@gmail.com",
    description="AI Personal Agent SDK for automation with OpenAI, Zapier, and security features",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/arun250492/AI_Personal_Agent_SDK",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "openai>=1.0.0",
        "requests>=2.28.0",
        "cryptography>=41.0.0",
        "flask>=2.3.0",
        "flask-cors>=4.0.0",
        "apscheduler>=3.10.0",
        "python-dotenv>=1.0.0",
        "oauth2client>=4.1.3",
        "google-api-python-client>=2.95.0",
        "google-auth-httplib2>=0.1.0",
        "google-auth-oauthlib>=1.0.0",
        "twilio>=8.2.0",
        "plyer>=2.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ],
    },
    package_data={
        "ai_personal_agent_sdk": ["ui/templates/*", "ui/static/*"],
    },
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "ai-personal-agent=examples.basic_usage:main",
        ],
    },
)