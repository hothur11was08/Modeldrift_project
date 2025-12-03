-- scripts/init_db.sql

CREATE TABLE IF NOT EXISTS predictions (
  id SERIAL PRIMARY KEY,
  timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
  model_version TEXT NOT NULL,
  request_json TEXT NOT NULL,
  features_vector TEXT NOT NULL,
  prediction_value DOUBLE PRECISION NOT NULL,
  latency_ms INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS drift_metrics (
  id SERIAL PRIMARY KEY,
  timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
  feature_name TEXT NOT NULL,
  statistic_name TEXT NOT NULL,   -- e.g., 'PSI', 'KS'
  statistic_value DOUBLE PRECISION NOT NULL,
  p_value DOUBLE PRECISION,
  drift_flag BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS bias_metrics (
  id SERIAL PRIMARY KEY,
  timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
  subgroup_name TEXT NOT NULL,    -- e.g., 'housing'
  subgroup_value TEXT NOT NULL,   -- e.g., 'rent'
  sample_size INTEGER NOT NULL,
  approval_rate DOUBLE PRECISION NOT NULL,
  disparity_vs_reference DOUBLE PRECISION,
  bias_flag BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS accuracy_metrics (
  id SERIAL PRIMARY KEY,
  timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
  dataset TEXT NOT NULL,          -- 'train', 'test', 'live'
  metric_name TEXT NOT NULL,      -- 'accuracy', 'auc'
  metric_value DOUBLE PRECISION NOT NULL,
  model_version TEXT NOT NULL
);

