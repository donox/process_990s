CREATE TABLE grant_analysis_results (
    id SERIAL PRIMARY KEY,
    ein VARCHAR(9) NOT NULL REFERENCES filer(ein),
    foundation_name TEXT,
    score FLOAT,
    semantic_similarity FLOAT,
    total_relevant_grants INTEGER,
    avg_grant_size FLOAT,
    geographic_coverage FLOAT,
    grant_center POINT,
    distance_to_target FLOAT,
    scored_date TIMESTAMP
);

CREATE INDEX idx_grant_results_ein ON grant_analysis_results(ein);
ALTER TABLE grant_analysis_results ADD CONSTRAINT unique_ein UNIQUE (ein);

COMMENT ON TABLE grant_analysis_results IS 'Collected scores for a foundation';
COMMENT ON COLUMN grant_analysis_results.geographic_coverage IS
    'This is an indication of the foundations willingness to
    provide grants at a distance from their home.  For foundations
    with less than 3 grants - it is None.  Otherwise
    it is the stdev of the spread of the grants.';
COMMENT ON COLUMN grant_analysis_results.distance_to_target IS
    'Distance in miles from foundation zipcode to target.  If
    zip is unknown, use centroid of grants.
    ';