import os
import numpy as np
import matplotlib.pyplot as plt

# 下面的两行是用于生成图例中线条和色块的对象
import matplotlib.lines as mlines
import matplotlib.patches as mpatches

def read_execution_times(base_path, group_number):
    """
    从 time_lockwith_group_{group_number}.txt 中读取所有的执行时间，
    返回一个一维列表，包含该 group 所有轮次的全部线程耗时（已展开）。
    """
    filename = os.path.join(base_path, f"time_lockwith_group_{group_number}.txt")
    all_times = []

    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # 每行是一轮的执行时间列表，用逗号分隔
            str_times = line.split(',')
            # 转成浮点数
            float_times = [float(t) for t in str_times]
            # 将这一轮的所有线程时间追加到 all_times
            all_times.extend(float_times)

    return all_times


def plot_box_lockwith():
    """
    读取 5 个 time_lockwith_group_X.txt 文件，绘制箱线图。
      - 横轴: [20, 40, 60, 80, 100] 代表不同冲突对数量
      - 纵轴: 执行时间(s)
      - 所有箱子使用统一颜色 (不区分组)
      - 添加图例说明 (Box / Median / Mean / Outliers)
    """
    base_path = r"E:\研究生信息收集\论文材料\IoT-Event-Detector\Synchronizer\Mutex\LLSC\Data\LockWith"

    conflict_labels = [20, 40, 60, 80, 100]

    data_for_5_groups = []
    for gnum in range(1, 6):
        g_times = read_execution_times(base_path, gnum)
        data_for_5_groups.append(g_times)

    # 创建画布
    plt.figure(figsize=(8, 6))

    # 绘制箱线图
    box = plt.boxplot(data_for_5_groups,
                      labels=conflict_labels,  # 横轴标签
                      showmeans=True,          # 显示均值
                      meanline=True,           # 均值用线段表示
                      patch_artist=True        # 允许为箱子填充颜色
                     )

    # ---------------------------
    # (1) 给所有箱子用统一颜色
    # ---------------------------
    box_color = "#87CEFA"  # 浅蓝色示例
    for patch in box['boxes']:
        patch.set_facecolor(box_color)
        patch.set_alpha(0.5)

    # ---------------------------
    # (2) 中位数线(红色实线)
    # ---------------------------
    for median in box['medians']:
        median.set(color='red', linewidth=1.5)

    # ---------------------------
    # (3) 均值线(蓝色虚线)
    # ---------------------------
    for mean_line in box['means']:
        mean_line.set(color='blue', linestyle='--')

    # ---------------------------
    # (4) 异常值(Outliers)红色圆点
    # ---------------------------
    for flier in box['fliers']:
        flier.set(marker='o', markerfacecolor='red', alpha=0.5)

    # ---------------------------
    # (5) 手动创建图例(legend)
    # ---------------------------
    #   ①箱子 ②中位数 ③均值 ④离群值
    box_patch = mpatches.Patch(color=box_color, alpha=0.5, label='Box (IQR range)')
    median_line = mlines.Line2D([], [], color='red', linewidth=1.5, label='Median')
    mean_line   = mlines.Line2D([], [], color='blue', linestyle='--', label='Mean')
    outlier_dot = mlines.Line2D([], [], color='red', marker='o', linestyle='None', alpha=0.5, label='Outliers')

    # 将它们组合进 legend
    plt.legend(handles=[box_patch, median_line, mean_line, outlier_dot],
               loc='best')  # loc='best' 会自动选择合适的位置

    # 设置X轴、Y轴标签和标题
    plt.xlabel("Number of Potential Mutex Conflicts", fontsize=12)
    plt.ylabel("Execution Time (s)", fontsize=12)
    plt.title("Execution Time Distribution On Block Mutex", fontsize=14)

    # 动态设置y轴刻度:每2个单位一格
    max_val = max(max(g_times) for g_times in data_for_5_groups)
    step = 2
    y_ticks = np.arange(0, max_val + step, step)
    plt.yticks(y_ticks)

    # 显示 y方向网格
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    plot_box_lockwith()
