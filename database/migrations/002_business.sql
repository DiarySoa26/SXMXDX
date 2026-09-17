SET search_path TO sxmxdx;


-- ==========================================================
-- 1. MOIS
-- ==========================================================

CREATE TABLE mois
(
    mois_id SMALLINT PRIMARY KEY,

    code VARCHAR(10) NOT NULL UNIQUE,

    libelle VARCHAR(20) NOT NULL,

    ordre SMALLINT NOT NULL UNIQUE,

    CONSTRAINT ck_mois
        CHECK (mois_id BETWEEN 1 AND 12)
);


-- ==========================================================
-- 2. SITES
-- ==========================================================

CREATE TABLE site
(
    site_id BIGSERIAL PRIMARY KEY,

    code VARCHAR(50) NOT NULL UNIQUE,

    libelle VARCHAR(150) NOT NULL,

    actif BOOLEAN NOT NULL DEFAULT TRUE
);


-- ==========================================================
-- 3. PRODUITS
-- ==========================================================

CREATE TABLE produit
(
    produit_id BIGSERIAL PRIMARY KEY,

    code VARCHAR(100) NOT NULL UNIQUE,

    libelle VARCHAR(255) NOT NULL,

    categorie VARCHAR(100),

    unite VARCHAR(50),

    actif BOOLEAN NOT NULL DEFAULT TRUE
);


-- ==========================================================
-- 4. CLIENTS
-- ==========================================================

CREATE TABLE client
(
    client_id BIGSERIAL PRIMARY KEY,

    code VARCHAR(100),

    nom VARCHAR(255) NOT NULL,

    pays VARCHAR(100),

    actif BOOLEAN NOT NULL DEFAULT TRUE
);


-- ==========================================================
-- 5. COMPTES COMPTABLES
-- ==========================================================

CREATE TABLE compte_comptable
(
    compte_id BIGSERIAL PRIMARY KEY,

    numero VARCHAR(30) NOT NULL UNIQUE,

    intitule VARCHAR(255),

    niveau_1 VARCHAR(20),

    niveau_2 VARCHAR(20),

    niveau_3 VARCHAR(20),

    niveau_4 VARCHAR(20)
);


-- ==========================================================
-- 6. COMMANDES
-- ==========================================================

CREATE TABLE commande
(
    commande_id BIGSERIAL PRIMARY KEY,

    exercice_id BIGINT NOT NULL,

    reference VARCHAR(100),

    produit_id BIGINT,

    client_id BIGINT,

    date_commande DATE,

    unite VARCHAR(30),

    commentaire TEXT,

    CONSTRAINT fk_commande_exercice
        FOREIGN KEY (exercice_id)
        REFERENCES exercice(exercice_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_commande_produit
        FOREIGN KEY (produit_id)
        REFERENCES produit(produit_id),

    CONSTRAINT fk_commande_client
        FOREIGN KEY (client_id)
        REFERENCES client(client_id)
);


-- ==========================================================
-- 7. COMMANDES MENSUELLES
-- ==========================================================

CREATE TABLE commande_mensuelle
(
    commande_mensuelle_id BIGSERIAL PRIMARY KEY,

    commande_id BIGINT NOT NULL,

    mois_id SMALLINT NOT NULL,

    quantite NUMERIC(20,6),

    montant NUMERIC(20,6),

    CONSTRAINT fk_cmd_mensuelle_commande
        FOREIGN KEY (commande_id)
        REFERENCES commande(commande_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_cmd_mensuelle_mois
        FOREIGN KEY (mois_id)
        REFERENCES mois(mois_id),

    CONSTRAINT uq_commande_mois
        UNIQUE (commande_id, mois_id)
);


-- ==========================================================
-- 8. PRODUCTION
-- ==========================================================

CREATE TABLE production_mensuelle
(
    production_id BIGSERIAL PRIMARY KEY,

    exercice_id BIGINT NOT NULL,

    mois_id SMALLINT NOT NULL,

    produit_id BIGINT NOT NULL,

    site_id BIGINT,

    quantite NUMERIC(20,6),

    unite VARCHAR(30),

    source VARCHAR(100),

    CONSTRAINT fk_prod_exercice
        FOREIGN KEY (exercice_id)
        REFERENCES exercice(exercice_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_prod_mois
        FOREIGN KEY (mois_id)
        REFERENCES mois(mois_id),

    CONSTRAINT fk_prod_produit
        FOREIGN KEY (produit_id)
        REFERENCES produit(produit_id),

    CONSTRAINT fk_prod_site
        FOREIGN KEY (site_id)
        REFERENCES site(site_id)
);


-- ==========================================================
-- 9. BESOINS MATIERES
-- ==========================================================

CREATE TABLE besoin_matiere
(
    besoin_matiere_id BIGSERIAL PRIMARY KEY,

    exercice_id BIGINT NOT NULL,

    mois_id SMALLINT NOT NULL,

    produit_id BIGINT,

    site_id BIGINT,

    type_matiere VARCHAR(150),

    quantite NUMERIC(20,6),

    unite VARCHAR(30),

    montant NUMERIC(20,6),

    CONSTRAINT fk_besoin_exercice
        FOREIGN KEY (exercice_id)
        REFERENCES exercice(exercice_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_besoin_mois
        FOREIGN KEY (mois_id)
        REFERENCES mois(mois_id),

    CONSTRAINT fk_besoin_produit
        FOREIGN KEY (produit_id)
        REFERENCES produit(produit_id),

    CONSTRAINT fk_besoin_site
        FOREIGN KEY (site_id)
        REFERENCES site(site_id)
);


-- ==========================================================
-- 10. VENTES / CHIFFRE D'AFFAIRES
-- ==========================================================

CREATE TABLE vente
(
    vente_id BIGSERIAL PRIMARY KEY,

    exercice_id BIGINT NOT NULL,

    mois_id SMALLINT,

    reference VARCHAR(100),

    produit_id BIGINT,

    client_id BIGINT,

    date_vente DATE,

    pays VARCHAR(100),

    quantite NUMERIC(20,6),

    prix_unitaire NUMERIC(20,6),

    montant_mga NUMERIC(20,6),

    montant_usd NUMERIC(20,6),

    montant_eur NUMERIC(20,6),

    CONSTRAINT fk_vente_exercice
        FOREIGN KEY (exercice_id)
        REFERENCES exercice(exercice_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_vente_mois
        FOREIGN KEY (mois_id)
        REFERENCES mois(mois_id),

    CONSTRAINT fk_vente_produit
        FOREIGN KEY (produit_id)
        REFERENCES produit(produit_id),

    CONSTRAINT fk_vente_client
        FOREIGN KEY (client_id)
        REFERENCES client(client_id)
);


-- ==========================================================
-- 11. ACHATS
-- ==========================================================

CREATE TABLE achat_mensuel
(
    achat_id BIGSERIAL PRIMARY KEY,

    exercice_id BIGINT NOT NULL,

    mois_id SMALLINT NOT NULL,

    site_id BIGINT,

    categorie VARCHAR(150) NOT NULL,

    libelle VARCHAR(255),

    montant_ht NUMERIC(20,6),

    montant_tva NUMERIC(20,6),

    montant_ttc NUMERIC(20,6),

    decaisse BOOLEAN DEFAULT TRUE,

    CONSTRAINT fk_achat_exercice
        FOREIGN KEY (exercice_id)
        REFERENCES exercice(exercice_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_achat_mois
        FOREIGN KEY (mois_id)
        REFERENCES mois(mois_id),

    CONSTRAINT fk_achat_site
        FOREIGN KEY (site_id)
        REFERENCES site(site_id)
);


-- ==========================================================
-- 12. SALAIRES / MASSE SALARIALE
-- ==========================================================

CREATE TABLE masse_salariale
(
    masse_salariale_id BIGSERIAL PRIMARY KEY,

    exercice_id BIGINT NOT NULL,

    mois_id SMALLINT NOT NULL,

    site_id BIGINT,

    service VARCHAR(150),

    qualification VARCHAR(150),

    effectif NUMERIC(12,2),

    salaire_brut NUMERIC(20,6),

    irsa NUMERIC(20,6),

    cnaps NUMERIC(20,6),

    ostie NUMERIC(20,6),

    salaire_net NUMERIC(20,6),

    CONSTRAINT fk_salaire_exercice
        FOREIGN KEY (exercice_id)
        REFERENCES exercice(exercice_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_salaire_mois
        FOREIGN KEY (mois_id)
        REFERENCES mois(mois_id),

    CONSTRAINT fk_salaire_site
        FOREIGN KEY (site_id)
        REFERENCES site(site_id)
);


-- ==========================================================
-- 13. PRESTATIONS
-- ==========================================================

CREATE TABLE prestation_mensuelle
(
    prestation_id BIGSERIAL PRIMARY KEY,

    exercice_id BIGINT NOT NULL,

    mois_id SMALLINT NOT NULL,

    site_id BIGINT,

    categorie VARCHAR(150),

    libelle VARCHAR(255),

    quantite NUMERIC(20,6),

    prix_unitaire NUMERIC(20,6),

    montant NUMERIC(20,6),

    CONSTRAINT fk_prestation_exercice
        FOREIGN KEY (exercice_id)
        REFERENCES exercice(exercice_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_prestation_mois
        FOREIGN KEY (mois_id)
        REFERENCES mois(mois_id),

    CONSTRAINT fk_prestation_site
        FOREIGN KEY (site_id)
        REFERENCES site(site_id)
);


-- ==========================================================
-- 14. CHARGES
-- ==========================================================

CREATE TABLE charge_mensuelle
(
    charge_id BIGSERIAL PRIMARY KEY,

    exercice_id BIGINT NOT NULL,

    mois_id SMALLINT NOT NULL,

    domaine VARCHAR(100),

    categorie VARCHAR(150),

    libelle VARCHAR(255),

    montant NUMERIC(20,6),

    CONSTRAINT fk_charge_exercice
        FOREIGN KEY (exercice_id)
        REFERENCES exercice(exercice_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_charge_mois
        FOREIGN KEY (mois_id)
        REFERENCES mois(mois_id)
);


-- ==========================================================
-- 15. BALANCE COMPTABLE
-- ==========================================================

CREATE TABLE balance_mensuelle
(
    balance_id BIGSERIAL PRIMARY KEY,

    exercice_id BIGINT NOT NULL,

    compte_id BIGINT NOT NULL,

    mois_id SMALLINT,

    type_periode VARCHAR(20)
        NOT NULL DEFAULT 'MONTH',

    montant NUMERIC(20,6),

    CONSTRAINT fk_balance_exercice
        FOREIGN KEY (exercice_id)
        REFERENCES exercice(exercice_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_balance_compte
        FOREIGN KEY (compte_id)
        REFERENCES compte_comptable(compte_id),

    CONSTRAINT fk_balance_mois
        FOREIGN KEY (mois_id)
        REFERENCES mois(mois_id)
);


-- ==========================================================
-- 16. RESULTATS BUDGETAIRES
-- ==========================================================

CREATE TABLE resultat_budgetaire
(
    resultat_id BIGSERIAL PRIMARY KEY,

    exercice_id BIGINT NOT NULL,

    mois_id SMALLINT,

    domaine VARCHAR(100) NOT NULL,

    code_indicateur VARCHAR(100) NOT NULL,

    libelle VARCHAR(255),

    montant NUMERIC(20,6),

    unite VARCHAR(30) DEFAULT 'MGA',

    date_calcul TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_resultat_exercice
        FOREIGN KEY (exercice_id)
        REFERENCES exercice(exercice_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_resultat_mois
        FOREIGN KEY (mois_id)
        REFERENCES mois(mois_id)
);


-- ==========================================================
-- INDEX
-- ==========================================================

CREATE INDEX idx_production_exercice_mois
ON production_mensuelle(exercice_id, mois_id);

CREATE INDEX idx_besoin_exercice_mois
ON besoin_matiere(exercice_id, mois_id);

CREATE INDEX idx_vente_exercice_mois
ON vente(exercice_id, mois_id);

CREATE INDEX idx_achat_exercice_mois
ON achat_mensuel(exercice_id, mois_id);

CREATE INDEX idx_salaire_exercice_mois
ON masse_salariale(exercice_id, mois_id);

CREATE INDEX idx_charge_exercice_mois
ON charge_mensuelle(exercice_id, mois_id);

CREATE INDEX idx_balance_exercice_compte
ON balance_mensuelle(exercice_id, compte_id);

CREATE INDEX idx_resultat_exercice
ON resultat_budgetaire(exercice_id, domaine);