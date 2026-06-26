"use client";

import { useEffect } from "react";
import type { DesignParameters } from "@/lib/types";
import { useTranslations } from "@/i18n/use-translations";
import { useLanguage } from "@/i18n/language-provider";

export interface PricingBreakdown {
  floorArea: number;
  totalJoints: number;
  timberVolume: number;
  totalTrusses: number;
  supportNodes: number;
  bracketCount: number;
  gussetPlateCost: number;
  timberCost: number;
  assemblyCost: number;
  hangerCost: number;
  metalworkCost: number;
  subtotalCZK: number;
  roofType: string;
  roofTypeFactor: number;
  totalCZK: number;
  totalEUR: number;
}

const ROOF_TYPE_FACTORS: Record<string, number> = {
  gable: 1.0,
  hip: 1.3,
  "mono-pitch": 0.9,
  flat: 0.8,
};

export function computePricingBreakdown(
  parameters: DesignParameters
): PricingBreakdown | null {
  const dimStr = parameters.floorPlanDimensions?.trim();
  if (!dimStr) return null;

  const match = dimStr.match(
    /(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)\s*m?/i
  );
  if (!match) return null;

  const width = parseFloat(match[1]);
  const height = parseFloat(match[2]);
  const floorArea = width * height;

  const totalJoints = Math.round(floorArea * 1.32);
  const timberVolume = floorArea * 0.254;
  const totalTrusses = Math.round(floorArea * 0.147);
  const supportNodes = totalTrusses * 2;
  const bracketCount = Math.round(supportNodes * 1.6);

  const gussetPlateCost = totalJoints * 50;
  const timberCost = timberVolume * 6200;
  const assemblyCost = (totalTrusses / 20) * 18000;
  const hangerCost = totalTrusses * 120;
  const metalworkCost = bracketCount * 370;

  const roofTypeStr = parameters.roofType?.trim() ?? "";
  const roofTypeFactor =
    ROOF_TYPE_FACTORS[roofTypeStr.toLowerCase()] ?? 1.0;

  const subtotalCZK =
    gussetPlateCost + timberCost + assemblyCost + hangerCost + metalworkCost;
  const totalCZK = subtotalCZK * roofTypeFactor;
  const totalEUR = Math.round(totalCZK / 25);

  return {
    floorArea,
    totalJoints,
    timberVolume,
    totalTrusses,
    supportNodes,
    bracketCount,
    gussetPlateCost,
    timberCost,
    assemblyCost,
    hangerCost,
    metalworkCost,
    subtotalCZK,
    roofType: roofTypeStr,
    roofTypeFactor,
    totalCZK,
    totalEUR,
  };
}

interface PricingBreakdownModalProps {
  open: boolean;
  onClose: () => void;
  parameters: DesignParameters;
  price: number | "---";
}

export function PricingBreakdownModal({
  open,
  onClose,
  parameters,
  price,
}: PricingBreakdownModalProps) {
  const t = useTranslations("pricing");
  const { locale } = useLanguage();
  const numberLocale = locale === "sk" ? "sk-SK" : "en-US";

  function fmt(n: number): string {
    return new Intl.NumberFormat(numberLocale).format(n);
  }

  useEffect(() => {
    if (!open) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [open, onClose]);

  if (!open) return null;

  const breakdown = computePricingBreakdown(parameters);

  return (
    <div
      className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center"
      onClick={onClose}
    >
      <div
        className="bg-[#1a1a2e] rounded-2xl shadow-2xl p-6 max-w-lg w-[90vw] max-h-[85vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold text-white">
            {t("title")}
          </h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white text-xl leading-none"
          >
            &times;
          </button>
        </div>

        {breakdown ? (
          <table className="w-full text-sm text-left">
            <tbody>
              <tr className="border-b border-white/10">
                <td className="py-1.5 text-gray-300 underline decoration-dotted cursor-pointer" title={t("floorAreaTooltip")}>{t("floorArea")}</td>
                <td className="py-1.5 text-white text-right">
                  {fmt(breakdown.floorArea)} m&sup2;
                </td>
              </tr>
              <tr className="border-b border-white/10">
                <td className="py-1.5 text-gray-300 underline decoration-dotted cursor-pointer" title={t("jointsTooltip")}>{t("joints")}</td>
                <td className="py-1.5 text-white text-right">
                  {fmt(breakdown.totalJoints)}
                </td>
              </tr>
              <tr className="border-b border-white/10">
                <td className="py-1.5 text-gray-300 underline decoration-dotted cursor-pointer" title={t("gussetPlateCostTooltip")}>{t("gussetPlateCost")}</td>
                <td className="py-1.5 text-white text-right">
                  {fmt(breakdown.totalJoints)} &times; 50 ={" "}
                  {fmt(breakdown.gussetPlateCost)} CZK
                </td>
              </tr>
              <tr className="border-b border-white/10">
                <td className="py-1.5 text-gray-300 underline decoration-dotted cursor-pointer" title={t("timberVolumeTooltip")}>{t("timberVolume")}</td>
                <td className="py-1.5 text-white text-right">
                  {fmt(breakdown.timberVolume)} m&sup3;
                </td>
              </tr>
              <tr className="border-b border-white/10">
                <td className="py-1.5 text-gray-300 underline decoration-dotted cursor-pointer" title={t("timberCostTooltip")}>{t("timberCost")}</td>
                <td className="py-1.5 text-white text-right">
                  {fmt(breakdown.timberVolume)} &times; 6,200 ={" "}
                  {fmt(breakdown.timberCost)} CZK
                </td>
              </tr>
              <tr className="border-b border-white/10">
                <td className="py-1.5 text-gray-300 underline decoration-dotted cursor-pointer" title={t("trussesTooltip")}>{t("trusses")}</td>
                <td className="py-1.5 text-white text-right">
                  {fmt(breakdown.totalTrusses)}
                </td>
              </tr>
              <tr className="border-b border-white/10">
                <td className="py-1.5 text-gray-300 underline decoration-dotted cursor-pointer" title={t("assemblyCostTooltip")}>{t("assemblyCost")}</td>
                <td className="py-1.5 text-white text-right">
                  {fmt(breakdown.totalTrusses)}/20 &times; 18,000 ={" "}
                  {fmt(breakdown.assemblyCost)} CZK
                </td>
              </tr>
              <tr className="border-b border-white/10">
                <td className="py-1.5 text-gray-300 underline decoration-dotted cursor-pointer" title={t("hangerCostTooltip")}>{t("hangerCost")}</td>
                <td className="py-1.5 text-white text-right">
                  {fmt(breakdown.totalTrusses)} &times; 120 ={" "}
                  {fmt(breakdown.hangerCost)} CZK
                </td>
              </tr>
              <tr className="border-b border-white/10">
                <td className="py-1.5 text-gray-300 underline decoration-dotted cursor-pointer" title={t("metalworkCostTooltip")}>{t("metalworkCost")}</td>
                <td className="py-1.5 text-white text-right">
                  {fmt(breakdown.bracketCount)} &times; 370 ={" "}
                  {fmt(breakdown.metalworkCost)} CZK
                </td>
              </tr>
              <tr className="border-b border-white/20 font-semibold">
                <td className="py-1.5 text-gray-200 underline decoration-dotted cursor-pointer" title={t("subtotalTooltip")}>{t("subtotal")}</td>
                <td className="py-1.5 text-white text-right">
                  {fmt(breakdown.subtotalCZK)} CZK
                </td>
              </tr>
              <tr className="border-b border-white/10">
                <td className="py-1.5 text-gray-300 underline decoration-dotted cursor-pointer" title={t("roofTypeTooltip")}>{t("roofType")}</td>
                <td className="py-1.5 text-white text-right">
                  {breakdown.roofType || t("unknown")} (&times;
                  {breakdown.roofTypeFactor})
                </td>
              </tr>
              <tr className="border-b border-white/20 font-semibold">
                <td className="py-1.5 text-gray-200 underline decoration-dotted cursor-pointer" title={t("totalCZKTooltip")}>{t("totalCZK")}</td>
                <td className="py-1.5 text-white text-right">
                  {fmt(breakdown.totalCZK)} CZK
                </td>
              </tr>
              <tr className="font-bold">
                <td className="py-1.5 text-gray-100 underline decoration-dotted cursor-pointer" title={t("totalEURTooltip")}>{t("totalEUR")}</td>
                <td className="py-1.5 text-white text-right">
                  &euro;{fmt(breakdown.totalEUR)}
                </td>
              </tr>
            </tbody>
          </table>
        ) : (
          <p className="text-gray-400 text-sm">
            {t("error")}
          </p>
        )}

        {price != null && (
          <p className="mt-4 pt-3 border-t border-white/10 text-xs text-gray-400">
            {t("storedPrice")} {price === "---" ? "---" : `\u20AC${new Intl.NumberFormat(numberLocale).format(Number(price))}`} {t("exclVAT")}
          </p>
        )}
      </div>
    </div>
  );
}
