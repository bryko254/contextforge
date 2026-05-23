import JSZip from "jszip";

export type StackSummary = {
  languages: string[];
  frameworks: string[];
  database: string[];
  infrastructure: string[];
  package_managers: string[];
  confidence_notes: string[];
};

export type SelectedFile = {
  path: string;
  content: string;
  size: number;
};

export type ScanResult = {
  project_name: string;
  file_tree: string[];
  selected_files: SelectedFile[];
  skipped_files: number;
  total_size: number;
  tech_stack: StackSummary;
  files: string[];
};

export type GeneratedDocsPayload = {
  readme: string;
  agent_md: string;
  setup: string;
  architecture: string;
  summary: {
    project_name_guess: string;
    detected_stack: string[];
    main_features: string[];
    risks_or_unknowns: string[];
  };
};

export type GenerateResponse = {
  project_name: string;
  source: string;
  docs: GeneratedDocsPayload;
  scan: ScanResult;
};

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

export async function generateFromSample(): Promise<GenerateResponse> {
  const response = await fetch(apiUrl("/api/sample"));
  return parseGenerateResponse(response);
}

export async function generateFromZip(file: File): Promise<GenerateResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(apiUrl("/api/generate"), {
    method: "POST",
    body: formData
  });
  return parseGenerateResponse(response);
}

export async function downloadDocsZip(docs: GeneratedDocsPayload): Promise<void> {
  const zip = new JSZip();
  zip.file("README.md", docs.readme);
  zip.file("AGENT.md", docs.agent_md);
  zip.file("SETUP.md", docs.setup);
  zip.file("ARCHITECTURE.md", docs.architecture);

  const blob = await zip.generateAsync({ type: "blob" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = "contextforge-docs.zip";
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

async function parseGenerateResponse(response: Response): Promise<GenerateResponse> {
  if (!response.ok) {
    throw new Error(await getErrorMessage(response));
  }

  const payload = await response.json();
  return {
    project_name: payload.project_name,
    source: payload.source,
    docs: payload.docs,
    scan: payload.scan ?? payload.file_summary
  };
}

async function getErrorMessage(response: Response): Promise<string> {
  try {
    const body = await response.json();
    if (typeof body.detail === "string") {
      if (body.detail.includes("GEMINI_API_KEY")) {
        return "Gemini API key is missing. Add GEMINI_API_KEY or enable USE_MOCK_AI=true.";
      }
      return body.detail;
    }
  } catch {
    // Fall through to generic error below.
  }
  return `Request failed with status ${response.status}`;
}

function apiUrl(path: string): string {
  return `${API_BASE_URL}${path}`;
}
