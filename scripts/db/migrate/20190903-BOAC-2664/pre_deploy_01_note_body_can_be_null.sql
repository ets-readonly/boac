BEGIN;

ALTER TABLE ONLY notes ALTER COLUMN body DROP NOT NULL;

COMMIT;