# AI-Assisted Code Review and Test Generation Agent

FastAPI service for AI-assisted pull-request review and test generation.

## Architecture
- FastAPI API layer
- RAG abstraction backed by FAISS
- LLM tool/function-calling adapter
- MongoDB audit records
- pytest evaluation tests
- GitLab CI
- Kubernetes deployment manifests
- AWS-ready container deployment

The LLM provider is intentionally configured through environment variables so the project can use a compatible API without hard-coding credentials.

## Run
`python -m venv .venv`
`pip install -r requirements.txt`
`uvicorn app.main:app --reload`
