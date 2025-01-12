import os
import matplotlib.pyplot as plt
import numpy as np

# 文件路径
base_path = r"E:\\研究生信息收集\\论文材料\\IoT-Event-Detector\\Detector\\Mutex\\Atomicity\\MiJia\\Unit\\Data"
file_prefixes = ["device_name", "device_type", "room"]
rule_counts = [20, 40, 60, 80, 100]

# 初始化颜色和线条样式，便于区分
types_styles = {
    "device_name": {"color": "blue", "linestyle": "-", "label": "Device Name Lock"},
    "device_type": {"color": "green", "linestyle": "--", "label": "Device Type Lock"},
    "room": {"color": "red", "linestyle": "-.", "label": "Room Lock"},
}

# 存储数据
all_data = {}

for prefix in file_prefixes:
    data = []
    for count in rule_counts:
        file_name = f"{prefix}_lock_groups_{count}.txt"
        file_path = os.path.join(base_path, file_name)

        # 读取文件
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                values = [float(line.strip()) for line in f if line.strip()]
                avg_time = np.mean(values)
                data.append(avg_time)

    all_data[prefix] = data

# 绘制
plt.figure(figsize=(10, 6))
for prefix, times in all_data.items():
    style = types_styles[prefix]
    plt.plot(rule_counts, times, color=style["color"], linestyle=style["linestyle"], marker="o", label=style["label"])

# 图表标题和标签
plt.title("Average Time to Acquire Locks vs. Rule Frequency", fontsize=14)
plt.xlabel("Number of Rules", fontsize=12)
plt.ylabel("Average Time to Acquire Locks (s)", fontsize=12)
plt.xticks(rule_counts, fontsize=10)
plt.yticks(np.arange(0, max(max(times) for times in all_data.values()) + 0.5, 0.5), fontsize=10)
plt.grid(True, linestyle="--", alpha=0.6)
plt.legend(fontsize=10)

# 保存和显示
output_image_path = os.path.join(base_path, "lock_time_analysis.png")
plt.savefig(output_image_path, dpi=300)
plt.show()
