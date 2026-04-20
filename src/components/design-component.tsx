import { useEffect, useState } from "react";
import { AgentState } from "@/lib/types";

export interface DesignComponentProps {
  state: AgentState;
  setState: (state: AgentState) => void;
}

export function DesignComponent({ state, setState }: DesignComponentProps) {
  const designs = state.designs ?? [];
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
              className="bg-white/20 backdrop-blur-md rounded-2xl shadow-xl p-4"
            >
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
