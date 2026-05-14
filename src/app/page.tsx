"use client";

// Commented out for genericization - this imports a procurement-specific component
// import { ProcurementCodes } from "@/components/procurement-codes";

// To integrate your custom components:
// 1. Create your component in src/components/
// 2. Import it here
// 3. Render it in YourMainContent with appropriate props
// Example:
// import { YourCustomComponent } from "@/components/your-custom-component";

import { DesignComponent } from "@/components/design-component";
import { AgentState, MaterialStats } from "@/lib/types";
import {
  useCoAgent,
  useCopilotReadable,
  useFrontendTool,
} from "@copilotkit/react-core";
import { CopilotSidebar, InputProps } from "@copilotkit/react-ui";
import { CopilotTextarea } from "@copilotkit/react-textarea";
import { useState, useRef, ChangeEvent, useMemo, useEffect } from "react";
import Papa from "papaparse";
import { read, utils } from "xlsx";

export default function CopilotKitPage() {
  return (
    <main>
      <CopilotSidebar
        defaultOpen={true}
        disableSystemMessage={true}
        clickOutsideToClose={false}
        labels={{
          title: "Design Assistant",
          initial: "Hi! I can help you generate and customize building designs. To get started, I'll need a few details: floor plan dimensions, building section, roof shape and layout, eaves shape, and attic usage.",
        }}
        suggestions={[
          {
            title: "How can you help me?",
            message: "How can you help me?",
          },
          {
            title: "What info do I need for a design?",
            message: "What information do I need to generate a design?",
          },
          {
            title: "What's the price?",
            message: "What's the price?",
          },
          {
            title: "Clear designs.",
            message: "Clear the current designs.",
          },
        ]}
        Input={CustomInput}
      >
        <YourMainContent />
      </CopilotSidebar>
    </main>
  );
}

function CustomInput(props: InputProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [text, setText] = useState("");
  const [attachedFiles, setAttachedFiles] = useState<{ name: string, content: string }[]>([]);

  // Safety limits: ~400k chars is approx 100k tokens. Limit file size to avoid reading massive files.
  const MAX_TOTAL_CHARS = 400000;
  const MAX_FILE_SIZE_BYTES = 2 * 1024 * 1024; // 2MB

  const handleFileUpload = (event: ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    const newFiles: { name: string, content: string }[] = [];
    let processedCount = 0;

    Array.from(files).forEach(file => {
      // 1. Check File Size BEFORE reading
      if (file.size > MAX_FILE_SIZE_BYTES) {
        alert(`File "${file.name}" is too large (max 2MB). Skipping.`);
        processedCount++;
        if (processedCount === files.length) finalizeUpload(newFiles);
        return;
      }

      const processFileContent = (name: string, content: string) => {
        // 2. Check cumulative Length
        const currentTotal = attachedFiles.reduce((sum, f) => sum + f.content.length, 0);
        const newTotal = newFiles.reduce((sum, f) => sum + f.content.length, 0);

        if (currentTotal + newTotal + content.length > MAX_TOTAL_CHARS) {
          alert(`Upload limit reached! Adding "${name}" would exceed the maximum context size. Please upload files in smaller batches.`);
        } else {
          newFiles.push({ name: name, content });
        }

        processedCount++;
        if (processedCount === files.length) {
          finalizeUpload(newFiles);
        }
      };

      // Handle CSV files
      if (file.type === "text/csv" || file.name.endsWith(".csv")) {
        Papa.parse(file, {
          complete: (results) => {
            // Unparse back to string to ensure clean formatting
            const csvString = Papa.unparse(results.data);
            processFileContent(file.name, csvString);
          },
          error: (error) => {
            console.error("CSV Parse Error:", error);
            alert(`Failed to parse CSV file "${file.name}".`);
            processedCount++;
            if (processedCount === files.length) finalizeUpload(newFiles);
          }
        });
        return;
      }

      // Handle Excel files
      if (file.type === "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" ||
        file.type === "application/vnd.ms-excel" ||
        file.name.endsWith(".xlsx") ||
        file.name.endsWith(".xls") ||
        file.name.endsWith(".xml")) {
        const reader = new FileReader();
        reader.onload = (e) => {
          try {
            const data = e.target?.result;
            const workbook = read(data, { type: 'array' });
            // Convert first sheet to CSV
            const firstSheetName = workbook.SheetNames[0];
            const worksheet = workbook.Sheets[firstSheetName];
            const csvContent = utils.sheet_to_csv(worksheet);
            processFileContent(file.name, csvContent);
          } catch (error) {
            console.error("Excel Parse Error:", error);
            alert(`Failed to parse Excel file "${file.name}".`);
            processedCount++;
            if (processedCount === files.length) finalizeUpload(newFiles);
          }
        };
        reader.readAsArrayBuffer(file);
        return;
      }

      // Handle Text files
      if (file.type === "text/plain" || file.name.endsWith(".txt")) {
        const reader = new FileReader();
        reader.onload = (e) => {
          const content = e.target?.result as string;
          processFileContent(file.name, content);
        };
        reader.readAsText(file);
        return;
      }

      // Fallback for unsupported types
      processedCount++;
      if (processedCount === files.length) finalizeUpload(newFiles);
    });
  };

  const finalizeUpload = (newFiles: { name: string, content: string }[]) => {
    setAttachedFiles(prev => [...prev, ...newFiles]);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const removeFile = (index: number) => {
    setAttachedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleSend = () => {
    // Allow sending if there is text OR attached files
    if (!text.trim() && attachedFiles.length === 0) return;

    let messageContent = text;

    if (attachedFiles.length > 0) {
      const fileContexts = attachedFiles.map(f => `[Context from uploaded file "${f.name}"]:\n${f.content}`).join("\n\n");
      if (messageContent) {
        messageContent = `${messageContent}\n\n${fileContexts}`;
      } else {
        messageContent = fileContexts;
      }
    }

    props.onSend(messageContent);
    setText("");
    setAttachedFiles([]);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey && !props.inProgress) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="relative w-full p-4 bg-[#252526] border-t border-[#454545]">
      {/* File Previews */}
      {attachedFiles.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-2">
          {attachedFiles.map((file, index) => (
            <div key={index} className="flex items-center gap-2 p-2 bg-[#2d2d2d] border border-[#454545] rounded-md w-fit animate-in fade-in slide-in-from-bottom-1 duration-200">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-4 h-4 text-[#007fd4]">
                <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
              </svg>
              <span className="text-sm text-[#d4d4d4] font-medium truncate max-w-37.5">{file.name}</span>
              <button
                onClick={() => removeFile(index)}
                className="ml-1 text-[#858585] hover:text-[#d4d4d4] focus:outline-none"
              >
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
                  <path d="M6.28 5.22a.75.75 0 0 0-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 1 0 1.06 1.06L10 11.06l3.72 3.72a.75.75 0 1 0 1.06-1.06L11.06 10l3.72-3.72a.75.75 0 0 0-1.06-1.06L10 8.94 6.28 5.22Z" />
                </svg>
              </button>
            </div>
          ))}
        </div>
      )}

      <div className="relative flex items-center w-full border border-[#454545] rounded-lg focus-within:ring-2 focus-within:ring-[#007fd4] overflow-hidden bg-[#3c3c3c]">

        {/* Upload Button */}
        <button
          onClick={() => fileInputRef.current?.click()}
          className="p-3 text-[#d4d4d4] hover:text-[#007fd4] transition-colors border-r border-[#454545]"
          title="Upload Context"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
          </svg>
        </button>

        {/* Text Area */}
        <CopilotTextarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type a message..."
          disableBranding
          className="flex-1 w-full max-h-40 overflow-y-auto overflow-x-hidden bg-transparent border-none focus:ring-0 p-3 resize-none outline-none text-base text-[#d4d4d4] placeholder-[#858585]"
          autosuggestionsConfig={{
            textareaPurpose: "Provide details for your specific application tasks.",
            chatApiConfigs: {}
          }}
        />

        {/* Send Button */}
        <button
          onClick={handleSend}
          disabled={props.inProgress || (!text.trim() && attachedFiles.length === 0)}
          className={`p-3 transition-colors ${props.inProgress || (!text.trim() && attachedFiles.length === 0) ? "text-[#5b5b5b]" : "text-[#007fd4] hover:bg-[#2d2d2d]"}`}
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
            <path d="M3.478 2.404a.75.75 0 0 0-.926.941l2.432 7.905H13.5a.75.75 0 0 1 0 1.5H4.984l-2.432 7.905a.75.75 0 0 0 .926.94 60.519 60.519 0 0 0 18.445-8.986.75.75 0 0 0 0-1.218A60.517 60.517 0 0 0 3.478 2.404Z" />
          </svg>
        </button>
      </div>

      <input
        type="file"
        ref={fileInputRef}
        className="hidden"
        style={{ display: "none" }}
        accept=".txt,.csv,.xlsx,.xls,.xml"
        multiple
        onChange={handleFileUpload}
      />
    </div>
  );
}

// DEMO-ONLY: roof-type-to-image mapping for simulated design generation
const ROOF_TYPE_IMAGE_MAP: Record<string, string> = {
  "Gable": "/design-gable.svg",
  "Hip": "/design-hip.svg",
  "Mono-pitch": "/design-mono.svg",
  "Flat": "/design-flat.svg",
};

// DEMO-ONLY: artificial delay for demo presentation
const DESIGN_GENERATION_DELAY_MS = 3000;

function computeMaterialStats(parameters: Record<string, unknown>): MaterialStats | null {
  const dimStr = (parameters.floorPlanDimensions as string)?.trim();
  if (!dimStr) return null;
  const match = dimStr.match(/(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)\s*m?/i);
  if (!match) return null;
  const width = parseFloat(match[1]);
  const height = parseFloat(match[2]);
  const floorArea = width * height;
  const pitchDeg = Number(parameters.roofPitch) || 30;
  const pitchRad = (pitchDeg * Math.PI) / 180;
  const cosPitch = Math.cos(pitchRad);
  const roofArea = cosPitch > 0.01 ? floorArea / cosPitch : floorArea;
  return {
    totalTrusses: Math.round(floorArea * 0.147),
    timberVolume: Math.round(floorArea * 0.254 * 100) / 100,
    totalJoints: Math.round(floorArea * 1.32),
    roofArea: Math.round(roofArea * 100) / 100,
  };
}

function YourMainContent() {
  // 🪁 Shared State: https://docs.copilotkit.ai/pydantic-ai/shared-state
  const { state, setState } = useCoAgent<AgentState>({
    name: "my_agent",
    initialState: {
      designs: [],
      parameters: {},
    },
  });

  const designs = useMemo(() => {
    const d = state.designs ?? [];
    if (d.length === 0) return d;
    const needsBackfill = d.some((entry) => entry.id == null);
    if (!needsBackfill) return d;
    let nextId = Math.max(...d.map((entry) => entry.id ?? 0), 0);
    return d.map((entry) => {
      if (entry.id != null) return entry;
      nextId += 1;
      return { ...entry, id: nextId };
    });
  }, [state.designs]);

  if ((state.designs ?? []).some((entry) => entry.id == null)) {
    setState({ ...state, designs });
  }

  // DEMO-ONLY: refs for simulated design generation timer
  const generationTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const latestStateRef = useRef(state);
  useEffect(() => { latestStateRef.current = state; });

  useEffect(() => {
    return () => {
      if (generationTimerRef.current) {
        clearTimeout(generationTimerRef.current);
      }
    };
  }, []);

  // DEMO-ONLY: generate_design frontend tool for simulated design generation
  useFrontendTool({
    name: "generate_design",
    parameters: [
      {
        name: "prompt_text",
        description: "The user's original prompt text for the design",
        required: true,
      },
      { name: "building_type", type: "string", description: "Building type (e.g. House, Garage, Agricultural building)", required: false },
      { name: "floor_plan_dimensions", type: "string", description: "Floor plan dimensions (e.g. 10x15m)", required: false },
      { name: "roof_type", type: "string", description: "Roof type (Gable, Hip, Mono-pitch, Flat)", required: false },
      { name: "roof_pitch", type: "string", description: "Roof pitch in degrees (2-45)", required: false },
      { name: "attic_usage", type: "string", description: "Attic usage (None, Storage, Living space)", required: false },
      { name: "eaves_shape", type: "string", description: "Eaves shape (Open, Boxed, Flush)", required: false },
      { name: "wall_construction", type: "string", description: "Wall construction (Brick, SIP panels, Concrete block, Mixed)", required: false },
      { name: "location", type: "string", description: "Location (e.g. Bratislava)", required: false },
      { name: "overhang", type: "string", description: "Overhang (e.g. 450mm)", required: false },
      { name: "price", type: "string", description: "Estimated price (e.g. €1,752)", required: false },
    ],
    handler({ prompt_text, building_type, floor_plan_dimensions, roof_type, roof_pitch, attic_usage, eaves_shape, wall_construction, location, overhang, price }) {
      const currentState = latestStateRef.current;
      const currentDesigns = currentState.designs ?? [];
      const nextId = Math.max(...currentDesigns.map((d) => d.id ?? 0), 0) + 1;
      const roofImage = (roof_type && ROOF_TYPE_IMAGE_MAP[roof_type]) || "/design-gable.svg";

      const parameters: Record<string, unknown> = {
        buildingType: building_type ?? "---",
        floorPlanDimensions: floor_plan_dimensions ?? "---",
        roofType: roof_type ?? "---",
        roofPitch: roof_pitch !== undefined ? Number(roof_pitch) : "---",
        atticUsage: attic_usage ?? "---",
        eavesShape: eaves_shape ?? "---",
        wallConstruction: wall_construction ?? "---",
        location: location ?? "---",
        overhang: overhang ?? "---",
      };

      const newEntry = {
        id: nextId,
        imageUrl: "/design-gable.svg",
        promptText: prompt_text,
        status: "processing" as const,
        parameters,
        ...(price !== undefined ? { price } : {}),
      };
      const newState = { ...currentState, designs: [...currentDesigns, newEntry] };
      setState(newState);
      latestStateRef.current = newState;

      generationTimerRef.current = setTimeout(() => {
        const timerState = latestStateRef.current;
        const stats = computeMaterialStats(parameters);
        const updatedDesigns = (timerState.designs ?? []).map((d) =>
          d.id === nextId
            ? { ...d, status: "complete" as const, imageUrl: roofImage, materialStats: stats }
            : d
        );
        const timerNewState = { ...timerState, designs: updatedDesigns };
        setState(timerNewState);
        latestStateRef.current = timerNewState;
      }, DESIGN_GENERATION_DELAY_MS);
    },
  });
  useFrontendTool({
    name: "modify_design_entry",
    parameters: [
      {
        name: "design_id",
        type: "number",
        description: "The 1-based ID of the design entry to modify",
        required: true,
      },
      {
        name: "image_name",
        type: "string",
        description:
          'The filename of the image to set (e.g. "design-alpha.svg" or "design-beta.svg"). Optional.',
        required: false,
      },
      {
        name: "image_url",
        type: "string",
        description:
          "A full image URL to set directly (e.g. /api/serve-image/test-image-123.png). Use for dynamically downloaded images. Takes precedence over image_name. Optional.",
        required: false,
      },
      {
        name: "prompt_text",
        type: "string",
        description: "The new prompt text. Optional.",
        required: false,
      },
      {
        name: "price",
        type: "string",
        description: "The estimated price to set (e.g. €1,752). Optional.",
        required: false,
      },
    ],
    handler({ design_id, image_name, image_url, prompt_text, price }) {
      const ALLOWED_IMAGES = ["design-alpha.svg", "design-beta.svg"];

      if (!image_name && !image_url && !prompt_text && !price) {
        return "Error: at least one of image_name, image_url, prompt_text, or price must be provided.";
      }

      const currentState = latestStateRef.current;
      const currentDesigns = currentState.designs ?? [];

      if (image_name && !ALLOWED_IMAGES.includes(image_name)) {
        return `Error: invalid image_name "${image_name}". Valid images: ${ALLOWED_IMAGES.join(", ")}.`;
      }

      const index = currentDesigns.findIndex((d) => d.id === design_id);

      if (index === -1) {
        const validIds = currentDesigns.map((d) => d.id);
        return `Error: design_id ${design_id} not found. Valid IDs: [${validIds.join(", ")}].`;
      }

      const imageUrl = image_url || (image_name ? `/${image_name}` : undefined);

      const updated = [...currentDesigns];
      updated[index] = {
        ...updated[index],
        ...(imageUrl ? { imageUrl } : {}),
        ...(prompt_text ? { promptText: prompt_text } : {}),
        ...(price !== undefined ? { price } : {}),
      };
      const newState = { ...currentState, designs: updated };
      setState(newState);
      latestStateRef.current = newState;
      return `Design entry #${design_id} updated successfully.`;
    },
  });

  useFrontendTool({
    name: "update_design_parameters",
    parameters: [
      { name: "building_type", type: "string", description: "Building type (e.g. House, Garage, Agricultural building)", required: false },
      { name: "floor_plan_dimensions", type: "string", description: "Floor plan dimensions (e.g. 10x15m)", required: false },
      { name: "roof_type", type: "string", description: "Roof type (Gable, Hip, Mono-pitch, Flat)", required: false },
      { name: "roof_pitch", type: "string", description: "Roof pitch in degrees (2-45)", required: false },
      { name: "attic_usage", type: "string", description: "Attic usage (None, Storage, Living space)", required: false },
      { name: "eaves_shape", type: "string", description: "Eaves shape (Open, Boxed, Flush)", required: false },
      { name: "wall_construction", type: "string", description: "Wall construction (Brick, SIP panels, Concrete block, Mixed)", required: false },
      { name: "location", type: "string", description: "Location (e.g. Bratislava)", required: false },
      { name: "overhang", type: "string", description: "Overhang (e.g. 450mm)", required: false },
    ],
    handler({ building_type, floor_plan_dimensions, roof_type, roof_pitch, attic_usage, eaves_shape, wall_construction, location, overhang }) {
      const updatedFields: string[] = [];
      const updated: Record<string, unknown> = {};

      if (building_type !== undefined) { updated.buildingType = building_type; updatedFields.push("buildingType"); }
      if (floor_plan_dimensions !== undefined) { updated.floorPlanDimensions = floor_plan_dimensions; updatedFields.push("floorPlanDimensions"); }
      if (roof_type !== undefined) { updated.roofType = roof_type; updatedFields.push("roofType"); }
      if (roof_pitch !== undefined) { updated.roofPitch = Number(roof_pitch); updatedFields.push("roofPitch"); }
      if (attic_usage !== undefined) { updated.atticUsage = attic_usage; updatedFields.push("atticUsage"); }
      if (eaves_shape !== undefined) { updated.eavesShape = eaves_shape; updatedFields.push("eavesShape"); }
      if (wall_construction !== undefined) { updated.wallConstruction = wall_construction; updatedFields.push("wallConstruction"); }
      if (location !== undefined) { updated.location = location; updatedFields.push("location"); }
      if (overhang !== undefined) { updated.overhang = overhang; updatedFields.push("overhang"); }

      if (updatedFields.length > 0) {
        const currentState = latestStateRef.current;
        const newParameters = { ...currentState.parameters, ...updated };
        const updatedDesigns = (currentState.designs ?? []).map((d) => {
          const mergedParams = { ...(d.parameters ?? {}), ...updated };
          const stats = d.status === "complete" ? computeMaterialStats(mergedParams) : d.materialStats;
          return {
            ...d,
            parameters: mergedParams,
            ...(stats !== undefined ? { materialStats: stats } : {}),
          };
        });
        const newState = { ...currentState, parameters: newParameters, designs: updatedDesigns };
        setState(newState);
        latestStateRef.current = newState;
      }

      const requiredFields = ["buildingType", "floorPlanDimensions", "roofType", "roofPitch"];
      const missingRequired = requiredFields.filter((f) => !updated[f]);

      let summary = `Updated fields: ${updatedFields.length > 0 ? updatedFields.join(", ") : "none"}. `;
      summary += missingRequired.length > 0
        ? `Missing required fields: ${missingRequired.join(", ")}. All required fields are NOT complete.`
        : "All required fields are complete.";

      return summary;
    },
  });

  // END DEMO-ONLY

  useFrontendTool({
    name: "reset_design",
    parameters: [
      { name: "design_ids", type: "number[]", description: "IDs to reset; omit to target all designs", required: false },
      { name: "remove_designs", type: "boolean", description: "true = remove entries entirely (full scrap). Default false = partial reset.", required: false },
      { name: "clear_parameters", type: "string[]", description: "Param keys to set to '---' on targeted entries", required: false },
      { name: "clear_all_parameters", type: "boolean", description: "Set ALL entry params to '---'. Takes precedence over clear_parameters.", required: false },
      { name: "clear_session_parameters", type: "string[]", description: "Param keys to clear from session-level AgentState.parameters", required: false },
    ],
    handler({ design_ids, remove_designs, clear_parameters, clear_all_parameters, clear_session_parameters }) {
      const ALL_PARAM_KEYS = [
        "buildingType", "floorPlanDimensions", "roofType", "roofPitch",
        "atticUsage", "eavesShape", "wallConstruction", "location", "overhang",
      ] as const;

      const currentDesigns = latestStateRef.current.designs ?? [];
      const validIds = currentDesigns.map((d) => d.id);

      if (clear_parameters && clear_parameters.length > 0) {
        const invalid = clear_parameters.filter((k) => !ALL_PARAM_KEYS.includes(k as any));
        if (invalid.length > 0) {
          return `Error: invalid parameter keys: ${invalid.join(", ")}. Valid keys: ${ALL_PARAM_KEYS.join(", ")}.`;
        }
      }

      if (clear_session_parameters && clear_session_parameters.length > 0) {
        const invalid = clear_session_parameters.filter((k) => !ALL_PARAM_KEYS.includes(k as any));
        if (invalid.length > 0) {
          return `Error: invalid session parameter keys: ${invalid.join(", ")}. Valid keys: ${ALL_PARAM_KEYS.join(", ")}.`;
        }
      }

      let targetIds = design_ids;
      if (targetIds && targetIds.length > 0) {
        const notFound = targetIds.filter((id) => !validIds.includes(id));
        if (notFound.length > 0) {
          return `Error: design IDs not found: ${notFound.join(", ")}. Valid IDs: [${validIds.join(", ")}].`;
        }
      } else {
        targetIds = validIds;
      }

      let updatedDesigns = currentDesigns;
      let summary = "";

      if (remove_designs) {
        updatedDesigns = currentDesigns.filter((d) => !targetIds!.includes(d.id));
        const removedIds = targetIds!;
        summary = `Removed ${removedIds.length} design entry${removedIds.length !== 1 ? "s" : ""} entirely.`;
      } else if (clear_all_parameters || (clear_parameters && clear_parameters.length > 0)) {
        updatedDesigns = currentDesigns.map((d) => {
          if (!targetIds!.includes(d.id)) return d;

          const existing = d.parameters ?? {};
          const keysToClear = clear_all_parameters
            ? [...ALL_PARAM_KEYS]
            : clear_parameters!;
          const newParams = { ...existing };
          for (const key of keysToClear) {
            (newParams as Record<string, string>)[key] = "---";
          }
          return { ...d, parameters: newParams, price: "---" };
        });

        const clearedKeys = clear_all_parameters
          ? "all parameters"
          : clear_parameters!.join(", ");
        const targetedEntries = targetIds!.map((id) => currentDesigns.find((d) => d.id === id)).filter(Boolean);
        const preservedParts: string[] = [];
        for (const entry of targetedEntries) {
          if (!entry?.parameters) continue;
          const preservedKeys = Object.entries(entry.parameters)
            .filter(([k, v]) => v != null && v !== "" && v !== "---" && !((clear_all_parameters || clear_parameters!.includes(k))))
            .map(([k, v]) => `${k}=${v}`);
          if (preservedKeys.length > 0) {
            preservedParts.push(preservedKeys.join(", "));
          }
        }
        summary = `Reset ${targetIds!.length} design entry${targetIds!.length !== 1 ? "s" : ""} (ID${targetIds!.length !== 1 ? "s" : ""}: ${targetIds!.join(", ")}). Cleared parameters: ${clearedKeys}.`;
        if (preservedParts.length > 0) {
          summary += ` Preserved parameters: ${preservedParts.join("; ")}.`;
        }
      }

      let sessionSummary = "";
      if (clear_session_parameters && clear_session_parameters.length > 0) {
        const currentState = latestStateRef.current;
        const currentParams = currentState.parameters ?? {};
        const newParams = { ...currentParams };
        for (const key of clear_session_parameters) {
          delete (newParams as Record<string, unknown>)[key];
        }
        const newState = { ...currentState, designs: updatedDesigns, parameters: newParams };
        setState(newState);
        latestStateRef.current = newState;

        const remaining = Object.entries(newParams)
          .filter(([, v]) => v != null && v !== "")
          .map(([k, v]) => `${k}=${v}`);
        sessionSummary = ` Cleared session parameters: ${clear_session_parameters.join(", ")}.`;
        if (remaining.length > 0) {
          sessionSummary += ` Remaining session parameters: ${remaining.join(", ")}.`;
        } else {
          sessionSummary += " No session parameters remaining.";
        }
      } else {
        const newState = { ...latestStateRef.current, designs: updatedDesigns };
        setState(newState);
        latestStateRef.current = newState;
      }

      return (summary + sessionSummary).trim();
    },
  });

  useCopilotReadable({
    description: "The application state data - customize this for your application",
    value: JSON.stringify({ designs, parameters: state.parameters }),
  });

  return (
    <div
      style={{}}
      className="h-screen flex items-center pt-[10vh] flex-col transition-colors duration-300"
    >
      <DesignComponent state={state} setState={setState} />
    </div>
  );
}
