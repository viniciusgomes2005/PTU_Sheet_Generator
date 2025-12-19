import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
from os import environ as env
from typing import Any, Dict, Optional
from trainer_service import DEFAULT_COMBAT_STATS, DEFAULT_SKILLS, compute_derived, _calc_ap_max

load_dotenv()

cred_path = env["FIREBASE_SERVICE_KEY"]

if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

def get_edges():
    docs = db.collection("edges").stream()
    return [
        {**doc.to_dict(), "id": doc.id}
        for doc in docs
    ]

def get_features():
    docs = db.collection("features").stream()
    return [
        {**doc.to_dict(), "id": doc.id}
        for doc in docs
    ]

def get_classes():
    docs = db.collection("classes").stream()
    return [
        {**doc.to_dict(), "id": doc.id}
        for doc in docs
    ]


def create_trainer_level0(
    db,
    name: str,
    gender: Optional[str] = None,
    age: Optional[int] = None,
    background: Optional[str] = None,
    height_m: Optional[float] = None,
    weight_kg: Optional[float] = None,
    doc_id: Optional[str] = None,
) -> Dict[str, Any]:
    trainer: Dict[str, Any] = {
        "basic_info": {
            "name": name,
            "gender": gender,
            "age": age,
            "background": background,
            "height_m": height_m,
            "weight_kg": weight_kg,
        },
        "progression": {
            "level": 0,
            "exp_current": 0,
            "exp_to_next": 10, 
        },
        "action_points": {
            "current": _calc_ap_max(0),
            "bound": 0,
            "drained": 0,
        },
        "combat_stats": DEFAULT_COMBAT_STATS,
        "skills": DEFAULT_SKILLS,
        "derived": {},  # vamos preencher abaixo
        "build": {
            "classes": [],   # IDs de classes
            "features": [],  # IDs de features
            "edges": [],     # IDs de edges
            "moves": [],     # IDs (ou strings) de moves, se você for modelar isso depois
            "pokemon": [],   # ids de pokémon do treinador, se você for guardar aqui
        },
        "notes": "",
        "created_at": firestore.SERVER_TIMESTAMP,
        "updated_at": firestore.SERVER_TIMESTAMP,
    }

    trainer["derived"] = compute_derived(trainer)
    trainer["action_points"]["current"] = trainer["derived"]["ap_max"]

    col = db.collection("trainers")
    if doc_id:
        ref = col.document(doc_id)
        ref.set(trainer, merge=False)
        trainer_id = doc_id
    else:
        ref = col.document()
        ref.set(trainer, merge=False)
        trainer_id = ref.id

    return {"id": trainer_id, **trainer}
