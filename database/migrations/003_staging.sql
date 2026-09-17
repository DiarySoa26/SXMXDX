CREATE SCHEMA IF NOT EXISTS staging;


CREATE TABLE staging.import_cell
(
    staging_cell_id BIGSERIAL PRIMARY KEY,

    import_batch_id BIGINT NOT NULL,

    sheet_name VARCHAR(150) NOT NULL,

    cell_reference VARCHAR(30) NOT NULL,

    row_number INTEGER NOT NULL,

    column_number INTEGER NOT NULL,

    technical_type VARCHAR(30),

    raw_value TEXT,

    number_format VARCHAR(100),

    created_at TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_staging_batch
        FOREIGN KEY (import_batch_id)
        REFERENCES sxmxdx.import_batch(import_batch_id)
        ON DELETE CASCADE
);


CREATE INDEX idx_staging_sheet
ON staging.import_cell
(
    import_batch_id,
    sheet_name
);


CREATE INDEX idx_staging_position
ON staging.import_cell
(
    import_batch_id,
    sheet_name,
    row_number,
    column_number
);