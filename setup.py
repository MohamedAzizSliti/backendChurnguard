from setuptools import setup, find_packages

setup(
    name="backend",
    version="0.1.0",
    description="ChurnGuard API backend",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.95.1",
        "uvicorn==0.22.0",
        "firebase-admin==6.1.0",
        "pyjwt>=2.6.0,<3.0.0",
        "python-multipart==0.0.6",
        "pydantic==1.10.7",
        "email-validator==2.0.0"
    ],
)

# Project structure:
# backend/
# ├── main.py
# ├── setup.py
# ├── backend/
# │   ├── __init__.py
# │   ├── presentation/
# │   │   ├── __init__.py
# │   │   ├── api/
# │   │   │   ├── __init__.py
# │   │   │   ├── auth_api.py
# │   │   │   ├── client_api.py
# │   │   │   ├── report_api.py