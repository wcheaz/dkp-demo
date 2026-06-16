import logging
import os

from src.agent import YourState, StateDeps, agent, DesignParameters
from src.dxf_builder import build_dxf
from src.ifc_builder import build_ifc
import logfire
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("/home/ncheaz/git/dkp-demo/logs/backend.log"),
        logging.StreamHandler()
    ]
)

logfire.configure()
logfire.instrument_pydantic_ai()

app = agent.to_ag_ui(deps=StateDeps(state=YourState()))

ui_origin = os.getenv("UI_ORIGIN", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ui_origin],
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["content-type"],
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

    logging.info("[dxf] request received — params: %s", body)

    try:
        dxf_bytes = build_dxf(params)
    except ValueError as exc:
        logging.error("[dxf] build_dxf failed: %s", exc)
        return JSONResponse(
            status_code=400,
            content={"error": str(exc)},
        )

    logging.info("[dxf] response sent — %d bytes", len(dxf_bytes))

    return Response(
        content=dxf_bytes,
        media_type="application/dxf",
        headers={
            "Content-Disposition": 'attachment; filename="design.dxf"',
        },
    )


async def ifc_generate(request: Request):
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

    logging.info("[ifc] request received — params: %s", body)

    try:
        ifc_bytes = build_ifc(params)
    except ValueError as exc:
        logging.error("[ifc] build_ifc failed: %s", exc)
        return JSONResponse(
            status_code=400,
            content={"error": str(exc)},
        )

    logging.info("[ifc] response sent — %d bytes", len(ifc_bytes))

    return Response(
        content=ifc_bytes,
        media_type="application/ifc",
        headers={
            "Content-Disposition": 'attachment; filename="design.ifc"',
        },
    )


app.router.add_route("/api/health", health_check, methods=["GET"])
app.router.add_route("/api/dxf/generate", dxf_generate, methods=["POST"])
app.router.add_route("/api/ifc/generate", ifc_generate, methods=["POST"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=True)
