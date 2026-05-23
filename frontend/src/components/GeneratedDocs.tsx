import { useMemo, useState } from "react";

import { downloadDocsZip, type GeneratedDocsPayload } from "../api";

type GeneratedDocsProps = {
  docs: GeneratedDocsPayload;
};

type DocTab = {
  label: "README.md" | "AGENT.md" | "SETUP.md" | "ARCHITECTURE.md";
  value: string;
};

export function GeneratedDocs({ docs }: GeneratedDocsProps) {
  const [activeTab, setActiveTab] = useState<DocTab["label"]>("README.md");
  const [copyStatus, setCopyStatus] = useState("");

  const tabs = useMemo<DocTab[]>(
    () => [
      { label: "README.md", value: docs.readme },
      { label: "AGENT.md", value: docs.agent_md },
      { label: "SETUP.md", value: docs.setup },
      { label: "ARCHITECTURE.md", value: docs.architecture }
    ],
    [docs]
  );
  const activeDoc = tabs.find((tab) => tab.label === activeTab) ?? tabs[0];
  const hasDocs = tabs.some((tab) => tab.value.trim().length > 0);

  async function copyDoc(tab: DocTab): Promise<void> {
    try {
      await copyText(tab.value);
      setCopyStatus(`Copied ${tab.label}`);
    } catch {
      setCopyStatus("Copy failed");
    }
    window.setTimeout(() => setCopyStatus(""), 1800);
  }

  return (
    <section className="generated-docs">
      <div className="docs-header">
        <h2>Generated Docs</h2>
        <div className="doc-actions">
          <button className="button primary compact" type="button" onClick={() => void downloadDocsZip(docs)}>
            Download docs as ZIP
          </button>
        </div>
      </div>

      {hasDocs ? (
        <>
          <div className="tabs" role="tablist" aria-label="Generated documents">
            {tabs.map((tab) => (
              <button
                key={tab.label}
                className={tab.label === activeDoc.label ? "tab active" : "tab"}
                type="button"
                role="tab"
                aria-selected={tab.label === activeDoc.label}
                onClick={() => setActiveTab(tab.label)}
              >
                {tab.label}
              </button>
            ))}
          </div>

          <div className="copy-grid" aria-label="Copy generated documents">
            {tabs.map((tab) => (
              <button
                key={tab.label}
                className="button secondary compact"
                type="button"
                onClick={() => void copyDoc(tab)}
              >
                Copy {tab.label}
              </button>
            ))}
          </div>

          {copyStatus && <p className="copy-status">{copyStatus}</p>}
          <pre className="doc-output">{activeDoc.value}</pre>
        </>
      ) : (
        <div className="docs-empty-state">
          <h3>Generated docs will appear here</h3>
          <p>Run the sample project or upload a ZIP to create documentation tabs.</p>
        </div>
      )}
    </section>
  );
}

async function copyText(value: string): Promise<void> {
  if (navigator.clipboard) {
    await navigator.clipboard.writeText(value);
    return;
  }

  const textarea = document.createElement("textarea");
  textarea.value = value;
  textarea.style.position = "fixed";
  textarea.style.left = "-9999px";
  document.body.appendChild(textarea);
  textarea.focus();
  textarea.select();
  document.execCommand("copy");
  textarea.remove();
}
