"""
PCB视觉分拣系统 - 主程序
功能：实时捕获摄像头画面，进行图像处理（转灰度、模糊、二值化）
用途：用于PCB板缺陷检测或元件识别的预处理
"""
import cv2      # OpenCV库：用于图像处理和计算机视觉
import yaml     # PyYAML库：用于读取配置文件
import sys      # 系统库：用于程序退出等操作
import time     # 时间库：用于生成时间戳文件名

# ============================================
# 第一步：读取配置文件
# ============================================
# config.yaml 存储了所有可调参数，避免硬编码
# 使用 with open 自动管理文件关闭
with open("config.yaml", "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)  # 将YAML格式转为Python字典

# 配置文件结构示例：
# camera:
#   index: 0              # 摄像头编号（0=默认摄像头，1=外接摄像头）
#   width: 640            # 画面宽度（像素）
#   height: 480           # 画面高度（像素）
# processing:
#   blur_kernel: 5        # 高斯模糊核大小（必须是奇数：3,5,7,9...）
#   adaptive_block: 11    # 自适应阈值块大小（必须是奇数：3,5,7,9...）
#   adaptive_C: 2         # 自适应阈值常数（从块平均值中减去的值）


# ============================================
# 第二步：打开摄像头
# ============================================
# cv2.VideoCapture(): 创建视频捕获对象
# 参数说明：
#   - index: 摄像头设备编号
#     * 0 = 笔记本内置摄像头或第一个USB摄像头
#     * 1 = 第二个摄像头
#     * -1 = 系统自动选择
#     * 也可以传入视频文件路径，如 "video.mp4"
#
# 调参技巧：
#   如果打不开摄像头，尝试修改 config.yaml 中的 camera.index
#   Windows系统通常从0开始，Linux可能从0或1开始
cap = cv2.VideoCapture(cfg["camera"]["index"])

# 检查摄像头是否成功打开
if not cap.isOpened():
    print("❌ 打不开摄像头，请检查config.yaml里的index是不是0")
    print("💡 提示：可以尝试将index改为1或-1")
    sys.exit()  # 终止程序


# ============================================
# 第三步：设置摄像头画面分辨率
# ============================================
# cap.set(): 设置摄像头属性
# cv2.CAP_PROP_FRAME_WIDTH: 画面宽度属性标识符
# cv2.CAP_PROP_FRAME_HEIGHT: 画面高度属性标识符
#
# 调参技巧：
#   - 常见分辨率：640x480（VGA）、1280x720（HD）、1920x1080（Full HD）
#   - 分辨率越高，处理速度越慢，但细节更清晰
#   - 分辨率越低，处理速度越快，但可能丢失细节
#   - 如果设置后实际分辨率不对，说明摄像头不支持该分辨率
#   - 可以通过 cap.get(cv2.CAP_PROP_FRAME_WIDTH) 查看实际分辨率
cap.set(cv2.CAP_PROP_FRAME_WIDTH, cfg["camera"]["width"])
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cfg["camera"]["height"])

# 打印提示信息
cv2.setUseOptimized(True)  # 启用OpenCV优化（加速处理）
print("✅ 摄像头已打开 | 按键盘 Q 退出 | 按 S 保存截图")
print(f"📐 设置分辨率: {cfg['camera']['width']}x{cfg['camera']['height']}")


# ============================================
# 第四步：主循环 - 实时图像处理
# ============================================
# while True: 无限循环，直到按Q键退出
# 每一帧都会执行以下操作：
while True:
    # ① 读取一帧画面
    # cap.read() 返回两个值：
    #   - ret: 布尔值，True表示成功读取，False表示失败
    #   - frame: 图像数据（numpy数组），格式为BGR（蓝绿红）
    ret, frame = cap.read()

    # 如果读取失败（摄像头断开），退出循环
    if not ret:
        print("⚠️ 读取画面失败，摄像头可能已断开")
        break


    # ========================================
    # 图像处理步骤①：彩色图转灰度图
    # ========================================
    # cv2.cvtColor(): 颜色空间转换函数
    # 参数说明：
    #   - frame: 输入图像（BGR格式）
    #   - cv2.COLOR_BGR2GRAY: 转换代码，表示BGR转灰度
    #
    # 为什么要转灰度？
    #   - 减少数据量：从3通道（BGR）变为1通道，处理速度提升3倍
    #   - 很多图像处理算法只需要灰度图
    #   - PCB检测通常关注形状和纹理，不需要颜色信息
    #
    # 其他常用转换代码：
    #   cv2.COLOR_BGR2RGB    : BGR转RGB（用于显示）
    #   cv2.COLOR_BGR2HSV    : BGR转HSV（用于颜色识别）
    #   cv2.COLOR_GRAY2BGR   : 灰度转BGR（用于合并显示）
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # ========================================
    # 图像处理步骤②：高斯模糊（去噪）
    # ========================================
    # cv2.GaussianBlur(): 高斯模糊函数
    # 参数说明：
    #   - gray: 输入图像（灰度图）
    #   - (kernel_size, kernel_size): 核大小（必须是正奇数）
    #     * kernel_size=3: 轻微模糊，保留更多细节
    #     * kernel_size=5: 中等模糊，推荐起点
    #     * kernel_size=7: 较强模糊，去除更多噪点
    #     * kernel_size=9+: 强模糊，可能丢失细节
    #     * (cfg["processing"]["blur_kernel"],) * 2 生成 (5, 5) 这样的元组
    #   - 0: 标准差（sigma），0表示自动根据核大小计算
    #
    # 调参技巧：
    #   - 如果画面噪点多（小斑点），增大 blur_kernel（5→7→9）
    #   - 如果细节丢失严重，减小 blur_kernel（5→3）
    #   - 核大小必须是奇数，否则会报错
    #   - 常见设置：3（轻微）、5（推荐）、7（强）
    #   - 可以在 config.yaml 中修改 processing.blur_kernel
    blur = cv2.GaussianBlur(
        gray,
        (cfg["processing"]["blur_kernel"],) * 2,  # 例如: (5, 5)
        0  # 标准差自动计算
    )

    # ========================================
    # 图像处理步骤③：自适应阈值二值化
    # ========================================
    # cv2.adaptiveThreshold(): 自适应阈值函数
    # 作用：将灰度图转为纯黑白图（二值图），像素值只有0或255
    #
    # 参数详细说明：
    #   1. blur: 输入图像（模糊后的灰度图）
    #
    #   2. 255: 满足条件时赋予的像素值（最大值）
    #      * 255 = 白色
    #      * 可以根据需要改为其他值（0-255）
    #
    #   3. cv2.ADAPTIVE_THRESH_GAUSSIAN_C: 自适应方法
    #      * GAUSSIAN_C: 使用高斯加权计算邻域平均值（推荐，效果更好）
    #      * MEAN_C: 使用简单平均值计算（速度快，但对光线敏感）
    #
    #   4. cv2.THRESH_BINARY_INV: 阈值类型
    #      * THRESH_BINARY_INV: 反转二值化（亮的变黑，暗的变白）
    #        - 小于阈值 → 255（白）
    #        - 大于阈值 → 0（黑）
    #      * THRESH_BINARY: 普通二值化（不反转）
    #        - 小于阈值 → 0（黑）
    #        - 大于阈值 → 255（白）
    #
    #   5. cfg["processing"]["adaptive_block"]: 邻域块大小（必须是奇数）
    #      * 3x3: 很小邻域，对局部光线敏感
    #      * 11x11: 中等邻域，推荐起点
    #      * 21x21: 大邻域，适合光线不均匀的场景
    #      * 51x51: 很大邻域，全局光线差异大时使用
    #
    #   6. cfg["processing"]["adaptive_C"]: 常数C（从平均值中减去的值）
    #      * C=0: 直接使用平均值作为阈值
    #      * C>0: 提高阈值，使白色区域减少（更严格）
    #      * C<0: 降低阈值，使白色区域增加（更宽松）
    #      * 常见范围：-10 到 10
    #
    # 调参技巧：
    #   - 如果二值图噪点多：增大 adaptive_block（11→21→31）
    #   - 如果细节丢失：减小 adaptive_block（11→7→5）
    #   - 如果白色区域太少：减小 adaptive_C（2→0→-2）
    #   - 如果白色区域太多：增大 adaptive_C（2→5→10）
    #   - 光线不均匀时：增大 adaptive_block（11→21→51）
    #   - 光线均匀时：可以改用 cv2.threshold()（全局阈值，更快）
    #
    # 替代方案 - 全局阈值（光线均匀时使用）：
    #   _, thresh = cv2.threshold(blur, 127, 255, cv2.THRESH_BINARY_INV)
    #   # 127是固定阈值，可以根据实际调整（0-255）
    thresh = cv2.adaptiveThreshold(
        blur,                          # 输入图像
        255,                           # 最大值（白色）
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, # 自适应方法（高斯加权）
        cv2.THRESH_BINARY_INV,         # 反转二值化
        cfg["processing"]["adaptive_block"],  # 邻域块大小（奇数）
        cfg["processing"]["adaptive_C"]       # 常数C
    )


    # ========================================
    # 显示处理结果
    # ========================================
    # cv2.imshow(): 显示图像窗口
    # 参数说明：
    #   - 第一个参数: 窗口标题（字符串）
    #   - 第二个参数: 要显示的图像
    #
    # 注意：
    #   - 窗口会自动适应图像大小
    #   - 可以拖动窗口查看不同区域
    #   - 多个窗口可以同时显示
    cv2.imshow("原图（彩色）", frame)         # 显示原始彩色图像
    cv2.imshow("处理后（黑白二值）", thresh)  # 显示二值化处理结果


    # ========================================
    # 键盘事件监听
    # ========================================
    # cv2.waitKey(1): 等待键盘输入
    # 参数说明：
    #   - 1: 等待时间（毫秒）
    #     * 1ms: 实时视频流（推荐，约30-60帧/秒）
    #     * 10ms: 降低帧率，减少CPU占用
    #     * 100ms: 慢速播放，用于调试
    #     * 0: 无限等待，直到按键（暂停）
    #   - 返回值: 按下键的ASCII码，没按键返回-1
    #
    # & 0xFF: 位运算，确保兼容不同操作系统
    #   - Windows返回256+ASCII码，Linux直接返回ASCII码
    #   - 0xFF = 255（二进制11111111），取低8位
    #
    # 常用按键检测：
    #   ord('q'): 字母q的ASCII码（113）
    #   ord('s'): 字母s的ASCII码（115）
    #   27: ESC键的ASCII码
    #   32: 空格键的ASCII码
    key = cv2.waitKey(1) & 0xFF

    # 按 Q 键：退出程序
    if key == ord("q"):
        print("👋 用户按下 Q 键，准备退出...")
        break

    # 按 S 键：保存当前处理结果
    elif key == ord("s"):
        # 生成带时间戳的文件名，避免覆盖
        # time.time(): 当前时间戳（秒），如 1713772800.123
        # int(): 转为整数，如 1713772800
        # f-string: 格式化字符串，生成如 "debug_1713772800.png"
        filename = f"debug_{int(time.time())}.png"

        # cv2.imwrite(): 保存图像到文件
        # 参数说明：
        #   - filename: 文件路径和名称
        #   - thresh: 要保存的图像
        # 支持格式：.png（无损）、.jpg（有损）、.bmp（未压缩）
        cv2.imwrite(filename, thresh)
        print(f"📷 已保存: {filename}")
        print(f"💡 提示：可以在当前目录查看保存的图片")


# ============================================
# 第五步：清理资源并退出
# ============================================
# 程序退出前必须释放资源，否则可能导致：
#   - 摄像头被占用，其他程序无法使用
#   - 内存泄漏
#   - 窗口无法正常关闭

# cap.release(): 释放摄像头设备
#   - 必须在程序结束前调用
#   - 释放后摄像头可以被其他程序使用
cap.release()

# cv2.destroyAllWindows(): 关闭所有OpenCV创建的窗口
#   - 释放窗口占用的内存
#   - 如果不关闭，窗口可能残留
cv2.destroyAllWindows()

print("✅ 资源已释放，程序已安全退出")
print("📁 如有保存的截图，请查看当前目录下的 debug_*.png 文件")


