from time import time

import mysql.connector
from mysql.connector import Error
import json

from Synchronizer.Mutex.LLSC import StatusMapping


# 连接到 MySQL 数据库
def connect_to_mysql():
    try:
        connection = mysql.connector.connect(
            host="114.55.74.144",
            user="root",
            password="Root123456.",
            database="rule_db",
            autocommit=True  # MyISAM 不需要事务，直接启用自动提交
        )
        return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None


# 创建数据库
def create_database():
    try:
        connection = connect_to_mysql()
        if connection is not None:
            cursor = connection.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS rule_db")
            cursor.execute("USE rule_db")
            connection.close()
    except Error as e:
        print(f"Error while creating database: {e}")


# 创建表并设置 MyISAM 引擎
def create_myisam_table():
    try:
        connection = connect_to_mysql()
        if connection is not None:
            cursor = connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rule_execution_log_myisam (
                    logid INT AUTO_INCREMENT PRIMARY KEY,
                    ruleid INT,
                    trigger_device JSON,
                    condition_device JSON,
                    action_device JSON,
                    description TEXT,
                    lock_device JSON,
                    timestamp BIGINT,
                    status BOOLEAN,
                    INDEX idx_timestamp_status (timestamp, status),
                    INDEX idx_ruleid (ruleid)
                ) ENGINE=MYISAM
            """)
            print("Table `rule_execution_log_myisam` created with MyISAM engine.")
            connection.close()
    except Error as e:
        print(f"Error while creating table: {e}")



# 插入规则日志（使用 MyISAM）
def insert_log(ruleid, trigger_device, condition_device, action_device, description, lock_device, timestamp, start_time):
    """
    插入规则执行日志，禁用事务并使用 READ UNCOMMITTED 隔离级别。
    """
    connection = connect_to_mysql()
    if not connection:
        return 0  # 无法连接时返回 0

    cursor = connection.cursor()

    try:
        # 将设备名称列表转换为 JSON 格式的字符串
        trigger_device_json = json.dumps(trigger_device)
        condition_device_json = json.dumps(condition_device)
        action_device_json = json.dumps(action_device)
        lock_device_json = json.dumps(lock_device)

        # 检查冲突规则
        current_timestamp = time()
        conflict_rule_ids = StatusMapping.rule_conflict_map.get(ruleid, set())

        if conflict_rule_ids:
            conflict_rule_ids_placeholder = ','.join(map(str, conflict_rule_ids))
            cursor.execute(f"""
                SELECT 1 FROM rule_execution_log_myisam
                WHERE ruleid IN ({conflict_rule_ids_placeholder})
                AND timestamp >= %s
                AND status = TRUE
                LIMIT 1
            """, (timestamp,))
            conflict_result = cursor.fetchone()

            if conflict_result:
                print(f"{ruleid} find conflict")
                status = False  # 如果有冲突，设置为 False
            else:
                print(f"{ruleid} don't find conflict")
                status = True  # 如果没有冲突，设置为 True

            # 插入记录
            cursor.execute("""
                INSERT INTO rule_execution_log_myisam (ruleid, trigger_device, condition_device, action_device, description, lock_device, timestamp, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                ruleid, trigger_device_json, condition_device_json, action_device_json, description,
                lock_device_json, current_timestamp, status
            ))
        else:
            print(f"{ruleid} no conflict")
            # 如果没有冲突，直接插入
            cursor.execute("""
                INSERT INTO rule_execution_log_myisam (ruleid, trigger_device, condition_device, action_device, description, lock_device, timestamp, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                ruleid, trigger_device_json, condition_device_json, action_device_json, description,
                lock_device_json, current_timestamp, True
            ))

        exec_time = current_timestamp - start_time
    except Exception as e:
        print(f"Error during log insertion for rule {ruleid}: {e}")
        exec_time = 0
    finally:
        connection.close()

    return exec_time


# 清空表内容
def clear_table():
    try:
        connection = connect_to_mysql()
        if connection:
            cursor = connection.cursor()
            cursor.execute("TRUNCATE TABLE rule_execution_log_myisam")
            print("Table `rule_execution_log_myisam` cleared successfully.")
            connection.close()
    except Error as e:
        print(f"Error while clearing table: {e}")


