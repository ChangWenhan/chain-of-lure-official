import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['ytick.labelsize'] = 14  # y轴刻度字体大小

# Define the models and datasets
models = ['DeepSeek-V3-1226', 'Gemma-2-27B-it', 'Qwen2.5-turbo-1101']
x = np.arange(len(models))  # the label locations
width = 0.25  # the width of the bars

# Define the ASR values
advbench_asr = [0.99, 0.61, 0.70]
gptfuzz_asr = [0.99, 0.85, 0.89]

# Create figure and axis
fig, ax = plt.subplots(figsize=(6, 5))

# Create bars for each dataset
rects1 = ax.bar(x - width/2, advbench_asr, width, label='AdvBench', color='tab:blue')
rects2 = ax.bar(x + width/2, gptfuzz_asr, width, label='GPTFuzz', color='tab:orange')

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Attack Success Rate (ASR)', fontsize=16)
ax.set_title('Human Craft ASR Comparison Across LLMs', fontsize=16, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(models, rotation=15, fontsize=14)
ax.set_ylim(0, 1.1)
ax.legend(
    fontsize=12,
    bbox_to_anchor=(0.86, 1),  # 将0.95改为更小的值（如0.85）可左移
    loc='upper right',
    borderaxespad=0.
)
ax.grid(True, linestyle='--', alpha=0.3)

# Function to attach a text label above each bar
def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        ax.annotate(f'{height:.2f}',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=14)

# Call the function for both sets of bars
autolabel(rects1)
autolabel(rects2)

# Adjust layout and save to PDF
fig.tight_layout()
plt.savefig('ASR_Comparison.pdf', bbox_inches='tight')
# plt.show()