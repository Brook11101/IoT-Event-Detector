import os
import time
from StaticSimulation import run_static_simulation
from WithOutCV_TALOCK import WithOutCV_TALOCK
from WithOutCV_LLSC import WithOutCV_LLSC
from WithCV import WithCV

# **定义数据存储的根目录**
BASE_DIR = r"E:\研究生信息收集\论文材料\IoT-Event-Detector\Synchronizer\CV\Data"

# **实验参数**
NUM_OF_OPERATIONS = [1, 2, 3, 4, 5]  # 扰动次数
NUM_TRIALS = 10  # 每个 num_of_operations 执行 10 轮实验


def run_experiment():
    """
    进行完整实验，测试不同 Num Of Operations (times=1~5)，每个 times 进行 10 轮实验。
    记录：
    - `withcv_time.txt` (WithCV 规则执行时间收集)
    """

    for num_ops in NUM_OF_OPERATIONS:
        # **定义当前 num_of_operations 目录**
        exp_dir = os.path.join(BASE_DIR, f"num_of_operations_{num_ops}")
        os.makedirs(exp_dir, exist_ok=True)

        withcv_path = os.path.join(exp_dir, "withcv_time.txt")

        # **清空文件**
        for file_path in [withcv_path]:
            with open(file_path, "w") as f:
                pass

        for trial in range(NUM_TRIALS):
            print(f"Num Of Operations: {num_ops}, Trial: {trial + 1}")

            # **运行静态模拟**
            rule_count = run_static_simulation(times=num_ops)

            # **执行 WithCV() CRI 检测**
            _, mismatch_count_withcv, time_list = WithCV()
            with open(withcv_path, "a") as f:
                f.write(f"{time_list}\n")

    print(f"Record Time, Operations Num-{num_ops}-{trial}  == Experiment Completed Successfully ==")


if __name__ == "__main__":
    run_experiment()
