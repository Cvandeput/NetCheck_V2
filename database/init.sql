-- Database: PostgreSQL

CREATE TABLE public.users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    hashpassword TEXT NOT NULL,
    role VARCHAR(20) DEFAULT 'membre' NOT NULL CHECK (role IN ('membre', 'admin')),
    is_temporary BOOLEAN DEFAULT false NOT NULL,
    is_active BOOLEAN DEFAULT true NOT NULL,
    failed_attempts INTEGER DEFAULT 0 NOT NULL,
    locked_until TIMESTAMP WITHOUT TIME ZONE,
    last_login TIMESTAMP WITHOUT TIME ZONE,
    lockout_count INTEGER DEFAULT 0 NOT NULL --ajoute du nombre de blocage
);

Create table public.userActions
(
    id_modification SERIAL PRIMARY KEY,
    ip_1 VARCHAR(15) NOT NULL,
    ip_2 VARCHAR(15) ,
    masque_1 VARCHAR(15) NOT NULL,
    masque_2 VARCHAR(15) ,
    number_subnet integer,
    number_ip integer ,
    user_id integer REFERENCES public.users(id),
    id_function INT Check (id_function IN (0, 1)) --1 ou 0 
);

CREATE TABLE adminResetMdp (
    user_id INTEGER PRIMARY KEY REFERENCES users(id),
    request_date TIMESTAMP(0) WITHOUT TIME ZONE
);

-- Création de la table CIDR
CREATE TABLE public.cidr_table (
    cidr INTEGER PRIMARY KEY CHECK (cidr >= 8 AND cidr <= 30),
    binaire VARCHAR(35) NOT NULL,
    decimal VARCHAR(15) NOT NULL
);

-- Insertion des masques CIDR de 8 à 30
INSERT INTO public.cidr_table (cidr, binaire, decimal) VALUES
    (8,  '11111111.00000000.00000000.00000000', '255.0.0.0'),
    (9,  '11111111.10000000.00000000.00000000', '255.128.0.0'),
    (10, '11111111.11000000.00000000.00000000', '255.192.0.0'),
    (11, '11111111.11100000.00000000.00000000', '255.224.0.0'),
    (12, '11111111.11110000.00000000.00000000', '255.240.0.0'),
    (13, '11111111.11111000.00000000.00000000', '255.248.0.0'),
    (14, '11111111.11111100.00000000.00000000', '255.252.0.0'),
    (15, '11111111.11111110.00000000.00000000', '255.254.0.0'),
    (16, '11111111.11111111.00000000.00000000', '255.255.0.0'),
    (17, '11111111.11111111.10000000.00000000', '255.255.128.0'),
    (18, '11111111.11111111.11000000.00000000', '255.255.192.0'),
    (19, '11111111.11111111.11100000.00000000', '255.255.224.0'),
    (20, '11111111.11111111.11110000.00000000', '255.255.240.0'),
    (21, '11111111.11111111.11111000.00000000', '255.255.248.0'),
    (22, '11111111.11111111.11111100.00000000', '255.255.252.0'),
    (23, '11111111.11111111.11111110.00000000', '255.255.254.0'),
    (24, '11111111.11111111.11111111.00000000', '255.255.255.0'),
    (25, '11111111.11111111.11111111.10000000', '255.255.255.128'),
    (26, '11111111.11111111.11111111.11000000', '255.255.255.192'),
    (27, '11111111.11111111.11111111.11100000', '255.255.255.224'),
    (28, '11111111.11111111.11111111.11110000', '255.255.255.240'),
    (29, '11111111.11111111.11111111.11111000', '255.255.255.248'),
    (30, '11111111.11111111.11111111.11111100', '255.255.255.252');

INSERT INTO public.users (username, hashpassword, role, is_temporary, is_active, locked_until, lockout_count) VALUES 
    ('User1', '$2b$13$bHlfV9VzzlDnd67MQoJtFOnjus0tPTc24YLoZ8uCYRjmQuZLbjiCi', 'admin',  false,  true, NULL, 0),
    ('User2', '$2b$13$bHlfV9VzzlDnd67MQoJtFOnjus0tPTc24YLoZ8uCYRjmQuZLbjiCi', 'membre', false,  true, NULL, 0),
    ('User3', '$2b$13$bHlfV9VzzlDnd67MQoJtFOnjus0tPTc24YLoZ8uCYRjmQuZLbjiCi', 'membre', true,   true, NULL, 0),
    ('User4', '$2b$13$bHlfV9VzzlDnd67MQoJtFOnjus0tPTc24YLoZ8uCYRjmQuZLbjiCi', 'membre', false,  true, '2026-12-31 23:59:59',3),
    ('User5', '$2b$13$bHlfV9VzzlDnd67MQoJtFOnjus0tPTc24YLoZ8uCYRjmQuZLbjiCi', 'membre', false, false, NULL, 0);
