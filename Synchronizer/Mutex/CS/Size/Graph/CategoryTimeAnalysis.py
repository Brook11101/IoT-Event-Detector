import os
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# 启用 Seaborn 主题，设定更柔和的背景
sns.set_theme(style="darkgrid")

# 文件路径
base_path = r"E:\研究生信息收集\论文材料\IoT-Event-Detector\Synchronizer\Mutex\CS\Size\Data"
dirpath = {'device_name': r"\DeviceName", 'device_type': r"\DeviceType", 'room': r"\Room", 'home': r"\Home"}

file_prefixes = ["device_name", "device_type", "room", "home"]
rule_counts = [10, 20, 30, 40, 50]

# 初始化颜色和线条样式
types_styles = {
    "device_name": {"color": sns.color_palette("tab10")[0], "linestyle": "-", "label": "Individual Device (27)", "marker": "o"},
    "device_type": {"color": sns.color_palette("tab10")[1], "linestyle": "--", "label": "Device Category (10)", "marker": "s"},
    "room": {"color": sns.color_palette("tab10")[2], "linestyle": "-.", "label": "Deployment Room (6)", "marker": "D"},
    "home": {"color": sns.color_palette("tab10")[3], "linestyle": ":", "label": "Deployment Home (1)", "marker": "P"},
}

# 存储数据
all_data = {}

for prefix in file_prefixes:
    data = []
    for count in rule_counts:
        file_name = f"{prefix}_lock_groups_{count}.txt"
        file_path = os.path.join(base_path + dirpath[prefix], file_name)

        # 读取文件
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                values = [float(line.strip()) for line in f if line.strip()]
                avg_time = np.mean(values)
                data.append(avg_time)

    all_data[prefix] = data

# 创建图表
plt.figure(figsize=(12, 8))
ax = plt.gca()

# 绘制折线图，并标注数据点
for prefix in file_prefixes:
    style = types_styles[prefix]
    y_values = all_data[prefix]
    ax.plot(rule_counts, y_values, color=style["color"], linestyle=style["linestyle"], marker=style["marker"],
            markersize=8, linewidth=2, label=style["label"])

    # 在数据点上标注数值，调整位置避免重叠
    for x, y in zip(rule_counts, y_values):
        ax.text(x, y * 1.05, f"{y:.1f}", fontsize=10, ha='center', va='bottom', color=style["color"], fontweight="bold")

# 设置 Y 轴为 log2 刻度
ax.set_yscale("log", base=2)
y_max = max(max(values) for values in all_data.values())
y_min = min(min(values) for values in all_data.values())
y_ticks = [2 ** i for i in range(int(np.log2(y_min)), int(np.log2(y_max)) + 1)]
ax.set_yticks(y_ticks)
ax.set_yticklabels([f"$2^{int(np.log2(i))}$" for i in y_ticks])  # 显示 2^n 形式

# 设置 X 轴
ax.set_xticks(rule_counts)
ax.set_xlabel("Total Number of Requests to Enter the Critical Section", fontsize=14, fontweight="bold")
ax.set_ylabel("Average Waiting Time Before Rule Enters Critical Section", fontsize=14, fontweight="bold")
ax.set_title("Average Waiting Time of Rules Under Different Critical Section Granularity", fontsize=16, fontweight="bold")

# 优化网格
ax.grid(True, linestyle="--", alpha=0.5)

# 添加图例
ax.legend(loc="upper left", fontsize=12, frameon=True)

# 调整布局
plt.tight_layout()

# 显示图形
plt.show()
