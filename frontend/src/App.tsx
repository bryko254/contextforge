import { useEffect, useState } from "react";

import { generateFromSample, generateFromZip, type GenerateResponse } from "./api";
import { FileSummary } from "./components/FileSummary";
import { GeneratedDocs } from "./components/GeneratedDocs";
import { UploadPanel } from "./components/UploadPanel";
import "./styles.css";

const LOADING_MESSAGES = ["Scanning project...", "Detecting stack...", "Asking Gemma 4...", "Generating docs..."];

export default function App() {
  const [result, setResult] = useState<GenerateResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!isLoading) {
      setLoadingStep(0);
      return;
    }

    const interval = window.setInterval(() => {
      setLoadingStep((current) => Math.min(current + 1, LOADING_MESSAGES.length - 1));
    }, 900);

    return () => window.clearInterval(interval);
  }, [isLoading]);

  async function runGeneration(action: () => Promise<GenerateResponse>): Promise<void> {
    setIsLoading(true);
    setError("");
    try {
      setResult(await action());
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Something went wrong");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="app-shell">
      <header className="app-header">
        <p className="eyebrow">ContextForge</p>
        <h1>ContextForge</h1>
        <p className="subtitle">
          Generate README.md and AGENT.md for humans and AI coding agents using Gemma 4.
        </p>
      </header>

      <section className="landing-section">
        <div>
          <h2>Durable Project Memory</h2>
          <p>
            After you clear an AI coding chat, the next agent loses context. ContextForge creates
            durable project memory.
          </p>
        </div>
      </section>

      <section className="info-grid">
        <article className="info-panel">
          <h2>Why AGENT.md matters</h2>
          <p>
            README files help humans start. AGENT.md helps future AI agents recover project context:
            important files, safe edit rules, setup clues, uncertainty, and validation steps.
          </p>
        </article>
        <article className="info-panel">
          <h2>Sample output preview</h2>
          <pre className="preview-output">{`# AGENT.md

## Project Map
- backend/app/routes: API endpoints
- backend/app/services: scanner, stack detection, Gemma client

## Safe Development Rules
- Do not invent dependencies.
- Preserve existing project conventions.
- Run focused checks after edits.`}</pre>
        </article>
      </section>

      <UploadPanel
        isLoading={isLoading}
        onUploadZip={(file) => void runGeneration(() => generateFromZip(file))}
        onTrySample={() => void runGeneration(generateFromSample)}
      />

      {isLoading && (
        <section className="status-panel" aria-live="polite">
          <span className="spinner" />
          <span>{LOADING_MESSAGES[loadingStep]}</span>
        </section>
      )}

      {error && (
        <section className="error-panel" role="alert">
          {error}
        </section>
      )}

      {result && (
        <section className="results-layout">
          <FileSummary scan={result.scan} />
          <GeneratedDocs docs={result.docs} />
        </section>
      )}

      {!result && !isLoading && !error && (
        <section className="empty-state">
          <h2>No docs generated yet</h2>
          <p>
            Upload a ZIP or try the sample Django project to generate README.md, AGENT.md, SETUP.md,
            and ARCHITECTURE.md.
          </p>
        </section>
      )}
    </main>
  );
}
