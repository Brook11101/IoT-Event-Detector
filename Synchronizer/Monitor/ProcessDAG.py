import networkx as nx
import ast
import matplotlib.pyplot as plt
import matplotlib

def parse_logs(log_data):
    """
    解析日志数据，转换为规则列表
    :param log_data: 日志文件内容
    :return: 解析后的规则列表
    """
    parsed_rules = []
    for line in log_data.strip().split("\n"):
        line = line.strip()
        if not line:  # 跳过空行
            continue
        try:
            rule = ast.literal_eval(line)  # 解析 JSON 格式规则
            parsed_rules.append(rule)
        except (SyntaxError, ValueError) as e:
            print(f"解析失败，跳过该行: {line}，错误信息: {e}")
    return parsed_rules


def build_dependency_graph(parsed_rules):
    """
    构建规则依赖有向无环图（DAG）
    :param parsed_rules: 解析后的规则列表
    :return: 依赖 DAG
    """
    dependency_graph = nx.DiGraph()

    # 按规则 ID 排序，确保依赖关系按顺序解析
    parsed_rules.sort(key=lambda rule: rule["id"])

    # 添加 DAG 节点
    for rule in parsed_rules:
        dependency_graph.add_node(rule["id"], description=rule["description"])

    # 构建 DAG 依赖关系（边）
    for i, current_rule in enumerate(parsed_rules):
        current_id = current_rule["id"]
        current_trigger = current_rule["Trigger"]
        current_actions = {action[0] for action in current_rule["Action"]}

        for j in range(i + 1, len(parsed_rules)):
            next_rule = parsed_rules[j]
            next_id = next_rule["id"]
            next_trigger = next_rule["Trigger"]
            next_actions = {action[0] for action in next_rule["Action"]}

            # 依赖条件 1: 当前规则的 Trigger 影响下一个规则
            if current_trigger[0] in next_trigger:
                dependency_graph.add_edge(current_id, next_id)

            # 依赖条件 2: 当前规则的 Action 影响下一个规则
            if current_actions & next_actions:
                dependency_graph.add_edge(current_id, next_id)

            # 依赖条件 3: 如果 id2 规则的 ancestor 指向 id1，则添加 (id1, id2) 依赖关系
            if "ancestor" in next_rule and next_rule["ancestor"] == current_id:
                dependency_graph.add_edge(current_id, next_id)

    # 确保 DAG 没有环
    if not nx.is_directed_acyclic_graph(dependency_graph):
        raise ValueError("生成的 DAG 存在环，检查规则的依赖关系")

    print("DAG 构建成功！")
    return dependency_graph


def visualize_dependency_graph(dependency_graph):
    """
    优化后的 Matplotlib 可视化 DAG
    :param dependency_graph: 依赖 DAG
    """
    # 使用 spring_layout 调整布局，减少节点重叠
    pos = nx.spring_layout(dependency_graph, k=0.6, seed=42)

    # 解决字体显示问题
    matplotlib.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei"]
    matplotlib.rcParams["axes.unicode_minus"] = False

    # 设置图形大小（加宽）
    plt.figure(figsize=(16, 10))

    # 绘制 DAG
    nx.draw(
        dependency_graph,
        pos,
        with_labels=True,
        node_color="lightblue",
        node_size=2000,  # 减小节点大小
        font_size=8,  # 减小字体大小
        font_weight="bold",
        edge_color="gray",
        width=1.5,  # 细一点的边，避免过多线条显得混乱
        alpha=0.7,
        style="solid",
    )

    # 添加规则描述
    labels = nx.get_node_attributes(dependency_graph, "description")
    custom_labels = {node: f"Rule-{node}\n{desc}" for node, desc in labels.items()}

    # 避免标签重叠，让标签稍微远离节点
    nx.draw_networkx_labels(dependency_graph, pos, labels=custom_labels, font_size=7, font_color="black",
                            verticalalignment="bottom")

    # 绘制带箭头的边
    nx.draw_networkx_edges(
        dependency_graph,
        pos,
        width=1.5,  # 细一点的边
        alpha=0.7,
        edge_color="gray",
        arrows=True,
        style="dotted",
    )

    # 设置标题
    plt.title("Optimized Dependency Graph (DFG)", fontsize=16, fontweight="bold")
    plt.axis("off")  # 关闭坐标轴
    plt.show()


def get_static_DAG():
    log_file_path = "E:\\研究生信息收集\\论文材料\\IoT-Event-Detector\\Synchronizer\\Monitor\\Data\\static_logs.txt"
    try:
        with open(log_file_path, "r", encoding="utf-8") as file:
            log_data = file.read()
    except FileNotFoundError:
        print(f"日志文件未找到: {log_file_path}")
        return

    # 解析日志数据（跳过空行 & 无效格式）
    parsed_rules = parse_logs(log_data)

    # 构建 DAG
    dependency_graph = build_dependency_graph(parsed_rules)

    # 可视化 DAG
    visualize_dependency_graph(dependency_graph)

    return dependency_graph


if __name__ == "__main__":
    get_static_DAG()
