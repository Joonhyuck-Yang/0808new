from fastapi import FastAPI
import os

app = FastAPI(title="Simple Gateway API")

@app.get("/")
async def root():
    return {"message": "Hello from Railway!"}

@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy!", "message": "Gateway API is running"}

@app.post("/api/v1/signup")
async def signup(request):
    return {
        "status": "success",
        "message": "회원가입됨!",
        "railway_logged": True
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
