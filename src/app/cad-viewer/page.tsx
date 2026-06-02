"use client";

import dynamic from "next/dynamic";
import { useCallback, useState, useRef, DragEvent, ChangeEvent } from "react";

const CadViewer = dynamic(
  () => import("@/components/cad-viewer").then((m) => m.CadViewer),
  { ssr: false }
);

const MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024;

export default function CadViewerPage() {
  const [dxfContent, setDxfContent] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const processFile = useCallback((file: File) => {
    if (!file.name.toLowerCase().endsWith(".dxf")) {
      setError("Please select a .dxf file");
      return;
    }
    if (file.size > MAX_FILE_SIZE_BYTES) {
      setError("File exceeds 10 MB limit");
      return;
    }
    setError(null);
    setLoading(true);
    setFileName(file.name);

    const reader = new FileReader();
    reader.onload = () => {
      const arrayBuffer = reader.result as ArrayBuffer;
      const bytes = new Uint8Array(arrayBuffer);
      let binary = "";
      const chunkSize = 8192;
      for (let i = 0; i < bytes.length; i += chunkSize) {
        const chunk = bytes.subarray(i, Math.min(i + chunkSize, bytes.length));
        binary += String.fromCharCode.apply(null, Array.from(chunk));
      }
      const base64 = btoa(binary);
      setDxfContent(base64);
      setLoading(false);
    };
    reader.onerror = () => {
      setError("Failed to read file");
      setLoading(false);
    };
    reader.readAsArrayBuffer(file);
  }, []);

  const handleDrop = useCallback(
    (e: DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      setIsDragOver(false);
      const file = e.dataTransfer.files?.[0];
      if (file) processFile(file);
    },
    [processFile]
  );

  const handleDragOver = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleFileInput = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) processFile(file);
      if (fileInputRef.current) fileInputRef.current.value = "";
    },
    [processFile]
  );

  const handleReset = useCallback(() => {
    setDxfContent(null);
    setFileName("");
    setError(null);
  }, []);

  return (
    <div className="min-h-screen bg-[#1e1e1e] text-[#d4d4d4] flex flex-col">
      <header className="flex items-center justify-between px-6 py-4 border-b border-[#333]">
        <h1 className="text-lg font-semibold tracking-wide text-[#e0e0e0]">
          CAD Test Viewer
        </h1>
        {fileName && (
          <div className="flex items-center gap-3">
            <span className="text-sm text-[#858585]">{fileName}</span>
            <button
              onClick={handleReset}
              className="px-3 py-1 text-sm rounded bg-[#333] hover:bg-[#444] text-[#d4d4d4] transition-colors"
            >
              Clear
            </button>
          </div>
        )}
      </header>

      <main className="flex-1 flex flex-col">
        {dxfContent ? (
          <div className="flex-1 relative">
            <CadViewer
              dxfContent={dxfContent}
              className="w-full h-full absolute inset-0"
            />
          </div>
        ) : (
          <div className="flex-1 flex items-center justify-center p-8">
            <div
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onClick={() => fileInputRef.current?.click()}
              className={`
                w-full max-w-xl h-72 rounded-xl border-2 border-dashed
                flex flex-col items-center justify-center gap-4 cursor-pointer
                transition-all duration-200
                ${
                  isDragOver
                    ? "border-[#007fd4] bg-[#007fd4]/10"
                    : "border-[#555] bg-[#252526] hover:border-[#007fd4] hover:bg-[#2a2a2a]"
                }
              `}
            >
              {loading ? (
                <div className="flex flex-col items-center gap-3">
                  <div className="w-8 h-8 border-2 border-[#007fd4] border-t-transparent rounded-full animate-spin" />
                  <span className="text-sm text-[#858585]">
                    Loading file...
                  </span>
                </div>
              ) : (
                <>
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    strokeWidth={1.5}
                    stroke="currentColor"
                    className="w-12 h-12 text-[#555]"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5m-13.5-9L12 3m0 0 4.5 4.5M12 3v13.5"
                    />
                  </svg>
                  <div className="text-center">
                    <p className="text-[#d4d4d4] text-sm font-medium">
                      Drag & drop a DXF file here
                    </p>
                    <p className="text-[#858585] text-xs mt-1">
                      or click to browse (max 10 MB)
                    </p>
                  </div>
                </>
              )}
            </div>
            <input
              ref={fileInputRef}
              type="file"
              accept=".dxf"
              className="hidden"
              onChange={handleFileInput}
            />
          </div>
        )}

        {error && (
          <div className="px-6 py-3 bg-red-900/30 border-t border-red-800 text-red-300 text-sm">
            {error}
          </div>
        )}
      </main>
    </div>
  );
}
