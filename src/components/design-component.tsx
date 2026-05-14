import { useEffect, useState } from "react";
import { AgentState, DesignParameters, MaterialStats } from "@/lib/types";
import { PricingBreakdownModal } from "@/components/pricing-breakdown-modal";

const MATERIAL_STAT_LABELS: Record<keyof MaterialStats, string> = {
  totalTrusses: "Trusses",
  timberVolume: "Timber Vol.",
  totalJoints: "Joints",
  roofArea: "Roof Area",
};

const MATERIAL_STAT_UNITS: Record<keyof MaterialStats, string> = {
  totalTrusses: "",
  timberVolume: " m\u00B3",
  totalJoints: "",
  roofArea: " m\u00B2",
};

const MATERIAL_STAT_KEYS: (keyof MaterialStats)[] = [
  "totalTrusses",
  "timberVolume",
  "totalJoints",
  "roofArea",
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

function isIncomplete(value: string | number | undefined): boolean {
  return value === undefined || value === null || value === "" || value === "---";
}

function hasIncompleteParameters(params: DesignParameters | undefined): boolean {
  if (!params) return true;
  return ALL_PARAM_KEYS.some((k) => isIncomplete(params[k]));
}

export interface DesignComponentProps {
  state: AgentState;
  setState: (state: AgentState) => void;
}

export function DesignComponent({ state, setState }: DesignComponentProps) {
  const designs = state.designs ?? [];
  const [modalImageUrl, setModalImageUrl] = useState<string | null>(null);
  const [pricingModalIndex, setPricingModalIndex] = useState<number | null>(null);

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
              <button
                onClick={() => setState({ ...state, designs: designs.filter((_, i) => i !== index) })}
                className="absolute top-2 right-3 z-10 w-6 h-6 flex items-center justify-center rounded-full text-gray-400 hover:text-white hover:bg-white/20 transition-colors"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 14 14" fill="none">
                  <path d="M1 1L13 13M1 13L13 1" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                </svg>
              </button>
              <div className="flex justify-center relative">
                {entry.status === "processing" ? (
                  <div className="w-[55%] h-[27vh] flex flex-col items-center justify-center bg-white/10 rounded-xl">
                    <div className="w-10 h-10 border-4 border-gray-400 border-t-transparent rounded-full animate-spin" />
                    <p className="mt-3 text-sm text-gray-300">Generating truss structure...</p>
                  </div>
                ) : hasIncompleteParameters(entry.parameters) ? (
                  <img
                    src="/design-in-progress.svg"
                    alt="Design In Progress"
                    className="w-[55%] h-[27vh] object-contain"
                  />
                ) : (
                  <img
                    src={entry.imageUrl}
                    alt={entry.promptText}
                    className="w-[55%] h-[27vh] object-contain cursor-pointer"
                    onClick={() => setModalImageUrl(entry.imageUrl)}
                  />
                )}
              </div>
              <p className="mt-3 text-center text-sm font-medium rounded-lg px-3 py-1.5 text-design-description-text bg-design-description-bg">
                {entry.promptText}
              </p>
              {(() => {
                const filledEntries = entry.parameters
                  ? ALL_PARAM_KEYS.filter(
                      (k) => entry.parameters?.[k] != null && entry.parameters?.[k] !== "" && entry.parameters?.[k] !== "---"
                    )
                  : [];
                if (filledEntries.length === 0 && !entry.price) return null;
                return (
                  <div className="mt-2 pt-2 border-t border-design-param-border">
                    <div className="grid grid-cols-2 gap-x-3 gap-y-1 text-sm">
                      {filledEntries.map((k) => (
                        <div key={k} className="flex items-center gap-1.5 bg-design-param-bg rounded-md px-2 py-1">
                          <span className="text-design-param-label font-medium">{PARAM_LABELS[k]}:</span>
                          <span className="text-design-param-value font-semibold">{String(entry.parameters![k])}</span>
                        </div>
                      ))}
                    </div>
                    {entry.materialStats && (
                      <>
                        <div className="flex items-center gap-2 my-2">
                          <div className="flex-1 border-t border-design-material-border" />
                          <span className="text-design-material-label text-xs font-medium tracking-wide uppercase">Material Estimate</span>
                          <div className="flex-1 border-t border-design-material-border" />
                        </div>
                        <div className="grid grid-cols-2 gap-x-3 gap-y-1 text-sm">
                          {MATERIAL_STAT_KEYS.map((k) => (
                            <div key={k} className="flex items-center gap-1.5 bg-design-material-bg rounded-md px-2 py-1">
                              <span className="text-design-material-label font-medium">{MATERIAL_STAT_LABELS[k]}:</span>
                              <span className="text-design-material-value font-semibold">
                                {k === "timberVolume" || k === "roofArea"
                                  ? entry.materialStats![k].toFixed(2)
                                  : entry.materialStats![k]}
                                {MATERIAL_STAT_UNITS[k]}
                              </span>
                            </div>
                          ))}
                        </div>
                      </>
                    )}
                    {entry.price && (
                      <div className="mt-1.5 grid grid-cols-2 gap-x-3 gap-y-1 text-sm">
                        <div className="flex items-center gap-1.5 bg-design-price-bg rounded-md px-2 py-1">
                          <span className="text-design-price-label font-medium">Price:</span>
                          <span className="text-design-price-value font-semibold">{entry.price}</span>
                          {entry.price !== "---" && (
                          <svg
                            xmlns="http://www.w3.org/2000/svg"
                            width="16"
                            height="16"
                            viewBox="0 0 16 16"
                            fill="none"
                            className="cursor-pointer text-gray-400 hover:text-white flex-shrink-0"
                            onClick={() => setPricingModalIndex(index)}
                          >
                            <circle cx="8" cy="8" r="7" stroke="currentColor" strokeWidth="1.5" fill="none" />
                            <text x="8" y="12" textAnchor="middle" fontSize="10" fontWeight="bold" fill="currentColor">!</text>
                          </svg>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })()}
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

      {pricingModalIndex !== null && designs[pricingModalIndex] && (
        <PricingBreakdownModal
          open={true}
          onClose={() => setPricingModalIndex(null)}
          parameters={designs[pricingModalIndex].parameters ?? {}}
          price={designs[pricingModalIndex].price ?? ""}
        />
      )}
    </div>
  );
}
