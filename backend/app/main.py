from fastapi import FastAPI

app = FastAPI(title="IBVAP API", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "ibvap-backend", "version": "0.1.0"}
