import matplotlib.pyplot as plt
import numpy as np

# 设置全局字体大小，增加学术感
plt.rcParams.update({'font.size': 12, 'font.family': 'sans-serif'})

# 创建画布 (1行2列)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# ==========================================
# 左图：Detection Performance (检测性能)
# ==========================================
detection_labels = ['Ground Truth\n(Total Faces)', 'Successfully\nDetected', 'Missed\n(FN-Detection)']
detection_values = [112, 72, 40]
colors_det = ['#4A90E2', '#50E3C2', '#E94E77']

bars1 = ax1.bar(detection_labels, detection_values, color=colors_det, width=0.6)
ax1.set_title('Face Detection Performance', fontsize=14, fontweight='bold', pad=15)
ax1.set_ylabel('Number of Faces')
ax1.set_ylim(0, 130)

# 在柱子上添加数值标签
for bar in bars1:
    yval = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2, yval + 2, int(yval), ha='center', va='bottom', fontweight='bold')

# ==========================================
# 右图：Recognition Confusion Matrix (识别混淆矩阵)
# ==========================================
recog_labels = ['True Positive\n(TP)', 'True Negative\n(TN)', 'False Negative\n(FN)', 'False Positive\n(FP)']
recog_values = [32, 36, 4, 0]
colors_rec = ['#50E3C2', '#4A90E2', '#F5A623', '#E94E77']

bars2 = ax2.bar(recog_labels, recog_values, color=colors_rec, width=0.6)
ax2.set_title('Face Recognition Metrics (n=72)', fontsize=14, fontweight='bold', pad=15)
ax2.set_ylabel('Number of Faces')
ax2.set_ylim(0, 45)

# 在柱子上添加数值标签
for bar in bars2:
    yval = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2, yval + 1, int(yval), ha='center', va='bottom', fontweight='bold')

# 调整布局并保存
plt.tight_layout()
plt.savefig('Figure_5_2_Performance.png', dpi=300, bbox_inches='tight')
plt.show()

print("✅ 图表已成功生成并保存为 Figure_5_2_Performance.png")