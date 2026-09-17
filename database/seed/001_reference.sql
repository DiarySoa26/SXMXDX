SET search_path TO sxmxdx;

INSERT INTO mois
(
    mois_id,
    code,
    libelle,
    ordre
)
VALUES
    (1,  'M01', 'Janvier',   1),
    (2,  'M02', 'Février',   2),
    (3,  'M03', 'Mars',      3),
    (4,  'M04', 'Avril',     4),
    (5,  'M05', 'Mai',       5),
    (6,  'M06', 'Juin',      6),
    (7,  'M07', 'Juillet',   7),
    (8,  'M08', 'Août',      8),
    (9,  'M09', 'Septembre', 9),
    (10, 'M10', 'Octobre',   10),
    (11, 'M11', 'Novembre',  11),
    (12, 'M12', 'Décembre',  12)
ON CONFLICT (mois_id)
DO NOTHING;


INSERT INTO site(code, libelle)
VALUES
    ('FORT_DAUPHIN', 'Fort Dauphin'),
    ('AMPANDRANDAVA', 'Ampandrandava'),
    ('TRANOMARO', 'Tranomaro')
ON CONFLICT (code)
DO NOTHING;