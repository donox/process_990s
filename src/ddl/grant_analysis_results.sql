CREATE TABLE grant_analysis_results (
    id SERIAL PRIMARY KEY,
    ein VARCHAR(9) NOT NULL REFERENCES filer(ein),
    name TEXT,
    score FLOAT,
    matched_keywords TEXT[],
    total_relevant_grants INTEGER,
    avg_grant_size FLOAT,
    geographic_coverage TEXT[],
    scored_date TIMESTAMP,
    run_id VARCHAR(50)
);

CREATE INDEX idx_grant_results_run_id ON grant_analysis_results(run_id);
CREATE INDEX idx_grant_results_date ON grant_analysis_results(scored_date);
CREATE INDEX idx_grant_results_ein ON grant_analysis_results(ein);