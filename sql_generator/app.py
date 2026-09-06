"""存过造数工具后端"""
from flask import Flask, render_template, jsonify, request


app = Flask(__name__)


# ========== MySQL 存过造数示例 ==========
MYSQL_PROCEDURE = r"""-- =============================================
-- MySQL 存储过程造数示例
-- 造数场景：用户表、订单表、日志表
-- =============================================

-- 1. 创建用户表
CREATE TABLE IF NOT EXISTS t_user (
    id          BIGINT PRIMARY KEY AUTO_INCREMENT,
    username    VARCHAR(50) NOT NULL,
    password    VARCHAR(100) NOT NULL,
    phone       VARCHAR(20),
    email       VARCHAR(100),
    age         INT,
    gender      TINYINT COMMENT '0-女 1-男',
    address     VARCHAR(200),
    status      TINYINT DEFAULT 1 COMMENT '0-禁用 1-启用',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_phone (phone),
    INDEX idx_create_time (create_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. 创建订单表
CREATE TABLE IF NOT EXISTS t_order (
    id          BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_no    VARCHAR(32) NOT NULL UNIQUE,
    user_id     BIGINT NOT NULL,
    product_name VARCHAR(100),
    quantity    INT,
    amount      DECIMAL(12, 2),
    status      TINYINT DEFAULT 0 COMMENT '0-待支付 1-已支付 2-已发货 3-已完成 4-已取消',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================
-- 存储过程：批量造用户数据
-- =============================================
DELIMITER $$
CREATE PROCEDURE sp_gen_user(IN p_count INT)
BEGIN
    DECLARE v_i INT DEFAULT 0;
    DECLARE v_username VARCHAR(50);
    DECLARE v_password VARCHAR(100);
    DECLARE v_phone VARCHAR(20);
    DECLARE v_email VARCHAR(100);
    DECLARE v_age INT;
    DECLARE v_gender TINYINT;
    DECLARE v_address VARCHAR(200);

    WHILE v_i < p_count DO
        SET v_username = CONCAT('user_', LPAD(v_i + 1, 6, '0'));
        SET v_password = MD5(CONCAT('pwd_', v_i));
        SET v_phone = CONCAT('1', ELT(1 + FLOOR(RAND() * 9), '3', '5', '7', '8', '9'),
            LPAD(FLOOR(RAND() * 10000000000) MOD 10000000000, 9, '0'));
        SET v_email = CONCAT('user', v_i, '@test.com');
        SET v_age = 18 + FLOOR(RAND() * 50);
        SET v_gender = FLOOR(RAND() * 2);
        SET v_address = CONCAT('北京市朝阳区XX路', FLOOR(RAND() * 999), '号');

        INSERT INTO t_user (username, password, phone, email, age, gender, address)
        VALUES (v_username, v_password, v_phone, v_email, v_age, v_gender, v_address);

        SET v_i = v_i + 1;
    END WHILE;
    SELECT CONCAT('成功造数 ', p_count, ' 条用户数据') AS result;
END$$
DELIMITER ;

-- 调用：CALL sp_gen_user(10000);

-- =============================================
-- 存储过程：批量造订单数据（关联用户）
-- =============================================
DELIMITER $$
CREATE PROCEDURE sp_gen_order(IN p_count INT)
BEGIN
    DECLARE v_i INT DEFAULT 0;
    DECLARE v_order_no VARCHAR(32);
    DECLARE v_user_id BIGINT;
    DECLARE v_product VARCHAR(100);
    DECLARE v_qty INT;
    DECLARE v_amount DECIMAL(12, 2);
    DECLARE v_status TINYINT;

    WHILE v_i < p_count DO
        SET v_order_no = CONCAT('ORD', DATE_FORMAT(NOW(), '%Y%m%d%H%i%s'), LPAD(v_i + 1, 6, '0'));
        SET v_user_id = FLOOR(RAND() * (SELECT MAX(id) FROM t_user)) + 1;
        SET v_product = ELT(1 + FLOOR(RAND() * 5), '手机', '电脑', '耳机', '鼠标', '键盘');
        SET v_qty = 1 + FLOOR(RAND() * 10);
        SET v_amount = ROUND(v_qty * (100 + RAND() * 900), 2);
        SET v_status = FLOOR(RAND() * 5);

        INSERT INTO t_order (order_no, user_id, product_name, quantity, amount, status)
        VALUES (v_order_no, v_user_id, v_product, v_qty, v_amount, v_status);

        SET v_i = v_i + 1;
    END WHILE;
    SELECT CONCAT('成功造数 ', p_count, ' 条订单数据') AS result;
END$$
DELIMITER ;

-- 调用：CALL sp_gen_order(50000);
"""


# ========== Oracle 存过造数示例 ==========
ORACLE_PROCEDURE = r"""-- =============================================
-- Oracle 存储过程造数示例
-- =============================================

-- 1. 创建用户表
CREATE TABLE t_user (
    id          NUMBER(20) PRIMARY KEY,
    username    VARCHAR2(50) NOT NULL,
    password    VARCHAR2(100) NOT NULL,
    phone       VARCHAR2(20),
    email       VARCHAR2(100),
    age         NUMBER(3),
    gender      NUMBER(1),
    address     VARCHAR2(200),
    status      NUMBER(1) DEFAULT 1,
    create_time DATE DEFAULT SYSDATE
);

-- 创建序列
CREATE SEQUENCE seq_user START WITH 1 INCREMENT BY 1;

-- 2. 创建订单表
CREATE TABLE t_order (
    id          NUMBER(20) PRIMARY KEY,
    order_no    VARCHAR2(32) UNIQUE,
    user_id     NUMBER(20) NOT NULL,
    product_name VARCHAR2(100),
    quantity    NUMBER(10),
    amount      NUMBER(12, 2),
    status      NUMBER(1) DEFAULT 0,
    create_time DATE DEFAULT SYSDATE
);

CREATE SEQUENCE seq_order START WITH 1 INCREMENT BY 1;

-- =============================================
-- 存储过程：批量造用户数据（FORALL 批量插入）
-- =============================================
CREATE OR REPLACE PROCEDURE sp_gen_user(p_count IN NUMBER) IS
    TYPE t_user_list IS TABLE OF t_user%ROWTYPE INDEX BY BINARY_INTEGER;
    v_batch t_user_list;
    v_idx BINARY_INTEGER;
BEGIN
    DBMS_OUTPUT.ENABLE;

    FOR i IN 1..p_count LOOP
        v_idx := v_batch.COUNT + 1;
        v_batch(v_idx).id := seq_user.NEXTVAL;
        v_batch(v_idx).username := 'user_' || LPAD(i, 6, '0');
        v_batch(v_idx).password := RAWTOHEX(DBMS_CRYPTO.HASH(UTL_RAW.CAST_TO_RAW('pwd_' || i), 2));
        v_batch(v_idx).phone := '1' || SUBSTR('35789', TRUNC(DBMS_RANDOM.VALUE(1, 5)), 1) ||
            LPAD(TRUNC(DBMS_RANDOM.VALUE(0, 9999999999)), 10, '0');
        v_batch(v_idx).email := 'user' || i || '@test.com';
        v_batch(v_idx).age := TRUNC(DBMS_RANDOM.VALUE(18, 68));
        v_batch(v_idx).gender := TRUNC(DBMS_RANDOM.VALUE(0, 2));
        v_batch(v_idx).address := '北京市朝阳区XX路' || TRUNC(DBMS_RANDOM.VALUE(1, 999)) || '号';

        -- 每1000条批量提交一次
        IF v_idx = 1000 THEN
            FORALL j IN 1..v_batch.COUNT INSERT INTO t_user VALUES v_batch(j);
            COMMIT;
            v_batch.DELETE;
        END IF;
    END LOOP;

    -- 提交剩余数据
    IF v_batch.COUNT > 0 THEN
        FORALL j IN 1..v_batch.COUNT INSERT INTO t_user VALUES v_batch(j);
        COMMIT;
    END IF;

    DBMS_OUTPUT.PUT_LINE('成功造数 ' || p_count || ' 条用户数据');
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        DBMS_OUTPUT.PUT_LINE('造数失败: ' || SQLERRM);
END;
/

-- 调用：EXEC sp_gen_user(10000);

-- =============================================
-- 存储过程：随机日期造数
-- =============================================
CREATE OR REPLACE FUNCTION fn_random_date(
    p_start_date IN DATE,
    p_end_date   IN DATE
) RETURN DATE IS
BEGIN
    RETURN p_start_date + DBMS_RANDOM.VALUE(0, p_end_date - p_start_date);
END;
/

-- 使用示例：INSERT INTO t_log (log_time) VALUES (fn_random_date(DATE '2025-01-01', SYSDATE));
"""


# ========== GaussDB 存过造数示例 ==========
GAUSS_PROCEDURE = r"""-- =============================================
-- GaussDB (openGauss) 存储过程造数示例
-- GaussDB 兼容 PostgreSQL 语法
-- =============================================

-- 1. 创建用户表
CREATE TABLE IF NOT EXISTS t_user (
    id          BIGSERIAL PRIMARY KEY,
    username    VARCHAR(50) NOT NULL,
    password    VARCHAR(100) NOT NULL,
    phone       VARCHAR(20),
    email       VARCHAR(100),
    age         INTEGER,
    gender      SMALLINT,
    address     VARCHAR(200),
    status      SMALLINT DEFAULT 1,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 创建订单表
CREATE TABLE IF NOT EXISTS t_order (
    id          BIGSERIAL PRIMARY KEY,
    order_no    VARCHAR(32) NOT NULL UNIQUE,
    user_id     BIGINT NOT NULL,
    product_name VARCHAR(100),
    quantity    INTEGER,
    amount      NUMERIC(12, 2),
    status      SMALLINT DEFAULT 0,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- 存储过程：批量造用户数据（unnest 批量插入）
-- =============================================
CREATE OR REPLACE PROCEDURE sp_gen_user(p_count INTEGER)
LANGUAGE plpgsql
AS $$
DECLARE
    v_usernames TEXT[];
    v_passwords  TEXT[];
    v_phones     TEXT[];
    v_emails     TEXT[];
    v_ages       INTEGER[];
    v_genders    SMALLINT[];
    v_addresses  TEXT[];
    v_i          INTEGER;
    v_phone_prefix TEXT;
BEGIN
    -- 准备数组数据
    FOR v_i IN 1..p_count LOOP
        v_usernames := array_append(v_usernames, 'user_' || LPAD(v_i::TEXT, 6, '0'));
        v_passwords  := array_append(v_passwords, MD5('pwd_' || v_i::TEXT));
        v_phone_prefix := (ARRAY['3', '5', '7', '8', '9'])[1 + (RANDOM() * 4)::INTEGER];
        v_phones     := array_append(v_phones, '1' || v_phone_prefix || LPAD((RANDOM() * 9999999999)::BIGINT::TEXT, 9, '0'));
        v_emails     := array_append(v_emails, 'user' || v_i || '@test.com');
        v_ages       := array_append(v_ages, (18 + RANDOM() * 50)::INTEGER);
        v_genders    := array_append(v_genders, (RANDOM() * 2)::SMALLINT);
        v_addresses  := array_append(v_addresses, '北京市朝阳区XX路' || (RANDOM() * 999)::INTEGER || '号');
    END LOOP;

    -- 批量插入
    INSERT INTO t_user (username, password, phone, email, age, gender, address)
    SELECT * FROM UNNEST(v_usernames, v_passwords, v_phones, v_emails, v_ages, v_genders, v_addresses);

    RAISE NOTICE '成功造数 % 条用户数据', p_count;
END;
$$;

-- 调用：CALL sp_gen_user(10000);

-- =============================================
-- 存储过程：批量造订单数据
-- =============================================
CREATE OR REPLACE PROCEDURE sp_gen_order(p_count INTEGER)
LANGUAGE plpgsql
AS $$
DECLARE
    v_user_max_id BIGINT;
    v_product     TEXT;
    v_status_arr  SMALLINT[] := ARRAY[0, 1, 2, 3, 4];
BEGIN
    SELECT MAX(id) INTO v_user_max_id FROM t_user;
    IF v_user_max_id IS NULL THEN
        RAISE NOTICE '请先造用户数据';
        RETURN;
    END IF;

    FOR v_i IN 1..p_count LOOP
        v_product := (ARRAY['手机', '电脑', '耳机', '鼠标', '键盘'])[1 + (RANDOM() * 4)::INTEGER];
        INSERT INTO t_order (order_no, user_id, product_name, quantity, amount, status)
        VALUES (
            'ORD' || TO_CHAR(NOW(), 'YYYYMMDDHH24MISS') || LPAD(v_i::TEXT, 6, '0'),
            (RANDOM() * v_user_max_id)::BIGINT + 1,
            v_product,
            1 + (RANDOM() * 9)::INTEGER,
            ROUND((100 + RANDOM() * 900) * (1 + (RANDOM() * 9)::INTEGER), 2),
            v_status_arr[1 + (RANDOM() * 4)::INTEGER]
        );
        -- 每1000条提交一次
        IF v_i % 1000 = 0 THEN
            COMMIT;
        END IF;
    END LOOP;

    RAISE NOTICE '成功造数 % 条订单数据', p_count;
END;
$$;

-- 调用：CALL sp_gen_order(50000);
"""


EXAMPLES = {
    'mysql': MYSQL_PROCEDURE,
    'oracle': ORACLE_PROCEDURE,
    'gauss': GAUSS_PROCEDURE,
}


@app.route('/')
def index():
    """首页"""
    return render_template('index.html')


@app.route('/api/example', methods=['GET'])
def get_example():
    """获取造数示例"""
    db_type = request.args.get('type', 'mysql')
    return jsonify({'success': True, 'code': EXAMPLES.get(db_type, '')})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5004)
