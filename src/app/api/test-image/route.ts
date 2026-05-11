import { NextResponse } from "next/server";
import { readFile } from "fs/promises";
import { join } from "path";

export async function GET() {
  const filePath = join(process.cwd(), "tmp", "test-assets", "test-image.png");

  try {
    const buffer = await readFile(filePath);
    return new NextResponse(buffer, {
      status: 200,
      headers: {
        "Content-Type": "image/png",
      },
    });
  } catch {
    return NextResponse.json(
      { error: "Test image not found" },
      { status: 404 }
    );
  }
}
