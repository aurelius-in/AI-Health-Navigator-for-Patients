-- AI Health Navigator Database Initialization Script

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create custom types
CREATE TYPE user_role AS ENUM ('patient', 'provider', 'admin', 'researcher');
CREATE TYPE urgency_level AS ENUM ('low', 'medium', 'high', 'critical');
CREATE TYPE agent_status AS ENUM ('idle', 'running', 'completed', 'failed', 'error');
CREATE TYPE agent_priority AS ENUM ('low', 'normal', 'high', 'critical');

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_symptom_analysis_user_id ON symptom_analysis(user_id);
CREATE INDEX IF NOT EXISTS idx_triage_assessment_user_id ON triage_assessment(user_id);
CREATE INDEX IF NOT EXISTS idx_health_records_user_id ON health_records(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);

-- Create full-text search indexes
CREATE INDEX IF NOT EXISTS idx_providers_name_fts ON healthcare_providers USING gin(to_tsvector('english', name));
CREATE INDEX IF NOT EXISTS idx_providers_specialty_fts ON healthcare_providers USING gin(to_tsvector('english', specialty));

-- Create composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_symptom_analysis_user_created ON symptom_analysis(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_triage_assessment_user_created ON triage_assessment(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_providers_location_specialty ON healthcare_providers(location, specialty);

-- Grant permissions (adjust as needed for your security model)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;

-- Create views for common queries
CREATE OR REPLACE VIEW active_users AS
SELECT id, email, first_name, last_name, created_at, last_login
FROM users
WHERE is_active = true;

CREATE OR REPLACE VIEW recent_symptom_analyses AS
SELECT sa.id, sa.user_id, u.email, sa.symptoms, sa.conditions, sa.confidence, sa.created_at
FROM symptom_analysis sa
JOIN users u ON sa.user_id = u.id
WHERE sa.created_at >= NOW() - INTERVAL '7 days'
ORDER BY sa.created_at DESC;

CREATE OR REPLACE VIEW provider_summary AS
SELECT 
    hp.id,
    hp.name,
    hp.specialty,
    hp.location,
    hp.accepting_patients,
    COUNT(DISTINCT hp.insurance_accepted) as insurance_count
FROM healthcare_providers hp
GROUP BY hp.id, hp.name, hp.specialty, hp.location, hp.accepting_patients;

-- Create functions for common operations
CREATE OR REPLACE FUNCTION update_user_last_login(user_id UUID)
RETURNS void AS $$
BEGIN
    UPDATE users 
    SET last_login = NOW() 
    WHERE id = user_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_user_health_summary(user_id UUID)
RETURNS TABLE(
    total_analyses INTEGER,
    recent_analyses INTEGER,
    avg_confidence DECIMAL,
    most_common_conditions TEXT[]
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::INTEGER as total_analyses,
        COUNT(CASE WHEN created_at >= NOW() - INTERVAL '30 days' THEN 1 END)::INTEGER as recent_analyses,
        AVG(confidence) as avg_confidence,
        ARRAY_AGG(DISTINCT unnest(conditions)) as most_common_conditions
    FROM symptom_analysis
    WHERE user_id = get_user_health_summary.user_id;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for audit logging
CREATE OR REPLACE FUNCTION audit_user_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_log (table_name, record_id, action, old_values, new_values, user_id, timestamp)
        VALUES (TG_TABLE_NAME, NEW.id, 'UPDATE', to_jsonb(OLD), to_jsonb(NEW), NEW.id, NOW());
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_log (table_name, record_id, action, old_values, new_values, user_id, timestamp)
        VALUES (TG_TABLE_NAME, OLD.id, 'DELETE', to_jsonb(OLD), NULL, OLD.id, NOW());
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Apply audit trigger to users table
CREATE TRIGGER users_audit_trigger
    AFTER UPDATE OR DELETE ON users
    FOR EACH ROW EXECUTE FUNCTION audit_user_changes();

-- Create materialized view for analytics
CREATE MATERIALIZED VIEW IF NOT EXISTS daily_analytics AS
SELECT 
    DATE(created_at) as date,
    COUNT(*) as total_analyses,
    COUNT(DISTINCT user_id) as unique_users,
    AVG(confidence) as avg_confidence,
    MODE() WITHIN GROUP (ORDER BY urgency) as most_common_urgency
FROM symptom_analysis
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- Create index on materialized view
CREATE INDEX IF NOT EXISTS idx_daily_analytics_date ON daily_analytics(date);

-- Refresh function for materialized view
CREATE OR REPLACE FUNCTION refresh_daily_analytics()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW daily_analytics;
END;
$$ LANGUAGE plpgsql;

-- Create a scheduled job to refresh analytics (requires pg_cron extension)
-- SELECT cron.schedule('refresh-analytics', '0 2 * * *', 'SELECT refresh_daily_analytics();');

COMMENT ON DATABASE ai_health_navigator IS 'AI Health Navigator - Advanced healthcare navigation platform with intelligent triage and provider matching';
