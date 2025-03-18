import os
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.patches as mpatches

# 应用 seaborn "darkgrid" 风格
sns.set(style="darkgrid")

def read_execution_times(base_path, file_prefix, group_number):
    """
    从 {file_prefix}_group_{group_number}.txt 中读取所有执行时间，返回一个 list (展开后的全部线程耗时)。
    例如: file_prefix='time_lockfree', group_number=1 => time_lockfree_group_1.txt
    """
    filename = os.path.join(base_path, f"{file_prefix}_group_{group_number}.txt")
    all_times = []
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            float_times = [float(t) for t in line.split(',')]
            all_times.extend(float_times)
    return all_times


def gather_all_data():
    """
    返回 (data_for_plot, conflict_labels):
      data_for_plot: 依次存放 15 组箱线数据 [LockFree_20, LockOut_20, LockWith_20, LockFree_40, ...]
      conflict_labels: [20, 40, 60, 80, 100]
    """
    # 根据自己的目录进行修改
    base_path_free = r"E:\研究生信息收集\论文材料\IoT-Event-Detector\Synchronizer\Mutex\LLSC\Data\LockFree"
    base_path_out  = r"E:\研究生信息收集\论文材料\IoT-Event-Detector\Synchronizer\Mutex\LLSC\Data\LockOut"
    base_path_with = r"E:\研究生信息收集\论文材料\IoT-Event-Detector\Synchronizer\Mutex\LLSC\Data\LockWith"

    conflict_labels = [20, 40, 60, 80, 100]
    data_for_plot = []

    for group_num in range(1, 6):
        # 1) LockFree
        lf_data = read_execution_times(base_path_free, "time_lockfree", group_num)
        data_for_plot.append(lf_data)

        # 2) LockOut
        lo_data = read_execution_times(base_path_out,  "time_lockout",  group_num)
        data_for_plot.append(lo_data)

        # 3) LockWith
        lw_data = read_execution_times(base_path_with, "time_lockwith", group_num)
        data_for_plot.append(lw_data)

    return data_for_plot, conflict_labels


def plot_box_all_in_one():
    data_for_plot, conflict_labels = gather_all_data()

    # 5 组 × 3 种方案 = 15 个箱线图
    # 定义每组在 x 轴的分布: group1: x=1,2,3; group2: x=5,6,7; ... group5: x=17,18,19
    positions = [1,2,3, 5,6,7, 9,10,11, 13,14,15, 17,18,19]

    # 不同方案使用的填充色 (示例)
    approach_colors = ["#87CEFA", "#FFD700", "#90EE90"]  # 浅蓝 / 金色 / 浅绿

    plt.figure(figsize=(10, 6))

    # 绘制箱线图
    box = plt.boxplot(
        data_for_plot,
        positions=positions,
        showmeans=True,
        meanline=True,
        patch_artist=True  # 允许填充
    )

    # 1) 分别给 3 种方案的箱体着色
    for i, patch in enumerate(box['boxes']):
        color_idx = i % 3
        patch.set_facecolor(approach_colors[color_idx])
        patch.set_alpha(0.5)

    # 2) 中位数线(红色实线)
    for median in box['medians']:
        median.set(color='red', linewidth=1.5)

    # 3) 均值线(蓝色虚线)
    for mean_line in box['means']:
        mean_line.set(color='blue', linestyle='--')

    # 4) 异常值(Outliers) - 使用白色圆点
    for flier in box['fliers']:
        flier.set(marker='o', markerfacecolor='white', alpha=0.9)

    # 设置 x 轴刻度: 只在各组中间位置[2,6,10,14,18]标注
    plt.xticks([2, 6, 10, 14, 18], conflict_labels, fontsize=16)

    # ========== (1) 对数刻度 ==========
    plt.yscale("log", base=2)

    # ========== (2) y 轴从 2^0 到 2^6 ==========
    plt.ylim(1, 64)  # 1 = 2^0, 64 = 2^6
    # 如果确实想显示 "0" 刻度，log 轴无法在 0 处显示；这里从 1 开始即可

    # 自定义 y 轴刻度为 2^0 ~ 2^6 并显示成指数形式
    y_locs = [1,2,4,8,16,32,64]  # 2^0 ~ 2^6
    y_labels = [r'$2^0$', r'$2^1$', r'$2^2$', r'$2^3$', r'$2^4$', r'$2^5$', r'$2^6$']
    plt.yticks(y_locs, y_labels, fontsize=16)

    # 图例: 3 个方案 + 中位数/均值/离群值
    lockfree_patch = mpatches.Patch(color=approach_colors[0], alpha=0.5, label='LL/SC-Mutex')
    lockout_patch  = mpatches.Patch(color=approach_colors[1], alpha=0.5, label='Without Mutex')
    lockwith_patch = mpatches.Patch(color=approach_colors[2], alpha=0.5, label='CAS-Mutex')

    median_line = mlines.Line2D([], [], color='red', linewidth=1.5, label='Median')
    mean_line   = mlines.Line2D([], [], color='blue', linestyle='--', label='Mean')
    outlier_dot = mlines.Line2D([], [], color='black', marker='o', markerfacecolor='white',
                                linestyle='None', alpha=0.9, label='Outliers')

    plt.legend(
        handles=[lockfree_patch, lockout_patch, lockwith_patch, median_line, mean_line, outlier_dot],
        loc='upper left',
        fontsize=10,

    )

    # 坐标轴标题 & 图标题，字号统一为 16
    plt.xlabel("Potential Mutex Conflicts in Rule Set", fontsize=16)
    plt.ylabel("Execution Time (s)", fontsize=16)
    plt.title("Execution Time Distribution of Three Mutex Schemes", fontsize=16)

    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    # 保存图像为 SVG
    output_path = "mutex_time.svg"
    plt.savefig(output_path, format="svg")

    plt.show()


if __name__ == "__main__":
    plot_box_all_in_one()
