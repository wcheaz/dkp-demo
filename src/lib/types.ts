export interface DesignEntry {
  id: number;
  imageUrl: string;
  promptText: string;
}

export type AgentState = {
  designs: DesignEntry[];
};
