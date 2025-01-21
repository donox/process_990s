DROP TABLE IF EXISTS grant_geo_score;
CREATE TABLE grant_geo_score (
    id SERIAL PRIMARY KEY,
    ein VARCHAR(9) NOT NULL REFERENCES filer(ein),
    grant_count INT,
	longtitude FLOAT,
	latitude FLOAT,
	deviation FLOAT,
	filer_to_centroid FLOAT
);

CREATE INDEX idx_grant_results_ein ON grant_geo_score(ein);