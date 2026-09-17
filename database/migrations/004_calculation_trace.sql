SET search_path TO sxmxdx;


CREATE TABLE IF NOT EXISTS calculation_run
(
    calculation_run_id BIGSERIAL PRIMARY KEY,

    exercice_id BIGINT NOT NULL,

    domaine VARCHAR(100) NOT NULL,

    moteur VARCHAR(50) NOT NULL,

    version_moteur VARCHAR(50),

    statut VARCHAR(30)
        NOT NULL DEFAULT 'RUNNING',

    date_debut TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP,

    date_fin TIMESTAMP,

    CONSTRAINT fk_calculation_exercice
        FOREIGN KEY (exercice_id)
        REFERENCES exercice(exercice_id)
        ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS calculation_comparison
(
    comparison_id BIGSERIAL PRIMARY KEY,

    calculation_run_id BIGINT NOT NULL,

    sheet_name VARCHAR(150),

    cell_reference VARCHAR(30),

    regle_code VARCHAR(100),

    valeur_excel NUMERIC(24,6),

    valeur_sxmxdx NUMERIC(24,6),

    ecart NUMERIC(24,6),

    conforme BOOLEAN,

    CONSTRAINT fk_comparison_run
        FOREIGN KEY (calculation_run_id)
        REFERENCES calculation_run(
            calculation_run_id
        )
        ON DELETE CASCADE
);


CREATE INDEX IF NOT EXISTS
idx_calculation_run_exercice
ON calculation_run(exercice_id);


CREATE INDEX IF NOT EXISTS
idx_comparison_run
ON calculation_comparison(
    calculation_run_id
);