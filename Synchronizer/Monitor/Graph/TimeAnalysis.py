import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.lines as mlines
import matplotlib.patches as mpatches

# **启用 Seaborn 风格**
sns.set_theme(style="darkgrid")

# **实验数据目录**
BASE_DIR = r"E:\研究生信息收集\论文材料\IoT-Event-Detector\Synchronizer\Monitor\Data"
NUM_OF_OPERATIONS = [1, 2, 3, 4, 5]  # 扰动次数

# **读取执行时间数据**
def read_execution_times(file_path):
    """读取 `time.txt` 文件中的执行时间，每行是一个逗号分隔的时间列表，转换为秒 (s)"""
    if not os.path.exists(file_path):
        print(f"文件 {file_path} 不存在，跳过。")
        return []

    execution_times = []  # 存储当前 `num_ops` 下的所有时间数据
    with open(file_path, "r") as f:
        for line in f:
            try:
                time_list = [float(value.strip()) / 1000.0 for value in line.strip().split(",")]  # **转换为秒**
                execution_times.append(time_list)
            except Exception as e:
                print(f"解析失败: {e}, 行内容: {line.strip()}")

    # **展平数据（因为每轮是列表）**
    return [t for sublist in execution_times for t in sublist]

# **读取 InMonitor 的执行时间**
inmonitor_execution_times = []

for num_ops in NUM_OF_OPERATIONS:
    exp_dir = os.path.join(BASE_DIR, f"num_of_operations_{num_ops}")
    inmonitor_execution_times.append(read_execution_times(os.path.join(exp_dir, "inmonitor_time.txt")))

# **创建 Matplotlib 图**
fig, ax = plt.subplots(figsize=(10, 6))

# **绘制箱线图**
box = ax.boxplot(
    inmonitor_execution_times,
    labels=[str(num) for num in NUM_OF_OPERATIONS],
    showmeans=True,   # 显示均值
    meanline=True,    # 均值用线段表示
    patch_artist=True, # 允许箱子填充颜色
    whis=3
)

# ========== 样式设置 (与示例图一致) ==========
# 1) 统一使用浅蓝色箱子
box_color = "#87CEFA"
for patch in box['boxes']:
    patch.set_facecolor(box_color)
    patch.set_alpha(0.5)

# 2) 中位数线(红色实线)
for median in box['medians']:
    median.set(color='red', linewidth=1.5)

# 3) 均值线(蓝色虚线)
for mean_line in box['means']:
    mean_line.set(color='blue', linestyle='--')

# 4) 异常值(Outliers)红色圆点
for flier in box['fliers']:
    flier.set(marker='o', markerfacecolor='red', alpha=0.5)

# ========== 动态设置 y 轴刻度 ==========
y_max = max(max(times) for times in inmonitor_execution_times if times)
y_step = round(y_max / 10, 1)
y_ticks = np.arange(0, 10, 0.2)  # **Y 轴刻度 0.2s 递增**
plt.yticks(y_ticks)

# ========== 手动创建图例 (legend) ==========
box_patch   = mpatches.Patch(color=box_color, alpha=0.5, label='Box (IQR range)')
median_line = mlines.Line2D([], [], color='red', linewidth=1.5, label='Median')
mean_line   = mlines.Line2D([], [], color='blue', linestyle='--', label='Mean')
outlier_dot = mlines.Line2D([], [], color='red', marker='o', linestyle='None', alpha=0.5, label='Outliers')
plt.legend(handles=[box_patch, median_line, mean_line, outlier_dot], loc='upper left')

# ========== 图表设置 ==========
plt.xlabel("Num of Operations", fontsize=14, fontweight="bold")
plt.ylabel("Execution Time (s)", fontsize=14, fontweight="bold")
plt.title("Execution Time Distribution Using Monitor", fontsize=16, fontweight="bold")

# ========== 添加虚线网格 ==========
plt.grid(axis='y', linestyle='--', alpha=0.7)

# 调整布局
plt.tight_layout()

# **显示 InMonitor 图**
plt.show()

