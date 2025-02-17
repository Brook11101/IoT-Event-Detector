import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.ticker as ticker

# 使用 Seaborn 样式
plt.style.use("seaborn")

# 实验数据存储的根目录
BASE_DIR = r"E:\研究生信息收集\论文材料\IoT-Event-Detector\Synchronizer\Monitor\Data"
NUM_OF_OPERATIONS = [1, 2, 3, 4, 5]  # 实验操作次数

# 存储计算结果
trigger_counts = []
inmonitor_counts = []
outmonitor_counts = []

# 读取数据并计算平均值
def read_avg(file_path):
    """读取文件中的数值并计算平均值"""
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            values = [int(line.strip()) for line in f.readlines()]
            return np.mean(values) if values else 0
    return 0

# 遍历每个 num_of_operations
for num_ops in NUM_OF_OPERATIONS:
    exp_dir = os.path.join(BASE_DIR, f"num_of_operations_{num_ops}")
    trigger_counts.append(read_avg(os.path.join(exp_dir, "log_num.txt")))
    inmonitor_counts.append(read_avg(os.path.join(exp_dir, "inmonitor_num.txt")))
    outmonitor_counts.append(read_avg(os.path.join(exp_dir, "outmonitor_num.txt")))

# 转换数据为 DataFrame 以便绘图
df = pd.DataFrame({
    "Num of Operations": NUM_OF_OPERATIONS,
    "Triggered Rules": trigger_counts,
    "InMonitor": inmonitor_counts,
    "OutMonitor": outmonitor_counts
})

# 创建图和轴
fig, ax = plt.subplots(figsize=(8, 6))

# 去掉顶部和右侧的边框脊，使图更简洁
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)

# 设定 y 轴刻度：0～220，每 20 一步
all_ticks = np.arange(0, 211, 10)
ax.set_yticks(all_ticks)
ax.yaxis.set_major_locator(ticker.FixedLocator(all_ticks))
ax.set_ylim(-1, 220)

# 给 x 轴稍微留点左右空白，让首尾柱子不紧贴边框
ax.margins(x=0.1)

# 画柱状图
index = np.arange(len(NUM_OF_OPERATIONS))
bar_width = 0.2

bars_inmonitor = ax.bar(index - 0.5 * bar_width, df["InMonitor"], bar_width,
                         label="Use Monitor", color="brown", edgecolor='black', hatch='/')
bars_outmonitor = ax.bar(index + 0.5 * bar_width, df["OutMonitor"], bar_width,
                          label="Not Use Monitor", color="orange", edgecolor='black', hatch='/')

# 画折线图
ax.plot(index, df["Triggered Rules"], marker='o', linestyle='-', color='blue',
        label="Triggered Rules", markersize=6, linewidth=2)

# 在折线图上也添加数值标签
for x_, y_ in zip(index, df["Triggered Rules"]):
    ax.text(x_, y_+3, f"{y_:.0f}", ha="center", va="bottom", fontsize=9, color="blue")

# 设置 x 轴刻度和标签
ax.set_xticks(index)
ax.set_xticklabels(NUM_OF_OPERATIONS)
ax.set_xlabel("Num of Operations")
ax.set_ylabel("Race Condition Conflict Count")

# 让图显示水平网格线（只在 Y 轴方向），便于对比数值
ax.yaxis.grid(True, linestyle='--', alpha=0.7)
ax.xaxis.grid(False)

# 给柱形图添加数值标签的函数
def add_bar_labels(ax, bars, offset=0.5):
    """在每个柱子上方标注数值"""
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + offset,
            f"{height:.0f}",
            ha='center', va='bottom', fontsize=9
        )

# 给柱状图添加数值标签
add_bar_labels(ax, bars_inmonitor)
add_bar_labels(ax, bars_outmonitor)

# 图例放在图外右侧，以防止遮挡数据
ax.legend(loc='best', borderaxespad=0.)

ax.set_title("Race Condition Violations Detection With/WithOut Monitor")

plt.tight_layout()
plt.show()
