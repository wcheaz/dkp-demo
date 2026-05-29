"use client";

import { useEffect, useRef, useState } from "react";

interface CadViewerProps {
  dxfContent: string;
  className?: string;
  onCapturePreview?: (dataUrl: string) => void;
}

function base64ToArrayBuffer(base64: string): ArrayBuffer {
  const binaryString = atob(base64);
  const bytes = new Uint8Array(binaryString.length);
  for (let i = 0; i < binaryString.length; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  return bytes.buffer;
}

function captureViewToDataUrl(
  docManager: import("@mlightcad/cad-simple-viewer").AcApDocManager,
): string | null {
  try {
    const view = docManager.curView;
    const renderer = view.renderer.internalRenderer;
    const scene = view.internalScene;
    const camera = view.internalCamera;
    if (!scene || !camera) return null;

    const width = view.width;
    const height = view.height;

    const originalRt = renderer.getRenderTarget();
    renderer.setRenderTarget(null);
    renderer.render(scene, camera);

    const gl = renderer.getContext() as WebGL2RenderingContext;
    const pixels = new Uint8Array(width * height * 4);
    gl.readPixels(0, 0, width, height, gl.RGBA, gl.UNSIGNED_BYTE, pixels);
    renderer.setRenderTarget(originalRt);

    // Flip vertically (WebGL renders upside-down)
    const flipped = new Uint8Array(width * height * 4);
    for (let y = 0; y < height; y++) {
      const srcRow = (height - 1 - y) * width * 4;
      const dstRow = y * width * 4;
      for (let x = 0; x < width * 4; x++) {
        flipped[dstRow + x] = pixels[srcRow + x];
      }
    }

    const canvas = document.createElement("canvas");
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext("2d")!;
    const imageData = ctx.createImageData(width, height);
    imageData.data.set(flipped);
    ctx.putImageData(imageData, 0, 0);

    return canvas.toDataURL("image/png");
  } catch {
    return null;
  }
}

export function CadViewer({ dxfContent, className, onCapturePreview }: CadViewerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const initializedRef = useRef(false);
  const moduleRef = useRef<typeof import("@mlightcad/cad-simple-viewer") | null>(null);
  const docManagerRef = useRef<import("@mlightcad/cad-simple-viewer").AcApDocManager | null>(null);
  const [error, setError] = useState<string | null>(null);
  const onCapturePreviewRef = useRef(onCapturePreview);
  useEffect(() => { onCapturePreviewRef.current = onCapturePreview; });

  function emitPreview() {
    if (!docManagerRef.current) return;
    const dataUrl = captureViewToDataUrl(docManagerRef.current);
    if (dataUrl) onCapturePreviewRef.current?.(dataUrl);
  }

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
        autoResize: true,
        webworkerFileUrls: {
          dxfParser: "/workers/dxf-parser-worker.js",
          dwgParser: "/workers/libredwg-parser-worker.js",
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
            setTimeout(() => {
              try {
                docManager.regen();
                docManager.curView.zoomToFitDrawing(5000);
              } catch { /* best-effort zoom */ }
              setTimeout(() => { if (!destroyed) emitPreview(); }, 1500);
            }, 500);
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
        emitPreview();
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
            setTimeout(() => {
              try {
                docManagerRef.current?.regen();
                docManagerRef.current?.curView.zoomToFitDrawing(5000);
              } catch { /* best-effort zoom */ }
              setTimeout(() => { if (!cancelled) emitPreview(); }, 1500);
            }, 500);
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
