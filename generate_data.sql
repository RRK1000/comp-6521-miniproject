-- Insert 'x' additional rows into table R
DO $$
DECLARE
    i INTEGER;
BEGIN
    FOR i IN 1..x LOOP
        INSERT INTO R (A1, A2, A3, A4, Ann)
        VALUES (random_int(), random_int(), random_int(), random_int(), 'R' || (SELECT COUNT(*) FROM R) + i);
    END LOOP;
END $$;

-- Insert 'x' additional rows into table S
DO $$
DECLARE
    j INTEGER;
BEGIN
    FOR j IN 1..x LOOP
        INSERT INTO S (B1, B2, B3, B4, Ann)
        VALUES (random_int(), random_int(), random_int(), random_int(), 'S' || (SELECT COUNT(*) FROM S) + j);
    END LOOP;
END $$;