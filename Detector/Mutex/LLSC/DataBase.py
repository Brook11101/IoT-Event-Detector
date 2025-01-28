import random
from time import sleep, time

import mysql.connector
import json
from mysql.connector import Error
import StatusMapping
from datetime import datetime

from Detector.Mutex.LLSC import RuleSet


# 连接到 MySQL 数据库
def connect_to_mysql():
    try:
        connection = mysql.connector.connect(
            host="114.55.74.144",
            user="root",
            password="Root123456.",
            database="rule_db",
            autocommit=True
        )
        return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None


# 创建数据库
def create_database():
    try:
        connection = mysql.connector.connect(
            host="114.55.74.144",
            user="root",
            password="Root123456."
        )
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS rule_db")
        cursor.execute("USE rule_db")  # 使用数据库
        connection.close()
    except Error as e:
        print(f"Error while creating database: {e}")


def create_table():
    try:
        connection = connect_to_mysql()
        if connection is not None:
            cursor = connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rule_execution_log (
                    logid INT AUTO_INCREMENT PRIMARY KEY,
                    ruleid INT,
                    trigger_device JSON,
                    condition_device JSON,
                    action_device JSON,
                    description TEXT,
                    lock_device JSON,
                    timestamp BIGINT,
                    status BOOLEAN,  -- 表示规则是否成功执行
                    INDEX idx_timestamp_status (timestamp, status),  -- 为 timestamp 和 status 添加联合索引
                    INDEX idx_ruleid (ruleid)        -- 为 ruleid 添加单独索引
                )
            """)
            connection.close()
    except Error as e:
        print(f"Error while creating table: {e}")


def clear_table():
    """
    清空 rule_execution_log 表中的所有内容。
    """
    try:
        # 连接到数据库
        connection = mysql.connector.connect(
            host="114.55.74.144",
            user="root",
            password="Root123456.",
            database="rule_db"
        )
        cursor = connection.cursor()

        # 清空表内容
        cursor.execute("TRUNCATE TABLE rule_execution_log")

        print("Table rule_execution_log has been cleared successfully.")

    except Error as e:
        print(f"Error while clearing table: {e}")

    finally:
        # 关闭连接
        if connection.is_connected():
            connection.close()


# 以LLSC的方式插入规则执行日志
def insert_log(ruleid, trigger_device, condition_device, action_device, description, lock_device, timestamp, start_time):
    """
    插入规则执行日志，禁用事务并使用 READ UNCOMMITTED 隔离级别。
    """
    # 获取数据库连接
    connection = connect_to_mysql()
    cursor = connection.cursor()

    try:
        # 将设备名称列表转换为 JSON 格式的字符串
        trigger_device_json = json.dumps(trigger_device)
        condition_device_json = json.dumps(condition_device)
        action_device_json = json.dumps(action_device)
        lock_device_json = json.dumps(lock_device)

        # 获取当前规则的冲突规则ID集合
        conflict_rule_ids = StatusMapping.rule_conflict_map.get(ruleid, set())

        # 设置当前会话的事务隔离级别为 READ UNCOMMITTED
        cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED")

        # 冲突检测
        current_timestamp = int(datetime.now().timestamp())
        if conflict_rule_ids:
            # 构建冲突规则ID的查询，检查是否有冲突规则在传入时间戳后执行且 status 为 TRUE
            conflict_rule_ids_placeholder = ','.join([str(rid) for rid in conflict_rule_ids])
            cursor.execute(f"""
                SELECT 1 FROM rule_execution_log
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

            # 插入当前记录
            cursor.execute("""
                INSERT INTO rule_execution_log (ruleid, trigger_device, condition_device, action_device, description, lock_device, timestamp, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                ruleid, trigger_device_json, condition_device_json, action_device_json, description,
                lock_device_json, current_timestamp, status
            ))
        else:
            print(f"{ruleid} no conflict")
            # 如果没有冲突规则，直接插入记录
            cursor.execute("""
                INSERT INTO rule_execution_log (ruleid, trigger_device, condition_device, action_device, description, lock_device, timestamp, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                ruleid, trigger_device_json, condition_device_json, action_device_json, description,
                lock_device_json, current_timestamp, True
            ))

        # 计算并返回执行时间
        exec_time = current_timestamp - start_time

    except Exception as e:
        print(f"Error during log insertion for rule {ruleid}: {e}")
        exec_time = 0  # 标记为失败的执行时间

    finally:
        # 关闭数据库连接
        connection.close()

    return exec_time  # 返回执行时间
