import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.ticker as ticker

# -- 如果你想使用 Seaborn 样式，不想要可去掉 --
plt.style.use("seaborn")

# 实验数据存储的根目录
BASE_DIR = r"E:\研究生信息收集\论文材料\IoT-Event-Detector\Synchronizer\CV\Data"
NUM_OF_OPERATIONS = [1, 2, 3, 4,5]  # 实验操作次数

# 存储计算结果
cri_withcv = []
cri_talock = []
cri_llsc = []
cri_without = []  # 新增，用于存储 without_num.txt 的数据
trigger_counts = []

def read_avg(file_path):
    """读取文件并返回内容的均值"""
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
    cri_without.append(read_avg(os.path.join(exp_dir, "without_num.txt")))   # 新增
    trigger_counts.append(read_avg(os.path.join(exp_dir, "log_num.txt")))

# 转换数据为 DataFrame 以便绘图
df = pd.DataFrame({
    "Num of Operations": NUM_OF_OPERATIONS,
    "WithCV": cri_withcv,
    "WithoutCV_TALOCK": cri_talock,
    "WithoutCV_LLSC": cri_llsc,
    "Without": cri_without,  # 新增
    "Triggered Rules": trigger_counts
})

# 创建图和轴
fig, ax = plt.subplots(figsize=(8, 6))

# 去掉顶部和右侧的边框脊，使图更简洁
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)

# 设定 y 轴刻度：0～220，每 20 一步
all_ticks = np.arange(0, 221, 20)
ax.set_yticks(all_ticks)
# 不自动加小刻度
ax.yaxis.set_major_locator(ticker.FixedLocator(all_ticks))

# 设置 y 轴范围：略微把下限设到 -1，避免 0 值的柱子紧贴 x 轴
ax.set_ylim(-1, 220)

# 给 x 轴稍微留点左右空白，让首尾柱子不紧贴边框
ax.margins(x=0.1)

# 画柱状图
index = np.arange(len(NUM_OF_OPERATIONS))
bar_width = 0.15

# 1) WithCV (红色, 斜线)
bars_withcv = ax.bar(index - 1.5 * bar_width, df["WithCV"], bar_width,
                     label="WithCV", color="red", edgecolor='black', hatch='/')

# 2) WithoutCV_TALOCK (橙色, 反斜线)
bars_talock = ax.bar(index - 0.5 * bar_width, df["WithoutCV_TALOCK"], bar_width,
                     label="WithoutCV_TALOCK", color="orange", edgecolor='black', hatch='\\')

# 3) WithoutCV_LLSC (棕色, 横线)
bars_llsc = ax.bar(index + 0.5 * bar_width, df["WithoutCV_LLSC"], bar_width,
                   label="WithoutCV_LLSC", color="brown", edgecolor='black', hatch='-')

# 4) Without (绿色, “x” 阴影)
bars_without = ax.bar(index + 1.5 * bar_width, df["Without"], bar_width,
                      label="Without", color="green", edgecolor='black', hatch='x')

# 画折线图: 触发规则数
ax.plot(index, df["Triggered Rules"], marker='o', linestyle='-', color='blue',
        label="Triggered Rules", markersize=6, linewidth=2)

# 在折线图上添加数值标签（可选）
for x_, y_ in zip(index, df["Triggered Rules"]):
    ax.text(x_, y_ + 3, f"{y_:.0f}", ha="center", va="bottom", fontsize=9, color="blue")

# 设置 x 轴刻度和标签
ax.set_xticks(index)
ax.set_xticklabels(NUM_OF_OPERATIONS)
ax.set_xlabel("Num of Operations")
ax.set_ylabel("Count")

# 让图显示水平网格线（只在 Y 轴方向），便于对比数值
ax.yaxis.grid(True, linestyle='--', alpha=0.7)
ax.xaxis.grid(False)

def add_bar_labels(ax, bars, offset=0.5):
    """在每个柱子上方标注数值，offset 表示数值距离柱顶的偏移量"""
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + offset,
            f"{height:.0f}",
            ha='center', va='bottom', fontsize=9
        )

# 分别给四组柱状图添加数值标签
add_bar_labels(ax, bars_withcv)
add_bar_labels(ax, bars_talock)
add_bar_labels(ax, bars_llsc)
add_bar_labels(ax, bars_without)

# 图例位置
ax.legend(loc='best', borderaxespad=0.)

ax.set_title("Race Condition Violations Detection On Different Num of Operations")

plt.tight_layout()
plt.show()
