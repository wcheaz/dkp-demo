"use client";

import dynamic from "next/dynamic";
import { useEffect, useMemo, useState } from "react";
import { AgentState, DesignParameters, MaterialStats } from "@/lib/types";
import { PricingBreakdownModal } from "@/components/pricing-breakdown-modal";
import { useTranslations } from "@/i18n/use-translations";
import { useLanguage } from "@/i18n/language-provider";

const CadViewer = dynamic(() => import("@/components/cad-viewer").then((m) => m.CadViewer), { ssr: false });

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

function DxfDownloadButton({ dxfContent, entryId }: { dxfContent: string; entryId: string | number }) {
  const t = useTranslations("designs");
  const blobUrl = useMemo(() => {
    const binary = atob(dxfContent);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
    return URL.createObjectURL(new Blob([bytes], { type: "application/dxf" }));
  }, [dxfContent]);

  useEffect(() => {
    return () => URL.revokeObjectURL(blobUrl);
  }, [blobUrl]);

  return (
    <a
      href={blobUrl}
      download={`design-${entryId}.dxf`}
      className="mt-2 inline-flex items-center gap-1.5 text-sm text-blue-400 hover:text-blue-300 transition-colors"
    >
      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 14 14" fill="none">
        <path d="M7 1v9M3 7l4 4 4-4M1 12h12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
      {t("downloadDxf")}
    </a>
  );
}

export interface DesignComponentProps {
  state: AgentState;
  setState: (state: AgentState) => void;
}

export function DesignComponent({ state, setState }: DesignComponentProps) {
  const designs = state.designs ?? [];
  const [modalImageUrl, setModalImageUrl] = useState<string | null>(null);
  const [pricingModalIndex, setPricingModalIndex] = useState<number | null>(null);
  const t = useTranslations();
  const { locale } = useLanguage();
  const numberLocale = locale === "sk" ? "sk-SK" : "en-US";

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
    <div className="w-full p-6">
      <h2 className="text-2xl font-bold mb-4">{t("designs.heading")}</h2>

      {designs.length === 0 ? (
        <p className="text-gray-400 text-center py-12">
          {t("designs.empty")}
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
                    <p className="mt-3 text-sm text-gray-300">{t("designs.generating")}</p>
                  </div>
                ) : hasIncompleteParameters(entry.parameters) ? (
                  <img
                    src="/design-in-progress.svg"
                    alt={t("designs.designInProgress")}
                    className="w-[55%] h-[27vh] object-contain"
                  />
                ) : entry.dxfContent ? (
                  <div className="w-[55%]">
                    <CadViewer dxfContent={entry.dxfContent} className="w-full h-[27vh]" />
                    <DxfDownloadButton dxfContent={entry.dxfContent} entryId={entry.id} />
                  </div>
                ) : (
                  <div className="w-[55%]">
                    <img
                      src={entry.imageUrl}
                      alt={entry.promptText}
                      className="w-full h-[27vh] object-contain cursor-pointer"
                      onClick={() => setModalImageUrl(entry.imageUrl)}
                    />
                    <div className="flex items-center justify-center gap-2 mt-1">
                      <div className="w-4 h-4 border-2 border-gray-400 border-t-transparent rounded-full animate-spin" />
                      <p className="text-sm text-gray-300">{t("designs.generatingCad")}</p>
                    </div>
                  </div>
                )}
              </div>
              <p className="mt-3 text-center text-sm font-medium rounded-lg px-3 py-1.5 text-design-description-text bg-design-description-bg">
                {entry.promptText}
              </p>
              {(() => {
                const filledEntries = entry.parameters
                  ? ALL_PARAM_KEYS
                  : [];
                if (filledEntries.length === 0 && entry.price == null) return null;
                return (
                  <div className="mt-2 pt-2 border-t border-design-param-border">
                    <div className="grid grid-cols-2 gap-x-3 gap-y-1 text-sm">
                      {filledEntries.map((k) => (
                        <div key={k} className="flex items-center gap-1.5 bg-design-param-bg rounded-md px-2 py-1">
                          <span className="text-design-param-label font-medium">{t(`designs.params.${k}`)}:</span>
                          <span className="text-design-param-value font-semibold">{String(entry.parameters![k])}</span>
                        </div>
                      ))}
                    </div>
                    {entry.materialStats && (
                      <>
                        <div className="flex items-center gap-2 my-2">
                          <div className="flex-1 border-t border-design-material-border" />
                          <span className="text-design-material-label text-xs font-medium tracking-wide uppercase">{t("designs.materialEstimate")}</span>
                          <div className="flex-1 border-t border-design-material-border" />
                        </div>
                        <div className="grid grid-cols-2 gap-x-3 gap-y-1 text-sm">
                          {MATERIAL_STAT_KEYS.map((k) => (
                            <div key={k} className="flex items-center gap-1.5 bg-design-material-bg rounded-md px-2 py-1">
                              <span className="text-design-material-label font-medium">{t(`designs.labels.${k}`)}:</span>
                              <span className="text-design-material-value font-semibold">
                                {entry.materialStats![k] === "---"
                                  ? "---"
                                  : k === "timberVolume" || k === "roofArea"
                                    ? (entry.materialStats![k] as number).toFixed(2)
                                    : entry.materialStats![k]}
                                {entry.materialStats![k] !== "---" && MATERIAL_STAT_UNITS[k]}
                              </span>
                            </div>
                          ))}
                        </div>
                      </>
                    )}
                    {entry.price && (
                      <div className="mt-1.5 grid grid-cols-2 gap-x-3 gap-y-1 text-sm">
                        <div className="flex items-center gap-1.5 bg-design-price-bg rounded-md px-2 py-1">
                          <span className="text-design-price-label font-medium">{t("designs.price")}</span>
                          <span className="text-design-price-value font-semibold">
                            {entry.price === "---" ? "---" : `${t("designs.currency")}${new Intl.NumberFormat(numberLocale).format(entry.price)}`}
                          </span>
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
          price={designs[pricingModalIndex].price ?? "---"}
        />
      )}
    </div>
  );
}
