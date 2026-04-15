import { AgentState } from "@/lib/types";
import { utils, writeFile } from "xlsx";

export interface ProcurementCodesProps {
    state: AgentState;
    setState: (state: AgentState) => void;
}

export function ProcurementCodes({ state, setState }: ProcurementCodesProps) {
    const handleDownloadText = () => {
        if (!state.procurement_codes?.length) return;

        const content = state.procurement_codes
            .map(item => `${item.code} - ${item.description}`)
            .join('\n');

        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'procurement_codes.txt';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    };

    const handleDownloadCSV = () => {
        if (!state.procurement_codes?.length) return;

        // Manual CSV construction to avoid extra dependency for simple case, 
        // or re-use papaparse if available. Since we didn't import papaparse here,
        // let's use a simple map, but xlsx can also do it.
        // Let's use xlsx for consistency and robustness or just manual string for simple CSV.
        // Actually, let's use xlsx for both to be safe with escaping.
        const ws = utils.json_to_sheet(state.procurement_codes.map(item => ({
            Code: item.code,
            Description: item.description
        })));
        const csv = utils.sheet_to_csv(ws);
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'procurement_codes.csv';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    };

    const handleDownloadExcel = () => {
        if (!state.procurement_codes?.length) return;

        const ws = utils.json_to_sheet(state.procurement_codes.map(item => ({
            Code: item.code,
            Description: item.description
        })));
        const wb = utils.book_new();
        utils.book_append_sheet(wb, ws, "Procurement Codes");
        writeFile(wb, "procurement_codes.xlsx");
    };

    return (
        <div className="bg-white/20 backdrop-blur-md p-8 rounded-2xl shadow-xl max-w-2xl w-full">
            <h1 className="text-4xl font-bold text-white mb-2 text-center">Procurement Codes</h1>
            <p className="text-gray-200 text-center italic mb-6">Previously generated procurement codes and descriptions.</p>

            {state.procurement_codes && state.procurement_codes.length > 0 && (
                <div className="flex justify-center mb-6 gap-2">
                    <button
                        onClick={handleDownloadText}
                        className="bg-white/20 hover:bg-white/30 text-white font-bold py-2 px-4 rounded-full transition-all flex items-center gap-2 text-sm"
                        title="Download as Text"
                    >
                        <span>TXT</span>
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                    </button>
                    <button
                        onClick={handleDownloadCSV}
                        className="bg-white/20 hover:bg-white/30 text-white font-bold py-2 px-4 rounded-full transition-all flex items-center gap-2 text-sm"
                        title="Download as CSV"
                    >
                        <span>CSV</span>
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M3 14h18m-9-4v8m-7-2.5l7.5-7.5 7.5 7.5" />
                        </svg>
                    </button>
                    <button
                        onClick={handleDownloadExcel}
                        className="bg-white/20 hover:bg-white/30 text-white font-bold py-2 px-4 rounded-full transition-all flex items-center gap-2 text-sm"
                        title="Download as Excel"
                    >
                        <span>XLSX</span>
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                    </button>
                </div>
            )}

            <hr className="border-white/20 my-6" />
            <div className="flex flex-col gap-3">
                {state.procurement_codes?.map((item, index) => (
                    <div
                        key={index}
                        className="bg-white/15 p-4 rounded-xl text-white relative group hover:bg-white/20 transition-all"
                    >
                        <div className="pr-8">
                            <span className="font-mono font-bold bg-black/20 px-2 py-1 rounded text-yellow-300 mr-2">{item.code}</span>
                            <span>{item.description}</span>
                        </div>
                        <button
                            onClick={() => setState({
                                ...state,
                                procurement_codes: state.procurement_codes?.filter((_, i) => i !== index),
                            })}
                            className="absolute right-3 top-3 opacity-0 group-hover:opacity-100 transition-opacity 
                bg-red-500 hover:bg-red-600 text-white rounded-full h-6 w-6 flex items-center justify-center"
                        >
                            ✕
                        </button>
                    </div>
                ))}
            </div>

            {(state.procurement_codes?.length === 0 || !state.procurement_codes) && <p className="text-center text-white/80 italic my-8">
                No previously generated procurement codes detected.
            </p>}
        </div>
    );
}
