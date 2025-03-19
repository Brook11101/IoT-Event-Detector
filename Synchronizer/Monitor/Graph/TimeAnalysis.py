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


def plot_in_out_together():
    data_for_plot, op_labels = gather_in_out_data()

    # 一共 5 组, 每组 2 个箱线 => 10 个箱线
    # 在 x 轴上, 采用如下 positions 布局:
    # group1(num_ops=1): x=1(in), x=2(out)
    # group2(num_ops=2): x=4(in), x=5(out)
    # group3(num_ops=3): x=7(in), x=8(out)
    # group4(num_ops=4): x=10(in), x=11(out)
    # group5(num_ops=5): x=13(in), x=14(out)
    positions = [1,2, 4,5, 7,8, 10,11, 13,14]

    # 为在 x 轴上显示标签，居中显示 => (1.5, 4.5, 7.5, 10.5, 13.5)
    xtick_positions = [1.5, 4.5, 7.5, 10.5, 13.5]

    fig, ax = plt.subplots(figsize=(10, 6))

    # 绘制箱线图
    box = ax.boxplot(
        data_for_plot,
        positions=positions,
        showmeans=True,
        meanline=True,
        patch_artist=True,
        whis=1.5
    )

    # 颜色区分: InMonitor(浅蓝), OutMonitor(浅绿)
    # 切记 data_for_plot[i], i 是 0~9, 奇偶区分
    in_color  = "#87CEFA"  # 浅蓝
    out_color = "#90EE90"  # 浅绿

    for i, patch in enumerate(box['boxes']):
        if i % 2 == 0:
            # InMonitor
            patch.set_facecolor(in_color)
        else:
            # OutMonitor
            patch.set_facecolor(out_color)
        patch.set_alpha(0.5)

    # 中位数线(红色实线)
    for median in box['medians']:
        median.set(color='red', linewidth=1.5)

    # 均值线(蓝色虚线)
    for mean_line in box['means']:
        mean_line.set(color='blue', linestyle='--')

    # 异常值 - 使用白色圆点
    for flier in box['fliers']:
        flier.set(marker='o', markerfacecolor='white', alpha=0.9, markeredgecolor='black')

    # 设置 x 轴标签 & 刻度
    plt.xticks(xtick_positions, [str(lab) for lab in op_labels], fontsize=16)

    # 对数刻度 (base=2), 范围 2^0 -> 2^4
    ax.set_yscale("log", base=2)
    ax.set_ylim(1, 16)  # 若实际数据超出此范围, 需调整
    y_locs = [1,2,4,8,16]
    y_labels = [r"$2^0$", r"$2^1$", r"$2^2$", r"$2^3$", r"$2^4$"]
    plt.yticks(y_locs, y_labels, fontsize=16)

    # 手动创建图例
    in_patch = mpatches.Patch(color=in_color,  alpha=0.5, label='Using Monitor')
    out_patch= mpatches.Patch(color=out_color, alpha=0.5, label='Not Using Monitor')
    median_line = mlines.Line2D([], [], color='red', linewidth=1.5, label='Median')
    mean_line   = mlines.Line2D([], [], color='blue', linestyle='--', label='Mean')
    outlier_dot = mlines.Line2D([], [], color='black', marker='o', markerfacecolor='white',
                                linestyle='None', alpha=0.9, label='Outliers')
    plt.legend(
        handles=[in_patch, out_patch, median_line, mean_line, outlier_dot],
        loc='upper left'
    )

    # 坐标轴标题 & 图标题, 字号=16
    plt.xlabel("Num of Operations", fontsize=16)
    plt.ylabel("Execution Time (s)", fontsize=16)
    plt.title("Execution time distribution with and without Monitor", fontsize=16)

    # 虚线网格 (y 方向)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    output_file = "in_out_monitor_comparison.svg"
    plt.savefig(output_file, format="svg")

    plt.show()


if __name__ == "__main__":
    plot_in_out_together()
