-- ============================================================================
-- StreamVault - CORRECTED Stored Procedures for RGC Database
-- Updated to match actual database schema from RGC_Project_Part1.pdf
-- ============================================================================

USE RGC;

DELIMITER $$

-- ============================================================================
-- 1. STORED PROCEDURE: Safe Series Addition with Validation
-- ============================================================================
DROP PROCEDURE IF EXISTS sp_add_web_series$$
CREATE PROCEDURE sp_add_web_series(
    IN p_series_id VARCHAR(10),
    IN p_series_name VARCHAR(50),
    IN p_num_episodes INT,
    IN p_release_date DATE,
    IN p_country_origin VARCHAR(30),
    IN p_language VARCHAR(30),
    IN p_house_id VARCHAR(10)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SIGNAL SQLSTATE '45000' 
            SET MESSAGE_TEXT = 'Error adding web series - transaction rolled back';
    END;

    START TRANSACTION;

    -- Validate: series must NOT already exist
    IF EXISTS (SELECT 1 
               FROM RGC_WEB_SERIES 
               WHERE SERIES_ID = p_series_id) THEN
        SIGNAL SQLSTATE '45000' 
            SET MESSAGE_TEXT = 'Series ID already exists';
    END IF;

    -- Validate: production house MUST exist
    IF NOT EXISTS (SELECT 1 
                   FROM RGC_PRODUCTION_HOUSE 
                   WHERE HOUSE_ID = p_house_id) THEN
        SIGNAL SQLSTATE '45000' 
            SET MESSAGE_TEXT = 'Invalid production house ID';
    END IF;

    -- Insert new series
    INSERT INTO RGC_WEB_SERIES 
    (SERIES_ID, SERIES_NAME, NUM_EPISODES, RELEASE_DATE, COUNTRY_OF_ORIGIN, LANGUAGE, HOUSE_ID)
    VALUES 
    (p_series_id, p_series_name, p_num_episodes, p_release_date, p_country_origin, p_language, p_house_id);

    COMMIT;
    SELECT 'Series added successfully' AS message;
END$$

-- ============================================================================
-- 2. STORED PROCEDURE: Cascading Delete with Transaction Safety
-- ============================================================================
DROP PROCEDURE IF EXISTS sp_delete_web_series$$
CREATE PROCEDURE sp_delete_web_series(
    IN p_series_id VARCHAR(10)
)
BEGIN
    DECLARE v_count INT DEFAULT 0;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Error deleting series - transaction rolled back';
    END;
    
    START TRANSACTION;
    
    -- Check if series exists
    SELECT COUNT(*) INTO v_count FROM RGC_WEB_SERIES WHERE SERIES_ID = p_series_id;
    IF v_count = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Series not found';
    END IF;
    --- DEADLOCK ISSUE FIXED BY REORDERING DELETES ---
    -- Delete in order (respecting foreign keys) - CORRECTED TABLE NAMES
    DELETE FROM RGC_FEEDBACK WHERE SERIES_ID = p_series_id;
    
    DELETE FROM RGC_AIRING_SCHEDULE 
    WHERE EPISODE_ID IN (SELECT EPISODE_ID FROM RGC_EPISODE WHERE SERIES_ID = p_series_id);
    
    DELETE FROM RGC_EPISODE WHERE SERIES_ID = p_series_id;
    DELETE FROM RGC_CONTRACT WHERE SERIES_ID = p_series_id;
    DELETE FROM RGC_WEB_SERIES_SERIES_TYPE WHERE SERIES_ID = p_series_id;
    DELETE FROM RGC_WEBSERIES_SUBTITLE WHERE SERIES_ID = p_series_id;
    DELETE FROM RGC_WEBSERIES_DUBBING WHERE SERIES_ID = p_series_id;
    DELETE FROM RGC_WS_RELEASE_COUNTRY WHERE SERIES_ID = p_series_id;
    DELETE FROM RGC_WEB_SERIES WHERE SERIES_ID = p_series_id;
    
    COMMIT;
    SELECT 'Series deleted successfully' AS message;
END$$

-- ============================================================================
-- 3. STORED PROCEDURE: Add Feedback with Duplicate Prevention
-- ============================================================================
DROP PROCEDURE IF EXISTS sp_add_feedback$$
CREATE PROCEDURE sp_add_feedback(
    IN p_feedback_id VARCHAR(30),
    IN p_feedback_text VARCHAR(300),
    IN p_rating INT,
    IN p_series_id VARCHAR(10),
    IN p_account_id VARCHAR(30)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error adding feedback';
    END;
    
    START TRANSACTION;
    
    -- Validate rating
    IF p_rating < 1 OR p_rating > 5 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Rating must be between 1 and 5';
    END IF;
    
    -- Check for duplicate feedback
    IF EXISTS (
        SELECT 1 FROM RGC_FEEDBACK 
        WHERE SERIES_ID = p_series_id AND ACCOUNT_ID = p_account_id
    ) THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'You have already submitted feedback for this series';
    END IF;
    
    INSERT INTO RGC_FEEDBACK 
    (FEEDBACK_ID, FEEDBACK_TEXT, RATING, FEEDBACK_DATE, SERIES_ID, ACCOUNT_ID)
    VALUES 
    (p_feedback_id, p_feedback_text, p_rating, CURDATE(), p_series_id, p_account_id);
    
    COMMIT;
    SELECT 'Feedback added successfully' AS message;
END$$

-- ============================================================================
-- 4. STORED PROCEDURE: Update Episode Viewers (Concurrency Safe)
-- ============================================================================
DROP PROCEDURE IF EXISTS sp_update_episode_viewers$$
CREATE PROCEDURE sp_update_episode_viewers(
    IN p_episode_id VARCHAR(10),
    IN p_viewer_increment INT
)
BEGIN
    DECLARE v_current_viewers INT;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error updating viewers';
    END;
    
    START TRANSACTION;
    
    -- Lock row for update (prevents concurrent modification)
    SELECT TOTAL_VIEWERS INTO v_current_viewers
    FROM RGC_EPISODE
    WHERE EPISODE_ID = p_episode_id
    FOR UPDATE; --concurrecny example 3
    
    -- Update with incremented value
    UPDATE RGC_EPISODE 
    SET TOTAL_VIEWERS = TOTAL_VIEWERS + p_viewer_increment
    WHERE EPISODE_ID = p_episode_id;
    
    COMMIT;
    SELECT TOTAL_VIEWERS FROM RGC_EPISODE WHERE EPISODE_ID = p_episode_id;
END$$

-- ============================================================================
-- 5. FUNCTION: Calculate Average Rating for Series
-- ============================================================================
DROP FUNCTION IF EXISTS fn_get_series_avg_rating$$
CREATE FUNCTION fn_get_series_avg_rating(p_series_id VARCHAR(10))
RETURNS DECIMAL(3,2)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE v_avg_rating DECIMAL(3,2);
    
    SELECT AVG(RATING) INTO v_avg_rating
    FROM RGC_FEEDBACK
    WHERE SERIES_ID = p_series_id;
    
    RETURN IFNULL(v_avg_rating, 0);
END$$

-- ============================================================================
-- 6. FUNCTION: Get Total Viewers for Series
-- ============================================================================
DROP FUNCTION IF EXISTS fn_get_series_total_viewers$$
CREATE FUNCTION fn_get_series_total_viewers(p_series_id VARCHAR(10))
RETURNS BIGINT
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE v_total_viewers BIGINT;
    
    SELECT SUM(TOTAL_VIEWERS) INTO v_total_viewers
    FROM RGC_EPISODE
    WHERE SERIES_ID = p_series_id;
    
    RETURN IFNULL(v_total_viewers, 0);
END$$

-- ============================================================================
-- 7. STORED PROCEDURE: Add Episode with Schedule (Atomic Operation)
-- ============================================================================
DROP PROCEDURE IF EXISTS sp_add_episode_with_schedule$$
CREATE PROCEDURE sp_add_episode_with_schedule(
    IN p_episode_id VARCHAR(10),
    IN p_episode_title VARCHAR(50),
    IN p_series_id VARCHAR(10),
    IN p_schedule_id VARCHAR(10),
    IN p_start_ts DATETIME,
    IN p_end_ts DATETIME
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error adding episode and schedule';
    END;
    
    START TRANSACTION;
    
    -- Add episode
    INSERT INTO RGC_EPISODE 
    (EPISODE_ID, EPISODE_TITLE, TOTAL_VIEWERS, TECHNICAL_INTERRUPTION, SERIES_ID)
    VALUES 
    (p_episode_id, p_episode_title, 0, 'NO', p_series_id);
    
    -- Add schedule - CORRECTED COLUMN NAME
    INSERT INTO RGC_AIRING_SCHEDULE 
    (AIRING_SCHEDULE_ID, START_TS, END_TS, EPISODE_ID)
    VALUES 
    (p_schedule_id, p_start_ts, p_end_ts, p_episode_id);
    
    COMMIT;
    SELECT 'Episode and schedule added successfully' AS message;
END$$

-- ============================================================================
-- 8. STORED PROCEDURE: Get Comprehensive Series Statistics
-- ============================================================================
DROP PROCEDURE IF EXISTS sp_get_series_statistics$$
CREATE PROCEDURE sp_get_series_statistics(
    IN p_series_id VARCHAR(10)
)
BEGIN
    SELECT 
        ws.SERIES_NAME,
        ws.NUM_EPISODES,
        COUNT(DISTINCT e.EPISODE_ID) as episodes_created,
        AVG(f.RATING) as avg_rating,
        COUNT(DISTINCT f.FEEDBACK_ID) as total_reviews,
        SUM(e.TOTAL_VIEWERS) as total_viewers,
        ph.HOUSE_NAME as production_house
    FROM RGC_WEB_SERIES ws
    LEFT JOIN RGC_EPISODE e ON ws.SERIES_ID = e.SERIES_ID
    LEFT JOIN RGC_FEEDBACK f ON ws.SERIES_ID = f.SERIES_ID
    LEFT JOIN RGC_PRODUCTION_HOUSE ph ON ws.HOUSE_ID = ph.HOUSE_ID
    WHERE ws.SERIES_ID = p_series_id
    GROUP BY ws.SERIES_ID;
END$$

-- ============================================================================
-- 9. STORED PROCEDURE: Advanced Series Search with Multiple Filters
-- ============================================================================
DROP PROCEDURE IF EXISTS sp_search_series$$
CREATE PROCEDURE sp_search_series(
    IN p_search_term VARCHAR(50),
    IN p_genre VARCHAR(30),
    IN p_min_rating DECIMAL(3,2),
    IN p_country VARCHAR(30)
)
BEGIN
    SELECT DISTINCT
        ws.SERIES_ID,
        ws.SERIES_NAME,
        ws.NUM_EPISODES,
        ws.RELEASE_DATE,
        ws.LANGUAGE,
        ws.COUNTRY_OF_ORIGIN,
        ph.HOUSE_NAME,
        AVG(f.RATING) as avg_rating,
        COUNT(DISTINCT f.FEEDBACK_ID) as review_count,
        GROUP_CONCAT(DISTINCT st.SERIES_TYPE_NAME) as genres
    FROM RGC_WEB_SERIES ws
    JOIN RGC_PRODUCTION_HOUSE ph ON ws.HOUSE_ID = ph.HOUSE_ID
    LEFT JOIN RGC_WEB_SERIES_SERIES_TYPE wst ON ws.SERIES_ID = wst.SERIES_ID
    LEFT JOIN RGC_SERIES_TYPE st ON wst.SERIES_TYPE_ID = st.SERIES_TYPE_ID
    LEFT JOIN RGC_FEEDBACK f ON ws.SERIES_ID = f.SERIES_ID
    WHERE 
        (p_search_term IS NULL OR ws.SERIES_NAME LIKE CONCAT('%', p_search_term, '%'))
        AND (p_genre IS NULL OR st.SERIES_TYPE_NAME = p_genre)
        AND (p_country IS NULL OR ws.COUNTRY_OF_ORIGIN = p_country)
    GROUP BY ws.SERIES_ID, ws.SERIES_NAME, ws.NUM_EPISODES, 
             ws.RELEASE_DATE, ws.LANGUAGE, ws.COUNTRY_OF_ORIGIN, ph.HOUSE_NAME
    HAVING (p_min_rating IS NULL OR avg_rating >= p_min_rating)
    ORDER BY avg_rating DESC, review_count DESC;
END$$

-- ============================================================================
-- 10. STORED PROCEDURE: Update Viewer Subscription (With Audit)
-- ============================================================================
DROP PROCEDURE IF EXISTS sp_update_viewer_subscription$$
CREATE PROCEDURE sp_update_viewer_subscription(
    IN p_account_id VARCHAR(30),
    IN p_new_charge DECIMAL(6,2)
)
BEGIN
    DECLARE v_old_charge DECIMAL(6,2);
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error updating subscription';
    END;
    
    START TRANSACTION;
    
    -- Get old value
    SELECT MONTHLY_CHARGE INTO v_old_charge
    FROM RGC_VIEWER
    WHERE ACCOUNT_ID = p_account_id;
    
    -- Update
    UPDATE RGC_VIEWER 
    SET MONTHLY_CHARGE = p_new_charge
    WHERE ACCOUNT_ID = p_account_id;
    
    COMMIT;
    SELECT CONCAT('Subscription updated from ', v_old_charge, ' to ', p_new_charge) AS message;
END$$

-- ============================================================================
-- 11. STORED PROCEDURE: Get Contract Analytics
-- ============================================================================
DROP PROCEDURE IF EXISTS sp_get_contract_analytics$$
CREATE PROCEDURE sp_get_contract_analytics(
    IN p_house_id VARCHAR(10)
)
BEGIN
    SELECT 
        COUNT(*) as total_contracts,
        SUM(CASE WHEN END_DATE > CURDATE() THEN 1 ELSE 0 END) as active_contracts,
        SUM(CASE WHEN END_DATE <= CURDATE() THEN 1 ELSE 0 END) as expired_contracts,
        SUM(EPISODE_RATE) as total_value,
        AVG(EPISODE_RATE) as avg_episode_rate,
        MIN(CONTRACT_DATE) as oldest_contract,
        MAX(END_DATE) as latest_end_date
    FROM RGC_CONTRACT c
    JOIN RGC_WEB_SERIES ws ON c.SERIES_ID = ws.SERIES_ID
    WHERE p_house_id IS NULL OR ws.HOUSE_ID = p_house_id;
END$$

-- ============================================================================
-- 12. STORED PROCEDURE: Get Producer Production House Association
-- ============================================================================
DROP PROCEDURE IF EXISTS sp_get_producer_houses$$
CREATE PROCEDURE sp_get_producer_houses(
    IN p_producer_id VARCHAR(10)
)
BEGIN
    SELECT 
        p.PRODUCER_ID,
        CONCAT(p.P_FNAME, ' ', IFNULL(p.P_LNAME, '')) as producer_name,
        ph.HOUSE_ID,
        ph.HOUSE_NAME,
        pph.ASSOCIATION_DATE,
        pph.END_DATE,
        CASE 
            WHEN pph.END_DATE > CURDATE() THEN 'ACTIVE'
            ELSE 'EXPIRED'
        END as status
    FROM RGC_PRODUCER p
    JOIN RGC_PRODUCER_PRODUCTION_HOUSE pph ON p.PRODUCER_ID = pph.PRODUCER_ID
    JOIN RGC_PRODUCTION_HOUSE ph ON pph.HOUSE_ID = ph.HOUSE_ID
    WHERE p_producer_id IS NULL OR p.PRODUCER_ID = p_producer_id
    ORDER BY pph.ASSOCIATION_DATE DESC;
END$$

DELIMITER ;

-- ============================================================================
-- PERFORMANCE INDEXES (Database Optimization)
-- ============================================================================

-- Index for series name searches (most common query)
CREATE INDEX idx_series_name ON RGC_WEB_SERIES(SERIES_NAME);

-- Index for feedback queries by series and rating
CREATE INDEX idx_feedback_series_rating ON RGC_FEEDBACK(SERIES_ID, RATING);

-- Index for viewer country lookups
CREATE INDEX idx_viewer_country ON RGC_VIEWER(COUNTRY_CODE);

-- Composite index for episode queries
CREATE INDEX idx_episode_series_viewers ON RGC_EPISODE(SERIES_ID, TOTAL_VIEWERS);

-- Index for contract queries - CORRECTED TABLE NAME
CREATE INDEX idx_contract_series ON RGC_CONTRACT(SERIES_ID);

-- Index for episode schedules
CREATE INDEX idx_schedule_episode ON RGC_AIRING_SCHEDULE(EPISODE_ID);

-- Index for producer lookups
CREATE INDEX idx_producer_email ON RGC_PRODUCER(P_EMAIL);

-- Index for production house lookups
CREATE INDEX idx_house_name ON RGC_PRODUCTION_HOUSE(HOUSE_NAME);

-- ============================================================================
-- AUDIT TABLE (Security & History Tracking)
-- ============================================================================

CREATE TABLE IF NOT EXISTS RGC_AUDIT_LOG (
    LOG_ID INT AUTO_INCREMENT PRIMARY KEY,
    TABLE_NAME VARCHAR(50) NOT NULL,
    OPERATION_TYPE ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    RECORD_ID VARCHAR(50),
    OLD_VALUES TEXT,
    NEW_VALUES TEXT,
    CHANGED_BY VARCHAR(50),
    CHANGE_TIMESTAMP TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_table_timestamp (TABLE_NAME, CHANGE_TIMESTAMP),
    INDEX idx_operation (OPERATION_TYPE)
);

-- ============================================================================
-- TRIGGERS FOR AUDIT LOGGING
-- ============================================================================

DELIMITER $$

-- Trigger: Log series updates
DROP TRIGGER IF EXISTS trg_series_after_update$$
CREATE TRIGGER trg_series_after_update
AFTER UPDATE ON RGC_WEB_SERIES
FOR EACH ROW
BEGIN
    INSERT INTO RGC_AUDIT_LOG 
    (TABLE_NAME, OPERATION_TYPE, RECORD_ID, OLD_VALUES, NEW_VALUES)
    VALUES 
    ('RGC_WEB_SERIES', 'UPDATE', NEW.SERIES_ID,
     CONCAT('Episodes: ', OLD.NUM_EPISODES, ', Name: ', OLD.SERIES_NAME),
     CONCAT('Episodes: ', NEW.NUM_EPISODES, ', Name: ', NEW.SERIES_NAME));
END$$

-- Trigger: Log series deletions
DROP TRIGGER IF EXISTS trg_series_after_delete$$
CREATE TRIGGER trg_series_after_delete
AFTER DELETE ON RGC_WEB_SERIES
FOR EACH ROW
BEGIN
    INSERT INTO RGC_AUDIT_LOG 
    (TABLE_NAME, OPERATION_TYPE, RECORD_ID, OLD_VALUES)
    VALUES 
    ('RGC_WEB_SERIES', 'DELETE', OLD.SERIES_ID,
     CONCAT('Deleted: ', OLD.SERIES_NAME, ' (', OLD.NUM_EPISODES, ' episodes)'));
END$$

-- Trigger: Log feedback submissions
DROP TRIGGER IF EXISTS trg_feedback_after_insert$$
CREATE TRIGGER trg_feedback_after_insert
AFTER INSERT ON RGC_FEEDBACK
FOR EACH ROW
BEGIN
    INSERT INTO RGC_AUDIT_LOG 
    (TABLE_NAME, OPERATION_TYPE, RECORD_ID, NEW_VALUES)
    VALUES 
    ('RGC_FEEDBACK', 'INSERT', NEW.FEEDBACK_ID,
     CONCAT('Series: ', NEW.SERIES_ID, ', Rating: ', NEW.RATING, 
            ', Account: ', NEW.ACCOUNT_ID));
END$$

-- Trigger: Log contract changes - CORRECTED TABLE NAME
DROP TRIGGER IF EXISTS trg_contract_after_update$$
CREATE TRIGGER trg_contract_after_update
AFTER UPDATE ON RGC_CONTRACT
FOR EACH ROW
BEGIN
    INSERT INTO RGC_AUDIT_LOG 
    (TABLE_NAME, OPERATION_TYPE, RECORD_ID, OLD_VALUES, NEW_VALUES)
    VALUES 
    ('RGC_CONTRACT', 'UPDATE', NEW.CONTRACT_ID,
     CONCAT('Rate: ', OLD.EPISODE_RATE, ', End: ', OLD.END_DATE),
     CONCAT('Rate: ', NEW.EPISODE_RATE, ', End: ', NEW.END_DATE));
END$$

DELIMITER ;

-- ============================================================================
-- VIEWS FOR COMMON QUERIES (Performance Optimization)
-- ============================================================================

-- View: Series with full details
CREATE OR REPLACE VIEW vw_series_full_details AS
SELECT 
    ws.SERIES_ID,
    ws.SERIES_NAME,
    ws.NUM_EPISODES,
    ws.RELEASE_DATE,
    ws.COUNTRY_OF_ORIGIN,
    ws.LANGUAGE,
    ph.HOUSE_NAME,
    ph.ADDRESS_CITY as production_city,
    COUNT(DISTINCT e.EPISODE_ID) as episodes_created,
    SUM(e.TOTAL_VIEWERS) as total_viewers,
    AVG(f.RATING) as avg_rating,
    COUNT(DISTINCT f.FEEDBACK_ID) as review_count,
    GROUP_CONCAT(DISTINCT st.SERIES_TYPE_NAME) as genres
FROM RGC_WEB_SERIES ws
JOIN RGC_PRODUCTION_HOUSE ph ON ws.HOUSE_ID = ph.HOUSE_ID
LEFT JOIN RGC_EPISODE e ON ws.SERIES_ID = e.SERIES_ID
LEFT JOIN RGC_FEEDBACK f ON ws.SERIES_ID = f.SERIES_ID
LEFT JOIN RGC_WEB_SERIES_SERIES_TYPE wst ON ws.SERIES_ID = wst.SERIES_ID
LEFT JOIN RGC_SERIES_TYPE st ON wst.SERIES_TYPE_ID = st.SERIES_TYPE_ID
GROUP BY ws.SERIES_ID;

-- View: Top rated series
CREATE OR REPLACE VIEW vw_top_rated_series AS
SELECT 
    ws.SERIES_ID,
    ws.SERIES_NAME,
    AVG(f.RATING) as avg_rating,
    COUNT(f.FEEDBACK_ID) as review_count
FROM RGC_WEB_SERIES ws
LEFT JOIN RGC_FEEDBACK f ON ws.SERIES_ID = f.SERIES_ID
GROUP BY ws.SERIES_ID, ws.SERIES_NAME
HAVING review_count > 0
ORDER BY avg_rating DESC, review_count DESC;

-- View: Active contracts - CORRECTED TABLE NAME
CREATE OR REPLACE VIEW vw_active_contracts AS
SELECT 
    c.CONTRACT_ID,
    ws.SERIES_NAME,
    ph.HOUSE_NAME,
    c.CONTRACT_DATE,
    c.END_DATE,
    c.EPISODE_RATE,
    DATEDIFF(c.END_DATE, CURDATE()) as days_remaining
FROM RGC_CONTRACT c
JOIN RGC_WEB_SERIES ws ON c.SERIES_ID = ws.SERIES_ID
JOIN RGC_PRODUCTION_HOUSE ph ON ws.HOUSE_ID = ph.HOUSE_ID
WHERE c.END_DATE > CURDATE()
ORDER BY c.END_DATE;

-- ============================================================================
-- TEST EXAMPLES
-- ============================================================================

-- Test stored procedures:
-- CALL sp_get_series_statistics('S001');
-- CALL sp_search_series('Stranger', NULL, NULL, NULL);
-- CALL sp_get_contract_analytics(NULL);
-- CALL sp_get_producer_houses('P001');

-- Test functions:
-- SELECT fn_get_series_avg_rating('S001');
-- SELECT fn_get_series_total_viewers('S001');

-- Test views:
-- SELECT * FROM vw_series_full_details;
-- SELECT * FROM vw_top_rated_series LIMIT 10;
-- SELECT * FROM vw_active_contracts;

SELECT 'All stored procedures, functions, triggers, indexes, and views created successfully!' as Status;