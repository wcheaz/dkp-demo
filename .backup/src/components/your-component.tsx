import { AgentState } from "@/lib/types";

export interface YourComponentProps {
    state: AgentState;
    setState: (state: AgentState) => void;
}

export function YourComponent({ state, setState }: YourComponentProps) {
    return (
        <div className="your-component">
            <h2 className="text-2xl font-bold mb-4">Your Application</h2>
            <div className="space-y-4">
                <p className="text-gray-600">
                    Customize this component for your specific application needs.
                </p>
                <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                    <h3 className="font-semibold mb-2">Current State:</h3>
                    <pre className="text-sm bg-gray-100 p-2 rounded overflow-auto">
                        {JSON.stringify(state, null, 2)}
                    </pre>
                </div>
            </div>
        </div>
    );
}