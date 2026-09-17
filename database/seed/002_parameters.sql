SET search_path TO sxmxdx;


INSERT INTO parametre_definition
(
    code,
    libelle,
    unite,
    categorie,
    excel_sheet,
    excel_cell
)
VALUES

(
    'TAUX_CHANGE_USD',
    'Taux de change USD',
    'MGA/USD',
    'DEVISE',
    'Données SOMIDA',
    'E5'
),

(
    'TAUX_CHANGE_EUR',
    'Taux de change EUR',
    'MGA/EUR',
    'DEVISE',
    'Données SOMIDA',
    'E6'
),

(
    'AUGMENTATION_GLOBALE_SALAIRE',
    'Augmentation globale de salaire',
    '%',
    'RH',
    'Données SOMIDA',
    'E7'
),

(
    'TAUX_TVA',
    'Taux de TVA',
    '%',
    'FISCALITE',
    'Données SOMIDA',
    'E8'
),

(
    'RENDEMENT_MICA_BRUT_GAZ',
    'Rendement micas bruts vs gaz',
    '%',
    'PRODUCTION',
    'Données SOMIDA',
    'D58'
),

(
    'PART_ACHAT_TRANOMARO',
    'Part achat Tranomaro',
    '%',
    'ACHAT',
    'Données SOMIDA',
    'D62'
),

(
    'PART_ACHAT_AMPANDRANDAVA',
    'Part achat Ampandrandava',
    '%',
    'ACHAT',
    'Données SOMIDA',
    'D63'
),

(
    'PART_ACHAT_FORT_DAUPHIN',
    'Part achat Fort Dauphin',
    '%',
    'ACHAT',
    'Données SOMIDA',
    'D64'
),

(
    'TAUX_PRODUIT_BRUT',
    'Taux produit brut',
    '%',
    'VENTE',
    'CA',
    'C43'
),

(
    'TAUX_PRODUITS_TRANSFORMES',
    'Taux produits transformés',
    '%',
    'VENTE',
    'CA',
    'C44'
),

(
    'LOYER_1_MENSUEL',
    'Loyer 1 mensuel',
    'MGA/mois',
    'CHARGE',
    'Données SOMIDA',
    'E27'
),

(
    'LOYER_2_MENSUEL',
    'Loyer 2 mensuel',
    'MGA/mois',
    'CHARGE',
    'Données SOMIDA',
    'E28'
)

ON CONFLICT (code)
DO UPDATE SET

    libelle = EXCLUDED.libelle,
    unite = EXCLUDED.unite,
    categorie = EXCLUDED.categorie,
    excel_sheet = EXCLUDED.excel_sheet,
    excel_cell = EXCLUDED.excel_cell;