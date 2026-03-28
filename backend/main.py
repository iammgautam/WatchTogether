# def main():
#     print("Hello from backend!")


# if __name__ == "__main__":
#     main()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# This is critical! It allows our Vue frontend to talk to our API safely.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/ping")
def get_ping():
    return {"message": "Pong! The FastAPI backend is alive and connected!"}
