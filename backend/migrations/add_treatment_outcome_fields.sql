-- Migration: Add outcome fields to treatments table
-- Run this in the Supabase SQL editor (Dashboard → SQL Editor → New query)

ALTER TABLE treatments
  ADD COLUMN IF NOT EXISTS outcome        TEXT,
  ADD COLUMN IF NOT EXISTS outcome_score  INTEGER CHECK (outcome_score BETWEEN 1 AND 5),
  ADD COLUMN IF NOT EXISTS total_mortality INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS outcome_notes  TEXT;

-- Optional: add a comment for documentation
COMMENT ON COLUMN treatments.outcome          IS 'healthy | minor_loss | major_loss | total_loss';
COMMENT ON COLUMN treatments.outcome_score    IS '1 (very poor) to 5 (excellent)';
COMMENT ON COLUMN treatments.total_mortality  IS 'Total fish found dead over the entire treatment period';
COMMENT ON COLUMN treatments.outcome_notes    IS 'Free-text notes recorded at graduation';
