CREATE TABLE zip_coordinates
(
    zipcode    VARCHAR(5) PRIMARY KEY,
    city       VARCHAR(100),
    state      CHAR(2),
    area_codes VARCHAR(100),
    latitude   DECIMAL(9, 6),
    longitude  DECIMAL(9, 6),
    population INTEGER
);

CREATE INDEX idx_zip_coords_state ON zip_coordinates (state);
CREATE INDEX idx_zip_coords_latlong ON zip_coordinates (latitude, longitude);