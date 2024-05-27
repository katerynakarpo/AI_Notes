CREATE OR REPLACE FUNCTION f_name_1()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO cnt_notes (user_id, cnt)
    VALUES (NEW.user_id, 0);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER add_0_notes
AFTER INSERT ON users
FOR EACH ROW
EXECUTE FUNCTION f_name_1();



CREATE OR REPLACE FUNCTION f_name()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE cnt_notes
        SET cnt = cnt + 1 ;
    ELSIF TG_OP = 'UPDATE' THEN
        IF NEW.is_deleted and not old.is_deleted THEN
            UPDATE cnt_notes
         SET cnt = cnt - 1 ;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER update_cnt_notes
AFTER INSERT OR UPDATE OF is_deleted ON notes
FOR EACH ROW
EXECUTE FUNCTION f_name();


