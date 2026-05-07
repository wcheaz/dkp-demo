import { NextResponse } from "next/server";
import { readFile, stat } from "fs/promises";
import { join } from "path";

const CONTENT_TYPES: Record<string, string> = {
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".gif": "image/gif",
  ".svg": "image/svg+xml",
  ".webp": "image/webp",
};

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ filename: string }> }
) {
  const { filename } = await params;

  if (!/^[a-zA-Z0-9._-]+$/.test(filename)) {
    return NextResponse.json({ error: "Invalid filename" }, { status: 403 });
  }

  const filePath = join(
    process.cwd(),
    "tmp",
    "downloaded-images",
    filename
  );

  try {
    await stat(filePath);
  } catch {
    return NextResponse.json({ error: "Image not found" }, { status: 404 });
  }

  const ext = filename.substring(filename.lastIndexOf(".")).toLowerCase();
  const contentType = CONTENT_TYPES[ext] ?? "application/octet-stream";

  const buffer = await readFile(filePath);
  return new NextResponse(buffer, {
    status: 200,
    headers: {
      "Content-Type": contentType,
    },
  });
}
