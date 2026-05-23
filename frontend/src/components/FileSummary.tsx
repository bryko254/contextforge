import type { ScanResult } from "../api";

type FileSummaryProps = {
  scan: ScanResult;
};

export function FileSummary({ scan }: FileSummaryProps) {
  const stackLabels = [
    ...scan.tech_stack.languages,
    ...scan.tech_stack.frameworks,
    ...scan.tech_stack.database,
    ...scan.tech_stack.infrastructure,
    ...scan.tech_stack.package_managers
  ];

  return (
    <aside className="file-summary">
      <h2>File Summary</h2>
      <dl>
        <div>
          <dt>Detected stack</dt>
          <dd>{stackLabels.length ? stackLabels.join(", ") : "Unknown"}</dd>
        </div>
        <div>
          <dt>Selected files</dt>
          <dd>{scan.selected_files.length}</dd>
        </div>
        <div>
          <dt>Skipped files</dt>
          <dd>{scan.skipped_files}</dd>
        </div>
      </dl>
      <div className="selected-files">
        <h3>Selected Files</h3>
        <ul>
          {scan.selected_files.slice(0, 10).map((file) => (
            <li key={file.path}>{file.path}</li>
          ))}
        </ul>
      </div>
    </aside>
  );
}
