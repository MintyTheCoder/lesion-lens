import { useState } from "react";
import { analyze } from "../api/client";
import type { AnalysisResult } from "../api/types";
import mock from "../mocks/analysis.json";
import BurdenCard from "../components/BurdenCard";
import LesionTable from "../components/LesionTable";
import ScanViewer from "../components/ScanViewer";
import SummaryCard from "../components/SummaryCard";
import UploadDropzone from "../components/UploadDropzone";
import ValidationPanel from "../components/ValidationPanel";

export default function Analyze() {
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<number | null>(null);

  const onFile = async (file: File) => {
    setBusy(true);
    setError(null);
    setSelected(null);
    try {
      setResult(await analyze(file));
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="space-y-6">
      <UploadDropzone onFile={onFile} busy={busy} />
      {error && <div className="text-sm text-red-400">{error}</div>}
      {!result && (
        <button className="text-xs text-slate-500 underline" onClick={() => setResult(mock as AnalysisResult)}>
          Load mock result (frontend dev)
        </button>
      )}

      {result && (
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
          <div className="lg:col-span-3">
            <ScanViewer result={result} selected={selected} onSelect={setSelected} />
          </div>
          <div className="lg:col-span-2 space-y-4">
            <BurdenCard burden={result.burden} />
            <LesionTable lesions={result.lesions} selected={selected} onSelect={setSelected} />
            <SummaryCard summary={result.summary} />
            <p className="text-xs text-slate-500">
              model {result.model.id} - trained on {result.model.trained_on}
            </p>
          </div>
        </div>
      )}

      <ValidationPanel />
    </div>
  );
}
