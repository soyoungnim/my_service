from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from pathlib import Path
from datetime import datetime, timezone, timedelta
import json
import uuid
import random

app = FastAPI(title="Location API")

LOCATIONS = {
    "강남": {"lat": 37.4979, "lon": 127.0276},
    "여의도": {"lat": 37.5219, "lon": 126.9245},
    "마포": {"lat": 37.5663, "lon": 126.9014},
    "울산": {"lat": 35.5384, "lon": 129.3114},
    "광주": {"lat": 35.1595, "lon": 126.8526},
    "충청": {"lat": 36.6357, "lon": 127.4917},
    "강릉": {"lat": 37.7519, "lon": 128.8761},
    "제주": {"lat": 33.4996, "lon": 126.5312},
}

DATA_FILE = Path(__file__).parent / "data" / "records.jsonl"


class RecordCreate(BaseModel):
    user_name: str = Field(..., min_length=1, max_length=20)
    region: str
    score: int = Field(..., ge=1, le=5)
    memo: str = Field(default="", max_length=100)


class Record(RecordCreate):
    id: str
    lat: float
    lon: float
    created_at: str


DATA_FILE.parent.mkdir(parents=True, exist_ok=True)


@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/locations")
def get_locations():
    return LOCATIONS


@app.get("/locations/{name}")
def get_location(name: str):
    if name not in LOCATIONS:
        raise HTTPException(status_code=404, detail="location not found")
    return LOCATIONS[name]


@app.post("/records", status_code=201, response_model=Record)
def create_record(record_create: RecordCreate):
    if record_create.region not in LOCATIONS:
        raise HTTPException(status_code=400, detail="Invalid region")

    base_location = LOCATIONS[record_create.region]
    lat = base_location["lat"] + random.uniform(-0.01, 0.01)
    lon = base_location["lon"] + random.uniform(-0.01, 0.01)
    created_at = datetime.now(timezone(timedelta(hours=9))).isoformat()

    record = {
        "id": uuid.uuid4().hex[:8],
        "user_name": record_create.user_name,
        "region": record_create.region,
        "score": record_create.score,
        "memo": record_create.memo,
        "lat": lat,
        "lon": lon,
        "created_at": created_at,
    }

    with open(DATA_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return record


@app.get("/records")
def get_records():
    records = []
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))

    records.reverse()
    return {"count": len(records), "records": records}


@app.get("/records/user/{user_name}")
def get_records_by_user(user_name: str):
    records = []
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    if record["user_name"] == user_name:
                        records.append(record)

    records.reverse()

    avg_score = 0.0
    if records:
        avg_score = round(sum(r["score"] for r in records) / len(records), 1)

    return {
        "user_name": user_name,
        "count": len(records),
        "avg_score": avg_score,
        "records": records
    }


@app.get("/stats")
def get_stats():
    records = []
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))

    if not records:
        return {
            "total": 0,
            "user_count": 0,
            "overall_avg": 0,
            "by_region": []
        }

    total = len(records)
    user_count = len(set(r["user_name"] for r in records))
    overall_avg = round(sum(r["score"] for r in records) / total, 1)

    region_stats = {}
    for record in records:
        region = record["region"]
        if region not in region_stats:
            region_stats[region] = {"count": 0, "total_score": 0}
        region_stats[region]["count"] += 1
        region_stats[region]["total_score"] += record["score"]

    by_region = [
        {
            "region": region,
            "count": stats["count"],
            "avg_score": round(stats["total_score"] / stats["count"], 1)
        }
        for region, stats in region_stats.items()
    ]

    by_region.sort(key=lambda x: x["count"], reverse=True)

    return {
        "total": total,
        "user_count": user_count,
        "overall_avg": overall_avg,
        "by_region": by_region
    }


@app.delete("/records/{record_id}")
def delete_record(record_id: str):
    if not DATA_FILE.exists():
        raise HTTPException(status_code=404, detail="Record not found")

    records = []
    found = False
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                record = json.loads(line)
                if record["id"] == record_id:
                    found = True
                else:
                    records.append(record)

    if not found:
        raise HTTPException(status_code=404, detail="Record not found")

    temp_file = DATA_FILE.with_suffix(".tmp")
    with open(temp_file, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    temp_file.replace(DATA_FILE)

    return {"deleted": record_id}
