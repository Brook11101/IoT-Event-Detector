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
    - `log_num.txt` (触发规则数量)
    - `withoutcv_talock_num.txt` (TALOCK CRI 检测结果)
    - `withoutcv_llsc_num.txt` (LLSC CRI 检测结果)
    - `withcv_num.txt` (WithCV CRI 检测结果)
    """

    for num_ops in NUM_OF_OPERATIONS:
        # **定义当前 num_of_operations 目录**
        exp_dir = os.path.join(BASE_DIR, f"num_of_operations_{num_ops}")
        os.makedirs(exp_dir, exist_ok=True)

        log_num_path = os.path.join(exp_dir, "log_num.txt")
        talock_path = os.path.join(exp_dir, "withoutcv_talock_num.txt")
        llsc_path = os.path.join(exp_dir, "withoutcv_llsc_num.txt")
        withcv_path = os.path.join(exp_dir, "withcv_num.txt")

        # **清空文件**
        for file_path in [log_num_path, talock_path, llsc_path, withcv_path]:
            with open(file_path, "w") as f:
                pass

        for trial in range(NUM_TRIALS):
            print(f"Num Of Operations: {num_ops}, Trial: {trial + 1}")

            # **运行静态模拟**
            rule_count = run_static_simulation(times=num_ops)

            # **记录触发规则数量**
            with open(log_num_path, "a") as f:
                f.write(f"{rule_count}\n")

            # **执行 WithoutCV_TALOCK() CRI 检测**
            _, mismatch_count_talock = WithOutCV_TALOCK()
            with open(talock_path, "a") as f:
                f.write(f"{mismatch_count_talock}\n")

            # **执行 WithoutCV_LLSC() CRI 检测**
            _, mismatch_count_llsc = WithOutCV_LLSC()
            with open(llsc_path, "a") as f:
                f.write(f"{mismatch_count_llsc}\n")

            # **执行 WithCV() CRI 检测**
            _, mismatch_count_withcv = WithCV()
            with open(withcv_path, "a") as f:
                f.write(f"{mismatch_count_withcv}\n")


    print(f"Operations Num-{num_ops}-{trial}  == Experiment Completed Successfully ==")


if __name__ == "__main__":
    run_experiment()
