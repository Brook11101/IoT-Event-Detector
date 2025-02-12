import os
import numpy as np
import matplotlib.pyplot as plt

# **实验数据存储的根目录**
BASE_DIR = r"E:\研究生信息收集\论文材料\IoT-Event-Detector\Synchronizer\CV\Data"
NUM_OF_OPERATIONS = [1, 2, 3, 4]  # 实验操作次数

# **存储计算结果**
cri_withcv = []
cri_talock = []
cri_llsc = []
trigger_counts = []

# **遍历每个 num_of_operations**
for num_ops in NUM_OF_OPERATIONS:
    exp_dir = os.path.join(BASE_DIR, f"num_of_operations_{num_ops}")

    # **读取数据文件**
    withcv_file = os.path.join(exp_dir, "withcv_num.txt")
    talock_file = os.path.join(exp_dir, "withoutcv_talock_num.txt")
    llsc_file = os.path.join(exp_dir, "withoutcv_llsc_num.txt")
    log_num_file = os.path.join(exp_dir, "log_num.txt")

    # **读取并计算平均值**
    def read_avg(file_path):
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                values = [int(line.strip()) for line in f.readlines()]
                return np.mean(values) if values else 0
        return 0

    cri_withcv.append(read_avg(withcv_file))
    cri_talock.append(read_avg(talock_file))
    cri_llsc.append(read_avg(llsc_file))
    trigger_counts.append(read_avg(log_num_file))

# **绘制图表**
fig, ax1 = plt.subplots(figsize=(8, 6))

# **左侧 Y 轴 (CRI 统计)**
ax1.set_xlabel("Num of Operations")
ax1.set_ylabel("CRI Count", color="tab:red")
ax1.plot(NUM_OF_OPERATIONS, cri_withcv, 'o-', label="WithCV", color="red")
ax1.plot(NUM_OF_OPERATIONS, cri_talock, 's-', label="WithoutCV_TALOCK", color="orange")
ax1.plot(NUM_OF_OPERATIONS, cri_llsc, '^-', label="WithoutCV_LLSC", color="brown")
ax1.tick_params(axis="y", labelcolor="tab:red")

# **右侧 Y 轴 (触发规则数量统计)**
ax2 = ax1.twinx()
ax2.set_ylabel("Triggered Rules Count", color="tab:blue")
ax2.plot(NUM_OF_OPERATIONS, trigger_counts, 'd-', label="Triggered Rules", color="blue")
ax2.tick_params(axis="y", labelcolor="tab:blue")

# **图例**
fig.legend(loc="upper left", bbox_to_anchor=(0.15, 0.85))

# **标题**
plt.title("CRI Detection & Triggered Rules vs Num of Operations")

# **显示图表**
plt.show()
