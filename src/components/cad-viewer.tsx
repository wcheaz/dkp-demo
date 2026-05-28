"use client";

import { useEffect, useRef, useState } from "react";

interface CadViewerProps {
  dxfContent: string;
  className?: string;
}

function base64ToArrayBuffer(base64: string): ArrayBuffer {
  const binaryString = atob(base64);
  const bytes = new Uint8Array(binaryString.length);
  for (let i = 0; i < binaryString.length; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  return bytes.buffer;
}

export function CadViewer({ dxfContent, className }: CadViewerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const initializedRef = useRef(false);
  const moduleRef = useRef<typeof import("@mlightcad/cad-simple-viewer") | null>(null);
  const docManagerRef = useRef<import("@mlightcad/cad-simple-viewer").AcApDocManager | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;
    if (initializedRef.current) return;

    let destroyed = false;

    async function init() {
      const mod = await import("@mlightcad/cad-simple-viewer");

      if (destroyed) return;

      moduleRef.current = mod;

      const result = mod.AcApDocManager.createInstance({
        container: containerRef.current!,
        webworkerFileUrls: {
          dxfParser: "/workers/libredwg-parser-worker.js",
          mtextRender: "/workers/mtext-renderer-worker.js",
        },
      });

      const docManager = result ?? mod.AcApDocManager.instance;
      docManagerRef.current = docManager;

      initializedRef.current = true;

      if (dxfContent) {
        try {
          const arrayBuffer = base64ToArrayBuffer(dxfContent);
          const success = await docManager.openDocument("design.dxf", arrayBuffer, {});
          if (!success) {
            setError("Failed to load CAD drawing");
          } else {
            setError(null);
          }
        } catch {
          setError("Failed to load CAD drawing");
        }
      }
    }

    init();

    return () => {
      destroyed = true;
      if (initializedRef.current && moduleRef.current) {
        moduleRef.current.AcApDocManager.instance.destroy();
        initializedRef.current = false;
        moduleRef.current = null;
        docManagerRef.current = null;
      }
    };
  }, []);

  useEffect(() => {
    if (!dxfContent || !initializedRef.current || !docManagerRef.current) return;

    let cancelled = false;

    async function loadDxf() {
      try {
        const arrayBuffer = base64ToArrayBuffer(dxfContent);
        const success = await docManagerRef.current!.openDocument("design.dxf", arrayBuffer, {});
        if (!cancelled) {
          if (!success) {
            setError("Failed to load CAD drawing");
          } else {
            setError(null);
          }
        }
      } catch {
        if (!cancelled) {
          setError("Failed to load CAD drawing");
        }
      }
    }

    loadDxf();

    return () => {
      cancelled = true;
    };
  }, [dxfContent]);

  return (
    <div
      ref={containerRef}
      className={className}
    >
      {error && (
        <div className="flex items-center justify-center w-full h-full text-red-500">
          {error}
        </div>
      )}
    </div>
  );
}
