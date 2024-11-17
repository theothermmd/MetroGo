from collections import defaultdict
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from core import find_best_route
import time
import os
from dotenv import load_dotenv

load_dotenv()

CASHE = os.getenv('CASHE')
PORT = os.getenv('PORT')
LISTEN = os.getenv('LISTEN')


app = FastAPI()


RATE_LIMIT = 40
TIME_WINDOW = 60


request_counts = defaultdict(lambda: {"count": 0, "start_time": time.time()})


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "*"],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["Authorization", "Content-Type"],
)


class RouteRequest(BaseModel):
    source: str
    destination: str

    @field_validator("source", "destination")
    def not_empty(cls, value):
        if not value.strip():
            raise ValueError("Source and destination cannot be empty")
        return value


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    current_time = time.time()
    request_data = request_counts[client_ip]

    if current_time - request_data["start_time"] > TIME_WINDOW:

        request_counts[client_ip] = {"count": 1, "start_time": current_time}
    else:
        if request_data["count"] >= RATE_LIMIT:

            return JSONResponse(
                status_code=429,
                content={"message": "Rate limit exceeded. Please try again later."}
            )
        request_counts[client_ip]["count"] += 1

    response = await call_next(request)
    return response


@app.post("/get_route/")
async def get_route(request: RouteRequest):
    try:
        route_data = find_best_route(request.source, request.destination, CASHE)
        return JSONResponse(content=route_data, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=LISTEN, port=PORT)