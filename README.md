# Alfred Monorepo

## Overview

Alfred is a comprehensive software ecosystem developed and maintained by JUDICIAL ARTIFICIAL INTELLIGENCE LABS. This monorepo houses all frontend applications, backend services, machine learning models, shared packages, scripts, and documentation necessary for the development, deployment, and maintenance of our software solutions.

## Repository Structure

```
alfred/
├── apps/                  # Frontend clients
│   ├── web/               # Web application
│   │   ├── public/        # Static assets (MDX, images)
│   │   ├── src/           # Source code (NEXTJS, CONVEX)
│   │   ├── tests/         # Unit/integration tests
│   │   └── package.json   # Web dependencies
│   └── mobile/            # Mobile application
│       ├── android/       # Android-specific code
│       ├── ios/           # iOS-specific code
│       └── tests/         # Mobile tests
├── services/              # Backend and ML services
│   ├── api/               # Main backend API
│   │   ├── src/           # API source (Python, Node.js, etc.)
│   │   ├── tests/         # API tests
│   │   ├── Dockerfile     # Containerization
│   │   └── requirements.txt # Python dependencies
│   └── llm/               # LLM-related code
│       ├── training/      # Training scripts/data
│       │   ├── scripts/   # Jupyter notebooks, Python scripts
│       │   └── data/      # Sample datasets (avoid large files)
│       └── serving/       # LLM serving (FastAPI, Flask)
│           ├── src/       # Model API code
│           ├── Dockerfile # Containerization
│           └── models/    # Pretrained models (ignored by Git)
├── packages/              # Shared code/libs
│   └── shared/            # Reusable utilities/types
│       ├── src/           # Shared code (TypeScript, Python)
│       └── package.json   # JS package config
├── docs/                  # Documentation
│   ├── setup.md           # Development setup guide
│   └── api-reference.md   # API specs
├── scripts/               # Utility scripts
│   ├── deploy.sh          # Deployment scripts
│   └── setup-env.sh       # Environment setup
├── .github/               # CI/CD workflows
│   └── workflows/         # GitHub Actions workflows
│       ├── web.yml        # Web app CI
│       ├── mobile.yml     # Mobile app CI
│       └── api.yml        # API/LLM CI
├── .gitignore             # Ignore node_modules, models, .env, etc.
├── LICENSE                # Proprietary license file
├── README.md              # This document
├── docker-compose.yml     # Orchestrate services (API, LLM, databases)
```

## Getting Started

### Prerequisites

Ensure you have the following installed:

- Node.js (for frontend and package management)
- Python (for backend and ML services)
- Docker (for containerized services)
- Git (for version control)

### Setup

1. Clone the repository:
   ```sh
   git clone https://github.com/judicialartificialintelligencelab/Alfred.git
   cd Alfred
   ```
2. Install dependencies for the web app:
   ```sh
   cd apps/web
   bun install
   ```
3. Install dependencies for backend services:
   ```sh
   cd ../../services/api
   pip install -r requirements.txt
   ```
4. Run Docker containers:
   ```sh
   docker-compose up -d
   ```

## Development

### Running Services Locally

- **Frontend:**
  ```sh
  cd apps/web
  bun start
  ```
- **Backend API:**
  ```sh
  cd services/api
  uvicorn src.main:app --reload
  ```
- **LLM Serving:**
  ```sh
  cd services/llm/serving
  python src/server.py
  ```

### Testing

Run unit tests:

```sh
bun test  # For frontend
pytest    # For backend
```

## Deployment

### CI/CD

GitHub Actions workflows automate testing and deployment. Ensure all changes pass CI before merging.

### Deployment Steps

- Deploy frontend:
  ```sh
  bun run build
  ```
- Deploy backend:
  ```sh
  docker-compose up --build -d
  ```

## Contributing

1. Create a new feature branch:
   ```sh
   git checkout -b feature-branch
   ```
2. Make changes and commit:
   ```sh
   git commit -m "feat: add new feature"
   ```
3. Push the branch:
   ```sh
   git push origin feature-branch
   ```
4. Open a pull request on GitHub.

## License

This software is proprietary and confidential. Unauthorized distribution is prohibited.

© 2025 JUDICIAL ARTIFICIAL INTELLIGENCE LABS. All rights reserved.
