import mysql.connector
import json
from mysql.connector import Error


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
                    timestamp TIMESTAMP,
                    status BOOLEAN,  -- 表示规则是否成功执行
                    INDEX idx_timestamp_status (timestamp, status),  -- 为 timestamp 和 status 添加联合索引
                    INDEX idx_ruleid (ruleid)        -- 为 ruleid 添加单独索引
                )
            """)
            connection.close()
    except Error as e:
        print(f"Error while creating table: {e}")



# 插入规则执行日志
def insert_log(ruleid, trigger_device, condition_device, action_device, description, lock_device, timestamp):
    connection = connect_to_mysql()
    cursor = connection.cursor()

    # 将设备名称列表转换为 JSON 格式的字符串
    trigger_device_json = json.dumps(trigger_device)
    condition_device_json = json.dumps(condition_device)
    action_device_json = json.dumps(action_device)
    lock_device_json = json.dumps(lock_device)

    cursor.execute("""
        INSERT INTO rule_execution_log (ruleid, trigger_device, condition_device, action_device, description, lock_device, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (ruleid, trigger_device_json, condition_device_json, action_device_json, description, lock_device_json, timestamp))

    connection.commit()
    connection.close()

create_table()
