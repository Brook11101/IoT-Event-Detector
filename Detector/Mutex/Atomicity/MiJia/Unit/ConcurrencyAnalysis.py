import os
import matplotlib.pyplot as plt
import numpy as np

# 文件路径
base_path = r"E:\\研究生信息收集\\论文材料\\IoT-Event-Detector\\Detector\\Mutex\\Atomicity\\MiJia\\Unit\\Data"
rule_count = 60
file_mapping = {
    "room": "room_lock_groups_60.txt",
    "device_type": "device_type_lock_groups_60.txt",
    "device_name": "device_name_lock_groups_60.txt",
}
concurrency_levels = {
    "room": 6,
    "device_type": 10,
    "device_name": 27,
}

# 初始化数据
avg_times = {}

# 读取文件并计算平均时间
for key, file_name in file_mapping.items():
    file_path = os.path.join(base_path, file_name)
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            values = [float(line.strip()) for line in f if line.strip()]
            avg_times[key] = np.mean(values)

# 提取数据
categories = list(file_mapping.keys())
average_time_values = [avg_times[cat] for cat in categories]
concurrency_values = [concurrency_levels[cat] for cat in categories]

# 创建双轴图
fig, ax1 = plt.subplots(figsize=(10, 6))

# 时间折线（左轴）
ax1.plot(categories, average_time_values, color="blue", marker="o", linestyle="-", label="Average Time (s)")
ax1.set_xlabel("Lock Granularity", fontsize=12)
ax1.set_ylabel("Average Time to Acquire Locks (s)", color="blue", fontsize=12)
ax1.tick_params(axis="y", labelcolor="blue")
ax1.set_ylim(0, max(average_time_values) + 1)

# 并发度折线（右轴）
ax2 = ax1.twinx()
ax2.plot(categories, concurrency_values, color="red", marker="x", linestyle="--", label="Concurrency Level")
ax2.set_ylabel("Concurrency Level", color="red", fontsize=12)
ax2.tick_params(axis="y", labelcolor="red")
ax2.set_ylim(0, max(concurrency_values) + 5)

# 标题和图例
plt.title("Comparison of Average Time and Concurrency Levels", fontsize=14)
fig.tight_layout()
plt.grid(True, linestyle="--", alpha=0.6)

# 保存和显示图表
output_image_path = os.path.join(base_path, "time_vs_concurrency_comparison.png")
plt.savefig(output_image_path, dpi=300)
plt.show()
