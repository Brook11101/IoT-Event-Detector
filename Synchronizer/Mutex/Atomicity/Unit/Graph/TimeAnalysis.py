import os
import matplotlib.pyplot as plt
import numpy as np


# 用来分析RealUser规则集下随着规则数目增多，互斥锁申请的时间的变化曲线
# 但说实话设计的不够合理，横轴应该是规则集下锁申请的平均数量。而不是规则的数量

# 文件路径
base_path = r"E:\研究生信息收集\论文材料\IoT-Event-Detector\Synchronizer\Mutex\Atomicity\Unit\Data\DeviceName"
file_prefixes = ["device_name"]
rule_counts = [5, 10, 15, 20, 25]

# 初始化颜色和线条样式，便于区分
types_styles = {
    "device_name": {"color": "blue", "linestyle": "-", "label": "Device Name Lock"},
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
plt.figure(figsize=(12, 8))

# 绘制主图，展示 room, device_type, device_name
for prefix in ["device_name"]:
    style = types_styles[prefix]
    plt.plot(rule_counts, all_data[prefix], color=style["color"], linestyle=style["linestyle"], marker="o",
             label=style["label"])

# 为 home 单独设置右侧刻度轴
ax = plt.gca()

# 动态计算 Y 轴刻度
main_max_time = max(max(all_data[prefix]) for prefix in ["device_name"])
main_min_time = min(min(all_data[prefix]) for prefix in ["device_name"])
main_y_ticks = np.arange(0, main_max_time + 0.5, 0.5)  # 主图刻度间隔为 0.5
ax.set_yticks(main_y_ticks)

# 图表标题和标签
plt.title("Average Lock Apply Time vs. Lock Apply Total Numbers", fontsize=14)
ax.set_xlabel("Number of Rules", fontsize=12)
ax.set_ylabel("Average Lock Apply Time for Device_Name Lock(s)", fontsize=12)
plt.xticks(rule_counts, fontsize=10)
ax.tick_params(axis='y', labelsize=10)
ax.grid(True, linestyle="--", alpha=0.6)

# 合并图例
lines_1, labels_1 = ax.get_legend_handles_labels()
ax.legend(lines_1, labels_1, loc="upper left", fontsize=10)

# 保存和显示
output_image_path = os.path.join("lock_apply_time_analysis.png")
plt.show()
