import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.lines as mlines
import matplotlib.patches as mpatches

# 使用 Seaborn "darkgrid" 风格
sns.set_theme(style="darkgrid")

# 实验数据目录
BASE_DIR = r"E:\研究生信息收集\论文材料\IoT-Event-Detector\Synchronizer\Monitor\Data"
NUM_OF_OPERATIONS = [1, 2, 3, 4, 5]  # 扰动次数

def read_execution_times(file_path):
    """
    读取给定路径下的逗号分隔时间（毫秒），转换为秒返回平坦列表
    """
    if not os.path.exists(file_path):
        print(f"文件 {file_path} 不存在，跳过。")
        return []

    execution_times = []
    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                # 转为秒
                time_list = [float(value.strip()) / 1000.0 for value in line.split(",")]
                execution_times.extend(time_list)
            except Exception as e:
                print(f"解析失败: {e}, 行内容: {line.strip()}")
    return execution_times

def gather_in_out_data():
    """
    依次读取 NUM_OF_OPERATIONS 下 inmonitor_time.txt / outmonitor_time.txt
    共得到 10 份数据 (每个 num_ops 对应 2 份).
    返回一个按顺序排列的列表 data_for_plot:
      [ inmonitor(ops=1), outmonitor(ops=1),
        inmonitor(ops=2), outmonitor(ops=2),
        ...
        inmonitor(ops=5), outmonitor(ops=5) ]
    以及 xlabels: 5 个标签(1,2,3,4,5)
    """
    data_for_plot = []

    for num_ops in NUM_OF_OPERATIONS:
        exp_dir = os.path.join(BASE_DIR, f"num_of_operations_{num_ops}")

        # 1) 读取 inmonitor
        in_path = os.path.join(exp_dir, "inmonitor_time.txt")
        in_data = read_execution_times(in_path)
        data_for_plot.append(in_data)

        # 2) 读取 outmonitor
        out_path = os.path.join(exp_dir, "outmonitor_time.txt")
        out_data = read_execution_times(out_path)
        data_for_plot.append(out_data)

    return data_for_plot, NUM_OF_OPERATIONS


def plot_in_out_separate():
    """
    将原先合并在一张图中的数据，拆分为两张图：
      - 图1: Using Monitor (inmonitor_time.txt)
      - 图2: Not Using Monitor (outmonitor_time.txt)
    每张图都是5个箱线图，positions = 1..5
    """
    data_for_plot, op_labels = gather_in_out_data()

    # data_for_plot 长度=10, 下标从0到9:
    #   偶数下标 (0,2,4,6,8) => inmonitor
    #   奇数下标 (1,3,5,7,9) => outmonitor
    inmonitor_data  = [data_for_plot[i] for i in range(0, 10, 2)]
    outmonitor_data = [data_for_plot[i] for i in range(1, 10, 2)]

    # 颜色区分
    in_color  = "#87CEFA"  # 浅蓝
    out_color = "#90EE90"  # 浅绿

    # 通用的x轴位置 => 5个箱线 => x=1..5
    x_positions = range(1, 6)

    # 通用的 y 轴对数刻度 => 范围 2^0 ~ 2^4
    y_locs   = [1, 2, 4, 8, 16]
    y_labels = [r"$2^0$", r"$2^1$", r"$2^2$", r"$2^3$", r"$2^4$"]

    # ========== 图1: Using Monitor ==========
    plt.figure(figsize=(7, 5))
    box_in = plt.boxplot(
        inmonitor_data,
        positions=x_positions,
        showmeans=True,
        meanline=True,
        patch_artist=True,
        whis=1.5,
        widths=0.5       # 通过此参数缩小箱线宽度
    )

    # 上色：Using Monitor
    for patch in box_in['boxes']:
        patch.set_facecolor(in_color)
        patch.set_alpha(0.5)

    # 中位数 / 均值 / 异常值
    for median in box_in['medians']:
        median.set(color='red', linewidth=1.5)
    for mean_line in box_in['means']:
        mean_line.set(color='blue', linestyle='--')
    for flier in box_in['fliers']:
        flier.set(marker='o', markerfacecolor='white', alpha=0.9, markeredgecolor='black')

    # X 轴
    plt.xticks(x_positions, [str(op) for op in op_labels], fontsize=16)
    plt.xlabel("Num of Operations", fontsize=16)

    # Y 轴(对数刻度)
    plt.yscale("log", base=2)
    plt.ylim(1, 16)
    plt.yticks(y_locs, y_labels, fontsize=16)
    plt.ylabel("Execution Time (s)", fontsize=16)

    # 图例
    in_patch     = mpatches.Patch(color=in_color, alpha=0.5, label="Using Monitor")
    median_line  = mlines.Line2D([], [], color='red', linewidth=1.5, label='Median')
    mean_line    = mlines.Line2D([], [], color='blue', linestyle='--', label='Mean')
    outlier_dot  = mlines.Line2D([], [], color='black', marker='o', markerfacecolor='white',
                                 linestyle='None', alpha=0.9, label='Outliers')
    plt.legend(handles=[in_patch, median_line, mean_line, outlier_dot],
               loc='upper left', fontsize=10)

    plt.title("Execution Time Distribution Using Monitor", fontsize=16)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig("inmonitor_distribution.svg", format="svg")
    plt.show()


    # ========== 图2: Not Using Monitor ==========
    plt.figure(figsize=(7, 5))
    box_out = plt.boxplot(
        outmonitor_data,
        positions=x_positions,
        showmeans=True,
        meanline=True,
        patch_artist=True,
        whis=1.5,
        widths=0.5       # 同样这里也缩小箱线宽度
    )

    # 上色：Not Using Monitor
    for patch in box_out['boxes']:
        patch.set_facecolor(out_color)
        patch.set_alpha(0.5)

    # 中位数 / 均值 / 异常值
    for median in box_out['medians']:
        median.set(color='red', linewidth=1.5)
    for mean_line in box_out['means']:
        mean_line.set(color='blue', linestyle='--')
    for flier in box_out['fliers']:
        flier.set(marker='o', markerfacecolor='white', alpha=0.9, markeredgecolor='black')

    # X 轴
    plt.xticks(x_positions, [str(op) for op in op_labels], fontsize=16)
    plt.xlabel("Num of Operations", fontsize=16)

    # Y 轴(对数刻度)
    plt.yscale("log", base=2)
    plt.ylim(1, 16)
    plt.yticks(y_locs, y_labels, fontsize=16)
    plt.ylabel("Execution Time (s)", fontsize=16)

    # 图例
    out_patch   = mpatches.Patch(color=out_color, alpha=0.5, label="Not Using Monitor")
    median_line = mlines.Line2D([], [], color='red', linewidth=1.5, label='Median')
    mean_line   = mlines.Line2D([], [], color='blue', linestyle='--', label='Mean')
    outlier_dot = mlines.Line2D([], [], color='black', marker='o', markerfacecolor='white',
                                linestyle='None', alpha=0.9, label='Outliers')
    plt.legend(handles=[out_patch, median_line, mean_line, outlier_dot],
               loc='upper left', fontsize=10)

    plt.title("Execution Time Distribution Not Using Monitor", fontsize=16)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig("outmonitor_distribution.svg", format="svg")
    plt.show()


if __name__ == "__main__":
    # 调用拆分后的绘图函数
    plot_in_out_separate()
