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


def plot_two_categories_box():
    data_for_plot, op_labels = gather_two_categories()

    # 共有 5 组，每组 2 条箱线 => 共 10 个箱线图
    # 分别放在下述 x 位置:
    # 第1组: x=1,2    第2组: x=4,5
    # 第3组: x=7,8    第4组: x=10,11
    # 第5组: x=13,14
    positions = [1, 2, 4, 5, 7, 8, 10, 11, 13, 14]

    # 用于设置 x 轴刻度的中间位置
    group_centers = [1.5, 4.5, 7.5, 10.5, 13.5]

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

    # 颜色区分
    color_time = "#87CEFA"  # 浅蓝 => withcv_time
    color_lock = "#90EE90"  # 浅绿 => withcv_lock_time

    # 给两个类别着色
    for i, patch in enumerate(box['boxes']):
        if i % 2 == 0:
            # withcv_time
            patch.set_facecolor(color_time)
        else:
            # withcv_lock_time
            patch.set_facecolor(color_lock)
        patch.set_alpha(0.5)

    # 中位数线(红色)
    for median in box['medians']:
        median.set(color='red', linewidth=1.5)

    # 均值线(蓝色虚线)
    for mean_line in box['means']:
        mean_line.set(color='blue', linestyle='--')

    # 异常值 => 白色圆点
    for flier in box['fliers']:
        flier.set(marker='o', markerfacecolor='white', alpha=0.9, markeredgecolor='black')

    # x 轴
    plt.xticks(group_centers, [str(n) for n in op_labels], fontsize=16)
    plt.xlabel("Num of Operations", fontsize=16)

    # y 轴设为 2 为底的对数刻度, 范围 1~16 (2^0 ~ 2^4)
    ax.set_yscale("log", base=2)
    ax.set_ylim(1, 16)
    y_locs = [1, 2, 4, 8, 16]
    y_labels = [r"$2^0$", r"$2^1$", r"$2^2$", r"$2^3$", r"$2^4$"]
    plt.yticks(y_locs, y_labels, fontsize=16)
    plt.ylabel("Execution Time (s)", fontsize=16)

    # 手动创建图例
    time_patch = mpatches.Patch(color=color_time, alpha=0.5, label="CV Using LL/SC-Mutex")
    lock_patch = mpatches.Patch(color=color_lock, alpha=0.5, label="CV Using CAS-Mutex")
    median_line = mlines.Line2D([], [], color='red', linewidth=1.5, label='Median')
    mean_line = mlines.Line2D([], [], color='blue', linestyle='--', label='Mean')
    outlier_dot = mlines.Line2D([], [], color='black', marker='o', markerfacecolor='white',
                                linestyle='None', alpha=0.9, label='Outliers')
    plt.legend(handles=[time_patch, lock_patch, median_line, mean_line, outlier_dot],
               loc='upper left', fontsize=10)

    # 标题
    plt.title("Execution time distribution of CV using different mutex", fontsize=16)

    # 网格: Y 方向虚线
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    plt.tight_layout()

    output_file = "cv_time_comparison.svg"
    plt.savefig(output_file, format="svg")

    plt.show()


if __name__ == "__main__":
    plot_two_categories_box()
