import os
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.patches as mpatches

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


def plot_separate():
    # 1. 读取全部数据
    data_for_plot, conflict_labels = gather_all_data()

    # data_for_plot 顺序:
    # [0] group1-LockFree
    # [1] group1-LockOut
    # [2] group1-LockWith
    # [3] group2-LockFree
    # [4] group2-LockOut
    # [5] group2-LockWith
    # ...
    # [12] group5-LockFree
    # [13] group5-LockOut
    # [14] group5-LockWith

    # 2. 拆分成 3 份数据：每份均对应 5 组 conflict
    lockfree_data = [data_for_plot[i] for i in [0, 3, 6, 9, 12]]  # indices 对应 LockFree
    lockout_data  = [data_for_plot[i] for i in [1, 4, 7, 10, 13]] # indices 对应 LockOut
    lockwith_data = [data_for_plot[i] for i in [2, 5, 8, 11, 14]] # indices 对应 LockWith

    # 3. 三种方案的颜色(与之前一致)
    approach_colors = ["#87CEFA", "#FFD700", "#90EE90"]  # 浅蓝 / 金色 / 浅绿
    # 我们这里分别只取每一张图自己的颜色
    color_lockfree = approach_colors[0]
    color_lockout  = approach_colors[1]
    color_lockwith = approach_colors[2]

    # 先准备一些通用的配置参数
    # 大小刻度/范围设置(三张图保持一致)
    y_locs   = [1,2,4,8,16,32,64]  # 2^0 ~ 2^6
    y_labels = [r'$2^0$', r'$2^1$', r'$2^2$', r'$2^3$', r'$2^4$', r'$2^5$', r'$2^6$']

    # ==============
    #   (A) LLSC-Mutex
    # ==============
    plt.figure(figsize=(6, 4))
    box = plt.boxplot(
        lockfree_data,
        positions=range(1, 6),   # 5 组 conflict
        showmeans=True,
        meanline=True,
        patch_artist=True
    )

    # 给箱体上色
    for patch in box['boxes']:
        patch.set_facecolor(color_lockfree)
        patch.set_alpha(0.5)

    # 中位数(红色实线)
    for median in box['medians']:
        median.set(color='red', linewidth=1.5)

    # 均值线(蓝色虚线)
    for mean_line in box['means']:
        mean_line.set(color='blue', linestyle='--')

    # 异常值(白色圆点)
    for flier in box['fliers']:
        flier.set(marker='o', markerfacecolor='white', alpha=0.9)

    plt.xticks(range(1, 6), conflict_labels, fontsize=16)
    plt.yscale("log", base=2)
    plt.ylim(1, 64)
    plt.yticks(y_locs, y_labels, fontsize=16)
    plt.xlabel("Potential Mutex Conflicts in Rule Set", fontsize=16)
    plt.ylabel("Execution Time (s)", fontsize=16)
    plt.title("Execution Time Distribution Using LL/SC-Mutex", fontsize=16)

    # 图例: 仅自己这一种箱线颜色 + 中位数/均值/离群值
    approach_patch = mpatches.Patch(color=color_lockfree, alpha=0.5, label='LL/SC-Mutex')
    median_line = mlines.Line2D([], [], color='red', linewidth=1.5, label='Median')
    mean_line   = mlines.Line2D([], [], color='blue', linestyle='--', label='Mean')
    outlier_dot = mlines.Line2D([], [], color='black', marker='o', markerfacecolor='white',
                                linestyle='None', alpha=0.9, label='Outliers')
    plt.legend(handles=[approach_patch, median_line, mean_line, outlier_dot],
               loc='upper left', fontsize=8)

    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig("mutex_time_llsc.svg", format="svg")
    plt.show()


    # ==============
    #   (B) Without Mutex
    # ==============
    plt.figure(figsize=(6, 4))
    box = plt.boxplot(
        lockout_data,
        positions=range(1, 6),
        showmeans=True,
        meanline=True,
        patch_artist=True
    )

    for patch in box['boxes']:
        patch.set_facecolor(color_lockout)
        patch.set_alpha(0.5)

    for median in box['medians']:
        median.set(color='red', linewidth=1.5)

    for mean_line in box['means']:
        mean_line.set(color='blue', linestyle='--')

    for flier in box['fliers']:
        flier.set(marker='o', markerfacecolor='white', alpha=0.9)

    plt.xticks(range(1, 6), conflict_labels, fontsize=16)
    plt.yscale("log", base=2)
    plt.ylim(1, 64)
    plt.yticks(y_locs, y_labels, fontsize=16)
    plt.xlabel("Potential Mutex Conflicts in Rule Set", fontsize=16)
    plt.ylabel("Execution Time (s)", fontsize=16)
    plt.title("Execution Time Distribution Without Mutex", fontsize=16)

    # 图例
    approach_patch = mpatches.Patch(color=color_lockout, alpha=0.5, label='Without Mutex')
    median_line = mlines.Line2D([], [], color='red', linewidth=1.5, label='Median')
    mean_line   = mlines.Line2D([], [], color='blue', linestyle='--', label='Mean')
    outlier_dot = mlines.Line2D([], [], color='black', marker='o', markerfacecolor='white',
                                linestyle='None', alpha=0.9, label='Outliers')
    plt.legend(handles=[approach_patch, median_line, mean_line, outlier_dot],
               loc='upper left', fontsize=8)

    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig("mutex_time_without.svg", format="svg")
    plt.show()


    # ==============
    #   (C) CAS-Mutex
    # ==============
    plt.figure(figsize=(6, 4))
    box = plt.boxplot(
        lockwith_data,
        positions=range(1, 6),
        showmeans=True,
        meanline=True,
        patch_artist=True
    )

    for patch in box['boxes']:
        patch.set_facecolor(color_lockwith)
        patch.set_alpha(0.5)

    for median in box['medians']:
        median.set(color='red', linewidth=1.5)

    for mean_line in box['means']:
        mean_line.set(color='blue', linestyle='--')

    for flier in box['fliers']:
        flier.set(marker='o', markerfacecolor='white', alpha=0.9)

    plt.xticks(range(1, 6), conflict_labels, fontsize=16)
    plt.yscale("log", base=2)
    plt.ylim(1, 64)
    plt.yticks(y_locs, y_labels, fontsize=16)
    plt.xlabel("Potential Mutex Conflicts in Rule Set", fontsize=16)
    plt.ylabel("Execution Time (s)", fontsize=16)
    plt.title("Execution Time Distribution Using CAS-Mutex", fontsize=16)

    # 图例
    approach_patch = mpatches.Patch(color=color_lockwith, alpha=0.5, label='CAS-Mutex')
    median_line = mlines.Line2D([], [], color='red', linewidth=1.5, label='Median')
    mean_line   = mlines.Line2D([], [], color='blue', linestyle='--', label='Mean')
    outlier_dot = mlines.Line2D([], [], color='black', marker='o', markerfacecolor='white',
                                linestyle='None', alpha=0.9, label='Outliers')
    plt.legend(handles=[approach_patch, median_line, mean_line, outlier_dot],
               loc='upper left', fontsize=8)

    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig("mutex_time_cas.svg", format="svg")
    plt.show()


if __name__ == "__main__":
    plot_separate()
