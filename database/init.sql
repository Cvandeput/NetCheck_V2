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

Create table userActions
(
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES public.users(id),
    action VARCHAR(100) NOT NULL,
    details Varchar(255),
    timestamp TIMESTAMP WITHOUT TIME ZONE
);

INSERT INTO public.users (username, hashpassword, role, is_temporary, is_active, locked_until, lockout_count) VALUES 
    ('User1', '$2b$13$bHlfV9VzzlDnd67MQoJtFOnjus0tPTc24YLoZ8uCYRjmQuZLbjiCi', 'admin',  false,  true, NULL, 0),
    ('User2', '$2b$13$bHlfV9VzzlDnd67MQoJtFOnjus0tPTc24YLoZ8uCYRjmQuZLbjiCi', 'membre', false,  true, NULL, 0),
    ('User3', '$2b$13$bHlfV9VzzlDnd67MQoJtFOnjus0tPTc24YLoZ8uCYRjmQuZLbjiCi', 'membre', true,   true, NULL, 0),
    ('User4', '$2b$13$bHlfV9VzzlDnd67MQoJtFOnjus0tPTc24YLoZ8uCYRjmQuZLbjiCi', 'membre', false,  true, '2026-12-31 23:59:59',3),
    ('User5', '$2b$13$bHlfV9VzzlDnd67MQoJtFOnjus0tPTc24YLoZ8uCYRjmQuZLbjiCi', 'membre', false, false, NULL, 0);
