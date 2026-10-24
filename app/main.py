from fastapi import FastAPI
from pydantic import BaseModel, Field
from pymongo import MongoClient
import os,time,hashlib

app=FastAPI(title="AI Code Review Agent",version="1.0.0")
mongo=MongoClient(os.getenv("MONGODB_URL","mongodb://localhost:27017"))
audit=mongo["code_review"]["audit"]

class ReviewRequest(BaseModel):
    repository:str
    pull_request:int
    diff:str=Field(min_length=1)

class Finding(BaseModel):
    severity:str
    category:str
    message:str
    line:int|None=None

def retrieve_standards(query:str):
    # Production implementation can load embeddings into FAISS and retrieve
    # relevant internal standards before constructing the LLM prompt.
    terms=("security","testing","api","error handling")
    return [t for t in terms if t in query.lower()]

def review(diff:str):
    findings=[]
    if "eval(" in diff: findings.append(Finding(severity="high",category="security",message="Avoid eval() on untrusted input."))
    if "except:" in diff: findings.append(Finding(severity="medium",category="quality",message="Use a specific exception type instead of bare except."))
    if "TODO" in diff: findings.append(Finding(severity="low",category="maintenance",message="TODO marker requires review."))
    return findings

@app.get("/health")
def health(): return {"ok":True}

@app.post("/review")
def create_review(req:ReviewRequest):
    standards=retrieve_standards(req.diff)
    findings=[f.model_dump() for f in review(req.diff)]
    record={"repository":req.repository,"pull_request":req.pull_request,"standards":standards,
            "findings":findings,"created_at":time.time()}
    audit.insert_one(record)
    return {"findings":findings,"retrieved_standards":standards,"human_approval_required":True}

@app.post("/generate-tests")
def generate_tests(req:ReviewRequest):
    test_id=hashlib.sha256(req.diff.encode()).hexdigest()[:12]
    return {"test_id":test_id,"framework":"pytest","suggestions":[
        "test_expected_success_case()","test_invalid_input_case()","test_authorization_failure()",
        "test_external_dependency_failure()"],"human_review_required":True}

@app.get("/audit")
def audit_log():
    return [{"repository":x.get("repository"),"pull_request":x.get("pull_request"),
             "finding_count":len(x.get("findings",[]))} for x in audit.find().sort("created_at",-1).limit(100)]
