import threading
import time
import random
import ast

def read_static_logs(filename):
    """
    读取 `static_logs.txt`，按轮次 (epoch) 存储规则日志。
    """
    with open(filename, "r", encoding="utf-8") as f:
        data = f.read().strip()

    # 按空行分割不同轮次
    epochs = data.split("\n\n")
    logs_per_epoch = []

    for epoch in epochs:
        log_entries = [ast.literal_eval(line) for line in epoch.split("\n") if line.strip()]
        logs_per_epoch.append(log_entries)

    return logs_per_epoch

def execute_rule(log, output_list, lock):
    """
    执行单条规则，模拟 sleep(1-2s) 并记录执行顺序。
    """
    time.sleep(random.uniform(1, 2))  # 模拟不同执行时间

    with lock:
        output_list.append(log)  # 线程安全地添加到列表

def process_epoch(epoch_logs, output_logs):
    """
    并发执行单个轮次的所有规则，按实际完成顺序记录。
    """
    threads = []
    lock = threading.Lock()

    for log in epoch_logs:
        thread = threading.Thread(target=execute_rule, args=(log, output_logs, lock))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()  # 确保所有线程完成后再继续下一轮次

def main():
    input_file = "static_logs.txt"
    output_file = "nocv_logs.txt"

    # 读取所有轮次的日志
    epochs_logs = read_static_logs(input_file)
    final_logs = []

    for epoch_logs in epochs_logs:
        process_epoch(epoch_logs, final_logs)

    # 将最终执行顺序写入 `nocv_logs.txt`
    with open(output_file, "w", encoding="utf-8") as f:
        for log in final_logs:
            f.write(str(log) + "\n")

    print(f"Simulation completed. Results saved to {output_file}")

if __name__ == "__main__":
    main()
