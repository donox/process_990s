DROP TABLE IF EXISTS grant_semantic_score;
CREATE TABLE grant_semantic_score (
    EIN VARCHAR(15),
    foundation_name TEXT,
    purpose TEXT,
    similarity_score FLOAT,
    PRIMARY KEY (EIN, foundation_name, purpose),
    UNIQUE (ein, foundation_name)
);