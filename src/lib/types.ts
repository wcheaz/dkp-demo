// State of the agent, make sure this aligns with your agent's state.
export type YourDataType = {
  // Customize this for your specific application
  id?: string;
  data?: any;
  // Add your specific data types here
};

// Domain-specific state fields - uncomment and adapt for your project
// Example: procurement-specific state
// export type ProcurementCode = {
//   code: string;
//   description: string;
// };

// export type AgentState = {
//   your_data: YourDataType[];
//   procurement_codes?: ProcurementCode[];  // Commented out for genericization
// };

// AgentState defines the shared state between the frontend and agent.
// Project-specific fields should be defined here. Example patterns:
//   your_data: YourDataType[];
//   custom_field: CustomType[];
// Uncomment the procurement_codes field below if restoring procurement functionality.
export type AgentState = {
  your_data: YourDataType[];
  // procurement_codes?: ProcurementCode[];  // Commented out for genericization - procurement-specific state field
}