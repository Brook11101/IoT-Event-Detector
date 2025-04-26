import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.lines as mlines
import matplotlib.patches as mpatches

# 启用 Seaborn "darkgrid" 风格
sns.set_theme(style="darkgrid")

# 实验数据目录
BASE_DIR = r"E:\研究生信息收集\论文材料\IoT-Event-Detector\Synchronizer\CV\Data"
NUM_OF_OPERATIONS = [1, 2, 3, 4, 5]  # 扰动次数 (扩展为1~5)


def read_times_list(file_path, discard_under_1=False):
    """
    从 file_path 中读取数据：每行是一个可 eval() 解析的 list。
    若 discard_under_1=True，则丢弃所有 <1 的数据。
    返回处理后的执行时间列表。
    """
    if not os.path.exists(file_path):
        print(f"[警告] 文件 {file_path} 不存在: 跳过。")
        return []

    execution_times = []
    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                time_list = eval(line)  # 每行是一个 Python 列表
                if discard_under_1:
                    time_list = [t for t in time_list if t >= 1.0]
                execution_times.extend(time_list)
            except Exception as e:
                print(f"[错误] 解析失败: {e}, 行内容: {line.strip()}")
    return execution_times


def gather_two_categories():
    """
    读取 withcv_time.txt(丢弃 <1s) 和 withcv_lock_time.txt(保留全部) 两种文件。
    对于 num_ops ∈ [1..5]，每个 num_ops 得到 2 份箱线数据:
      - withcv_time
      - withcv_lock_time
    最终返回 (data_for_plot, NUM_OF_OPERATIONS)，
      data_for_plot 的长度 = 5组 × 2类别 = 10 个箱线图数据
    """
    data_for_plot = []
    for num_ops in NUM_OF_OPERATIONS:
        exp_dir = os.path.join(BASE_DIR, f"num_of_operations_{num_ops}")

        # 文件1: withcv_time.txt => 丢弃 <1s
        withcv_path = os.path.join(exp_dir, "withcv_time.txt")
        data_withcv = read_times_list(withcv_path, discard_under_1=True)

        # 文件2: withcv_lock_time.txt => 无需丢弃
        lockcv_path = os.path.join(exp_dir, "withcv_lock_time.txt")
        data_lockcv = read_times_list(lockcv_path, discard_under_1=False)

        data_for_plot.append(data_withcv)
        data_for_plot.append(data_lockcv)

    return data_for_plot, NUM_OF_OPERATIONS


def plot_two_categories_box_separate():
    """
    将原本5组×2种方案(共10个箱线)拆分为2张图，每张图各绘制5个箱线。
      - 图1: CV Using LL/SC-Mutex (withcv_time.txt)
      - 图2: CV Using CAS-Mutex (withcv_lock_time.txt)
    """
    data_for_plot, op_labels = gather_two_categories()

    # data_for_plot有10个元素，下标: 0,1,2,3,4,5,6,7,8,9
    # 下标偶数 => withcv_time   (LL/SC-Mutex)
    # 下标奇数 => withcv_lock_time (CAS-Mutex)

    # 1) 拆分成两组
    withcv_time_data = [data_for_plot[i] for i in range(0, 10, 2)]  # 0,2,4,6,8
    lockcv_time_data = [data_for_plot[i] for i in range(1, 10, 2)]  # 1,3,5,7,9

    # 2) 绘制参数
    color_time = "#87CEFA"  # 浅蓝 => withcv_time
    color_lock = "#90EE90"  # 浅绿 => withcv_lock_time

    # x 轴：5 个箱线 => x=1..5
    x_positions = range(1, 6)

    # y 轴对数刻度: 1~16 => 2^0 ~ 2^4
    y_locs   = [1, 2, 4, 8, 16]
    y_labels = [r"$2^0$", r"$2^1$", r"$2^2$", r"$2^3$", r"$2^4$"]

    # =============== 图1: CV Using LL/SC-Mutex ===============
    plt.figure(figsize=(8, 5))  # 也可自行调整尺寸
    box = plt.boxplot(
        withcv_time_data,
        positions=x_positions,
        showmeans=True,
        meanline=True,
        patch_artist=True,
        whis=1.5
    )

    # 给箱线上色
    for patch in box['boxes']:
        patch.set_facecolor(color_time)
        patch.set_alpha(0.5)

    # 中位数(红色)、均值线(蓝色虚线)
    for median in box['medians']:
        median.set(color='red', linewidth=1.5)
    for mean_line in box['means']:
        mean_line.set(color='blue', linestyle='--')

    # 异常值(白色圆点)
    for flier in box['fliers']:
        flier.set(marker='o', markerfacecolor='white', alpha=0.9, markeredgecolor='black')

    # X/Y轴 & 刻度设置
    plt.xticks(x_positions, [str(n) for n in op_labels], fontsize=16)
    plt.xlabel("Num of Operations", fontsize=16)

    plt.yscale("log", base=2)
    plt.ylim(1, 16)
    plt.yticks(y_locs, y_labels, fontsize=16)
    plt.ylabel("Execution Time (s)", fontsize=16)

    # 图例
    time_patch   = mpatches.Patch(color=color_time, alpha=0.5, label="CV(LL/SC-Mutex)")
    median_line  = mlines.Line2D([], [], color='red', linewidth=1.5, label='Median')
    mean_line    = mlines.Line2D([], [], color='blue', linestyle='--', label='Mean')
    outlier_dot  = mlines.Line2D([], [], color='black', marker='o', markerfacecolor='white',
                                 linestyle='None', alpha=0.9, label='Outliers')
    plt.legend(handles=[time_patch, median_line, mean_line, outlier_dot],
               loc='upper left', fontsize=8)

    plt.title("Execution Time Distribution With CV (LL/SC-Mutex)", fontsize=16)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig("cv_time_llsc.svg", format="svg")
    plt.show()

    # =============== 图2: CV Using CAS-Mutex ===============
    plt.figure(figsize=(8, 5))
    box = plt.boxplot(
        lockcv_time_data,
        positions=x_positions,
        showmeans=True,
        meanline=True,
        patch_artist=True,
        whis=1.5
    )

    # 给箱线上色
    for patch in box['boxes']:
        patch.set_facecolor(color_lock)
        patch.set_alpha(0.5)

    # 中位数(红色)、均值线(蓝色虚线)
    for median in box['medians']:
        median.set(color='red', linewidth=1.5)
    for mean_line in box['means']:
        mean_line.set(color='blue', linestyle='--')

    # 异常值(白色圆点)
    for flier in box['fliers']:
        flier.set(marker='o', markerfacecolor='white', alpha=0.9, markeredgecolor='black')

    # X/Y轴 & 刻度设置
    plt.xticks(x_positions, [str(n) for n in op_labels], fontsize=16)
    plt.xlabel("Num of Operations", fontsize=16)

    plt.yscale("log", base=2)
    plt.ylim(1, 16)
    plt.yticks(y_locs, y_labels, fontsize=16)
    plt.ylabel("Execution Time (s)", fontsize=16)

    # 图例
    lock_patch   = mpatches.Patch(color=color_lock, alpha=0.5, label="CV(CAS-Mutex)")
    median_line  = mlines.Line2D([], [], color='red', linewidth=1.5, label='Median')
    mean_line    = mlines.Line2D([], [], color='blue', linestyle='--', label='Mean')
    outlier_dot  = mlines.Line2D([], [], color='black', marker='o', markerfacecolor='white',
                                 linestyle='None', alpha=0.9, label='Outliers')
    plt.legend(handles=[lock_patch, median_line, mean_line, outlier_dot],
               loc='upper left', fontsize=8)

    plt.title("Execution Time Distribution With CV (CAS-Mutex)", fontsize=16)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig("cv_time_cas.svg", format="svg")
    plt.show()


if __name__ == "__main__":
    # 使用拆分后的绘图函数
    plot_two_categories_box_separate()
