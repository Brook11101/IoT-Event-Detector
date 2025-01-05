import networkx as nx
import ast
import matplotlib.pyplot as plt

def parse_logs(log_data):
    rules = []
    for line in log_data.strip().split("\n"):
        rules.append(ast.literal_eval(line.strip()))
    return rules

def build_dfg(rules):
    dag = nx.DiGraph()

    # 按规则 ID 排序
    rules.sort(key=lambda x: x["id"])

    # 构建 DAG 节点
    for rule in rules:
        dag.add_node(rule["id"], description=rule["description"])

    # 构建 DAG 边
    for i, current_rule in enumerate(rules):
        current_trigger = current_rule["Trigger"]
        current_actions = [action[0] for action in current_rule["Action"]]

        for j in range(i + 1, len(rules)):
            next_rule = rules[j]
            next_trigger = next_rule["Trigger"]
            next_actions = [action[0] for action in next_rule["Action"]]

            if current_trigger[0] in next_trigger:
                dag.add_edge(current_rule["id"], next_rule["id"])

            if any(action in next_actions for action in current_actions):
                dag.add_edge(current_rule["id"], next_rule["id"])

    if not nx.is_directed_acyclic_graph(dag):
        raise ValueError("生成的图中存在环，检查规则的依赖关系")

    print("DAG 构建成功！")
    return dag


def visualize_dfg(dag):
    """
    使用 matplotlib 可视化 DFG
    """
    # 使用 Kamada-Kawai 布局（有时会比 spring 布局更加清晰）
    pos = nx.kamada_kawai_layout(dag, weight='weight')  # 或者使用 nx.spring_layout(dag)

    # 创建图形对象，调整尺寸
    plt.figure(figsize=(12, 10))

    # 绘制节点和边
    nx.draw(
        dag,
        pos,
        with_labels=True,
        node_color="lightblue",  # 节点颜色
        node_size=3000,  # 节点大小
        font_size=10,  # 字体大小
        font_weight="bold",  # 字体粗细
        edge_color="gray",  # 边的颜色
        width=2,  # 边的宽度
        alpha=0.7,  # 边的透明度
        style='solid',  # 边的样式
    )

    # 获取节点标签（规则描述）
    labels = nx.get_node_attributes(dag, "description")
    custom_labels = {node: f"Rule-{node}\n{desc}" for node, desc in labels.items()}

    # 为每个节点设置自定义标签
    nx.draw_networkx_labels(dag, pos, labels=custom_labels, font_size=8, font_weight="bold", font_color="black")

    # 为每条边设置箭头（表示方向）
    nx.draw_networkx_edges(
        dag,
        pos,
        width=2,
        alpha=0.7,
        edge_color="gray",
        arrows=True,  # 启用箭头
        style="dotted"  # 边的样式：可以使用 "solid" 或 "dotted"
    )

    # 添加标题和其他格式设置
    plt.title("DFG Visualization", fontsize=16, fontweight="bold")
    plt.axis('off')  # 不显示坐标轴

    # 显示图形
    plt.show()

def main():
    log_file_path = "synclogs.txt"

    try:
        with open(log_file_path, "r", encoding="utf-8") as f:
            log_data = f.read()
    except FileNotFoundError:
        print(f"日志文件未找到: {log_file_path}")
        return

    # 解析日志数据
    rules = parse_logs(log_data)

    # 构建 DAG
    dag = build_dfg(rules)

    # 可视化 DAG
    visualize_dfg(dag)

if __name__ == "__main__":
    main()
