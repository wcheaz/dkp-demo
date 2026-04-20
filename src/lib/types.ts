export interface DesignEntry {
  imageUrl: string;
  promptText: string;
}

export type AgentState = {
  designs: DesignEntry[];
};
