-- Create protocol templates table
-- This stores reusable treatment protocols with complete instructions
CREATE TABLE IF NOT EXISTS protocol_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    purpose TEXT NOT NULL, -- e.g., "bacterial infections", "parasitic treatment"
    duration_days INTEGER, -- e.g., 10
    special_instructions TEXT, -- e.g., "reduce dosage by half after third day"
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    -- Success tracking for AI recommendations
    times_used INTEGER DEFAULT 0,
    successful_outcomes INTEGER DEFAULT 0,
    success_rate DECIMAL(5,2) GENERATED ALWAYS AS (
        CASE
            WHEN times_used > 0 THEN (successful_outcomes::DECIMAL / times_used * 100)
            ELSE 0
        END
    ) STORED
);

-- Create protocol template drugs junction table
-- Links protocol templates to specific drugs with dosage and frequency
CREATE TABLE IF NOT EXISTS protocol_template_drugs (
    id SERIAL PRIMARY KEY,
    protocol_template_id INTEGER NOT NULL REFERENCES protocol_templates(id) ON DELETE CASCADE,
    drug_protocol_id INTEGER NOT NULL REFERENCES drug_protocols(id) ON DELETE CASCADE,
    dosage VARCHAR(255) NOT NULL, -- e.g., "5 gr / 100 liter"
    frequency VARCHAR(255) NOT NULL, -- e.g., "every day", "twice daily"
    sequence_order INTEGER DEFAULT 1, -- for ordering multiple drugs in a protocol
    notes TEXT, -- additional drug-specific notes
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(protocol_template_id, drug_protocol_id)
);

-- Add index for faster lookups
CREATE INDEX idx_protocol_templates_purpose ON protocol_templates(purpose);
CREATE INDEX idx_protocol_template_drugs_template ON protocol_template_drugs(protocol_template_id);

-- Add trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_protocol_template_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_protocol_template_timestamp
    BEFORE UPDATE ON protocol_templates
    FOR EACH ROW
    EXECUTE FUNCTION update_protocol_template_timestamp();

-- Insert sample protocol template (dabitetracyclin for bacterial infections)
INSERT INTO protocol_templates (name, purpose, duration_days, special_instructions, times_used, successful_outcomes)
VALUES (
    'Dabitetracyclin Standard Treatment',
    'bacterial infections',
    10,
    'Reduce dosage by half after third day',
    0,
    0
) ON CONFLICT (name) DO NOTHING;

-- Link the sample protocol to a drug (assuming dabitetracyclin exists in drug_protocols)
-- First, ensure dabitetracyclin exists in drug_protocols
INSERT INTO drug_protocols (drug_name, dosage_min, dosage_max, dosage_unit, frequency, typical_treatment_period_days, notes)
VALUES (
    'Dabitetracyclin',
    5.0,
    5.0,
    'gr/100L',
    'daily',
    10,
    'Reduce dosage by half after third day. Monitor water quality closely.'
) ON CONFLICT (drug_name) DO NOTHING;

-- Now link the protocol template to the drug
INSERT INTO protocol_template_drugs (protocol_template_id, drug_protocol_id, dosage, frequency, sequence_order, notes)
SELECT
    pt.id,
    dp.id,
    '5 gr / 100 liter',
    'every day for 10 days',
    1,
    'Start with full dosage for first 3 days, then reduce by half'
FROM protocol_templates pt
CROSS JOIN drug_protocols dp
WHERE pt.name = 'Dabitetracyclin Standard Treatment'
AND dp.drug_name = 'Dabitetracyclin'
ON CONFLICT (protocol_template_id, drug_protocol_id) DO NOTHING;

-- Create view for easy protocol template lookup with drug details
CREATE OR REPLACE VIEW protocol_template_details AS
SELECT
    pt.id as template_id,
    pt.name as template_name,
    pt.purpose,
    pt.duration_days,
    pt.special_instructions,
    pt.times_used,
    pt.successful_outcomes,
    pt.success_rate,
    pt.created_at,
    pt.updated_at,
    json_agg(
        json_build_object(
            'drug_id', dp.id,
            'drug_name', dp.drug_name,
            'dosage_min', dp.dosage_min,
            'dosage_max', dp.dosage_max,
            'dosage_unit', dp.dosage_unit,
            'dosage', ptd.dosage,
            'frequency', ptd.frequency,
            'sequence_order', ptd.sequence_order,
            'notes', ptd.notes
        ) ORDER BY ptd.sequence_order
    ) as drugs
FROM protocol_templates pt
LEFT JOIN protocol_template_drugs ptd ON pt.id = ptd.protocol_template_id
LEFT JOIN drug_protocols dp ON ptd.drug_protocol_id = dp.id
GROUP BY pt.id;

COMMENT ON TABLE protocol_templates IS 'Reusable treatment protocol templates with success tracking for AI recommendations';
COMMENT ON TABLE protocol_template_drugs IS 'Links protocol templates to specific drugs with dosage and frequency details';
COMMENT ON VIEW protocol_template_details IS 'Complete protocol template information with all associated drugs';
