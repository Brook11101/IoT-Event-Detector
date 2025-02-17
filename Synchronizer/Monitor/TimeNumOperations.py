import ast
import os
import subprocess
import time
from StaticSimulation import run_static_simulation
from InMonitor import InMonitor, validate_execution_order
from OutMonitor import OutMonitor
from Synchronizer.CV.UserScenario import detectRaceCondition_per_epoch
from Synchronizer.Monitor.ProcessDAG import get_static_DAG

# **定义数据存储的根目录**
BASE_DIR = r"E:\研究生信息收集\论文材料\IoT-Event-Detector\Synchronizer\Monitor\Data"

# **实验参数**
NUM_OF_OPERATIONS = [1, 2, 3, 4, 5]  # 扰动次数
NUM_TRIALS = 10  # 每个 num_of_operations 执行 10 轮实验


def read_static_logs(log_file=os.path.join(BASE_DIR, "static_logs.txt")):
    """读取 `static_logs.txt`，解析成按轮次 (epoch) 分组的日志。"""
    with open(log_file, "r", encoding="utf-8") as f:
        data = f.read().strip()

    epochs = data.split("\n\n")
    return [[ast.literal_eval(line) for line in epoch.split("\n") if line.strip()] for epoch in epochs]


def match_execution_order_to_logs_grouped(execution_order, static_logs_per_epoch):
    """
    根据 `execution_order` 按 `static_logs_per_epoch` 的分组结构，生成 `execution_log_per_epoch`。

    :param execution_order: 扁平化的执行顺序列表（包含所有 epoch 的规则 ID）
    :param static_logs_per_epoch: 按轮次 (epoch) 分组的静态日志列表
    :return: execution_logs_per_epoch：按轮次分组的执行日志
    """
    execution_logs_per_epoch = []
    index = 0  # execution_order 当前处理的位置

    for epoch_logs in static_logs_per_epoch:
        epoch_rule_count = len(epoch_logs)  # 当前 epoch 中规则的数量
        # 提取 execution_order 中对应当前 epoch 的规则 ID
        epoch_execution_order = execution_order[index:index + epoch_rule_count]
        # 创建 ID 到规则的映射
        rule_map = {rule["id"]: rule for rule in epoch_logs}
        # 根据 epoch_execution_order 构建当前 epoch 的完整规则信息
        execution_log = [rule_map[rule_id] for rule_id in epoch_execution_order if rule_id in rule_map]
        execution_logs_per_epoch.append(execution_log)
        index += epoch_rule_count  # 更新索引

    return execution_logs_per_epoch


def detectRaceCondition_per_epoch_monitor(epochs_logs):
    """
    **对每个轮次(epoch)单独执行 Race Condition 检测，并记录冲突设备**。

    :param epochs_logs: 轮次划分的日志数据
    :return: (rc_dict, rc_dict_with_device)
             rc_dict:      { "AC": [...], "UC": [...], "CBK": [...], "CP": [...] }
             rc_dict_with_device:  { "AC": [...], "UC": [...], "CBK": [...], "CP": [...] }
    """

    rc_dict = {"AC": [], "UC": [], "CBK": [], "CP": []}  # **存储所有轮次的 Race Condition 结果**
    rc_dict_with_device = {"AC": [], "UC": [], "CBK": [], "CP": []}  # **存储冲突设备信息**
    logged_pairs = set()  # 记录已检测的 conflict pair，防止重复添加

    for epoch_logs in epochs_logs:  # **逐个轮次(epoch)执行Race Condition检测**
        for i in range(len(epoch_logs)):
            current_rule = epoch_logs[i]
            current_actions = current_rule["Action"]
            cur_rule_id = current_rule["id"]

            # **Condition Block (CBK)**
            if current_rule['status'] == 'skipped' and current_rule.get('Condition'):
                cond_dev, _ = current_rule['Condition'][0], current_rule['Condition'][1]
                for j in range(i - 1, -1, -1):  # **只在当前轮次(epoch)内回溯**
                    former_rule = epoch_logs[j]
                    frm_rule_id = former_rule["id"]
                    for former_act in former_rule["Action"]:
                        if former_act[0] == cond_dev:
                            pair_cbk = (frm_rule_id, cur_rule_id)
                            conflict_device = former_act[0]  # **冲突设备**
                            if frm_rule_id > cur_rule_id and pair_cbk not in logged_pairs:
                                logged_pairs.add(pair_cbk)
                                rc_dict["CBK"].append(pair_cbk)
                                rc_dict_with_device["CBK"].append((pair_cbk, conflict_device))
                            break
                    else:
                        continue
                    break

            # **Action Conflict / Unexpected Conflict**
            if current_rule['status'] == 'run':
                for j in range(i - 1, -1, -1):  # **只在当前轮次(epoch)内查找**
                    former_rule = epoch_logs[j]
                    frm_rule_id = former_rule["id"]

                    for latter_act in current_actions:
                        for former_act in former_rule["Action"]:
                            if latter_act[0] == former_act[0] and latter_act[1] != former_act[1]:
                                pair = (frm_rule_id, cur_rule_id)
                                conflict_device = latter_act[0]  # **冲突设备**
                                if former_rule["ancestor"] == current_rule["ancestor"]:
                                    if frm_rule_id > cur_rule_id and pair not in logged_pairs:
                                        logged_pairs.add(pair)
                                        rc_dict["AC"].append(pair)
                                        rc_dict_with_device["AC"].append((pair, conflict_device))
                                else:
                                    if frm_rule_id > cur_rule_id and pair not in logged_pairs:
                                        logged_pairs.add(pair)
                                        rc_dict["UC"].append(pair)
                                        rc_dict_with_device["UC"].append((pair, conflict_device))

                # **Condition Pass (CP)**
                if current_rule.get('Condition'):
                    cond_dev, cond_state = current_rule['Condition'][0], current_rule['Condition'][1]
                    for j in range(i - 1, -1, -1):
                        former_rule = epoch_logs[j]
                        frm_rule_id = former_rule["id"]
                        if [cond_dev, cond_state] in former_rule["Action"]:
                            pair_cp = (frm_rule_id, cur_rule_id)
                            conflict_device = cond_dev  # **冲突设备**
                            if frm_rule_id > cur_rule_id and pair_cp not in logged_pairs:
                                logged_pairs.add(pair_cp)
                                rc_dict["CP"].append(pair_cp)
                                rc_dict_with_device["CP"].append((pair_cp, conflict_device))
                            break

    return rc_dict, rc_dict_with_device  # **返回冲突对和对应的冲突设备**


def detect_and_write_rc_results_monitor(execution_order, time_list, static_logs_per_epoch, num_path, time_path):
    """
    处理 `execution_order`，生成完整日志 `execution_log_per_epoch`，进行 Race Condition 检测，
    并将冲突数量和执行时间分别写入 `num_path` 和 `time_path`。
    """

    # **1. 生成 execution_log_per_epoch**
    execution_log_per_epoch = match_execution_order_to_logs_grouped(execution_order, static_logs_per_epoch)

    # **2. 进行 Race Condition 检测**
    rc_dict, _ = detectRaceCondition_per_epoch_monitor(execution_log_per_epoch)

    print(rc_dict)

    # **3. 统计冲突数量**
    rc_counts = {key: len(value) for key, value in rc_dict.items()}
    total_rc_count = sum(rc_counts.values())

    print(f"当前检测出来的race condition数量{total_rc_count}")

    # **4. 写入 `num_path`**
    with open(num_path, "a") as f:
        f.write(f"{total_rc_count}\n")

    # **5. 写入 `time_path`**
    with open(time_path, "a") as f:
        f.write(",".join(map(str, time_list)) + "\n")


def detect_and_write_rc_results(execution_order, time_list, static_logs_per_epoch, num_path, time_path):
    """
    处理 `execution_order`，生成完整日志 `execution_log_per_epoch`，进行 Race Condition 检测，
    并将冲突数量和执行时间分别写入 `num_path` 和 `time_path`。
    """

    # **1. 生成 execution_log_per_epoch**
    execution_log_per_epoch = match_execution_order_to_logs_grouped(execution_order, static_logs_per_epoch)

    # **2. 进行 Race Condition 检测**
    rc_dict, _ = detectRaceCondition_per_epoch(execution_log_per_epoch)

    print(rc_dict)

    # **3. 统计冲突数量**
    rc_counts = {key: len(value) for key, value in rc_dict.items()}
    total_rc_count = sum(rc_counts.values())

    print(f"当前检测出来的race condition数量{total_rc_count}")

    # **4. 写入 `num_path`**
    with open(num_path, "a") as f:
        f.write(f"{total_rc_count}\n")

    # **5. 写入 `time_path`**
    with open(time_path, "a") as f:
        f.write("\n".join(map(str, time_list)) + "\n")


def parse_static_log(java_class_path="concurrency.experiment.StaticRuleParser"):
    """
    运行 Java 程序并生成日志文件
    :param java_class_path: Java 类的完整路径（包名 + 类名）
    """

    # 配置 Java 运行时的 classpath
    classpath = (
        "E:\\研究生信息收集\\论文材料\\IoT-Event-Proxy\\target\\classes;"
        "D:\\apache-maven-3.9.0\\repository\\jakarta\\activation\\jakarta.activation-api\\1.2.1\\jakarta.activation-api-1.2.1.jar;"
        "D:\\apache-maven-3.9.0\\repository\\com\\fasterxml\\jackson\\module\\jackson-module-jaxb-annotations\\2.12.3\\jackson-module-jaxb-annotations-2.12.3.jar;"
        "D:\\apache-maven-3.9.0\\repository\\com\\fasterxml\\jackson\\core\\jackson-core\\2.12.3\\jackson-core-2.12.3.jar;"
        "D:\\apache-maven-3.9.0\\repository\\org\\freemarker\\freemarker\\2.3.31\\freemarker-2.3.31.jar;"
        "D:\\apache-maven-3.9.0\\repository\\org\\codehaus\\woodstox\\stax2-api\\4.2.1\\stax2-api-4.2.1.jar;"
        "D:\\apache-maven-3.9.0\\repository\\com\\fasterxml\\jackson\\core\\jackson-annotations\\2.12.3\\jackson-annotations-2.12.3.jar;"
        "D:\\apache-maven-3.9.0\\repository\\com\\google\\code\\gson\\gson\\2.8.8\\gson-2.8.8.jar;"
        "D:\\apache-maven-3.9.0\\repository\\com\\fasterxml\\jackson\\core\\jackson-databind\\2.12.3\\jackson-databind-2.12.3.jar;"
        "D:\\apache-maven-3.9.0\\repository\\com\\fasterxml\\jackson\\dataformat\\jackson-dataformat-xml\\2.12.3\\jackson-dataformat-xml-2.12.3.jar;"
        "D:\\apache-maven-3.9.0\\repository\\jakarta\\xml\\bind\\jakarta.xml.bind-api\\2.3.2\\jakarta.xml.bind-api-2.3.2.jar;"
        "D:\\apache-maven-3.9.0\\repository\\com\\fasterxml\\woodstox\\woodstox-core\\6.2.4\\woodstox-core-6.2.4.jar"
    )

    try:
        result = subprocess.run(
            ["java", "-cp", classpath, java_class_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        print(f"刷新rules.json")

    except subprocess.CalledProcessError as e:
        print(f"刷新rules.json执行失败，错误信息: {e.stderr}")


def run_experiment():
    """进行完整实验，测试不同 Num Of Operations (times=1~5)，每个 times 进行 10 轮实验。"""
    for num_ops in NUM_OF_OPERATIONS:
        # **定义当前 num_of_operations 目录**
        exp_dir = os.path.join(BASE_DIR, f"num_of_operations_{num_ops}")
        os.makedirs(exp_dir, exist_ok=True)

        # **日志存储路径**
        log_num_path = os.path.join(exp_dir, "log_num.txt")
        inmonitor_num_path = os.path.join(exp_dir, "inmonitor_num.txt")
        inmonitor_time_path = os.path.join(exp_dir, "inmonitor_time.txt")
        outmonitor_num_path = os.path.join(exp_dir, "outmonitor_num.txt")
        outmonitor_time_path = os.path.join(exp_dir, "outmonitor_time.txt")

        # **清空文件**
        for file_path in [log_num_path, inmonitor_num_path, inmonitor_time_path, outmonitor_num_path,
                          outmonitor_time_path]:
            with open(file_path, "w") as f:
                pass

        for trial in range(NUM_TRIALS):
            print(f"Num Of Operations: {num_ops}, Trial: {trial + 1}")

            # **1. 运行静态模拟**
            rule_count = run_static_simulation(times=num_ops)
            static_logs_per_epoch = read_static_logs()

            # **2. 记录触发规则数量**
            with open(log_num_path, "a") as f:
                f.write(f"{rule_count}\n")

            # 将生成的日志解析为json
            parse_static_log()

            # 基于静态日志构建DAG
            dag = get_static_DAG()

            # **3. 规则使用 InMonitor 进行并发执行**
            execution_order, time_list = InMonitor()

            _, violations = validate_execution_order(dag, execution_order)
            print(f"InMonitor: 违反拓扑顺序的规则数量{violations}\n")

            # **4. 处理 InMonitor 结果**
            detect_and_write_rc_results_monitor(
                execution_order=execution_order,
                time_list=time_list,
                static_logs_per_epoch=static_logs_per_epoch,
                num_path=inmonitor_num_path,
                time_path=inmonitor_time_path
            )

            # **5. 规则使用 OutMonitor 进行并发执行**
            execution_order, time_list = OutMonitor()
            _, violations = validate_execution_order(dag, execution_order)
            print(f"OutMonitor: 违反拓扑顺序的规则数量{violations}\n")

            # **6. 处理 OutMonitor 结果**
            detect_and_write_rc_results(
                execution_order=execution_order,
                time_list=time_list,
                static_logs_per_epoch=static_logs_per_epoch,
                num_path=outmonitor_num_path,
                time_path=outmonitor_time_path
            )

    print(f"Operations Num-{num_ops}-{trial}  == Experiment Completed Successfully ==")


if __name__ == "__main__":
    run_experiment()
