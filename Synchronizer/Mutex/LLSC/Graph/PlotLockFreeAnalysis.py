import os
import numpy as np
import matplotlib.pyplot as plt

import matplotlib.lines as mlines      # 用于在图例中表示线
import matplotlib.patches as mpatches  # 用于在图例中表示色块

def read_execution_times(base_path, group_number):
    """
    从 time_lockfree_group_{group_number}.txt 中读取所有的执行时间,
    返回一个一维列表, 包含该 group 的所有轮次全部线程耗时(已展开).
    """
    filename = os.path.join(base_path, f"time_lockfree_group_{group_number}.txt")
    all_times = []
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # 每行是一轮中的所有线程执行时间(逗号分隔)
            str_times = line.split(',')
            float_times = [float(t) for t in str_times]
            all_times.extend(float_times)
    return all_times

def plot_box_lockfree():
    """
    读取 5 个 time_lockfree_group_X.txt 文件.
      - 统一使用浅蓝色箱子, 红色中位数, 蓝色均值线, 红色异常值
      - 添加图例说明
    """
    base_path = r"E:\研究生信息收集\论文材料\IoT-Event-Detector\Synchronizer\Mutex\LLSC\Data\LockFree"

    conflict_labels = [20, 40, 60, 80, 100]
    data_for_5_groups = []
    for gnum in range(1, 6):
        g_times = read_execution_times(base_path, gnum)
        data_for_5_groups.append(g_times)

    plt.figure(figsize=(8, 6))

    box = plt.boxplot(
        data_for_5_groups,
        labels=conflict_labels,
        showmeans=True,   # 显示均值
        meanline=True,    # 均值用线段表示
        patch_artist=True # 允许箱子填充颜色
    )

    # ========== 样式设置 (与 LockWith/LockOut 统一) ==========
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

    # ========== 手动创建图例 (legend) ==========
    # Box, Median, Mean, Outliers
    box_patch   = mpatches.Patch(color=box_color, alpha=0.5, label='Box (IQR range)')
    median_line = mlines.Line2D([], [], color='red', linewidth=1.5, label='Median')
    mean_line   = mlines.Line2D([], [], color='blue', linestyle='--', label='Mean')
    outlier_dot = mlines.Line2D([], [], color='red', marker='o', linestyle='None', alpha=0.5, label='Outliers')
    plt.legend(handles=[box_patch, median_line, mean_line, outlier_dot], loc='best')

    # ========== 坐标轴、标题等美观设置 ==========
    plt.xlabel("Potential Mutex Conflicts in Rule Set", fontsize=12)
    plt.ylabel("Execution Time (s)", fontsize=12)
    plt.title("Execution Time Distribution On LL/SC Mutex", fontsize=14)

    # ========== 动态设置 y 轴刻度 ==========
    max_val = max(max(g_times) for g_times in data_for_5_groups)
    step = 1
    import numpy as np
    y_ticks = np.arange(0, max_val + step, step)
    plt.yticks(y_ticks)

    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    plot_box_lockfree()
