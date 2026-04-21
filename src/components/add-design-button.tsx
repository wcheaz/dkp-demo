import { AgentState, DesignEntry } from "@/lib/types";

export interface AddDesignButtonProps {
  state: AgentState;
  setState: (state: AgentState) => void;
}

export function AddDesignButton({ state, setState }: AddDesignButtonProps) {
  const handleClick = () => {
    const designs = state.designs ?? [];
    const nextId = Math.max(...designs.map((d) => d.id ?? 0), 0) + 1;
    const newEntry: DesignEntry = {
      id: nextId,
      imageUrl: "/next.svg",
      promptText: `Test design #${nextId}`,
    };
    setState({
      ...state,
      designs: [...(state.designs ?? []), newEntry],
    });
  };

  return (
    <button
      onClick={handleClick}
      className="bg-white/20 hover:bg-white/30 text-white font-bold py-2 px-4 rounded-full"
    >
      Add Test Design
    </button>
  );
}
