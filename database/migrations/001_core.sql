CREATE SCHEMA IF NOT EXISTS sxmxdx;

SET search_path TO sxmxdx;


-- ==========================================================
-- EXERCICE
-- ==========================================================

CREATE TABLE exercice
(
    exercice_id BIGSERIAL PRIMARY KEY,

    annee INTEGER NOT NULL,

    libelle VARCHAR(100),

    statut VARCHAR(30) NOT NULL
        DEFAULT 'DRAFT',

    fichier_source VARCHAR(255),

    date_import TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP,

    date_creation TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_exercice_annee
        UNIQUE (annee),

    CONSTRAINT ck_exercice_annee
        CHECK (annee >= 2000)
);


-- ==========================================================
-- PARAMETRES METIER
-- ==========================================================

CREATE TABLE parametre_definition
(
    parametre_id BIGSERIAL PRIMARY KEY,

    code VARCHAR(100)
        NOT NULL UNIQUE,

    libelle VARCHAR(255)
        NOT NULL,

    unite VARCHAR(50),

    categorie VARCHAR(100),

    description TEXT,

    excel_sheet VARCHAR(150),

    excel_cell VARCHAR(30),

    actif BOOLEAN
        NOT NULL DEFAULT TRUE
);


-- ==========================================================
-- VALEUR DES PARAMETRES PAR EXERCICE
-- ==========================================================

CREATE TABLE parametre_exercice
(
    parametre_exercice_id BIGSERIAL
        PRIMARY KEY,

    exercice_id BIGINT
        NOT NULL,

    parametre_id BIGINT
        NOT NULL,

    valeur_numerique NUMERIC(20, 6),

    valeur_texte TEXT,

    date_creation TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_param_exercice
        FOREIGN KEY (exercice_id)
        REFERENCES exercice(exercice_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_param_definition
        FOREIGN KEY (parametre_id)
        REFERENCES parametre_definition(parametre_id),

    CONSTRAINT uq_param_exercice
        UNIQUE (
            exercice_id,
            parametre_id
        )
);


-- ==========================================================
-- IMPORT
-- ==========================================================

CREATE TABLE import_batch
(
    import_batch_id BIGSERIAL PRIMARY KEY,

    exercice_id BIGINT
        NOT NULL,

    fichier VARCHAR(255)
        NOT NULL,

    checksum VARCHAR(128),

    statut VARCHAR(30)
        NOT NULL DEFAULT 'PENDING',

    nombre_lignes BIGINT
        DEFAULT 0,

    nombre_erreurs BIGINT
        DEFAULT 0,

    date_debut TIMESTAMP,

    date_fin TIMESTAMP,

    date_creation TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_import_exercice
        FOREIGN KEY (exercice_id)
        REFERENCES exercice(exercice_id)
        ON DELETE CASCADE
);


-- ==========================================================
-- ANOMALIES D'IMPORT
-- ==========================================================

CREATE TABLE import_error
(
    import_error_id BIGSERIAL PRIMARY KEY,

    import_batch_id BIGINT
        NOT NULL,

    sheet_name VARCHAR(150),

    cell_reference VARCHAR(50),

    error_code VARCHAR(100),

    message TEXT NOT NULL,

    valeur_source TEXT,

    date_creation TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_error_batch
        FOREIGN KEY (import_batch_id)
        REFERENCES import_batch(import_batch_id)
        ON DELETE CASCADE
);


-- ==========================================================
-- REGLES METIER
-- ==========================================================

CREATE TABLE regle_metier
(
    regle_id BIGSERIAL PRIMARY KEY,

    code VARCHAR(100)
        NOT NULL UNIQUE,

    nom VARCHAR(255)
        NOT NULL,

    domaine VARCHAR(100)
        NOT NULL,

    description TEXT,

    formule_source TEXT,

    fonction_python VARCHAR(255),

    ordre_execution INTEGER,

    actif BOOLEAN
        DEFAULT TRUE,

    date_creation TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP
);


-- ==========================================================
-- INDEX
-- ==========================================================

CREATE INDEX idx_param_exercice
ON parametre_exercice(exercice_id);


CREATE INDEX idx_import_exercice
ON import_batch(exercice_id);


CREATE INDEX idx_regle_domaine
ON regle_metier(domaine);