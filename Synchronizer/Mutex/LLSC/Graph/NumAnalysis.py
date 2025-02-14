import matplotlib.pyplot as plt
import os
import numpy as np

from Synchronizer.Mutex.LLSC.RuleSet import Group1, Group2, Group3, Group4, Group5

# 采用 seaborn 风格
plt.style.use('seaborn')

# 配置路径和方案名称
base_paths = {
    "LockOut": r"E:\研究生信息收集\论文材料\IoT-Event-Detector\Synchronizer\Mutex\LLSC\Data\LockOut",
    "LockWith": r"E:\研究生信息收集\论文材料\IoT-Event-Detector\Synchronizer\Mutex\LLSC\Data\LockWith",
    "LockFree": r"E:\研究生信息收集\论文材料\IoT-Event-Detector\Synchronizer\Mutex\LLSC\Data\LockFree",
}

# 横轴对应的组的全部规则数量
group_rules_nums = [len(Group1), len(Group2), len(Group3), len(Group4), len(Group5)]

group_potential_conflicts = [20, 40, 60, 80, 100]  # 横轴：组号对应的潜在互斥冲突数量


def read_and_average_data(base_path, file_pattern):
    """
    从指定路径读取每组规则文件，并计算20轮冲突数量的平均值（向下取整）。
    """
    averages = []
    for group_number in range(1, 6):  # 遍历组号1~5
        file_path = os.path.join(base_path, file_pattern.format(group_number))
        with open(file_path, "r") as f:
            data = [int(line.strip()) for line in f.readlines()]
            avg = np.floor(np.mean(data))  # 计算平均值并向下取整
            averages.append(avg)
    return averages


# 读取三种方案的数据
results = {
    "No Mutex": read_and_average_data(base_paths["LockOut"], "num_lockout_group_{}.txt"),
    "Block Mutex": read_and_average_data(base_paths["LockWith"], "num_lockwith_group_{}.txt"),
    "LL/SC Mutex": read_and_average_data(base_paths["LockFree"], "num_lockfree_group_{}.txt"),
}

# 设置柱状图宽度
bar_width = 0.2

# 计算每种方案的位置
x_indexes = np.arange(len(group_potential_conflicts))

# 绘制柱状图
plt.figure(figsize=(10, 6))
for i, (scheme, averages) in enumerate(results.items()):
    adjusted_averages = [val if val > 0 else 0.5 for val in averages]  # 处理 Block Mutex 柱子为空的问题
    bars = plt.bar(x_indexes + i * bar_width, adjusted_averages, width=bar_width, label=scheme, alpha=0.8)

    # 添加数值标签
    for bar, value in zip(bars, averages):
        plt.text(bar.get_x() + bar.get_width() / 2, value + 1, f"{int(value)}", ha='center', fontsize=10, color='black')

# 绘制 group_rules_nums 作为折线图
plt.plot(x_indexes + bar_width, group_rules_nums, marker="o", linestyle="-", color="red", label="Total Rules")

# 为折线图上的每个点添加数值标注
for i, value in enumerate(group_rules_nums):
    plt.text(x_indexes[i] + bar_width, value + 1, f"{int(value)}", ha='center', fontsize=10)

# 配置图形
plt.title("Comparison of Different Mutex Schemes", fontsize=14)
plt.xlabel("Potential Mutex Conflicts in Rule Set", fontsize=12)
plt.ylabel("Average Mutex Conflict Count", fontsize=12)
plt.xticks(ticks=x_indexes + bar_width, labels=group_potential_conflicts)
plt.legend(title="Mutex Scheme")


# 让图显示水平网格线（只在 Y 轴方向），便于对比数值
plt.grid(axis='y', linestyle='--', alpha=0.7)


# 设置纵轴刻度
plt.yticks(range(0, 110, 10))

# 移除水平刻度线
plt.grid(False)

# 适配图像
plt.tight_layout()

# 显示图形
plt.show()
