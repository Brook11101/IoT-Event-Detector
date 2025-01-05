import subprocess
import networkx as nx
import os
from ProcessDAG import build_dfg, parse_logs

def run_java_and_generate_logs(java_class_path, log_file_path):
    """
    运行 Java 文件并生成日志文件
    :param java_class_path: Java 项目中目标类的完整路径（包名+类名）
    :param log_file_path: 日志文件路径
    """
    try:
        # 清空日志文件
        with open(log_file_path, "w", encoding="gbk") as f:
            pass

        # 调用 Java 文件
        classpath = (
            "E:\\研究生信息收集\\论文材料\\IoT-Event-Proxy\\target\\classes;"
            "D:\\apache-maven-3.9.0\\repository\\org\\freemarker\\freemarker\\2.3.31\\freemarker-2.3.31.jar;"
            "D:\\apache-maven-3.9.0\\repository\\com\\fasterxml\\jackson\\core\\jackson-core\\2.12.3\\jackson-core-2.12.3.jar;"
            "D:\\apache-maven-3.9.0\\repository\\com\\fasterxml\\jackson\\core\\jackson-annotations\\2.12.3\\jackson-annotations-2.12.3.jar;"
            "D:\\apache-maven-3.9.0\\repository\\com\\fasterxml\\jackson\\core\\jackson-databind\\2.12.3\\jackson-databind-2.12.3.jar;"
            "D:\\apache-maven-3.9.0\\repository\\com\\fasterxml\\jackson\\dataformat\\jackson-dataformat-xml\\2.12.3\\jackson-dataformat-xml-2.12.3.jar;"
            "D:\\apache-maven-3.9.0\\repository\\com\\fasterxml\\jackson\\module\\jackson-module-jaxb-annotations\\2.12.3\\jackson-module-jaxb-annotations-2.12.3.jar;"
            "D:\\apache-maven-3.9.0\\repository\\jakarta\\xml\\bind\\jakarta.xml.bind-api\\2.3.2\\jakarta.xml.bind-api-2.3.2.jar;"
            "D:\\apache-maven-3.9.0\\repository\\jakarta\\activation\\jakarta.activation-api\\1.2.1\\jakarta.activation-api-1.2.1.jar;"
            "D:\\apache-maven-3.9.0\\repository\\org\\codehaus\\woodstox\\stax2-api\\4.2.1\\stax2-api-4.2.1.jar;"
            "D:\\apache-maven-3.9.0\\repository\\com\\fasterxml\\woodstox\\woodstox-core\\6.2.4\\woodstox-core-6.2.4.jar;"
            "D:\\apache-maven-3.9.0\\repository\\com\\google\\code\\gson\\gson\\2.8.8\\gson-2.8.8.jar"
        )
        result = subprocess.run(
            ["java", "-cp", classpath, java_class_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )

        # 打印 Java 文件的标准输出
        print(f"Java 文件执行完成，控制台输出如下：\n{result.stdout}")

    except subprocess.CalledProcessError as e:
        print(f"Java 文件执行失败")


def read_execution_logs(log_file_path):
    """
    读取 Java 日志文件，提取规则 ID 执行顺序
    :param log_file_path: 日志文件路径
    :return: 规则 ID 的执行顺序
    """
    execution_order = []
    try:
        # 修改为 GBK 编码读取日志文件
        with open(log_file_path, "r", encoding="gbk") as f:
            for line in f:
                rule_id, _ = line.strip().split(",", 1)
                execution_order.append(int(rule_id))
    except FileNotFoundError:
        print(f"日志文件未找到: {log_file_path}")
    except Exception as e:
        print(f"读取日志文件时出错: {e}")
    return execution_order


def validate_execution_order(dfg, execution_order):
    """
    验证 Java 日志的执行顺序是否符合 DFG 的拓扑关系
    :param dfg: 静态构建的 DFG
    :param execution_order: 规则 ID 的执行顺序
    :return: 是否符合 DFG（布尔值），以及违规次数
    """
    executed_set = set()
    violations = 0

    for rule_id in execution_order:
        predecessors = list(dfg.predecessors(rule_id))
        if any(pred not in executed_set for pred in predecessors):
            print(f"拓扑违规: Rule-{rule_id} 的前置规则尚未执行")
            violations += 1
        executed_set.add(rule_id)

    return violations == 0, violations


def check_concurr_dag(java_class_path, log_file_path, dfg):
    """
    检查并发执行日志是否符合 DFG
    :param java_class_path: Java 项目中目标类的完整路径（包名+类名）
    :param log_file_path: 日志文件路径
    :param dfg: 静态构建的 DFG
    :return: 每轮违规次数的列表
    """
    # 运行并发执行任务并生成日志
    print("开始执行并发任务...")
    run_java_and_generate_logs(java_class_path, log_file_path)

    # 读取并发执行日志
    execution_order = read_execution_logs(log_file_path)

    # 验证执行顺序
    _, violations = validate_execution_order(dfg, execution_order)
    return violations


def check_sequence_dag(java_class_path, log_file_path, dfg):
    """
    检查顺序执行日志是否符合 DFG
    :param java_class_path: Java 项目中目标类的完整路径（包名+类名）
    :param log_file_path: 日志文件路径
    :param dfg: 静态构建的 DFG
    :return: 每轮违规次数的列表
    """
    # 运行顺序执行任务并生成日志
    print("开始执行顺序任务...")
    run_java_and_generate_logs(java_class_path, log_file_path)

    # 读取顺序执行日志
    execution_order = read_execution_logs(log_file_path)

    # 验证执行顺序
    _, violations = validate_execution_order(dfg, execution_order)
    return violations


def run_multiple_rounds(java_class_path_sequence, java_class_path_concurr, log_file_path_sequence, log_file_path_concurr, dfg, rounds=10):
    """
    多轮运行 Java 文件，记录日志并验证 DFG
    :param java_class_path_sequence: 顺序执行 Java 类路径
    :param java_class_path_concurr: 并发执行 Java 类路径
    :param log_file_path_sequence: 顺序执行日志路径
    :param log_file_path_concurr: 并发执行日志路径
    :param dfg: 静态构建的 DFG
    :param rounds: 执行轮数
    :return: 每轮违规次数的列表
    """
    violations_per_round = []

    for i in range(rounds):
        print(f"开始第 {i + 1} 轮执行...")

        # 检查顺序执行的违规次数
        sequence_violations = check_sequence_dag(java_class_path_sequence, log_file_path_sequence, dfg)

        # 检查并发执行的违规次数
        concurr_violations = check_concurr_dag(java_class_path_concurr, log_file_path_concurr, dfg)

        violations_per_round.append((sequence_violations, concurr_violations))

        print(f"第 {i + 1} 轮完成，顺序执行违规次数: {sequence_violations}, 并发执行违规次数: {concurr_violations}")

    return violations_per_round


if __name__ == "__main__":
    # 顺序执行 Java 类路径和日志路径
    java_class_path_sequence = "concurrency.experiment.RealUser.ThreadPool.RealUserPriorityExecutor"
    log_file_path_sequence = "E:\\研究生信息收集\\论文材料\\IoT-Event-Proxy\\execution_log.txt"

    # 并发执行 Java 类路径和日志路径
    java_class_path_concurr = "concurrency.experiment.RealUser.ThreadPool.RealUserConcurrentExecutor"
    log_file_path_concurr = "E:\\研究生信息收集\\论文材料\\IoT-Event-Proxy\\src\\main\\java\\concurrency\\experiment\\RealUser\\ThreadPool\\json\\concurr_execution_log.txt"

    # 构建 DAG
    synclog_path = "synclogs.txt"
    with open(synclog_path, "r", encoding="utf-8") as f:
        log_data = f.read()
    rules = parse_logs(log_data)
    dfg = build_dfg(rules)

    # 多轮执行 Java 文件并验证 DFG
    rounds = 15
    violations_per_round = run_multiple_rounds(
        java_class_path_sequence, java_class_path_concurr,
        log_file_path_sequence, log_file_path_concurr,
        dfg, rounds
    )

    # 输出总结果
    print("多轮执行完成！违规次数统计如下：")
    for i, (sequence_violations, concurr_violations) in enumerate(violations_per_round):
        print(f"第 {i + 1} 轮: 顺序执行违规次数 {sequence_violations}, 并发执行违规次数 {concurr_violations}")
