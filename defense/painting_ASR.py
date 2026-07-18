import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['ytick.labelsize'] = 15  # y轴刻度字体大小

# 定义受害模型
models = ['Vicuna-7B', 'Llama-3-8B', 'Llama-2-7B', 'Mistral-7B', 'GPT-3.5-turbo']
x = np.arange(len(models))

# 定义 AdvBench 数据（ASR 值）
advbench_pre = [0.52, 0.20, 0.44, 0.87, 0.14]
advbench_post = [0.78, 0.26, 0.36, 0.63, 0.32]

GPTFuzz_pre = [0.76, 0.01, 0.19, 0.81, 0.02]
GPTFuzz_post = [0.78, 0.10, 0.17, 0.34, 0.13]

# 创建一个图形对象，使用1行2列的布局
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# 绘制 AdvBench 数据集的折线图
axes[0].plot(x, advbench_pre, marker='o', linestyle='-', label='Pre-Intent Detection', color='tab:blue', markersize=8, linewidth=2)
axes[0].plot(x, advbench_post, marker='s', linestyle='--', label='Post-Threat Analysis', color='tab:orange', markersize=8, linewidth=2)
axes[0].set_xticks(x)
axes[0].set_xticklabels(models, rotation=30, fontsize=15)
axes[0].set_ylim(0, 1)
axes[0].set_ylabel('ASR', fontsize=17)
axes[0].set_title('ASR on AdvBench after Defense', fontsize=17, fontweight='bold')
axes[0].legend(fontsize=15)
axes[0].grid(True, linestyle='--', alpha=0.6)

# 保存 AdvBench 图像
fig_advbench = plt.figure(figsize=(6, 5))
plt.plot(x, advbench_pre, marker='o', linestyle='-', label='Pre-Intent Detection', color='tab:blue', markersize=8, linewidth=2)
plt.plot(x, advbench_post, marker='s', linestyle='--', label='Post-Threat Analysis', color='tab:orange', markersize=8, linewidth=2)
plt.xticks(x, models, rotation=30, fontsize=15)
plt.ylim(0, 1)
plt.ylabel('ASR', fontsize=17)
plt.title('ASR on AdvBench after Defense', fontsize=17, fontweight='bold')
plt.legend(loc="upper left", fontsize=15)
plt.grid(True, linestyle='--', alpha=0.6)
fig_advbench.tight_layout()
fig_advbench.savefig('defense_AdvBench_ASR.pdf')

# 绘制 GPTFuzz 数据集的折线图
axes[1].plot(x, GPTFuzz_pre, marker='o', linestyle='-', label='Pre-Intent Detection', color='tab:blue', markersize=8, linewidth=2)
axes[1].plot(x, GPTFuzz_post, marker='s', linestyle='--', label='Post-Threat Analysis', color='tab:orange', markersize=8, linewidth=2)
axes[1].set_xticks(x)
axes[1].set_xticklabels(models, rotation=30, fontsize=15)
axes[1].set_ylim(0, 1)
axes[1].set_ylabel('ASR', fontsize=16)
axes[1].set_title('ASR on GPTFuzz after Defense', fontsize=17, fontweight='bold')
axes[1].legend(fontsize=15)
axes[1].grid(True, linestyle='--', alpha=0.6)

# 保存 GPTFuzz 图像
fig_GPTFuzz = plt.figure(figsize=(6, 5))
plt.plot(x, GPTFuzz_pre, marker='o', linestyle='-', label='Pre-Intent Detection', color='tab:blue', markersize=8, linewidth=2)
plt.plot(x, GPTFuzz_post, marker='s', linestyle='--', label='Post-Threat Analysis', color='tab:orange', markersize=8, linewidth=2)
plt.xticks(x, models, rotation=30, fontsize=15)
plt.ylim(0, 1)
plt.ylabel('ASR', fontsize=17)
plt.title('ASR on GPTFuzz after Defense', fontsize=17, fontweight='bold')
plt.legend(loc="upper left", fontsize=15)
plt.grid(True, linestyle='--', alpha=0.6)
fig_GPTFuzz.tight_layout()
fig_GPTFuzz.savefig('defense_GPTFuzz_ASR.pdf')
