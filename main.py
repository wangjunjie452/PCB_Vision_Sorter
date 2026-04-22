import cv2
import yaml
import sys
import time

# 1. 读取配置文件
with open("config.yaml", "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)

# 2. 打开摄像头
cap = cv2.VideoCapture(cfg["camera"]["index"])
if not cap.isOpened():
    print("❌ 打不开摄像头，请检查config.yaml里的index是不是0")
    sys.exit()

# 3. 设置画面大小
cap.set(cv2.CAP_PROP_FRAME_WIDTH, cfg["camera"]["width"])
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cfg["camera"]["height"])

print("✅ 摄像头已打开 | 按键盘 Q 退出 | 按 S 保存截图")

# 4. 主循环（一直运行直到你按Q）
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # ① 转黑白
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # ② 稍微模糊一下，去掉噪点
    blur = cv2.GaussianBlur(gray, (cfg["processing"]["blur_kernel"],) * 2, 0)
    # ③ 自动根据光线明暗，把画面分成黑白两块
    thresh = cv2.adaptiveThreshold(
        blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        cfg["processing"]["adaptive_block"],
        cfg["processing"]["adaptive_C"]
    )

    # 弹出两个窗口
    cv2.imshow("原图", frame)
    cv2.imshow("黑白处理后", thresh)

    # 监听键盘
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    elif key == ord("s"):
        filename = f"debug_{int(time.time())}.png"
        cv2.imwrite(filename, thresh)
        print(f"📷 已保存: {filename}")

# 5. 退出清理
cap.release()
cv2.destroyAllWindows()
print("👋 程序已退出")

#11
