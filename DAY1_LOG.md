# Day1 视觉预处理调参记录
- 日期：2024-xx-xx
- 环境：Python 3.11 + OpenCV 4.x + PyCharm + .venv
- 默认参数：blur_kernel=5, adaptive_block=11, adaptive_C=2
  → 现象：画面噪点较多，边缘细碎（房间光暗+无PCB导致）
- 调大 C (C=8)：画面变干净，弱反光被过滤，适合光照均匀场景
- 调大 block (block=21)：边缘变粗/连片，适合大轮廓提取，但小细节易丢失
- 结论：工业现场需先固定光源距离与角度，再微调 C 值；block 保持 11~15 最稳妥
