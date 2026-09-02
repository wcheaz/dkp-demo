import logging
import os
from pathlib import Path

from src.agent import YourState, StateDeps, agent, DesignParameters
from src.dxf_builder import build_dxf
from src.ifc_builder import build_ifc
from src.mxf_builder import build_mxf
from src.patch_mxf_pricing import patch_mxf_bytes
import logfire
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

_LOG_FILE = Path(__file__).resolve().parents[2] / "logs" / "backend.log"
_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(_LOG_FILE),
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


async def mxf_generate(request: Request):
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

    logging.info("[mxf] request received — params: %s", body)

    try:
        mxf_bytes = build_mxf(params)
    except ValueError as exc:
        logging.error("[mxf] build_mxf failed: %s", exc)
        return JSONResponse(
            status_code=400,
            content={"error": str(exc)},
        )

    logging.info("[mxf] response sent — %d bytes", len(mxf_bytes))

    return Response(
        content=mxf_bytes,
        media_type="application/mxf",
        headers={
            "Content-Disposition": 'attachment; filename="design.mxf"',
        },
    )


async def mxf_patch_pricing(request: Request):
    try:
        mxf_bytes = await request.body()
    except Exception:
        return JSONResponse(
            status_code=422,
            content={"error": "Invalid or missing request body"},
        )

    logging.info("[mxf patch] request received — %d bytes", len(mxf_bytes))

    try:
        patched_bytes = patch_mxf_bytes(mxf_bytes)
    except Exception as exc:
        logging.error("[mxf patch] patch_mxf_bytes failed: %s", exc)
        return JSONResponse(
            status_code=400,
            content={"error": str(exc)},
        )

    logging.info("[mxf patch] response sent — %d bytes", len(patched_bytes))

    return Response(
        content=patched_bytes,
        media_type="application/mxf",
        headers={
            "Content-Disposition": 'attachment; filename="design_patched.mxf"',
        },
    )


app.router.add_route("/api/health", health_check, methods=["GET"])
app.router.add_route("/api/dxf/generate", dxf_generate, methods=["POST"])
app.router.add_route("/api/ifc/generate", ifc_generate, methods=["POST"])
app.router.add_route("/api/mxf/generate", mxf_generate, methods=["POST"])
app.router.add_route("/api/mxf/patch-pricing", mxf_patch_pricing, methods=["POST"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=True)
