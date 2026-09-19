import type { Lesion } from "../api/types";

interface Props {
  lesions: Lesion[];
  selected: number | null;
  onSelect: (id: number | null) => void;
}

export default function LesionTable({ lesions, selected, onSelect }: Props) {
  return (
    <table className="w-full text-sm">
      <thead className="text-slate-400 text-left">
        <tr>
          <th>#</th>
          <th>Pattern</th>
          <th>Location</th>
          <th>Conf.</th>
          <th>Area</th>
        </tr>
      </thead>
      <tbody>
        {lesions.map((l) => (
          <tr
            key={l.id}
            onClick={() => onSelect(selected === l.id ? null : l.id)}
            className={`cursor-pointer border-t border-slate-800 ${selected === l.id ? "bg-slate-800" : "hover:bg-slate-900"}`}
          >
            <td className="py-1">{l.id}</td>
            <td className={l.pattern === "ms_typical" ? "text-orange-400" : "text-sky-400"}>
              {l.pattern === "ms_typical" ? "MS-typical" : "Atypical"}
            </td>
            <td>{l.features.location.replace("_", " ")}</td>
            <td>{(l.confidence * 100).toFixed(0)}%</td>
            <td>{l.area_px} px</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
