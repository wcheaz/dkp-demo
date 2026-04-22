import {
  CopilotRuntime,
  ExperimentalEmptyAdapter,
  copilotRuntimeNextJSAppRouterEndpoint,
} from "@copilotkit/runtime";
import { HttpAgent } from "@ag-ui/client";
import { NextRequest, NextResponse } from "next/server";

const serviceAdapter = new ExperimentalEmptyAdapter();

const runtime = new CopilotRuntime({
  agents: {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    my_agent: new HttpAgent({ url: process.env.AGENT_URL || "http://localhost:8000/" }) as any,
  },
});

export const GET = async (req: NextRequest) => {
  const { searchParams } = new URL(req.url);
  const shouldFail = searchParams.get('fail') === 'true';

  if (shouldFail) {
    return NextResponse.json(
      { status: "unhealthy", timestamp: new Date().toISOString(), error: "Test failure scenario" },
      { status: 500 }
    );
  }

  return NextResponse.json(
    { status: "healthy", timestamp: new Date().toISOString() },
    { status: 200 }
  );
};

export const POST = async (req: NextRequest) => {
  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime,
    serviceAdapter,
    endpoint: "/api/copilotkit",
  });

  return handleRequest(req);
};
