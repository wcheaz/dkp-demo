"use client";

import { useEffect, useRef, useState } from "react";
import { useTranslations } from "@/i18n/use-translations";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { FontLoader } from "three/examples/jsm/loaders/FontLoader.js";
import { DXFLoader } from "three-dxf-loader";
// @ts-ignore
import { Text } from "troika-three-text";

// Monkey patch troika-three-text for compatibility with newer Three.js versions (r175+)
if (typeof window !== "undefined") {
  try {
    const TextPrototype = (Text as any)?.prototype;
    if (TextPrototype) {
      if (!Object.getOwnPropertyDescriptor(TextPrototype, "customDepthMaterial")?.set) {
        Object.defineProperty(TextPrototype, "customDepthMaterial", {
          get() {
            return this._customDepthMaterial;
          },
          set(value) {
            this._customDepthMaterial = value;
          },
          configurable: true,
        });
      }
      if (!Object.getOwnPropertyDescriptor(TextPrototype, "customDistanceMaterial")?.set) {
        Object.defineProperty(TextPrototype, "customDistanceMaterial", {
          get() {
            return this._customDistanceMaterial;
          },
          set(value) {
            this._customDistanceMaterial = value;
          },
          configurable: true,
        });
      }
    }
  } catch (e) {
    console.error("Failed to patch troika-three-text:", e);
  }
}

interface CadViewer3DProps {
  dxfContent: string; // Base64 DXF data
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

export function CadViewer3D({ dxfContent, className }: CadViewer3DProps) {
  const t = useTranslations("designs");
  const containerRef = useRef<HTMLDivElement>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const controlsRef = useRef<OrbitControls | null>(null);
  const activeCameraRef = useRef<THREE.PerspectiveCamera | THREE.OrthographicCamera | null>(null);
  
  // Camera instances stored in refs to swap easily
  const perspectiveCameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const orthographicCameraRef = useRef<THREE.OrthographicCamera | null>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const modelGroupRef = useRef<THREE.Group | null>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [cameraType, setCameraType] = useState<"perspective" | "orthographic">("perspective");
  
  // Track geometry center and bounding size for preset cameras
  const geometryCenterRef = useRef<THREE.Vector3>(new THREE.Vector3(0, 0, 0));
  const geometrySizeRef = useRef<THREE.Vector3>(new THREE.Vector3(0, 0, 0));

  // Initialize Scene, Renderer, and Cameras
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const width = container.clientWidth || 800;
    const height = container.clientHeight || 600;

    // 1. Scene Setup
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1e1e1e); // Dark theme matching app
    sceneRef.current = scene;

    // 2. Lights Setup
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
    scene.add(ambientLight);

    const dirLight1 = new THREE.DirectionalLight(0xffffff, 0.6);
    dirLight1.position.set(1, 1, 1).normalize();
    scene.add(dirLight1);

    const dirLight2 = new THREE.DirectionalLight(0xffffff, 0.3);
    dirLight2.position.set(-1, -1, 1).normalize();
    scene.add(dirLight2);

    // 3. Renderer Setup
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(width, height);
    renderer.domElement.style.display = "block";
    renderer.domElement.style.width = "100%";
    renderer.domElement.style.height = "100%";
    container.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // 4. Cameras Setup
    const aspect = width / height;
    const pCam = new THREE.PerspectiveCamera(45, aspect, 1, 500000);
    const oCam = new THREE.OrthographicCamera(
      -width / 2, width / 2,
      height / 2, -height / 2,
      1, 500000
    );

    perspectiveCameraRef.current = pCam;
    orthographicCameraRef.current = oCam;

    const activeCamera = cameraType === "perspective" ? pCam : oCam;
    activeCameraRef.current = activeCamera;

    // 5. Controls Setup
    const controls = new OrbitControls(activeCamera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.screenSpacePanning = true;
    controlsRef.current = controls;

    // 6. Animation Loop
    let animationFrameId: number;
    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      if (controlsRef.current) {
        controlsRef.current.update();
      }
      if (rendererRef.current && sceneRef.current && activeCameraRef.current) {
        rendererRef.current.render(sceneRef.current, activeCameraRef.current);
      }
    };
    animate();

    // 7. Handle Resize
    const handleResize = () => {
      if (!container) return;
      const w = container.clientWidth;
      const h = container.clientHeight;
      const newAspect = w / h;

      if (rendererRef.current) {
        rendererRef.current.setSize(w, h, false);
      }

      if (perspectiveCameraRef.current) {
        perspectiveCameraRef.current.aspect = newAspect;
        perspectiveCameraRef.current.updateProjectionMatrix();
      }

      if (orthographicCameraRef.current) {
        const d = (geometrySizeRef.current.length() || 10000) * 0.8;
        orthographicCameraRef.current.left = -d * newAspect;
        orthographicCameraRef.current.right = d * newAspect;
        orthographicCameraRef.current.top = d;
        orthographicCameraRef.current.bottom = -d;
        orthographicCameraRef.current.updateProjectionMatrix();
      }
    };

    window.addEventListener("resize", handleResize);

    // Call handleResize after a short delay to get correct dimensions after layout mounts
    const timer = setTimeout(() => {
      handleResize();
    }, 100);

    // Cleanup
    return () => {
      clearTimeout(timer);
      window.removeEventListener("resize", handleResize);
      cancelAnimationFrame(animationFrameId);
      if (container && renderer.domElement.parentNode === container) {
        try {
          container.removeChild(renderer.domElement);
        } catch { /* no-op */ }
      }
      renderer.dispose();
      controls.dispose();
    };
  }, []);

  // Watch cameraType to swap camera instances dynamically
  useEffect(() => {
    if (!rendererRef.current || !controlsRef.current) return;

    const currentCam = activeCameraRef.current;
    let nextCam: THREE.PerspectiveCamera | THREE.OrthographicCamera;

    if (cameraType === "perspective") {
      nextCam = perspectiveCameraRef.current!;
    } else {
      nextCam = orthographicCameraRef.current!;
    }

    if (currentCam && nextCam) {
      // Sync position, orientation and target
      nextCam.position.copy(currentCam.position);
      nextCam.rotation.copy(currentCam.rotation);
      
      const target = controlsRef.current.target.clone();
      
      activeCameraRef.current = nextCam;
      controlsRef.current.object = nextCam;
      controlsRef.current.target.copy(target);
      controlsRef.current.update();

      // Trigger resize to fix Orthographic projection bounds
      window.dispatchEvent(new Event("resize"));
    }
  }, [cameraType]);

  // Load DXF content when it changes
  useEffect(() => {
    if (!dxfContent || !sceneRef.current) return;

    setLoading(true);
    setError(null);

    // Remove existing model group if any
    if (modelGroupRef.current) {
      sceneRef.current.remove(modelGroupRef.current);
      modelGroupRef.current = null;
    }

    let isDestroyed = false;
    let objectUrl = "";

    async function load() {
      try {
        const fontLoader = new FontLoader();
        // Load font (local typeface JSON file downloaded previously)
        const font = await new Promise<any>((resolve, reject) => {
          fontLoader.load(
            "/fonts/helvetiker_regular.typeface.json",
            (f) => resolve(f),
            undefined,
            () => reject(new Error("Font loading failed"))
          );
        }).catch((err) => {
          console.warn("Could not load typeface font. Text entities may be missing.", err);
          return null; // fallback gracefully without text rendering
        });

        if (isDestroyed) return;

        const loader = new DXFLoader();
        if (font) {
          loader.setFont(font);
        }
        loader.setEnableLayer(true);
        loader.setConsumeUnits(true);
        loader.setDefaultColor(0xffffff); // default white on dark background

        // Convert base64 to Blob URL
        const arrayBuffer = base64ToArrayBuffer(dxfContent);
        const blob = new Blob([arrayBuffer], { type: "application/dxf" });
        objectUrl = URL.createObjectURL(blob);

        loader.load(
          objectUrl,
          (dxfData: any) => {
            if (isDestroyed) return;
            if (!dxfData || !dxfData.entity) {
              setError("Invalid DXF data format");
              setLoading(false);
              return;
            }

            const modelGroup = dxfData.entity;
            modelGroupRef.current = modelGroup;
            sceneRef.current!.add(modelGroup);

            // Compute model boundaries
            const box = new THREE.Box3().setFromObject(modelGroup);
            const center = new THREE.Vector3();
            box.getCenter(center);
            const size = new THREE.Vector3();
            box.getSize(size);

            geometryCenterRef.current.copy(center);
            geometrySizeRef.current.copy(size);

            // Center controls target
            if (controlsRef.current) {
              controlsRef.current.target.copy(center);
            }

            // Adjust camera to fit geometry
            fitCamera(center, size);

            setLoading(false);
          },
          undefined,
          (err: any) => {
            console.error("Error loading DXF:", err);
            if (!isDestroyed) {
              setError("Failed to parse CAD drawing");
              setLoading(false);
            }
          }
        );
      } catch (err) {
        console.error("Load process failed:", err);
        if (!isDestroyed) {
          setError("Failed to read CAD drawing");
          setLoading(false);
        }
      }
    }

    load();

    return () => {
      isDestroyed = true;
      if (objectUrl) {
        URL.revokeObjectURL(objectUrl);
      }
    };
  }, [dxfContent]);

  // Zoom camera to fit model size
  const fitCamera = (center: THREE.Vector3, size: THREE.Vector3) => {
    const maxDim = Math.max(size.x, size.y, size.z) || 10000;
    
    // Set perspective camera distance
    if (perspectiveCameraRef.current) {
      const fovRad = (perspectiveCameraRef.current.fov * Math.PI) / 180;
      let cameraDistance = maxDim / (2 * Math.tan(fovRad / 2));
      cameraDistance *= 1.5; // add buffer
      
      perspectiveCameraRef.current.position.set(
        center.x + cameraDistance * 0.5,
        center.y - cameraDistance * 0.8,
        center.z + cameraDistance * 0.8
      );
      perspectiveCameraRef.current.lookAt(center);
      perspectiveCameraRef.current.updateProjectionMatrix();
    }

    // Set orthographic camera bounds
    if (orthographicCameraRef.current && containerRef.current) {
      const aspect = containerRef.current.clientWidth / containerRef.current.clientHeight;
      const d = maxDim * 0.8;
      
      orthographicCameraRef.current.left = -d * aspect;
      orthographicCameraRef.current.right = d * aspect;
      orthographicCameraRef.current.top = d;
      orthographicCameraRef.current.bottom = -d;
      
      orthographicCameraRef.current.position.set(
        center.x + d * 0.5,
        center.y - d * 0.8,
        center.z + d * 0.8
      );
      orthographicCameraRef.current.lookAt(center);
      orthographicCameraRef.current.updateProjectionMatrix();
    }

    if (controlsRef.current) {
      controlsRef.current.target.copy(center);
      controlsRef.current.update();
    }
  };

  const handleResetCamera = () => {
    fitCamera(geometryCenterRef.current, geometrySizeRef.current);
  };

  const setViewPreset = (preset: "top" | "front" | "side" | "isometric") => {
    const center = geometryCenterRef.current;
    const size = geometrySizeRef.current;
    const maxDim = Math.max(size.x, size.y, size.z) || 10000;
    const distance = maxDim * 1.5;

    const activeCam = activeCameraRef.current;
    if (!activeCam || !controlsRef.current) return;

    // Keep current zoom factor if Orthographic
    const isOrtho = activeCam instanceof THREE.OrthographicCamera;

    switch (preset) {
      case "top":
        activeCam.position.set(center.x, center.y, center.z + distance);
        break;
      case "front":
        activeCam.position.set(center.x, center.y - distance, center.z);
        break;
      case "side":
        activeCam.position.set(center.x + distance, center.y, center.z);
        break;
      case "isometric":
        activeCam.position.set(
          center.x + distance * 0.577,
          center.y - distance * 0.577,
          center.z + distance * 0.577
        );
        break;
    }

    activeCam.lookAt(center);
    controlsRef.current.target.copy(center);
    controlsRef.current.update();
  };

  return (
    <div className={`relative flex flex-col ${className}`}>
      {/* 3D Scene View Container */}
      <div ref={containerRef} className="w-full h-full flex-1" />

      {/* Loading & Error States */}
      {loading && (
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-[#1e1e1e]/80 text-[#d4d4d4] gap-3">
          <div className="w-8 h-8 border-2 border-[#007fd4] border-t-transparent rounded-full animate-spin" />
          <span className="text-sm font-medium tracking-wide">{t("parsingGeometry")}</span>
        </div>
      )}

      {error && (
        <div className="absolute inset-0 flex items-center justify-center bg-[#1e1e1e]/90 text-red-500 font-medium">
          {error}
        </div>
      )}

      {/* Viewport Control Panel */}
      {!loading && !error && (
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex flex-wrap items-center gap-2 px-4 py-2.5 rounded-xl bg-[#252526]/85 border border-[#3c3c3c] backdrop-blur-md shadow-2xl z-10 max-w-[90%] md:max-w-max">
          {/* Preset Buttons */}
          <div className="flex items-center gap-1 border-r border-[#3c3c3c] pr-2">
            <button
              onClick={() => setViewPreset("top")}
              className="px-2.5 py-1 text-xs font-semibold rounded bg-[#2d2d2d] hover:bg-[#3e3e3f] text-[#e0e0e0] border border-[#3e3e3f] active:bg-[#007fd4] active:border-[#007fd4] transition-all cursor-pointer"
              title="2D Top View"
            >
              {t("topView")}
            </button>
            <button
              onClick={() => setViewPreset("front")}
              className="px-2.5 py-1 text-xs font-semibold rounded bg-[#2d2d2d] hover:bg-[#3e3e3f] text-[#e0e0e0] border border-[#3e3e3f] transition-all cursor-pointer"
              title="Front elevation view"
            >
              {t("frontView")}
            </button>
            <button
              onClick={() => setViewPreset("side")}
              className="px-2.5 py-1 text-xs font-semibold rounded bg-[#2d2d2d] hover:bg-[#3e3e3f] text-[#e0e0e0] border border-[#3e3e3f] transition-all cursor-pointer"
              title="Side elevation view"
            >
              {t("sideView")}
            </button>
            <button
              onClick={() => setViewPreset("isometric")}
              className="px-2.5 py-1 text-xs font-semibold rounded bg-[#2d2d2d] hover:bg-[#3e3e3f] text-[#e0e0e0] border border-[#3e3e3f] transition-all cursor-pointer"
              title="Isometric 3D view"
            >
              {t("isometricView")}
            </button>
          </div>

          {/* Toggle Camera Projection Mode */}
          <div className="flex items-center gap-1 border-r border-[#3c3c3c] pr-2">
            <button
              onClick={() => setCameraType("perspective")}
              className={`px-2.5 py-1 text-xs font-semibold rounded border transition-all cursor-pointer ${
                cameraType === "perspective"
                  ? "bg-[#007fd4] border-[#007fd4] text-white"
                  : "bg-[#2d2d2d] border-[#3e3e3f] hover:bg-[#3e3e3f] text-[#e0e0e0]"
              }`}
            >
              {t("perspective")}
            </button>
            <button
              onClick={() => setCameraType("orthographic")}
              className={`px-2.5 py-1 text-xs font-semibold rounded border transition-all cursor-pointer ${
                cameraType === "orthographic"
                  ? "bg-[#007fd4] border-[#007fd4] text-white"
                  : "bg-[#2d2d2d] border-[#3e3e3f] hover:bg-[#3e3e3f] text-[#e0e0e0]"
              }`}
            >
              {t("orthographic")}
            </button>
          </div>

          {/* Reset View Button */}
          <button
            onClick={handleResetCamera}
            className="flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded bg-[#2d2d2d] hover:bg-[#3e3e3f] text-[#e0e0e0] border border-[#3e3e3f] transition-all cursor-pointer"
            title="Recenter and auto-zoom to fit drawing bounds"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={2}
              stroke="currentColor"
              className="w-3 h-3"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M9 9V4.5M9 9H4.5M9 9 3.75 3.75M9 15v4.5M9 15H4.5M9 15l-5.25 5.25M15 9V4.5M15 9h4.5M15 9l5.25-5.25M15 15v4.5M15 15h4.5M15 15l5.25 5.25"
              />
            </svg>
            {t("resetView")}
          </button>
        </div>
      )}
    </div>
  );
}
