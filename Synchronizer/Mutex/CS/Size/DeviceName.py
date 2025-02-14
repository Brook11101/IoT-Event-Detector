import json
import random
import threading
import time
from time import sleep
import redis
from RuleSet import get_all_rules, DeviceName

# 统计以Device Name（Unique Device），作为临界区的粒度。按照section所需总数，不放回抽样划分出规则组。
# 统计所有规则在临界区上等待的总时间后，平均到在每个临界区上等待的时间。（这里我没有用规则的数量做除数，而是用临界区的去重个数做除数）


class RedisMutexLock:
    """Redis 分布式可重入锁"""

    def __init__(self, client, lock_name):
        self.client = client
        self.lock_name = lock_name

    def acquire(self):
        """获取锁，持续重试直到成功"""
        while True:
            if self.client.set(self.lock_name, "locked", nx=True):
                print(f"Thread {threading.get_ident()} acquired lock: {self.lock_name}")
                return True

    def release(self):
        """释放锁"""
        self.client.delete(self.lock_name)
        print(f"Thread {threading.get_ident()} released lock: {self.lock_name}")


def init_lock():


    """初始化 Redis 互斥锁"""

    client = redis.StrictRedis(host="114.55.74.144", port=6379, password='whd123456', decode_responses=True)
    client.flushall()
    print("Redis 已清空")
    return {device_name: RedisMutexLock(client, device_name) for device_name in DeviceName}


def apply_lock(rule, device_name_lock_dict, time_list):
    """
    按顺序申请锁 -> 记录等待时间 -> 执行规则 -> 释放锁
    """
    locks_to_acquire = sorted(rule["DeviceName"])
    start_time = time.time()
    acquired_locks = []

    try:
        for lock_name in locks_to_acquire:
            device_name_lock_dict[lock_name].acquire()
            acquired_locks.append(lock_name)

        elapsed_time = time.time() - start_time
        time_list.append(elapsed_time)
        print(f"Rule: {rule['description']} acquired all locks in {elapsed_time:.6f} seconds.")

        sleep(random.uniform(1, 2))  # 模拟执行规则占用时间

    finally:
        for lock_name in acquired_locks:
            device_name_lock_dict[lock_name].release()


def add_lock_count_to_rules(rules):
    """为每条规则添加独立临界区锁的数量"""
    for rule in rules:
        rule["lock_count"] = len(set(rule["DeviceName"]))
    return rules


def group_rules_by_section_count(rules, section_targets):
    """
    按临界区数量目标对规则分组
    采用不放回抽样，保证每组的锁数量尽可能接近目标值
    """
    grouped_rules = []
    remaining_rules = rules.copy()
    previous_group = []

    for target in section_targets:
        current_group = previous_group.copy()
        total_locks = sum(len(rule["DeviceName"]) for rule in current_group)

        while total_locks < target and remaining_rules:
            rule = random.choice(remaining_rules)
            current_group.append(rule)
            total_locks += len(rule["DeviceName"])
            remaining_rules.remove(rule)

        grouped_rules.append(current_group)
        previous_group = current_group

    return grouped_rules


def execute_rules_for_groups(rule_groups, rounds, base_output_dir):
    """
    执行规则组，并统计平均等待时间
    """
    device_name_lock_dict = init_lock()

    for group_idx, rules in enumerate(rule_groups):
        unique_locks = {lock for rule in rules for lock in rule["DeviceName"]}
        unique_locks_len = len(unique_locks)
        output_file = f"{base_output_dir}/device_name_lock_groups_{section_targets[group_idx]}.txt"

        with open(output_file, "w") as file:
            for round_num in range(1, rounds + 1):
                time_list = []
                threads = [threading.Thread(target=apply_lock, args=(rule, device_name_lock_dict, time_list)) for rule in rules]

                for thread in threads:
                    thread.start()
                for thread in threads:
                    thread.join()

                avg_time_section = sum(time_list) / unique_locks_len if unique_locks_len else 0
                avg_time_rules = sum(time_list) / len(rules)

                file.write(f"{avg_time_rules:.6f}\n")
                print(f"Group {group_idx + 1} - Size {len(rules)} - Round {round_num} completed. "
                      f"基于临界区元素个数的平均时间: {avg_time_section:.6f} seconds.")
                print(f"Group {group_idx + 1} - Size {len(rules)} - Round {round_num} completed. "
                      f"基于规则总数的平均时间: {avg_time_rules:.6f} seconds.")


if __name__ == "__main__":
    labeled_rules = add_lock_count_to_rules(get_all_rules())
    section_targets = [10, 20, 30, 40, 50]
    rule_groups = group_rules_by_section_count(labeled_rules, section_targets)
    rounds = 10
    output_base_dir = r"E:\研究生信息收集\论文材料\IoT-Event-Detector\Synchronizer\Mutex\CS\Size\Data\DeviceName"

    execute_rules_for_groups(rule_groups, rounds, output_base_dir)
