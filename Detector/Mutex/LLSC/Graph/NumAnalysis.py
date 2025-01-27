import matplotlib.pyplot as plt
import os
import numpy as np

# 配置路径和方案名称
base_paths = {
    "LockOut": r"E:\研究生信息收集\论文材料\IoT-Event-Detector\Detector\Mutex\LLSC\Data\LockOut",
    "LockWith": r"E:\研究生信息收集\论文材料\IoT-Event-Detector\Detector\Mutex\LLSC\Data\LockWith",
    "LockFree": r"E:\研究生信息收集\论文材料\IoT-Event-Detector\Detector\Mutex\LLSC\Data\LockFree",
}
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

# 绘图
plt.figure(figsize=(10, 6))
for scheme, averages in results.items():
    plt.plot(group_potential_conflicts, averages, marker="o", label=scheme)

# 配置图形
plt.title("Comparison of Different Mutex Schemes", fontsize=14)
plt.xlabel("Potential Mutex Conflicts in Rule Set", fontsize=12)
plt.ylabel("Average Mutex Conflict Count", fontsize=12)
plt.xticks(group_potential_conflicts)
plt.legend(title="Mutex Scheme")

# 设置纵轴刻度
plt.ylim(-1, max(max(results["No Mutex"]), 50))  # 设置 y 轴范围，避免 0 与 x 轴重合
plt.yticks(
    list(np.arange(0, 6, 1)) + list(range(10, 51, 10))  # 0-5细化刻度，步长为1；10以上步长为10
)

# 添加网格线
plt.grid(True, linestyle="--", alpha=0.6)
plt.tight_layout()

# 显示图形
plt.show()