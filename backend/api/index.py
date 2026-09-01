import sys
import os
import traceback

app = None

try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    backend_dir = os.path.join(parent_dir, "backend")

    for d in [current_dir, parent_dir, backend_dir]:
        if os.path.exists(d) and d not in sys.path:
            sys.path.insert(0, d)

    # Try importing from app.main or backend.app.main
    try:
        from app.main import app as real_app
    except ImportError:
        from backend.app.main import app as real_app

    app = real_app

except Exception as err:
    err_tb = traceback.format_exc()
    print(f"[Vercel Startup Error]: {err_tb}")
    
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    from fastapi.middleware.cors import CORSMiddleware

    app = FastAPI(title="Diagnostic Serverless Fallback")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    async def catch_all(full_path: str = ""):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Backend Startup Exception on Vercel",
                "detail": str(err),
                "traceback": err_tb
            }
        )
