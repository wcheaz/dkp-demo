"use client";

import { useEffect, useRef } from "react";

interface CadViewerProps {
  dxfContent: string;
  className?: string;
}

export function CadViewer({ dxfContent, className }: CadViewerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const initializedRef = useRef(false);
  const moduleRef = useRef<typeof import("@mlightcad/cad-simple-viewer") | null>(null);

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

      initializedRef.current = true;
    }

    init();

    return () => {
      destroyed = true;
      if (initializedRef.current && moduleRef.current) {
        moduleRef.current.AcApDocManager.instance.destroy();
        initializedRef.current = false;
        moduleRef.current = null;
      }
    };
  }, []);

  return (
    <div
      ref={containerRef}
      className={className}
    />
  );
}
