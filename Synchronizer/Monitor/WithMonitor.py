import subprocess
from ProcessDAG import get_static_DAG


def clear_log_file(log_file_path):
    """
    清空日志文件
    :param log_file_path: 日志文件路径
    """
    try:
        with open(log_file_path, "w", encoding="utf-8") as _:
            pass  # 清空文件内容
    except Exception as e:
        print(f"无法清空日志文件: {log_file_path}，错误: {e}")


def execute_with_monitor(java_class_path, log_file_path):
    """
    运行 Java 程序并生成日志文件
    :param java_class_path: Java 类的完整路径（包名 + 类名）
    :param log_file_path: 生成的日志文件路径
    """
    clear_log_file(log_file_path)  # 先清空日志文件

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
        print(f"Java 执行完成，输出如下：\n{result.stdout}")

    except subprocess.CalledProcessError as e:
        print(f"Java 执行失败，错误信息: {e.stderr}")


def read_execution_log(log_file_path):
    """
    读取 Java 执行日志，解析规则 ID 执行顺序
    :param log_file_path: 日志文件路径
    :return: 规则 ID 执行顺序（列表）
    """
    execution_order = []
    try:
        with open(log_file_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    rule_id, _ = line.strip().split(",", 1)
                    execution_order.append(int(rule_id))
    except FileNotFoundError:
        print(f"日志文件未找到: {log_file_path}")
    except Exception as e:
        print(f"读取日志文件时出错: {e}")
    return execution_order


def validate_execution_order(dag, execution_order):
    """
    验证 Java 执行顺序是否符合 DAG 的拓扑关系
    :param dag: 预先构建的静态 DAG
    :param execution_order: 规则 ID 的执行顺序
    :return: (是否符合 DAG, 违规次数)
    """
    executed_set = set()
    violations = 0

    for rule_id in execution_order:
        predecessors = list(dag.predecessors(rule_id))
        if any(pred not in executed_set for pred in predecessors):
            print(f"拓扑违规: Rule-{rule_id} 的前置规则尚未执行")
            violations += 1
        executed_set.add(rule_id)

    return violations == 0, violations


def run_multiple_rounds(java_class_path, log_file_path, dag, rounds=10):
    """
    多轮运行 Java 文件，记录日志并验证 DAG 依赖顺序
    :param java_class_path: Java 类路径（包名 + 类名）
    :param log_file_path: 日志文件路径
    :param dag: 预先构建的 DAG
    :param rounds: 执行轮数
    :return: 每轮违规次数的列表
    """
    violations_per_round = []

    for i in range(rounds):
        print(f"开始第 {i + 1} 轮执行...")
        execute_with_monitor(java_class_path, log_file_path)

        execution_order = read_execution_log(log_file_path)
        _, violations = validate_execution_order(dag, execution_order)

        violations_per_round.append(violations)
        print(f"第 {i + 1} 轮完成，违规次数: {violations}")

    return violations_per_round


if __name__ == "__main__":
    # Java 目标类路径
    java_class_path = "concurrency.experiment.WithMonitor"
    log_file_path = "E:\\研究生信息收集\\论文材料\\IoT-Event-Proxy\\src\\main\\java\\concurrency\\experiment\\data\\WithMonitorLog.txt"

    # 获取 DAG
    dag = get_static_DAG()

    # 运行多轮 Java 执行并验证 DAG 依赖
    rounds = 5
    violations_per_round = run_multiple_rounds(java_class_path, log_file_path, dag, rounds)

    # 输出统计结果
    print("\n多轮执行完成！违规次数统计如下：")
    for i, violations in enumerate(violations_per_round):
        print(f"第 {i + 1} 轮: 违规次数 {violations}")
