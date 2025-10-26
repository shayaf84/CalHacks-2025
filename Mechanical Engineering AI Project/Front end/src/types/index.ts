// Material types
export interface Material {
  id: string;
  material_id: string;
  formula: string;
  formula_pretty: string;
  properties?: MaterialProperties;
  structure_data?: StructureData;
  created_at: string;
}

export interface MaterialProperties {
  density?: string;
  band_gap?: string;
  formation_energy?: string;
  is_stable?: boolean;
  is_metal?: boolean;
  is_magnetic?: boolean;
  volume?: string;
}

export interface StructureData {
  sites: Array<{
    species: string;
    coords: number[];
  }>;
}

export interface LatticeParams {
  a: number;
  b: number;
  c: number;
  alpha: number;
  beta: number;
  gamma: number;
}

// Analysis types
export interface AnalysisResult {
  material_id: string;
  stability_analysis: {
    is_stable: boolean;
    formation_energy: string;
    is_metal: boolean;
    is_magnetic: boolean;
  };
  recommendations: string[];
}

export interface ApplicationSuggestion {
  material_id: string;
  suggested_applications: string[];
  confidence: string;
}

// API Response types
export interface ApiResponse<T> {
  status: 'success' | 'error';
  data?: T;
  message?: string;
}

