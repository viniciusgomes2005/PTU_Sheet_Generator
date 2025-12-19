from typing import Any, Dict, List, Optional
import firebase_admin
from firebase_admin import credentials, firestore
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from os import environ as env

from pydantic import BaseModel, Field

load_dotenv()  # carrega o .env

cred_path = env["FIREBASE_SERVICE_KEY"]

if not firebase_admin._apps: 
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

class Prerequisite(BaseModel):
    level: Optional[int] = None
    edges: List[str] = Field(default_factory=list)
    features: List[str] = Field(default_factory=list)
    moves: List[str] = Field(default_factory=list)
    stats: List[str] = Field(default_factory=list)

    anyOf: Optional[List["Prerequisite"]] = None

Prerequisite.model_rebuild()

class EdgeIn(BaseModel):
    id: Optional[str] = None  # se fornecido, vira o document id
    name: str
    effect: str
    prerequisite: Optional[Prerequisite] = None
    extra: Optional[Dict[str, Any]] = None  # caso você queira mandar campos adicionais

# --- HELPERS ---
def _edge_to_dict(edge: EdgeIn) -> Dict[str, Any]:
    data = {
        "name": edge.name,
        "effect": edge.effect,
        "prerequisite": edge.prerequisite.model_dump() if edge.prerequisite else {
            "level": None, "edges": [], "features": [], "moves": [], "stats": []
        },
    }
    # mescla campos extras se vierem
    if edge.extra:
        data.update(edge.extra)
    return data

# --- ENDPOINT ---
@app.post("/edges/bulk")
def insert_edges_bulk(edges: List[EdgeIn]):
    if not edges:
        raise HTTPException(status_code=400, detail="Lista vazia.")

    edges_col = db.collection("edges")

    batch = db.batch()
    results = {"created": 0, "updated": 0, "doc_ids": []}

    # Firestore batch tem limite de 500 operações por commit
    # Aqui vamos fazer commits em blocos.
    ops_in_batch = 0

    def commit_batch():
        nonlocal batch, ops_in_batch
        if ops_in_batch > 0:
            batch.commit()
            batch = db.batch()
            ops_in_batch = 0

    for e in edges:
        data = _edge_to_dict(e)

        if e.id:
            # upsert com doc id fixo
            doc_ref = edges_col.document(e.id)
            batch.set(doc_ref, data, merge=True)
            results["updated"] += 1
            results["doc_ids"].append(e.id)
            ops_in_batch += 1
        else:
            # gerar id manualmente para ainda usar batch
            doc_ref = edges_col.document()
            batch.set(doc_ref, data)
            results["created"] += 1
            results["doc_ids"].append(doc_ref.id)
            ops_in_batch += 1

        if ops_in_batch >= 450:  # folga do limite 500
            commit_batch()

    commit_batch()
    return results

class FeatureIn(BaseModel):
    id: Optional[str] = None  # se fornecido, vira o document id
    name: str
    effect: str

    tags: List[str] = Field(default_factory=list)
    target: Optional[str] = None
    trigger: Optional[str] = None
    note: Optional[str] = None

    prerequisite: Optional[Prerequisite] = None
    extra: Optional[Dict[str, Any]] = None  # campos adicionais livres

# --- HELPERS ---
def _default_prereq_dict() -> Dict[str, Any]:
    return {"level": None, "edges": [], "features": [], "moves": [], "stats": [], "anyOf": None}

def _feature_to_dict(feature: FeatureIn) -> Dict[str, Any]:
    data: Dict[str, Any] = {
        "name": feature.name,
        "effect": feature.effect,
        "tags": feature.tags,
        "target": feature.target,
        "trigger": feature.trigger,
        "note": feature.note,
        "prerequisite": feature.prerequisite.model_dump() if feature.prerequisite else _default_prereq_dict(),
    }
    # remove chaves None para não poluir o Firestore
    data = {k: v for k, v in data.items() if v is not None}
    if feature.extra:
        data.update(feature.extra)
    return data

# --- ENDPOINT ---
@app.post("/features/bulk")
def insert_features_bulk(features: List[FeatureIn]):
    if not features:
        raise HTTPException(status_code=400, detail="Lista vazia.")

    features_col = db.collection("features")
    batch = db.batch()

    results = {"created": 0, "updated": 0, "doc_ids": []}
    ops_in_batch = 0

    def commit_batch():
        nonlocal batch, ops_in_batch
        if ops_in_batch > 0:
            batch.commit()
            batch = db.batch()
            ops_in_batch = 0

    for f in features:
        data = _feature_to_dict(f)

        if f.id:
            doc_ref = features_col.document(f.id)
            batch.set(doc_ref, data, merge=True)  # upsert
            results["updated"] += 1
            results["doc_ids"].append(f.id)
        else:
            doc_ref = features_col.document()
            batch.set(doc_ref, data)
            results["created"] += 1
            results["doc_ids"].append(doc_ref.id)

        ops_in_batch += 1
        if ops_in_batch >= 450:
            commit_batch()

    commit_batch()
    return results

class ClassIn(BaseModel):
    id: Optional[str] = None
    name: str
    features: List[str] = Field(default_factory=list)  # IDs das features da classe
    extra: Optional[Dict[str, Any]] = None

def _class_to_dict(c: ClassIn) -> Dict[str, Any]:
    data: Dict[str, Any] = {
        "name": c.name,
        "features": c.features,
    }
    if c.extra:
        data.update(c.extra)
    return data

@app.post("/classes/bulk")
def insert_classes_bulk(classes: List[ClassIn]):
    if not classes:
        raise HTTPException(status_code=400, detail="Lista vazia.")

    col = db.collection("classes")
    batch = db.batch()

    results = {"created": 0, "updated": 0, "doc_ids": []}
    ops_in_batch = 0

    def commit_batch():
        nonlocal batch, ops_in_batch
        if ops_in_batch > 0:
            batch.commit()
            batch = db.batch()
            ops_in_batch = 0

    for c in classes:
        data = _class_to_dict(c)

        if c.id:
            doc_ref = col.document(c.id)
            batch.set(doc_ref, data, merge=True)
            results["updated"] += 1
            results["doc_ids"].append(c.id)
        else:
            doc_ref = col.document()
            batch.set(doc_ref, data)
            results["created"] += 1
            results["doc_ids"].append(doc_ref.id)

        ops_in_batch += 1
        if ops_in_batch >= 450:
            commit_batch()

    commit_batch()
    return results
