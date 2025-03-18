import os
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# 启用 Seaborn 主题，设定更柔和的背景
sns.set_theme(style="darkgrid")

# 文件路径
base_path = r"E:\研究生信息收集\论文材料\IoT-Event-Detector\Synchronizer\Mutex\CS\Size\Data"
dirpath = {
    'device_name': r"\DeviceName",
    'device_type': r"\DeviceType",
    'room': r"\Room",
    'home': r"\Home"
}

file_prefixes = ["device_name", "device_type", "room", "home"]
rule_counts = [10, 20, 30, 40, 50]

# 初始化颜色和线条样式
types_styles = {
    "device_name": {
        "color": sns.color_palette("tab10")[0],
        "linestyle": "-",
        "label": "Individual Device (26)",
        "marker": "o"
    },
    "device_type": {
        "color": sns.color_palette("tab10")[1],
        "linestyle": "--",
        "label": "Device Category (10)",
        "marker": "s"
    },
    "room": {
        "color": sns.color_palette("tab10")[2],
        "linestyle": "-.",
        "label": "Deployment Room (6)",
        "marker": "D"
    },
    "home": {
        "color": sns.color_palette("tab10")[3],
        "linestyle": ":",
        "label": "Deployment Home (1)",
        "marker": "P"
    },
}

# 存储数据 (平均值与标准差)
all_data = {}

for prefix in file_prefixes:
    data = []
    for count in rule_counts:
        file_name = f"{prefix}_lock_groups_{count}.txt"
        file_path = os.path.join(base_path + dirpath[prefix], file_name)

        # 读取文件并计算平均值与标准差
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                values = [float(line.strip()) for line in f if line.strip()]
                avg_time = np.mean(values)
                std_time = np.std(values)
                data.append((avg_time, std_time))
        else:
            data.append((0.0, 0.0))

    all_data[prefix] = data

# 创建图表
plt.figure(figsize=(12, 8))
ax = plt.gca()

# 绘制折线图 + 误差棒
for prefix in file_prefixes:
    style = types_styles[prefix]

    # 拆分均值和标准差
    y_values = [t[0] for t in all_data[prefix]]
    y_err_values = [t[1] for t in all_data[prefix]]

    ax.errorbar(
        rule_counts,
        y_values,
        yerr=y_err_values,
        color=style["color"],
        linestyle=style["linestyle"],
        marker=style["marker"],
        markersize=8,
        linewidth=2,
        label=style["label"],
        capsize=5  # 误差棒端点的小横杠长度
    )

    # 在数据点上方标注数值
    for x, y, err in zip(rule_counts, y_values, y_err_values):
        ax.text(
            x,
            y * 1.05,  # 显示在均值上方一点
            f"{y:.1f}",
            fontsize=10,
            ha='center',
            va='bottom',
            color=style["color"],
            fontweight="bold"
        )

# 设置 Y 轴为 log2 刻度
ax.set_yscale("log", base=2)
y_max = max(max(values[0] for values in all_data[prefix]) for prefix in file_prefixes)
y_min = min(min(values[0] for values in all_data[prefix]) for prefix in file_prefixes)
y_ticks = [2 ** i for i in range(int(np.log2(y_min)), int(np.log2(y_max)) + 1) if i >= 0]
ax.set_yticks(y_ticks)
ax.set_yticklabels([f"$2^{int(np.log2(i))}$" for i in y_ticks])

# 设置 X 轴刻度并增大刻度字号
ax.set_xticks(rule_counts)
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)

# 设置坐标轴标签和标题，并调整字号
ax.set_xlabel("Total Number of Requests to Enter the Critical Section", fontsize=16, fontweight="bold")
ax.set_ylabel("Average Waiting Time Before Rule Enters Critical Section", fontsize=16, fontweight="bold")
ax.set_title("Average Waiting Time of Rules Under Different Critical Section Granularity",
             fontsize=18, fontweight="bold")

# 优化网格
ax.grid(True, linestyle="--", alpha=0.5)

# 添加图例
ax.legend(loc="upper left", fontsize=12, frameon=True)

# 调整布局
plt.tight_layout()

# 保存为 SVG 文件
plt.savefig("average_waiting_time.svg", format="svg")

# 显示图形
plt.show()
