export type PriorityLevel = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
export type IncidentStatus = 'new' | 'investigating' | 'contained' | 'resolved';

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: 'admin' | 'analyst';
  is_active: boolean;
  created_at: string;
}

export interface FactorContributionItem {
  name: string;
  label: string;
  value: number;
  importance_pct: number;
  contribution_points: number;
  description: string;
}

export interface Incident {
  id: number;
  incident_code: string;
  title: string;
  description?: string;
  incident_type: string;
  status: IncidentStatus;
  asset_name: string;
  asset_type: string;
  
  severity: number;
  data_sensitivity: number;
  asset_importance: number;
  attack_confidence: number;
  raw_users: number;
  affected_users_normalized: number;
  business_impact: number;
  incident_type_encoded: number;
  asset_type_encoded: number;
  time_risk: number;
  historical_frequency: number;
  recurrence: number;
  raw_systems: number;
  affected_system_count_normalized: number;

  ml_score: number;
  rule_score: number;
  priority_score: number;
  priority_level: PriorityLevel;
  priority_rank: number;

  why_number_one?: string;
  factor_contributions?: Record<string, FactorContributionItem>;
  mitigation_recommendations?: string[];

  assigned_to?: string;
  detected_at: string;
  created_at: string;
  updated_at?: string;
}

export interface IncidentRankingResponse {
  total: number;
  limit: number;
  offset: number;
  items: Incident[];
  top_incident?: Incident;
}

export interface IncidentComparisonResponse {
  incident_a: Incident;
  incident_b: Incident;
  higher_priority_code: string;
  score_difference: number;
  plain_language_justification: string;
  divergent_factors: {
    factor: string;
    label: string;
    val_a: number;
    val_b: number;
    diff: number;
    favors: string;
  }[];
  ml_delta: number;
  rule_delta: number;
}

export interface SimulationRequest {
  incident_id?: number;
  title?: string;
  incident_type: string;
  asset_name: string;
  asset_type: string;
  severity: number;
  data_sensitivity: number;
  asset_importance: number;
  attack_confidence: number;
  raw_users: number;
  business_impact?: number;
  time_risk: number;
  historical_frequency: number;
  recurrence: number;
  raw_systems: number;
}

export interface SimulationResponse {
  simulated_priority_score: number;
  simulated_priority_level: PriorityLevel;
  ml_score: number;
  rule_score: number;
  estimated_rank_shift?: number;
  estimated_new_rank?: number;
  baseline_score?: number;
  baseline_level?: PriorityLevel;
  score_delta?: number;
  factor_contributions: Record<string, FactorContributionItem>;
  explainability_summary: string;
  mitigation_recommendations: string[];
}

export interface AnalyticsSummary {
  total_incidents: number;
  active_incidents: number;
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
  mean_ml_score: number;
  mean_priority_score: number;
  type_distribution: { name: string; count: number; avg_score: number }[];
  severity_distribution: { range: string; count: number }[];
  top_affected_assets: { asset_name: string; asset_type: string; incident_count: number; max_priority: number }[];
  status_distribution: { status: string; count: number }[];
  recent_trend: { date: string; critical: number; high: number; medium: number; low: number; total: number }[];
}

export interface ModelPerformance {
  metrics: {
    model_name: string;
    dataset_samples: number;
    train_samples: number;
    test_samples: number;
    r2_score: number;
    rmse: number;
    mae: number;
    trained_at: string;
  };
  feature_importances: { feature: string; importance: number; percentage: number }[];
  weights: {
    ml_weight: number;
    rule_weight: number;
  };
  formula: string;
}

export interface ReportItem {
  id: number;
  report_code: string;
  incident_id: number;
  title: string;
  report_type: string;
  file_path: string;
  download_url: string;
  generated_by: string;
  created_at: string;
}
