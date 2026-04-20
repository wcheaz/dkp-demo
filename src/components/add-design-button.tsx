import { AgentState, DesignEntry } from "@/lib/types";

export interface AddDesignButtonProps {
  state: AgentState;
  setState: (state: AgentState) => void;
}

export function AddDesignButton({ state, setState }: AddDesignButtonProps) {
  const handleClick = () => {
    const nextCount = (state.designs?.length ?? 0) + 1;
    const newEntry: DesignEntry = {
      imageUrl: "tmp/next.svg",
      promptText: `Test design #${nextCount}`,
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
