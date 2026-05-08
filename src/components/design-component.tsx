import { useEffect, useState } from "react";
import { AgentState, DesignParameters } from "@/lib/types";

const REQUIRED_FIELDS: (keyof DesignParameters)[] = [
  "buildingType",
  "floorPlanDimensions",
  "roofType",
  "roofPitch",
];

const PARAM_LABELS: Record<keyof DesignParameters, string> = {
  buildingType: "Building Type",
  floorPlanDimensions: "Floor Plan Dimensions",
  roofType: "Roof Type",
  roofPitch: "Roof Pitch",
  atticUsage: "Attic Usage",
  eavesShape: "Eaves Shape",
  wallConstruction: "Wall Construction",
  location: "Location",
  overhang: "Overhang",
};

const ALL_PARAM_KEYS: (keyof DesignParameters)[] = [
  "buildingType",
  "floorPlanDimensions",
  "roofType",
  "roofPitch",
  "atticUsage",
  "eavesShape",
  "wallConstruction",
  "location",
  "overhang",
];

export interface DesignComponentProps {
  state: AgentState;
  setState: (state: AgentState) => void;
}

export function DesignComponent({ state, setState }: DesignComponentProps) {
  const designs = state.designs ?? [];
  const parameters = state.parameters ?? {};
  const [modalImageUrl, setModalImageUrl] = useState<string | null>(null);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setModalImageUrl(null);
      }
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, []);

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">Designs</h2>

      <div className="mb-6 p-4 bg-white/10 backdrop-blur-md rounded-xl">
        <h3 className="text-lg font-semibold mb-3 text-gray-200">Design Parameters</h3>
        <div className="grid grid-cols-1 gap-1">
          {ALL_PARAM_KEYS.map((key) => {
            const value = parameters[key];
            const isRequired = REQUIRED_FIELDS.includes(key);
            return (
              <div key={key} className="flex items-center gap-2 text-sm">
                <span className="text-gray-400 min-w-[180px]">{PARAM_LABELS[key]}:</span>
                {value != null && value !== "" ? (
                  <span className="text-gray-200">{String(value)}</span>
                ) : isRequired ? (
                  <span className="text-yellow-400">&#9888; Required</span>
                ) : (
                  <span className="text-gray-500">&mdash;</span>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {designs.length === 0 ? (
        <p className="text-gray-400 text-center py-12">
          No designs available yet. Submit a prompt to generate your first
          design.
        </p>
      ) : (
        <div className="overflow-y-auto max-h-[80vh] space-y-4">
          {designs.map((entry, index) => (
            <div
              key={index}
              className="relative bg-white/20 backdrop-blur-md rounded-2xl shadow-xl p-4"
            >
              <span className="absolute top-2 left-3 text-xs font-semibold text-gray-300">
                #{entry.id}
              </span>
              <div className="flex justify-center">
                <img
                  src={entry.imageUrl}
                  alt={entry.promptText}
                  className="w-[55%] h-[27vh] object-contain cursor-pointer"
                  onClick={() => setModalImageUrl(entry.imageUrl)}
                />
              </div>
              <p className="mt-3 text-center text-sm text-gray-200">
                {entry.promptText}
              </p>
            </div>
          ))}
        </div>
      )}

      {modalImageUrl && (
        <div
          className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center"
          onClick={() => setModalImageUrl(null)}
        >
          <img
            src={modalImageUrl}
            alt="Enlarged design"
            className="max-w-[90vw] max-h-[90vh] object-contain"
            onClick={(e) => e.stopPropagation()}
          />
        </div>
      )}
    </div>
  );
}
