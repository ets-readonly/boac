BEGIN;

ALTER TABLE notes ADD COLUMN deleted_at TIMESTAMP WITH TIME ZONE;

COMMIT;
