// State of the agent, make sure this aligns with your agent's state.
export type YourDataType = {
  // Customize this for your specific application
  id?: string;
  data?: any;
  // Add your specific data types here
};

export type AgentState = {
  your_data: YourDataType[];
}