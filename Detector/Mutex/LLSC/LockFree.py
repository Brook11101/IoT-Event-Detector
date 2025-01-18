import threading
from datetime import datetime
from turtledemo.penrose import start

import RuleSet
from DataBase import insert_log  # 假设插入函数在 DataBase 模块里


def execute_rule(rule, start_timestamp):
    """
    执行单条规则，将数据插入数据库
    """

    # 获取规则的各项数据
    ruleid = rule["RuleId"]
    trigger_device = rule["Trigger"]
    condition_device = rule["Condition"]
    action_device = rule["Action"]
    description = rule["description"]
    lock_device = rule["Lock"]

    # 调用 insert_log 函数将数据插入数据库
    insert_log(ruleid, trigger_device, condition_device, action_device, description, lock_device, start_timestamp)


def execute_all_rules_concurrently():
    """
    并发执行所有规则
    """
    # 获取所有规则
    rules = RuleSet.get_all_rules()

    # 创建线程列表
    threads = []

    # 为每个线程生成一个新的 timestamp
    start_timestamp = int(datetime.now().timestamp())  # 获取当前 Unix 时间戳（秒）

    # 为每条规则创建一个线程
    for rule in rules:
        thread = threading.Thread(target=execute_rule, args=(rule, start_timestamp))
        threads.append(thread)
        thread.start()

    # 等待所有线程执行完毕
    for thread in threads:
        thread.join()


# 执行所有规则并发任务
execute_all_rules_concurrently()
