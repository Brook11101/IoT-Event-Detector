import time
from time import sleep
import random
import redis
import threading
from ExecuteOrder import XiaomiCloudConnector
from RuleSet import get_all_rules
from RuleSet import Room

# 以房间为粒度的分配方式
# 规则数量太大，规则选取方式不合理
# room标签的分配方式也不合理



class RedisMutexLock:
    def __init__(self, client, lock_name):
        """
        初始化 Redis 可重入锁
        :param client: Redis 客户端连接对象
        :param lock_name: 锁的名称
        """
        self.client = client
        self.lock_name = lock_name

    def acquire(self):
        """
        获取锁，持续重试直到成功。
        """
        while True:
            if self.client.set(self.lock_name, "locked", nx=True):
                print(f"Thread {threading.get_ident()} acquired lock: {self.lock_name}")
                return True

    def release(self):
        """
        释放锁。
        """
        self.client.delete(self.lock_name)
        print(f"Thread {threading.get_ident()} released lock: {self.lock_name}")


def initLock():
    client = redis.StrictRedis(host="114.55.74.144", port=6379, password='whd123456', decode_responses=True)
    # 创建 Redis 可重入锁字典
    room_lock_dict = {}
    # 遍历 Home 数组，为每个元素创建一个锁，并存储到字典中
    for room_name in Room:
        room_lock_dict[room_name] = RedisMutexLock(client, room_name)
    return room_lock_dict


# 模拟规则执行的线程函数
def apply_lock(connector, rule, room_lock_dict, time_differences):
    # Step 1: 获取需要申请的锁并排序
    locks_to_acquire = sorted(rule["Room"])  # 确保按字典序排序

    # Step 2: 开始计时
    start_time = time.time()

    # Step 3: 按顺序申请所有锁
    acquired_locks = []
    try:
        for lock_name in locks_to_acquire:
            room_lock_dict[lock_name].acquire()
            acquired_locks.append(lock_name)  # 记录已成功获取的锁

        # Step 4: 记录成功获取锁的时间
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Rule:  {rule['description']}    acquired all locks in {elapsed_time:.6f} seconds.")
        time_differences.append(elapsed_time)

        # 真实执行规则
        # value = str(random.randint(0, 100))
        # print(value)
        # response = connector.create_order("cn", value)
        # while True:
        #     status = connector.query_status("cn")
        #     print(status)
        #     status_dict = json.loads(status.decode('utf-8'))
        #     brightness = status_dict['result'][0]['value']
        #     if str(brightness) == str(value):  # 如果状态与发送的 value 一致
        #         print(f"Rule:  {rule['description']}   execute over.")
        #         break

        # 模拟执行规则占用时间
        sleep(random.uniform(1.5, 2.0))

    finally:
        # Step 5: 释放所有已获取的锁
        for lock_name in acquired_locks:
            room_lock_dict[lock_name].release()


def add_lock_count_to_rules(rules):
    for rule in rules:
        unique_locks = set(rule["Room"])
        rule["lock_count"] = len(unique_locks)
    return rules


def group_rules_by_lock_count(rules, lock_targets):
    """
    按锁数量目标对规则分组，统计锁的总数量，采用不放回抽样的方式增选规则。

    :param rules: 带有锁数量标签的规则列表
    :param lock_targets: 每组目标锁数量列表
    :return: 分组后的规则列表
    """
    grouped_rules = []
    remaining_rules = rules.copy()  # 剩余规则，不放回抽样

    previous_group = []  # 上一组的规则集合
    for target in lock_targets:
        current_group = previous_group.copy()  # 基于上一组的规则
        total_locks = sum(len(rule["Room"]) for rule in current_group)  # 初始化总锁数量

        while total_locks < target and remaining_rules:
            # 随机选择一个规则
            rule = random.choice(remaining_rules)
            current_group.append(rule)
            total_locks += len(rule["Room"])  # 累加锁数量

            # 从剩余规则中移除
            remaining_rules.remove(rule)

        grouped_rules.append(current_group)
        previous_group = current_group  # 更新上一组为当前组

    return grouped_rules


# 多轮执行并记录结果
def execute_rules_for_groups(connector, rule_groups, rounds, base_output_dir):
    room_lock_dict = initLock()
    for group_idx, rules in enumerate(rule_groups):
        group_size = len(rules)
        # 计算当前组涉及的唯一锁的数量
        unique_locks = {lock for rule in rules for lock in rule["Room"]}
        total_locks = len(unique_locks)  # 当前组的唯一锁数量
        output_file = f"{base_output_dir}/room_lock_groups_{lock_targets[group_idx]}.txt"

        with open(output_file, "w") as file:
            for round_num in range(1, rounds + 1):
                time_differences = []
                threads = []

                for rule in rules:
                    thread = threading.Thread(target=apply_lock,
                                              args=(connector, rule, room_lock_dict, time_differences))
                    threads.append(thread)
                    thread.start()

                print(f"当前的活动线程数量: {threading.active_count()}")

                for thread in threads:
                    thread.join()

                avg_time = sum(time_differences) / total_locks if total_locks else 0
                file.write(f"{avg_time:.6f}\n")
                print(
                    f"Group {group_idx + 1} - Size {group_size} - Round {round_num} completed. Average time: {avg_time:.6f} seconds.")


if __name__ == "__main__":
    labeled_rules = get_all_rules()
    labeled_rules = add_lock_count_to_rules(labeled_rules)
    lock_targets = [5, 10, 15, 20, 25]
    rule_groups = group_rules_by_lock_count(labeled_rules, lock_targets)

    rounds = 10
    output_base_dir = r"/Synchronizer/Mutex/Atomicity/Unit/Data/Room"

    username = "2844532281"
    password = "whd123456"

    connector = XiaomiCloudConnector(username, password)
    print("Logging in...")
    logged = True
    if logged:
        print("Login successful.")
        execute_rules_for_groups(connector, rule_groups, rounds, output_base_dir)
    else:
        print("Unable to log in.")
