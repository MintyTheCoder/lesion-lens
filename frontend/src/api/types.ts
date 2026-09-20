// Mirrors backend/app/schemas.py. Change both in the same PR.

export type Pattern = "ms_typical" | "atypical";
export type Location = "periventricular" | "juxtacortical" | "deep_wm";

export interface ImageInfo {
  data_url: string;
  width: number;
  height: number;
}

export interface LesionFeatures {
  elongation: number;
  orientation_deg: number;
  location: Location;
  ovoid_score: number;
}

export interface Lesion {
  id: number;
  bbox: [number, number, number, number]; // [x, y, w, h] px in the preprocessed image
  confidence: number;
  area_px: number;
  pattern: Pattern;
  features: LesionFeatures;
  reasons: string[];
}

export interface Burden {
  lesion_count: number;
  total_area_px: number;
  total_area_pct: number;
  ms_typical_count: number;
  atypical_count: number;
}

export interface ModelInfo {
  id: string;
  trained_on: string;
}

export interface AnalysisResult {
  case_id: string;
  created_at: string;
  image: ImageInfo;
  lesions: Lesion[];
  burden: Burden;
  summary: string;
  model: ModelInfo;
}

export interface CaseSummary {
  case_id: string;
  created_at: string;
  lesion_count: number;
  atypical_count: number;
}

export interface DatasetValidation {
  name: string;
  n_scans: number;
  precision: number;
  recall: number;
  fp_per_scan: number;
  atypical_pct: number;
}

export interface ValidationReport {
  datasets: DatasetValidation[];
  note: string;
}

export interface BurdenPoint {
  case_id: string;
  created_at: string;
  lesion_count: number;
  total_area_pct: number;
  atypical_count: number;
}

export interface BurdenTrend {
  session_id: string;
  points: BurdenPoint[];
  direction: "rising" | "stable" | "falling" | "insufficient_data";
}
