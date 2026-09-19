import { useRef, useState } from "react";

interface Props {
  onFile: (file: File) => void;
  busy: boolean;
}

export default function UploadDropzone({ onFile, busy }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [over, setOver] = useState(false);

  const accept = (files: FileList | null) => {
    const f = files?.[0];
    if (f) onFile(f);
  };

  return (
    <div
      onDragOver={(e) => { e.preventDefault(); setOver(true); }}
      onDragLeave={() => setOver(false)}
      onDrop={(e) => { e.preventDefault(); setOver(false); accept(e.dataTransfer.files); }}
      onClick={() => inputRef.current?.click()}
      className={`cursor-pointer rounded-lg border-2 border-dashed p-10 text-center transition
        ${over ? "border-sky-400 bg-sky-950/30" : "border-slate-700 hover:border-slate-500"}`}
    >
      <input ref={inputRef} type="file" accept="image/png,image/jpeg" hidden onChange={(e) => accept(e.target.files)} />
      <p className="text-slate-300">{busy ? "Analyzing..." : "Drop a FLAIR slice (PNG/JPG) or click to upload"}</p>
    </div>
  );
}
