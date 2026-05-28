import logging
import os

from src.agent import YourState, StateDeps, agent, DesignParameters
from src.dxf_builder import build_dxf
import logfire
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

logfire.configure()
logfire.instrument_pydantic_ai()

app = agent.to_ag_ui(deps=StateDeps(state=YourState()))

ui_origin = os.getenv("UI_ORIGIN", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ui_origin],
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["application/json", "content-type"],
)


async def health_check(request: Request):
    return JSONResponse(
        status_code=200,
        content={"status": "healthy", "message": "Application is running"},
    )


async def dxf_generate(request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            status_code=422,
            content={"error": "Invalid or malformed JSON body"},
        )

    try:
        params = DesignParameters(**body)
    except Exception:
        return JSONResponse(
            status_code=422,
            content={"error": "Invalid parameters"},
        )

    try:
        dxf_bytes = build_dxf(params)
    except ValueError as exc:
        return JSONResponse(
            status_code=400,
            content={"error": str(exc)},
        )

    return Response(
        content=dxf_bytes,
        media_type="application/dxf",
        headers={
            "Content-Disposition": 'attachment; filename="design.dxf"',
        },
    )


app.router.add_route("/api/health", health_check, methods=["GET"])
app.router.add_route("/api/dxf/generate", dxf_generate, methods=["POST"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=True)
