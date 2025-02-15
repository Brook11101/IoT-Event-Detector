import os
import matplotlib.pyplot as plt
import seaborn as sns

# **实验数据目录**
BASE_DIR = r"E:\研究生信息收集\论文材料\IoT-Event-Detector\Synchronizer\CV\Data"
NUM_OF_OPERATIONS = [1, 2, 3, 4, 5]  # 扰动次数

# **读取 `withcv_time.txt` 数据**
all_execution_times = []

for num_ops in NUM_OF_OPERATIONS:
    exp_dir = os.path.join(BASE_DIR, f"num_of_operations_{num_ops}")
    withcv_path = os.path.join(exp_dir, "withcv_time.txt")

    if not os.path.exists(withcv_path):
        print(f"文件 {withcv_path} 不存在，跳过。")
        continue

    execution_times = []  # 存储当前 `num_ops` 下的执行时间列表

    with open(withcv_path, "r") as f:
        for line in f:
            try:
                time_list = eval(line.strip())  # **解析每一行的时间数据**
                execution_times.append(time_list)
            except Exception as e:
                print(f"解析失败: {e}, 行内容: {line.strip()}")

    # **展平数据（因为每轮是列表）**
    flattened_times = [t for sublist in execution_times for t in sublist]
    all_execution_times.append(flattened_times)


# **绘制箱线图**
plt.figure(figsize=(10, 6))

plt.boxplot(all_execution_times, labels=[str(num) for num in NUM_OF_OPERATIONS], whis=1.5)

# **图表设置**
plt.xlabel("Num of Operations")
plt.ylabel("Execution Time of Rules Using Conditional Variables")
plt.title("Execution Time Distribution Under Conditional Variable")

# **显示图表**
plt.show()
