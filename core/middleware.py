# core/middleware.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging

logging.basicConfig(level=logging.INFO)

origins = [
    
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:5501",
    "http://localhost:5501",
]



class ResponseTimeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        """
        The dispatch method is called for every incoming request.
        """
        start_time = time.time()
        
        # Process the request and get the response
        response = await call_next(request)
        
        # Calculate the elapsed time
        process_time = time.time() - start_time
        
        # Add a custom header to the response with the processing time
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log the request and processing time
        logging.info(f"Request: {request.method} {request.url.path} | "
                     f"Status: {response.status_code} | "
                     f"Process Time: {process_time:.4f}s")
        
        return response
    

def add_all_middleware(app: FastAPI):
    """
    Add all middleware to the FastAPI app
    """
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Response time middleware
    app.add_middleware(ResponseTimeMiddleware)
    
    return app