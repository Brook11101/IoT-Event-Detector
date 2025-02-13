import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.ticker as ticker

# 实验数据存储的根目录
BASE_DIR = r"E:\研究生信息收集\论文材料\IoT-Event-Detector\Synchronizer\CV\Data"
NUM_OF_OPERATIONS = [1, 2, 3, 4, 5]  # 实验操作次数

# 存储计算结果
cri_withcv = []
cri_talock = []
cri_llsc = []
trigger_counts = []

# 读取数据并计算平均值
def read_avg(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            values = [int(line.strip()) for line in f.readlines()]
            return np.mean(values) if values else 0
    return 0

# 遍历每个 num_of_operations
for num_ops in NUM_OF_OPERATIONS:
    exp_dir = os.path.join(BASE_DIR, f"num_of_operations_{num_ops}")
    cri_withcv.append(read_avg(os.path.join(exp_dir, "withcv_num.txt")))
    cri_talock.append(read_avg(os.path.join(exp_dir, "withoutcv_talock_num.txt")))
    cri_llsc.append(read_avg(os.path.join(exp_dir, "withoutcv_llsc_num.txt")))
    trigger_counts.append(read_avg(os.path.join(exp_dir, "log_num.txt")))

# 转换数据为 DataFrame 以便绘图
df = pd.DataFrame({
    "Num of Operations": NUM_OF_OPERATIONS,
    "WithCV": cri_withcv,
    "WithoutCV_TALOCK": cri_talock,
    "WithoutCV_LLSC": cri_llsc,
    "Triggered Rules": trigger_counts
})

# 创建图和轴
fig, ax = plt.subplots(figsize=(8, 6))

# 设定 y 轴刻度：0～220，每 20 一步
all_ticks = np.arange(0, 221, 20)
ax.set_yticks(all_ticks)
# 如果想让 Matplotlib 不自动加小刻度
ax.yaxis.set_major_locator(ticker.FixedLocator(all_ticks))

# 设置 y 轴范围：略微把下限设到 -1，避免 0 值的柱子紧贴 x 轴
ax.set_ylim(-1, 220)

# X 轴位置
index = np.arange(len(NUM_OF_OPERATIONS))
bar_width = 0.2

# 画柱状图
bars_withcv = ax.bar(index - 1.5 * bar_width, df["WithCV"], bar_width,
                     label="WithCV", color="red", edgecolor='black', hatch='/')
bars_talock = ax.bar(index - 0.5 * bar_width, df["WithoutCV_TALOCK"], bar_width,
                     label="WithoutCV_TALOCK", color="orange", edgecolor='black', hatch='\\')
bars_llsc = ax.bar(index + 0.5 * bar_width, df["WithoutCV_LLSC"], bar_width,
                   label="WithoutCV_LLSC", color="brown", edgecolor='black', hatch='-')

# 画折线图
ax.plot(index, df["Triggered Rules"], marker='o', linestyle='-', color='blue',
        label="Triggered Rules", markersize=6, linewidth=2)

# 设置 x 轴刻度和标签
ax.set_xticks(index)
ax.set_xticklabels(NUM_OF_OPERATIONS)
ax.set_xlabel("Num of Operations")
ax.set_ylabel("Count")

# 给柱形图添加数值标签的函数
def add_bar_labels(ax, bars, offset=0.5):
    """在每个柱子上方标注数值，offset 表示数值距离柱顶的偏移量"""
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,  # x 坐标：柱子中点
            height + offset,                   # y 坐标：柱子高度 + offset
            f"{height:.0f}",                   # 显示数值（整数）
            ha='center', va='bottom', fontsize=9
        )

# 分别给三组柱状图添加数值标签
add_bar_labels(ax, bars_withcv)
add_bar_labels(ax, bars_talock)
add_bar_labels(ax, bars_llsc)

# 图例和标题
ax.legend(loc="upper left")
ax.set_title("Race Condition Violations Detection vs Num of Operations")

plt.tight_layout()
plt.show()
