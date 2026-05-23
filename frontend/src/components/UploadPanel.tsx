import { useRef } from "react";

type UploadPanelProps = {
  isLoading: boolean;
  onUploadZip: (file: File) => void;
  onTrySample: () => void;
};

export function UploadPanel({ isLoading, onUploadZip, onTrySample }: UploadPanelProps) {
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  return (
    <section className="upload-panel" aria-label="Project source">
      <input
        ref={fileInputRef}
        className="hidden-input"
        type="file"
        accept=".zip,application/zip"
        onChange={(event) => {
          const file = event.target.files?.[0];
          if (file) {
            onUploadZip(file);
            event.target.value = "";
          }
        }}
      />
      <button
        className="button secondary"
        type="button"
        disabled={isLoading}
        onClick={() => fileInputRef.current?.click()}
      >
        Upload ZIP
      </button>
      <button className="button primary" type="button" disabled={isLoading} onClick={onTrySample}>
        Try sample project
      </button>
    </section>
  );
}
