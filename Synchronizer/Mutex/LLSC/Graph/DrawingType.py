import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 1) 你的原始数据
data = [
    1.259829044342041, 1.5055336952209473, 1.8088059425354004, 1.5924534797668457,
    2.015284299850464, 1.2782824039459229, 1.5103371143341064, 3.019152879714966,
    3.496119976043701, 3.8023877143859863, 2.7839102745056152, 3.2517166137695312,
    4.668451309204102, 5.690021753311157, 5.6775901317596436, 5.745404958724976,
    7.055946111679077, 5.962702035903931, 7.688314914703369, 7.751343250274658,
    8.676956415176392, 9.371375799179077, 9.337777614593506, 10.003679037094116,
    8.350865364074707, 10.264721393585205, 11.546024560928345, 10.560171842575073,
    12.292646408081055, 11.933384895324707, 13.151108980178833, 12.492928504943848,
    11.639850378036499, 12.725627899169922, 14.25221872329712, 13.720829963684082,
    14.231946468353271, 14.643551349639893, 15.259887933731079, 16.800734996795654,
    16.1903977394104, 17.186115980148315, 17.357653379440308, 18.202972888946533,
    17.693299531936646, 18.943928241729736, 18.58619451522827, 19.518943071365356,
    19.720025300979614, 18.816986799240112, 20.113986492156982, 20.048991918563843,
    21.161516666412354, 19.96120047569275, 20.160090446472168, 22.028972387313843,
    21.82527995109558, 22.367741346359253, 23.06786036491394, 24.785882234573364,
    26.023960828781128
]

# 转换为 numpy 数组便于计算
data_arr = np.array(data)

# 2) 计算基础统计量
minimum = np.min(data_arr)
maximum = np.max(data_arr)
mean_val = np.mean(data_arr)
median_val = np.median(data_arr)
std_val = np.std(data_arr)
q1 = np.percentile(data_arr, 25)
q3 = np.percentile(data_arr, 75)
p95 = np.percentile(data_arr, 95)
p99 = np.percentile(data_arr, 99)

# 3) 打印统计结果
print("基本统计结果:")
print(f"  - 最小值 (min): {minimum:.4f}")
print(f"  - 第 25 百分位 (Q1): {q1:.4f}")
print(f"  - 中位数 (median): {median_val:.4f}")
print(f"  - 第 75 百分位 (Q3): {q3:.4f}")
print(f"  - 平均值 (mean): {mean_val:.4f}")
print(f"  - 标准差 (std): {std_val:.4f}")
print(f"  - P95: {p95:.4f}")
print(f"  - P99: {p99:.4f}")
print(f"  - 最大值 (max): {maximum:.4f}")

# ============== 可 视 化 部 分 ==============
sns.set_style("whitegrid")  # 设定 seaborn 风格

# 4) 直方图 (Histogram)
plt.figure(figsize=(8, 5))
plt.hist(data_arr, bins=10, color='skyblue', edgecolor='black', alpha=0.7)
plt.title("Histogram of Execution Times")
plt.xlabel("Time (s)")
plt.ylabel("Frequency")
plt.tight_layout()  # 自动调整布局

# 5) KDE 曲线 (核密度估计)
plt.figure(figsize=(8, 5))
sns.kdeplot(data_arr, fill=True, color='skyblue')
plt.title("KDE of Execution Times")
plt.xlabel("Time (s)")
plt.ylabel("Density")
plt.tight_layout()

# 6) 箱线图 (Box Plot)
plt.figure(figsize=(6, 6))
sns.boxplot(y=data_arr, color='lightgreen')
plt.title("Box Plot of Execution Times")
plt.ylabel("Time (s)")
plt.tight_layout()

# 7) 误差条 (Error Bar) / 柱状图 + 标准差
# 这里假设你只有一组数据，但为了演示，我们还是做一个简单的误差条图：
plt.figure(figsize=(5, 5))
mean_for_bar = [mean_val]  # 只有一个组
std_for_bar = [std_val]    # 只有一个组对应的 std
x_labels = ['Group1']      # 只有一个组，示意
plt.bar(x_labels, mean_for_bar, yerr=std_for_bar, capsize=5, color='orange', alpha=0.8)
plt.title("Mean & Standard Deviation (Single Group)")
plt.ylabel("Time (s)")
plt.tight_layout()

plt.show()
