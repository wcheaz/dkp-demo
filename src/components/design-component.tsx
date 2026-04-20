import { AgentState } from "@/lib/types";

export interface DesignComponentProps {
  state: AgentState;
  setState: (state: AgentState) => void;
}

export function DesignComponent({ state, setState }: DesignComponentProps) {
  return <div>DesignComponent placeholder</div>;
}
