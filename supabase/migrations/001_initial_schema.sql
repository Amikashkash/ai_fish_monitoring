-- Fish Monitoring System - Initial Database Schema
-- Supabase PostgreSQL Migration
-- Created: 2026-02-15
--
-- This migration creates all tables for the fish monitoring system.
-- Run this in Supabase SQL Editor to set up the database.

-- ============================================================================
-- TABLE 1: Shipments
-- Tracks fish shipments from suppliers
-- ============================================================================

CREATE TABLE IF NOT EXISTS shipments (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    scientific_name TEXT NOT NULL,
    common_name TEXT NOT NULL,
    source TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    fish_size TEXT,
    aquarium_volume_liters INTEGER NOT NULL CHECK (aquarium_volume_liters > 0),
    -- Auto-calculated density (fish per liter)
    density DECIMAL(10, 2) GENERATED ALWAYS AS (quantity::DECIMAL / aquarium_volume_liters) STORED,
    price_per_fish DECIMAL(10, 2),
    total_price DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX idx_shipments_source ON shipments(source);
CREATE INDEX idx_shipments_scientific_name ON shipments(scientific_name);
CREATE INDEX idx_shipments_date ON shipments(date);

COMMENT ON TABLE shipments IS 'Fish shipment records from suppliers';
COMMENT ON COLUMN shipments.density IS 'Auto-calculated: quantity / volume';

-- ============================================================================
-- TABLE 2: Drug Protocols
-- Standard medication protocols
-- ============================================================================

CREATE TABLE IF NOT EXISTS drug_protocols (
    id SERIAL PRIMARY KEY,
    drug_name TEXT NOT NULL UNIQUE,
    dosage_min DECIMAL(10, 2),
    dosage_max DECIMAL(10, 2),
    dosage_unit TEXT,
    frequency TEXT,
    typical_treatment_period_days INTEGER,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON TABLE drug_protocols IS 'Standard drug/medication protocols';

-- Insert common drug protocols
INSERT INTO drug_protocols (drug_name, dosage_min, dosage_max, dosage_unit, frequency, typical_treatment_period_days, notes)
VALUES
    ('Methylene Blue', 1.0, 5.0, 'mg/L', 'once daily', 7, 'Antibacterial and antifungal'),
    ('Aquarium Salt', 1.0, 3.0, 'g/L', 'continuous', 14, 'Stress relief and osmoregulation'),
    ('Malachite Green', 0.05, 0.15, 'mg/L', 'every other day', 3, 'Avoid with sensitive scaleless fish'),
    ('Copper Sulfate', 0.15, 0.20, 'mg/L', 'continuous', 14, 'For ich and velvet'),
    ('Formalin', 15.0, 25.0, 'mg/L', 'once', 1, 'Short bath treatment')
ON CONFLICT (drug_name) DO NOTHING;

-- ============================================================================
-- TABLE 3: Treatments
-- Treatment sessions for shipments
-- ============================================================================

CREATE TABLE IF NOT EXISTS treatments (
    id SERIAL PRIMARY KEY,
    shipment_id INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'completed', 'modified')),
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (shipment_id) REFERENCES shipments(id) ON DELETE CASCADE
);

CREATE INDEX idx_treatments_status ON treatments(status);
CREATE INDEX idx_treatments_shipment_id ON treatments(shipment_id);

COMMENT ON TABLE treatments IS 'Treatment sessions for fish shipments';

-- ============================================================================
-- TABLE 4: Treatment Drugs (Many-to-Many)
-- Links treatments to specific drugs used
-- ============================================================================

CREATE TABLE IF NOT EXISTS treatment_drugs (
    id SERIAL PRIMARY KEY,
    treatment_id INTEGER NOT NULL,
    drug_protocol_id INTEGER NOT NULL,
    actual_dosage DECIMAL(10, 2),
    actual_frequency TEXT,
    notes TEXT,
    FOREIGN KEY (treatment_id) REFERENCES treatments(id) ON DELETE CASCADE,
    FOREIGN KEY (drug_protocol_id) REFERENCES drug_protocols(id)
);

CREATE INDEX idx_treatment_drugs_treatment_id ON treatment_drugs(treatment_id);

COMMENT ON TABLE treatment_drugs IS 'Drugs used in specific treatments';

-- ============================================================================
-- TABLE 5: Daily Observations
-- Daily health observations during treatment
-- ============================================================================

CREATE TABLE IF NOT EXISTS daily_observations (
    id SERIAL PRIMARY KEY,
    treatment_id INTEGER NOT NULL,
    observation_date DATE NOT NULL,
    overall_condition_score INTEGER CHECK (overall_condition_score BETWEEN 1 AND 5),

    -- Symptom checkboxes
    symptoms_lethargy BOOLEAN DEFAULT FALSE,
    symptoms_loss_of_appetite BOOLEAN DEFAULT FALSE,
    symptoms_spots BOOLEAN DEFAULT FALSE,
    symptoms_fin_damage BOOLEAN DEFAULT FALSE,
    symptoms_breathing_issues BOOLEAN DEFAULT FALSE,
    symptoms_other TEXT,

    treatments_completed BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),

    FOREIGN KEY (treatment_id) REFERENCES treatments(id) ON DELETE CASCADE
);

CREATE INDEX idx_daily_observations_date ON daily_observations(observation_date);
CREATE INDEX idx_daily_observations_treatment_id ON daily_observations(treatment_id);

COMMENT ON TABLE daily_observations IS 'Daily health observations during treatment';
COMMENT ON COLUMN daily_observations.overall_condition_score IS '1=Critical, 5=Excellent';

-- ============================================================================
-- TABLE 6: Follow-up Assessments
-- 5-day post-treatment evaluations for AI learning
-- ============================================================================

CREATE TABLE IF NOT EXISTS followup_assessments (
    id SERIAL PRIMARY KEY,
    treatment_id INTEGER NOT NULL,
    followup_date DATE NOT NULL,
    stability_score INTEGER CHECK (stability_score BETWEEN 1 AND 5),
    symptoms_returned BOOLEAN DEFAULT FALSE,
    returned_symptoms TEXT,
    survival_count INTEGER,
    success_rate DECIMAL(5, 2) CHECK (success_rate BETWEEN 0 AND 100),
    recommendation TEXT,
    ai_learning_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),

    FOREIGN KEY (treatment_id) REFERENCES treatments(id) ON DELETE CASCADE
);

CREATE INDEX idx_followup_treatment_id ON followup_assessments(treatment_id);

COMMENT ON TABLE followup_assessments IS '5-day post-treatment assessments';
COMMENT ON COLUMN followup_assessments.success_rate IS 'Percentage of fish that survived (0-100)';

-- ============================================================================
-- TABLE 7: AI Knowledge Base
-- Learned patterns from historical data
-- ============================================================================

CREATE TABLE IF NOT EXISTS ai_knowledge (
    id SERIAL PRIMARY KEY,
    source_country TEXT NOT NULL,
    scientific_name TEXT NOT NULL,
    successful_protocols JSONB,
    success_rate DECIMAL(5, 2) CHECK (success_rate BETWEEN 0 AND 100),
    sample_size INTEGER DEFAULT 0,
    last_updated TIMESTAMP DEFAULT NOW(),
    insights TEXT,

    UNIQUE(source_country, scientific_name)
);

CREATE INDEX idx_ai_knowledge_source ON ai_knowledge(source_country);
CREATE INDEX idx_ai_knowledge_species ON ai_knowledge(scientific_name);

COMMENT ON TABLE ai_knowledge IS 'AI-learned patterns for fish/source combinations';
COMMENT ON COLUMN ai_knowledge.successful_protocols IS 'JSON array of successful drug combinations';

-- ============================================================================
-- VIEWS (Optional - for easier querying)
-- ============================================================================

-- View: Active treatments with shipment details
CREATE OR REPLACE VIEW active_treatments_view AS
SELECT
    t.id AS treatment_id,
    t.start_date,
    t.end_date,
    s.id AS shipment_id,
    s.scientific_name,
    s.common_name,
    s.source,
    s.quantity,
    s.density,
    COALESCE(t.end_date, CURRENT_DATE) - t.start_date AS days_active
FROM treatments t
JOIN shipments s ON t.shipment_id = s.id
WHERE t.status = 'active';

COMMENT ON VIEW active_treatments_view IS 'Currently active treatments with shipment details';

-- View: Supplier performance summary
CREATE OR REPLACE VIEW supplier_performance_view AS
SELECT
    s.source,
    COUNT(DISTINCT s.id) AS shipment_count,
    SUM(s.quantity) AS total_fish,
    COUNT(DISTINCT s.scientific_name) AS species_count,
    AVG(f.success_rate) AS avg_success_rate
FROM shipments s
LEFT JOIN treatments t ON s.id = t.shipment_id
LEFT JOIN followup_assessments f ON t.id = f.treatment_id
GROUP BY s.source
ORDER BY avg_success_rate DESC NULLS LAST;

COMMENT ON VIEW supplier_performance_view IS 'Performance metrics by supplier';

-- ============================================================================
-- FUNCTIONS (Optional - helpful utilities)
-- ============================================================================

-- Function: Calculate success rate for a treatment
CREATE OR REPLACE FUNCTION calculate_treatment_success_rate(
    p_treatment_id INTEGER,
    p_survived INTEGER,
    p_total INTEGER
) RETURNS DECIMAL AS $$
DECLARE
    v_success_rate DECIMAL(5, 2);
BEGIN
    IF p_total <= 0 THEN
        RAISE EXCEPTION 'Total must be positive';
    END IF;

    IF p_survived > p_total THEN
        RAISE EXCEPTION 'Survived cannot exceed total';
    END IF;

    v_success_rate := (p_survived::DECIMAL / p_total) * 100;
    RETURN ROUND(v_success_rate, 2);
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION calculate_treatment_success_rate IS 'Calculate survival percentage';

-- ============================================================================
-- PERMISSIONS (Important for Supabase)
-- ============================================================================

-- For development: Disable Row Level Security (RLS)
-- WARNING: Enable RLS in production and add appropriate policies!
ALTER TABLE shipments DISABLE ROW LEVEL SECURITY;
ALTER TABLE drug_protocols DISABLE ROW LEVEL SECURITY;
ALTER TABLE treatments DISABLE ROW LEVEL SECURITY;
ALTER TABLE treatment_drugs DISABLE ROW LEVEL SECURITY;
ALTER TABLE daily_observations DISABLE ROW LEVEL SECURITY;
ALTER TABLE followup_assessments DISABLE ROW LEVEL SECURITY;
ALTER TABLE ai_knowledge DISABLE ROW LEVEL SECURITY;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Run these after migration to verify setup:
-- SELECT tablename FROM pg_tables WHERE schemaname = 'public';
-- SELECT * FROM drug_protocols;
-- SELECT COUNT(*) FROM shipments;

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

-- Print success message
DO $$
BEGIN
    RAISE NOTICE 'Fish Monitoring System database schema created successfully!';
    RAISE NOTICE 'Tables created: 7';
    RAISE NOTICE 'Views created: 2';
    RAISE NOTICE 'Sample drug protocols inserted: 5';
    RAISE NOTICE '';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '1. Verify tables in Supabase Table Editor';
    RAISE NOTICE '2. Configure .env file with Supabase credentials';
    RAISE NOTICE '3. Start backend API: uvicorn app.main:app --reload';
END $$;
