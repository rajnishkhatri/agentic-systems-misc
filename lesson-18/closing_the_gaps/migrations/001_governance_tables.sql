-- Migration: 001_governance_tables.sql
-- Description: Create tables for governance layer (Gap 6: HITL, Gap 9: Security)
-- Created: December 2024
-- PRD Reference: tasks/0012-prd-closing-gaps-phase1-governance.md

-- =============================================================================
-- SECURITY EVENTS TABLE (Gap 9: PromptSecurityGuard)
-- =============================================================================

-- Main table for security scan events
CREATE TABLE IF NOT EXISTS security_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Input details (hashed for privacy - never store raw input)
    input_hash VARCHAR(64) NOT NULL,  -- SHA-256 of input
    input_length INTEGER NOT NULL,

    -- Scan result
    is_safe BOOLEAN NOT NULL,
    threat_type VARCHAR(50),  -- e.g., 'injection', 'role_hijack', 'prompt_leak'
    confidence FLOAT CHECK (confidence >= 0.0 AND confidence <= 1.0),
    matched_patterns TEXT[],  -- Array of matched pattern names
    scan_duration_ms FLOAT NOT NULL,

    -- Context
    session_id UUID,
    user_id VARCHAR(100),
    agent_id VARCHAR(50),

    -- Audit metadata
    scanner_version VARCHAR(20) NOT NULL DEFAULT '1.0.0',
    scan_type VARCHAR(20) DEFAULT 'user_input',  -- 'user_input', 'agent_output'

    -- Constraints
    CONSTRAINT valid_threat_type CHECK (
        threat_type IS NULL OR threat_type IN (
            'instruction_override',
            'role_hijack',
            'prompt_leak',
            'delimiter_injection',
            'jailbreak',
            'custom'
        )
    )
);

-- Indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_security_events_timestamp
    ON security_events (timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_security_events_threat_type
    ON security_events (threat_type)
    WHERE threat_type IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_security_events_session_id
    ON security_events (session_id)
    WHERE session_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_security_events_is_safe
    ON security_events (is_safe)
    WHERE is_safe = FALSE;

-- Partial index for blocked requests (faster threat analysis)
CREATE INDEX IF NOT EXISTS idx_security_events_blocked
    ON security_events (timestamp DESC, threat_type)
    WHERE is_safe = FALSE;

-- =============================================================================
-- PARTITIONING FOR SECURITY EVENTS (Performance optimization)
-- =============================================================================

-- Note: In production, convert security_events to partitioned table:
-- This is a template for monthly partitions

-- CREATE TABLE security_events_y2024m12 PARTITION OF security_events
--     FOR VALUES FROM ('2024-12-01') TO ('2025-01-01');

-- CREATE TABLE security_events_y2025m01 PARTITION OF security_events
--     FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');


-- =============================================================================
-- HITL DECISIONS TABLE (Gap 6: HITLController)
-- =============================================================================

-- Main table for HITL interrupt decisions
CREATE TABLE IF NOT EXISTS hitl_decisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    decision_id UUID UNIQUE NOT NULL,  -- External reference ID
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Decision details
    should_interrupt BOOLEAN NOT NULL,
    reason TEXT NOT NULL,
    tier VARCHAR(20) NOT NULL,  -- 'tier_1', 'tier_2', 'tier_3'

    -- Context that triggered decision
    confidence FLOAT NOT NULL CHECK (confidence >= 0.0 AND confidence <= 1.0),
    amount FLOAT,  -- Dispute amount (nullable for non-financial actions)
    dispute_type VARCHAR(50) NOT NULL,
    action_type VARCHAR(50),

    -- Session context
    session_id UUID,
    agent_id VARCHAR(50),

    -- Constraints
    CONSTRAINT valid_tier CHECK (
        tier IN ('tier_1', 'tier_2', 'tier_3')
    )
);

-- Indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_hitl_decisions_timestamp
    ON hitl_decisions (timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_hitl_decisions_tier
    ON hitl_decisions (tier);

CREATE INDEX IF NOT EXISTS idx_hitl_decisions_dispute_type
    ON hitl_decisions (dispute_type);

CREATE INDEX IF NOT EXISTS idx_hitl_decisions_decision_id
    ON hitl_decisions (decision_id);

-- Partial index for interrupted decisions (faster review queue queries)
CREATE INDEX IF NOT EXISTS idx_hitl_decisions_interrupted
    ON hitl_decisions (timestamp DESC, tier)
    WHERE should_interrupt = TRUE;


-- =============================================================================
-- HITL REVIEWS TABLE (Human reviewer actions)
-- =============================================================================

-- Table for human review requests and responses
CREATE TABLE IF NOT EXISTS hitl_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    review_id UUID UNIQUE NOT NULL,  -- External reference ID
    decision_id UUID NOT NULL REFERENCES hitl_decisions(decision_id),

    -- Request details
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    context JSONB NOT NULL,  -- Full context for reviewer (dispute details, etc.)
    priority VARCHAR(10) DEFAULT 'normal',  -- 'high', 'normal', 'low'

    -- Response details (populated when reviewed)
    reviewed_at TIMESTAMPTZ,
    approved BOOLEAN,
    reviewer_id VARCHAR(100),
    notes TEXT,

    -- Status tracking
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    expires_at TIMESTAMPTZ,  -- Optional SLA deadline

    -- Constraints
    CONSTRAINT valid_status CHECK (
        status IN ('pending', 'approved', 'rejected', 'expired', 'escalated')
    ),
    CONSTRAINT valid_priority CHECK (
        priority IN ('high', 'normal', 'low')
    )
);

-- Indexes for review queue queries
CREATE INDEX IF NOT EXISTS idx_hitl_reviews_status
    ON hitl_reviews (status)
    WHERE status = 'pending';

CREATE INDEX IF NOT EXISTS idx_hitl_reviews_decision_id
    ON hitl_reviews (decision_id);

CREATE INDEX IF NOT EXISTS idx_hitl_reviews_created_at
    ON hitl_reviews (created_at DESC)
    WHERE status = 'pending';

CREATE INDEX IF NOT EXISTS idx_hitl_reviews_reviewer_id
    ON hitl_reviews (reviewer_id)
    WHERE reviewer_id IS NOT NULL;

-- Priority queue index
CREATE INDEX IF NOT EXISTS idx_hitl_reviews_priority_queue
    ON hitl_reviews (priority, created_at)
    WHERE status = 'pending';


-- =============================================================================
-- VIEWS FOR REPORTING
-- =============================================================================

-- Security threat summary view
CREATE OR REPLACE VIEW security_threat_summary AS
SELECT
    DATE_TRUNC('day', timestamp) as date,
    threat_type,
    COUNT(*) as threat_count,
    AVG(scan_duration_ms) as avg_scan_ms
FROM security_events
WHERE is_safe = FALSE
GROUP BY DATE_TRUNC('day', timestamp), threat_type
ORDER BY date DESC, threat_count DESC;

-- HITL escalation summary view
CREATE OR REPLACE VIEW hitl_escalation_summary AS
SELECT
    DATE_TRUNC('day', timestamp) as date,
    tier,
    COUNT(*) as decision_count,
    SUM(CASE WHEN should_interrupt THEN 1 ELSE 0 END) as interrupted_count,
    AVG(confidence) as avg_confidence,
    AVG(amount) as avg_amount
FROM hitl_decisions
GROUP BY DATE_TRUNC('day', timestamp), tier
ORDER BY date DESC, tier;

-- Pending reviews view
CREATE OR REPLACE VIEW pending_reviews AS
SELECT
    r.review_id,
    r.created_at,
    r.priority,
    r.context,
    d.tier,
    d.dispute_type,
    d.amount,
    d.confidence,
    d.reason,
    EXTRACT(EPOCH FROM (NOW() - r.created_at)) / 60 as waiting_minutes
FROM hitl_reviews r
JOIN hitl_decisions d ON r.decision_id = d.decision_id
WHERE r.status = 'pending'
ORDER BY
    CASE r.priority
        WHEN 'high' THEN 1
        WHEN 'normal' THEN 2
        WHEN 'low' THEN 3
    END,
    r.created_at;


-- =============================================================================
-- FUNCTIONS FOR MAINTENANCE
-- =============================================================================

-- Function to expire old pending reviews
CREATE OR REPLACE FUNCTION expire_stale_reviews(max_age_hours INTEGER DEFAULT 24)
RETURNS INTEGER AS $$
DECLARE
    expired_count INTEGER;
BEGIN
    UPDATE hitl_reviews
    SET
        status = 'expired',
        reviewed_at = NOW()
    WHERE
        status = 'pending'
        AND created_at < NOW() - (max_age_hours || ' hours')::INTERVAL;

    GET DIAGNOSTICS expired_count = ROW_COUNT;
    RETURN expired_count;
END;
$$ LANGUAGE plpgsql;

-- Function to get threat statistics for a time period
CREATE OR REPLACE FUNCTION get_threat_stats(
    start_time TIMESTAMPTZ DEFAULT NOW() - INTERVAL '24 hours',
    end_time TIMESTAMPTZ DEFAULT NOW()
)
RETURNS TABLE (
    threat_type VARCHAR,
    count BIGINT,
    avg_confidence FLOAT,
    avg_scan_ms FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        se.threat_type,
        COUNT(*)::BIGINT,
        AVG(se.confidence)::FLOAT,
        AVG(se.scan_duration_ms)::FLOAT
    FROM security_events se
    WHERE
        se.timestamp BETWEEN start_time AND end_time
        AND se.is_safe = FALSE
    GROUP BY se.threat_type
    ORDER BY COUNT(*) DESC;
END;
$$ LANGUAGE plpgsql;


-- =============================================================================
-- COMMENTS FOR DOCUMENTATION
-- =============================================================================

COMMENT ON TABLE security_events IS 'Audit log of all security scans performed by PromptSecurityGuard (Gap 9)';
COMMENT ON TABLE hitl_decisions IS 'Record of all HITL interrupt decisions made by HITLController (Gap 6)';
COMMENT ON TABLE hitl_reviews IS 'Human review requests and their outcomes';

COMMENT ON COLUMN security_events.input_hash IS 'SHA-256 hash of input - raw input never stored for privacy';
COMMENT ON COLUMN security_events.threat_type IS 'Classification of detected threat per OWASP LLM Top 10';
COMMENT ON COLUMN hitl_decisions.tier IS 'Oversight tier: tier_1 (full HITL), tier_2 (sample), tier_3 (logged)';
COMMENT ON COLUMN hitl_reviews.context IS 'JSONB containing full dispute context for human reviewer';

