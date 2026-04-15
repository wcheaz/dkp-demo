from src.agent import YourState, StateDeps, agent
import logfire
from starlette.requests import Request
from starlette.responses import JSONResponse

logfire.configure()
logfire.instrument_pydantic_ai()

app = agent.to_ag_ui(deps=StateDeps(state=YourState()))


async def health_check(request: Request):
    return JSONResponse(
        status_code=200,
        content={"status": "healthy", "message": "Application is running"},
    )


app.router.add_route("/api/health", health_check, methods=["GET"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=True)
