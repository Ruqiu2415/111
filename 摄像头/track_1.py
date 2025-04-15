"""
 交通灯识别 & 二维码识别 & 循迹 - 全面优化版
"""
import math
import re
import sensor, image, time, lcd
import binascii
from Maix import GPIO
from machine import Timer, PWM, UART
from fpioa_manager import fm

# 全局变量初始化
angle = 0
# 交通灯
FlagOK = 0
# 直线检测（官方）
is_debug = False
is_debug1 = 1
servo_delay = 0  # 舵机延时计数器初始化

# 舵机控制参数 - 优化速度
max_angle = 5   # 最大向上角度
min_angle = -18  # 最小向下角度
angle_step = 1.2  # 增加角度步长，从0.7增加到1.5，使舵机移动更快
servo_delay_max = 1  # 减少舵机每次移动之间的延时帧数，从2减少到1，使舵机反应更快

# 扫描窗口相关变量 - 增加扫描速度
scan_roi_height = 120  # 扫描窗口高度
scan_roi_width = 320   # 扫描窗口宽度 - 全宽
scan_roi_y = 0  # 扫描窗口的Y坐标
scan_direction = 1  # 1表示向下扫描，-1表示向上扫描
scan_step = 2  # 每次移动的步长，从2增加到4，使扫描窗口移动更快
scan_animation_counter = 0  # 动画计数器
scan_wait_frames = 0  # 停留帧数计数
max_wait_frames = 5  # 找到二维码后停留的帧数
qr_detected = False  # 是否检测到二维码
last_qr_rect = None  # 上一次检测到的二维码区域
frame_skip = 0  # 帧跳过计数器，用于提高流畅度

# 黄色识别定制参数 - 专注于HSV和LAB颜色空间
# 采用极其宽松的阈值，确保能检测到各种色调的黄色
yellow_hsv_thresholds = [(15, 100, 10, 127, 10, 127)]  # 宽松的HSV黄色阈值
yellow_lab_thresholds = [(30, 127, -10, 80, 15, 127)]  # 宽松的LAB黄色阈值

# 黑色二维码识别参数
black_thresholds = [(0, 70)]  # 黑色阈值(灰度模式)

# 0: 红：(255，0，0)  1:橙: (255, 125, 0)  2:黄：(255，255，0)
# 3: 绿：(0，255，0)  4:青: (0, 255, 255)  5:蓝：(0，0，255)  6:紫: (255, 0, 255)
# 颜色表
color = [(255, 0, 0), (255, 125, 0), (255, 255, 0), (0, 255, 0), (0, 255, 255), (0, 0, 255), (255, 0, 255)]

DISTORTION_FACTOR = 1  # 设定畸变系数
IMG_WIDTH = 240
IMG_HEIGHT = 320


# --------------感光芯片配置  START -------------------
# 二维码
def inin_sensor_1():#二维码——静态A
    sensor.reset()
    sensor.set_vflip(1)
    sensor.set_brightness(-2)    # 设置摄像头亮度
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QVGA)
    sensor.set_contrast(100)  # 设置摄像头对比度
    sensor.set_brightness(0)
    #lcd.rotation(1)    # LCD屏旋转90°
    #sensor.set_auto_gain(False)  # 必须关闭此功能，以防止图像冲洗…

def inin_sensor_5():#二维码——静态B
    sensor.reset()
    sensor.set_vflip(1)
    sensor.set_brightness(-2)    # 设置摄像头亮度
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QVGA)
    sensor.set_contrast(100)  # 设置摄像头对比度
    sensor.set_brightness(0)
    #lcd.rotation(1)    # LCD屏旋转90°
    #sensor.set_auto_gain(False)  # 必须关闭此功能，以防止图像冲洗…

def init_sensor_3():
    #lcd.init(freq=15000000)  # 初始化LCD
    sensor.reset()
    sensor.set_vflip(1)
    #sensor.set_brightness(-3)    # 设置摄像头亮度
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QVGA)
    sensor.set_contrast(3)  # 设置摄像头对比度
    sensor.set_brightness(0)
    sensor.set_auto_gain(False) # 颜色跟踪必须关闭自动增益
    sensor.set_auto_whitebal(False) # 颜色跟踪必须关闭白平衡
    #lcd.rotation(1)    # LCD屏旋转90°
    #sensor.set_auto_gain(False)  # 必须关闭此功能，以防止图像冲洗…

# 黑色二维码专用初始化
def init_sensor_black_qr():
    sensor.reset()
    sensor.set_vflip(1)
    sensor.set_pixformat(sensor.GRAYSCALE)  # 灰度模式更适合黑色二维码
    sensor.set_framesize(sensor.QVGA)
    sensor.set_contrast(3)  # 增加对比度
    sensor.set_brightness(1)  # 轻微增加亮度
    # 不设置自动曝光，使用手动设置
    sensor.set_auto_exposure(False, exposure=10000)  # 中等曝光

# 循迹
def inin_sensor_2():
    sensor.reset()
    sensor.set_vflip(1)
    sensor.set_pixformat(sensor.GRAYSCALE)  # 设置像素格式为灰色
    sensor.set_framesize(sensor.QVGA)
    #sensor.set_contrast(2)  # 设置摄像头对比度
    sensor.set_brightness(-30)    # 设置摄像头亮度
    # sensor.set_auto_gain(0,13)  # 设置摄像自动增益模式

def init_sensor():
    lcd.init(freq=15000000)  # 初始化LCD
    # lcd.rotation(1)    # LCD屏旋转90°
    sensor.reset(freq=15000000)  # 复位和初始化摄像头
    sensor.set_vflip(1)  # 将摄像头设置成后置方式（所见即所得）
    # sensor.set_pixformat(sensor.RGB565)      # 设置像素格式为彩色 RGB565
    sensor.set_pixformat(sensor.GRAYSCALE)  # 设置像素格式为灰色
    sensor.set_framesize(sensor.QVGA)  # 设置帧大小为 QVGA (320x240)
    # sensor.set_vflip(True)      # 设置摄像头垂直翻转
    # sensor.set_hmirror(True)    # 设置摄像头水平镜像
    # sensor.set_saturation(-2)   # 设置摄像头饱和度
    sensor.set_contrast(2)  # 设置摄像头对比度
    # sensor.set_brightness(-2)    # 设置摄像头亮度
    # sensor.set_auto_gain(0,13)  # 设置摄像自动增益模式
    sensor.skip_frames(time=2000)  # 等待设置生效
    # clock = time.clock()  # 创建一个时钟来追踪 FPS（每秒拍摄帧数）

def Servo(symbol, angle):#这个是角度大于0
    if symbol == 43 or symbol == 3:  # 3是彩色二维码模式使用的
        if angle > 35:
            angle = 35  # 最大不超过35度
        # 保持angle不变（正数）
    elif symbol == 45 or angle < 0:  # 支持负数角度输入
        if angle < -18:
            angle = -18  # 修改为-18度，允许更大范围的向下角度
        angle = -angle  # 将负数转为正数，但反向动作

    tim_pwm = Timer(Timer.TIMER0, Timer.CHANNEL0, mode=Timer.MODE_PWM)
    S1 = PWM(tim_pwm, freq=50, duty=0, pin=17)
    S1.duty((angle + 90) / 180 * 10 + 2.5)

# 初始化传感器
init_sensor()  # 开机初始化
#init_sensor_3()


# --------------感光芯片配置  END -------------------


# ------------- 方法 START --------------------------
def max1(red, yellow, green):
    if red >= yellow and red >= green:
        return 1
    elif yellow >= red and yellow >= green:
        return 3
    else:
        return 2
# ------------- 方法 END --------------------------

# --------------串口UART部分  START -------------------

# 映射串口引脚
fm.register(6, fm.fpioa.UART1_RX, force=True)
fm.register(7, fm.fpioa.UART1_TX, force=True)

# 初始化串口
uart = UART(UART.UART1, 115200, read_buf_len=4096)

def UsartSend(str_data):
    # 串口发送函数
    uart.write(str_data)

# 交通灯
def Send_Traffical(src):
    print("发送")
    uart.write(bytes([0x55]))
    uart.write(bytes([0x02]))
    uart.write(bytes([0x92]))
    uart.write(bytes([0x01]))
    uart.write(bytes([src]))
    uart.write(bytes([0x00]))
    uart.write(bytes([0x00]))
    uart.write(bytes([0xBB]))

# 二维码
def Send_QR(src, fx):
    if len(src)==1:
        src+=' *'
    print(src)
    print("长度")
    print([len(src)])#长度
    print("方向")
    print(fx)#方向
    print("发送串口数据！！")
    uart.write(bytes([0x55]))
    uart.write(bytes([0x02]))
    uart.write(bytes([0x92]))
    uart.write(bytes([fx]))
    uart.write(bytes([len(src)]))  # 长度
    for qrdata in src:
        uart.write(qrdata)  # 返回对应的 ASCII 数值，或者 Unicode 数值，
    uart.write(bytes([0xBB]))

# 计算
def Send_QRDATA(src, fx):
    print(str(len(src)))
    print(str(fx))
    uart.write(bytes([0x55]))
    uart.write(bytes([0x02]))
    uart.write(bytes([0x92]))
    uart.write(bytes([fx]))
    uart.write(bytes([len(src)]))  # 长度
    for qrdata in src:
        uart.write(qrdata)  # 返回对应的 ASCII 数值，或者 Unicode 数值，
    uart.write(bytes([0xBB]))

# 二维码(发送中文)
def Send_QR2(src, fx):
    uart.write(bytes([0x55]))
    uart.write(bytes([0x02]))
    uart.write(bytes([0x92]))
    uart.write(bytes([fx]))
    uart.write(bytes([len(src) * 3]))  # 长度
    # for qrdata in src:
    #     print(qrdata)  # 返回对应的 ASCII 数值，或者 Unicode 数值，
    for qrdata in src:
        uart.write(qrdata)  # 返回对应的 ASCII 数值，或者 Unicode 数值，
    uart.write(bytes([0xBB]))

# 发生循迹数据
def Send_Trace(src1, src2, src3):
    uart.write(bytes([0x55]))
    uart.write(bytes([0x02]))
    uart.write(bytes([0x93]))
    uart.write(bytes([0x01]))
    uart.write(bytes([src1]))
    uart.write(bytes([src2]))
    uart.write(bytes([src3]))
    uart.write(bytes([0xBB]))

# --------------串口UART部分 END -------------------

# --------------定时器部分 START -------------------
# --------------交通灯识别优化版 START -------------------
# 颜色阈值
thresholds1 = [(60, 5, 30, 127, 20, 105)]  # 红色阈值
thresholds2 = [(100, 0, -128, -20, -128, 127)]  # 绿色阈值
thresholds3 = [(80, 60, -10, 127, 10, 127)]  # 黄色阈值

# 交通灯标签
traffic_light = ['Unknown', 'Red', 'Green', 'Yellow']

# 修改权重函数
def max1(red, yellow, green):
    # 如果都没有检测到，返回0表示未识别
    if red == 0 and yellow == 0 and green == 0:
        return 0

    # 调整权重
    red_weighted = red * 0.7     # 降低红色权重
    yellow_weighted = yellow * 1.5  # 提高黄色权重

    # 简化打印
    print("R:%.1f Y:%.1f G:%d" % (red_weighted, yellow_weighted, green))

    if red_weighted >= yellow_weighted and red_weighted >= green:
        return 1  # Red
    elif yellow_weighted >= red_weighted and yellow_weighted >= green:
        return 3  # Yellow
    else:
        return 2  # Green

def Traffical_Check():
    global FlagOK
    red = 0
    yellow = 0
    green = 0

    if FlagOK == 1:
        print("TRAFFIC DETECTION START")

        # 减少摄像头适应时间
        time.sleep(0.3)

        # 减少帧数以提高流畅度
        for i in range(10):  # 从15减少到10帧
            img1 = sensor.snapshot()

            # 先检测黄色
            yellow_detected = False
            bloby = img1.find_blobs(thresholds3, pixels_threshold=200, area_threshold=200, roi=(0, 0, 320, 120))
            if bloby:
                max_blob_y = max(bloby, key=lambda b: b.pixels())
                if max_blob_y.pixels() > 200:
                    yellow += 1
                    yellow_detected = True
                    img1.draw_rectangle(max_blob_y.rect(), color=(255, 255, 0))

            # 检测绿色
            green_detected = False
            blobb = img1.find_blobs(thresholds2, pixels_threshold=200, area_threshold=200, roi=(0, 0, 320, 120))
            if blobb:
                max_blob_g = max(blobb, key=lambda b: b.pixels())
                if max_blob_g.pixels() > 200:
                    green += 1
                    green_detected = True
                    img1.draw_rectangle(max_blob_g.rect(), color=(0, 255, 0))

            # 检测红色
            if not yellow_detected and not green_detected:
                blobr = img1.find_blobs(thresholds1, pixels_threshold=200, area_threshold=200, roi=(0, 0, 320, 120))
                if blobr:
                    max_blob_r = max(blobr, key=lambda b: b.pixels())
                    if max_blob_r.pixels() > 300:
                        red += 1
                        img1.draw_rectangle(max_blob_r.rect(), color=(255, 0, 0))

            # 显示当前帧但不打印
            lcd.display(img1)

        # 检查是否有颜色被检测到
        if red == 0 and yellow == 0 and green == 0:
            print("NO LIGHT DETECTED")
            Send_Traffical(0)
            return

        # 只打印关键统计结果
        print("R:%d Y:%d G:%d" % (red, yellow, green))

        # 确定最终结果
        m = max1(red, yellow, green)

        # 计算可信度
        total = red + yellow + green
        max_count = max(red, yellow, green)
        confidence = (max_count / total) * 100 if total > 0 else 0

        # 简化结果打印
        print("RESULT: %s (%.1f%%)" % (traffic_light[m], confidence))

        # 调整可信度判断标准
        if m == 3 and confidence >= 30:  # 黄色只需30%可信度
            print("SEND: %s" % traffic_light[m])
            Send_Traffical(m)
        elif m != 3 and confidence >= 50:  # 其他颜色需要50%可信度
            print("SEND: %s" % traffic_light[m])
            Send_Traffical(m)
        else:
            print("SEND: Unknown")
            Send_Traffical(0)

    # 重置状态
    if FlagOK == 2:
        FlagOK = 0
        print("DETECTION COMPLETE")
# --------------交通灯识别优化版 END ------------------
# #二维码算法处
##烽火台
def extract_qr_data(s1, s2):
    """
    从两个二维码字符串中提取有效信息并构建启动码

    参数:
    s1 (str): 第一个二维码信息字符串，例如 "5%@#<b3!#<1,3>"
    s2 (str): 第二个二维码信息字符串，例如 "2#A2%3b5|<2,4>"

    返回:
    str: 字符型字符串，对应6个字节
    """
    # 初始化结果数组 (6个字节的启动码，默认为0)
    startup_code = [0, 0, 0, 0, 0, 0]

    try:
        # 处理红色二维码
        # 提取第一个数字字符 (这里是5)
        digit_val = None
        for char in s1:
            if char.isdigit():
                digit_val = char
                break

        # 提取位置信息 (这里是<1,3>)
        position_match = re.search(r'<(\d+),(\d+)>', s1)
        if digit_val is not None and position_match:
            pos1 = int(position_match.group(1))  # 提取第一个位置 (1)
            pos2 = int(position_match.group(2))  # 提取第二个位置 (3)

            # 提取ASCII值
            q = ord(digit_val)  # 数字5的ASCII值 (0x35)
            w = ord('3')        # 数字3的ASCII值 (0x33)

            # 设置到启动码中对应位置
            if 0 <= pos1 < 6:
                startup_code[pos1] = q
            if 0 <= pos2 < 6:
                startup_code[pos2] = w

        # 处理绿色二维码
        # 查找第一个大写字母 (这里是A)
        uppercase_val = None
        for char in s2:
            if char.isupper():
                uppercase_val = char
                break

        # 查找第一个小写字母 (这里是b)
        lowercase_val = None
        for char in s2:
            if char.islower():
                lowercase_val = char
                break

        # 提取位置信息 (这里是<2,4>)
        position_match = re.search(r'<(\d+),(\d+)>', s2)
        if uppercase_val and lowercase_val and position_match:
            pos3 = int(position_match.group(1))  # 提取第一个位置 (2)
            pos4 = int(position_match.group(2))  # 提取第二个位置 (4)

            # 提取ASCII值
            m = ord(uppercase_val)  # 大写字母A的ASCII值 (0x41)
            n = ord(lowercase_val)  # 小写字母b的ASCII值 (0x62)

            # 设置到启动码中对应位置
            if 0 <= pos3 < 6:
                startup_code[pos3] = m
            if 0 <= pos4 < 6:
                startup_code[pos4] = n
        # 打印最终生成的启动码

        # 转换为字符型字符串
        result_str = ''.join(chr(b) for b in startup_code)

    except Exception as e:
        # 如果发生错误，返回默认值
        return "\x00\x00\x00\x00\x00\x00"

    # 返回最终的字符型字符串
    return result_str
###无线电算法
def char_to_hex(char1, char2):

    """将两个字符转换为一个十六进制字节"""
    try:

        hex_str = char1.upper() + char2.upper()

        return int(hex_str, 16)

    except ValueError as e:

        return 0x00
def extract_and_convert_to_s(qr1, qr2):
    """从两个二维码数据中提取差异字符并转换为4字节字符型字符串"""
    if qr1 is None or qr2 is None:

        print("Error: 二维码数据不能为空")

        return "\x02\x00\x00\x00"  # 返回默认字符型结果

    if len(qr1) != len(qr2):

        return "\x02\x00\x00\x00"

    if len(qr1) % 2 != 0:

        return "\x02\x00\x00\x00"
    result_qr1 = []
    result_qr2 = []
    for i in range(0, len(qr1), 2):

        pair1 = qr1[i:i + 2]

        pair2 = qr2[i:i + 2]
        if len(pair1) != 2 or len(pair2) != 2:

            return "\x02\x00\x00\x00"
        if pair1[0] != pair2[0]:

            result_qr1.append(pair1[0])

            result_qr2.append(pair2[0])

        if pair1[1] != pair2[1]:

            result_qr1.append(pair1[1])

            result_qr2.append(pair2[1])
    diff_chars = result_qr1 + result_qr2
    if len(diff_chars) != 6:

        return "\x02\x00\x00\x00"
    # 计算4个字节

    byte_list = [0x02]

    byte_list.append(char_to_hex(diff_chars[0], diff_chars[1]))

    byte_list.append(char_to_hex(diff_chars[2], diff_chars[3]))

    byte_list.append(char_to_hex(diff_chars[4], diff_chars[5]))
    # 转换为字符型字符串

    s = ''.join(chr(byte) for byte in byte_list)
    return s
def my_fullmatch(pattern, string):
    """
    如果整个字符串都匹配则返回匹配对象，否则返回 None。
    在 MicroPython 中，使用 match 方法需要特别注意参数传递。
    """
    try:
        m = re.match(pattern, string)
        if m and m.end() == len(string):
            return m
        return None
    except Exception as e:
        print("Error in my_fullmatch:", e)
        return None
def convert_format_to_regex(format_str):
    """
    将自定义格式字符串转换为正则表达式。
    约定：
      - X 表示大写字母 ([A-Z])
      - Y 表示数字 (\d)
    """
    mapping = {
        'X': '[A-Z]',
        'Y': '\\d'
    }
    regex_parts = []
    for ch in format_str:
        if ch in mapping:
            regex_parts.append(mapping[ch])
        else:
            # 非 X/Y 字符按字面值处理，进行转义
            regex_parts.append(re.escape(ch))
    regex_pattern = '^' + ''.join(regex_parts) + '$'
    return regex_pattern

def extract_bracket_data(qr_tab, selected_keys=None, include_prefix=False, valid_pattern=None, valid_format=None):
    """
    解析字符串中的括号数据。
    参数：
      - qr_tab: 待解析的字符串
      - selected_keys: 指定需要提取的括号类型，例如 ["<>", "[]", "{}", "()", "||"]。如果为 None，则提取所有类型。
      - include_prefix: 是否保留括号前的一个字符
      - valid_pattern: 直接提供一个正则表达式，用于校验括号内数据
      - valid_format: 可传入自定义格式。如果为字符串或字典形式

    返回：
      提取到的括号数据列表
    """
    # 定义需要解析的括号对 - 保持简洁
    brackets = {'[': ']', '<': '>', '{': '}', '(': ')', '|': '|'}
    stack = []  # 存储左括号及其索引
    result = []

    for i, char in enumerate(qr_tab):
        if char in brackets:  # 遇到左括号
            # 竖线特殊处理
            if char == '|' and stack and stack[-1][0] == '|':
                start_bracket, start_index = stack.pop()
                key = "||"  # 固定字符串比拼接更节省内存

                # 检查是否在选定的括号类型中
                if selected_keys is not None and key not in selected_keys:
                    continue

                content = qr_tab[start_index + 1:i]

                # 验证内容 - 内联验证以减少函数调用开销
                valid = True
                if isinstance(valid_format, dict) and key in valid_format:
                    format_str = valid_format[key]
                    if format_str == "XXY":
                        valid = (len(content) == 3 and
                                 content[0].isupper() and
                                 content[1].isupper() and
                                 content[2].isdigit())
                    elif format_str == "Y":
                        valid = (len(content) == 1 and content.isdigit())
                elif valid_pattern is not None:
                    try:
                        if not my_fullmatch(valid_pattern, content):
                            valid = False
                    except:
                        pass

                if not valid:
                    continue

                if include_prefix:
                    prefix = qr_tab[start_index - 1] if start_index > 0 else ''
                    result.append((prefix, key, content))
                else:
                    result.append((key, content))
            else:
                stack.append((char, i))
        elif char in brackets.values():  # 遇到右括号
            if not stack:
                continue  # 没有匹配的左括号，跳过

            start_bracket, start_index = stack[-1]
            if brackets.get(start_bracket) != char:
                continue  # 括号不匹配，跳过

            stack.pop()  # 弹出匹配的左括号
            key = start_bracket + char

            # 检查是否在选定的括号类型中
            if selected_keys is not None and key not in selected_keys:
                continue
            content = qr_tab[start_index + 1:i]
            # 验证内容 - 复用相同的验证逻辑
            valid = True
            if isinstance(valid_format, dict) and key in valid_format:
                format_str = valid_format[key]
                if format_str == "XXY":
                    valid = (len(content) == 3 and
                             content[0].isupper() and
                             content[1].isupper() and
                             content[2].isdigit())
                elif format_str == "Y":
                    valid = (len(content) == 1 and content.isdigit())
            elif valid_pattern is not None:
                try:
                    if not my_fullmatch(valid_pattern, content):
                        valid = False
                except:
                    pass

            if not valid:
                continue

            if include_prefix:
                prefix = qr_tab[start_index - 1] if start_index > 0 else ''
                result.append((prefix, key, content))
            else:
                result.append((key, content))

    return result

def move_char(ch, offset):
    """
    对字符进行移动位置操作：ch代表要要移动的对象，offset代表要移动几位
    """
    if len(ch) != 1:
        raise ValueError("输入必须为单个字符")

    if ch.isalpha():
        if ch.isupper():
            base = ord('A')
        else:
            base = ord('a')
        # 在字母表中循环（26个字母）
        new_ord = (ord(ch) - base + offset) % 26 + base
        return chr(new_ord)
    elif ch.isdigit():
        base = ord('0')
        new_ord = (ord(ch) - base + offset) % 10 + base
        return chr(new_ord)
    else:
        # 如果不是字母也不是数字，则直接返回原字符
        return ch

# 针对黄色模式的特殊处理函数
def process_yellow_qrcode(img, scan_roi, yellow_hsv_thresholds, yellow_lab_thresholds):
    # 步骤1: 直接在整个图像中查找二维码，使用极低的阈值
    # 对于黄色二维码，直接使用非常低的阈值
    direct_result = img.find_qrcodes(roi=scan_roi, threshold=50)
    if direct_result:
        return direct_result
    # 步骤2: 使用非常宽松的HSV阈值查找黄色区域
    hsv_blobs = img.find_blobs(yellow_hsv_thresholds, roi=scan_roi,
                            pixels_threshold=100, area_threshold=100, margin=20)
    # 步骤3: 如果找到黄色区域，在每个区域中寻找二维码
    if hsv_blobs:
        for blob in hsv_blobs:
            # 大幅扩展区域以确保包含完整二维码
            x, y, w, h = blob.rect()
            expanded_roi = (max(0, x-30), max(0, y-30),
                        min(w+60, 320-x), min(h+60, 240-y))

            # 在黄色区域中尝试多个非常低的阈值
            for threshold in [60, 50, 40, 30]:  # 非常低的阈值
                local_result = img.find_qrcodes(roi=expanded_roi, threshold=threshold)
                if local_result:
                    # 绘制找到的区域
                    img.draw_rectangle(expanded_roi, color=(255, 255, 0), thickness=2)
                    return local_result

    # 步骤4: 如果HSV失败，尝试LAB颜色空间
    lab_blobs = img.find_blobs(yellow_lab_thresholds, roi=scan_roi,
                            pixels_threshold=100, area_threshold=100, margin=20)

    if lab_blobs:
        for blob in lab_blobs:
            # 大幅扩展区域
            x, y, w, h = blob.rect()
            expanded_roi = (max(0, x-30), max(0, y-30),
                        min(w+60, 320-x), min(h+60, 240-y))

            # 尝试多个极低的阈值
            for threshold in [50, 40, 30, 25]:  # 非常低的阈值
                local_result = img.find_qrcodes(roi=expanded_roi, threshold=threshold)
                if local_result:
                    img.draw_rectangle(expanded_roi, color=(255, 255, 0), thickness=2)
                    return local_result

    # 步骤5: 最后尝试将整个图像分成几个区域，在每个区域中寻找
    regions = [
        (0, 0, 160, 120),       # 左上
        (160, 0, 160, 120),     # 右上
        (0, 120, 160, 120),     # 左下
        (160, 120, 160, 120),   # 右下
        (80, 60, 160, 120)      # 中间
    ]

    for region in regions:
        for threshold in [45, 35, 25]:
            local_result = img.find_qrcodes(roi=region, threshold=threshold)
            if local_result:
                img.draw_rectangle(region, color=(255, 255, 0), thickness=1)
                return local_result

    # 如果所有方法都失败，返回None
    return None

# 针对黑色二维码的处理函数
def process_black_qrcode(img, scan_roi):
    # 创建图像副本并增强对比度
    try:
        # 尝试直接在原图上寻找二维码
        result = img.find_qrcodes(roi=scan_roi, threshold=40)
        if result:
            return result

        # 二值化处理，更好地突出黑白边界
        binary_img = img.binary([(0, 70)], invert=False)

        # 在二值化图像上查找二维码
        binary_result = binary_img.find_qrcodes(roi=scan_roi, threshold=45)
        if binary_result:
            return binary_result

        # 使用更多区域扫描策略
        scan_regions = [
            (0, 0, 320, 80),     # 上部
            (0, 80, 320, 80),    # 中部
            (0, 160, 320, 80),   # 下部
            (80, 40, 160, 160)   # 中心区域(优先级高)
        ]

        # 优先扫描中心区域
        for region in scan_regions:
            region_result = binary_img.find_qrcodes(roi=region, threshold=40)
            if region_result:
                return region_result

        # 尝试最低阈值
        return img.find_qrcodes(roi=scan_roi, threshold=30)
    except Exception as e:
        print("Error in black QR processing:", e)
        # 发生错误时，退回到基本处理方法
        return img.find_qrcodes(roi=scan_roi, threshold=40)

# --------------二维码识别部分() START ----------
#左右滑动窗口
#roihd2=[(QR_j,0,130,240)]
#roi3=roihd2[0]
#QR_j=(QR_j+1)%190
#QR_j+=2
#上下滑动窗口
#roihd2=[(0,QR_j,320,120)]
#roi3=roihd2[0]
#QR_j=(QR_j+1)%120
#QR_j+=2

roi2 = [(0, 0, 340, 240), (0, 0, 320, 140), (0, 100, 320,140), (0, 0, 320, 180),(0,0,180,240),(150,0,180,240)]  # 上 下 全区域
roihd=[(0, 0, 320, 180),(0, 60, 320,180),(0,40,320,180),(0, 0, 340, 240)] #上下中全局滑动ROI
seen_qr_codes = set()

def Identify_QR(chars):
    s=""
    index=0
    """识别二维码并处理数据"""
    for roi in roi2:
        img.draw_rectangle(roi, color=color[6], thickness=2)
        for code in img.find_qrcodes(roi):
            qr_code_id = str(code.rect())
            if qr_code_id in seen_qr_codes:
                continue
            seen_qr_codes.add(qr_code_id)
            qr_tab = code.payload()
            print("原始数据:", qr_tab)
            """这里写判断逻辑"""
            try:
                selected_keys=["<>"]
                include_prefix=True
                S=extract_bracket_data(qr_tab,selected_keys=selected_keys,include_prefix=include_prefix)
                if str1 is None:
                    str1 = S
                elif str2 is None and str1 != S:
                    str2 = S
                if str1 and str2 and str1 != str2:
                    s = extract_and_convert_to_s(str1, str2)
                    index = 1
            except Exception as e:
                print("Error processing QR:", e)
            # 绘制二维码矩形框
            img.draw_rectangle(code.rect(), color=color[6], thickness=2)
            # 根据二维码的类型执行相应的操作
            if (chars[5] == 0 and index == 1) or (chars[5] == 24 and index == 1):
                print("车牌加烽火台第四位！")
                Send_QR(s, 0x03)
            elif (chars[5] == 8 and index == 2) or (chars[5] == 24 and index == 2):
                print("烽火台激活码！")
                Send_QR(s, 0x04)
            elif chars[5] & 0x04 == 0x04 and index == 3:  # 第三张二维码
                print("第三个二维码！")
                Send_QR(s, 0x03)
                break
            elif chars[5] == 0 and index == 26:  # 单个二维码
                print("单个二维码！")
                Send_QR(s, 0x03)
                break
            elif chars[5] == 0 and index == 56:  # 静态B第一个
                print("B1")
                Send_QR(s, 0x02)
                break
            elif chars[5] == 0 and index == 7:  # 静态B第二个
                print("B2")
                Send_QR(s, 0x04)
                break
# --------------彩色二维码识别部分() START ----------
# --------------彩色二维码识别部分() START ----------
roi5 = [(0, 0, 340, 240), (0, 0, 320, 140), (0, 100, 320,140), (0, 0, 320, 180),(0,0,180,240),(150,0,180,240)]

temp = 0
#nums=[1,1,1,0]
def lab_to_rgb(l, a, b):
    # 定义转换矩阵
    xyz_matrix = [[0.4124564, 0.3575761, 0.1804375],
                  [0.2126729, 0.7151522, 0.0721750],
                  [0.0193339, 0.1191920, 0.9503041]]
    # 将Lab颜色空间转换为XYZ颜色空间
    var_Y = (l + 16) / 116
    var_X = a / 500 + var_Y
    var_Z = var_Y - b / 200

    if var_Y ** 3 > 0.008856:
        var_Y_cubed = var_Y ** 3
    else:
        var_Y_cubed = (var_Y - 16 / 116) / 7.787

    if var_X ** 3 > 0.008856:
        var_X_cubed = var_X ** 3
    else:
        var_X_cubed = (var_X - 16 / 116) / 7.787

    if var_Z ** 3 > 0.008856:
        var_Z_cubed = var_Z ** 3
    else:
        var_Z_cubed = (var_Z - 16 / 116) / 7.787

    x = var_X_cubed * 95.047
    y = var_Y_cubed * 100.000
    z = var_Z_cubed * 108.883

    # 将XYZ颜色空间转换为RGB颜色空间
    r = x * xyz_matrix[0][0] + y * xyz_matrix[0][1] + z * xyz_matrix[0][2]
    g = x * xyz_matrix[1][0] + y * xyz_matrix[1][1] + z * xyz_matrix[1][2]
    b = x * xyz_matrix[2][0] + y * xyz_matrix[2][1] + z * xyz_matrix[2][2]

    return (r, g, b)

# 优化后的颜色识别函数 - 增强黄色识别能力
def get_improved_color(th):
    # 使用更宽松的阈值判断黄色
    r, g, b = th

    # 计算HSV值以更好地区分颜色
    max_val = max(r, g, b)
    min_val = min(r, g, b)
    delta = max_val - min_val

    # 黑白检测
    if max_val < 40:
        return (0, 0, 0)  # 黑色

    if min_val > 200 and delta < 30:
        return (255, 255, 255)  # 白色

    # 增强黄色识别 - 黄色的特征是R和G都很高，B较低
    if r > 150 and g > 150 and b < 120 and abs(r - g) < 80:
        return color[2]  # 黄色

    # 根据RGB分量的相对大小判断颜色
    if r > g and r > b and r > 100:
        return color[0]  # 红色

    if g > r and g > b and g > 100:
        return color[3]  # 绿色

    if b > r and b > g and b > 100:
        return color[5]  # 蓝色

    # 次级黄色检测 - 更宽松的条件
    if r > 120 and g > 120 and (r + g) > 2.5 * b:
        return color[2]  # 黄色

    # 默认返回一个颜色
    return color[4]  # 青色作为默认

# 旧的get_color函数，保留作为备份
def get_color(th):
    color_t=(0,0,0)
    if(th[0]>=10 and th[0]<=50):#蓝
        color_t = color[5]
    elif(th[0]>50 and th[0]<=79 and th[1]<50 and th[2]<220):#红色
        color_t = color[0]
    elif(th[0]>80 and th[0]<=96 and th[1]>50 and th[2]>220):#绿
        color_t = color[3]
    elif(th[0]>96):         #黄
        color_t = color[2]
    print("th: ", th)
    print(color_t)
    return color_t
qs=None
qs2=None
fenhou1=None
fenhou2=None

# 优化后的彩色二维码识别函数
def Identify_ColorQR(chars):
    global qs, qs2
    icc =0
    global fenhou1 ,fenhou2
    global angle, is_debug1, scan_roi_y, scan_direction, scan_wait_frames, qr_detected, last_qr_rect
    global scan_animation_counter, frame_skip, servo_delay
    # 帧跳过逻辑 - 黄色模式不跳过帧，其他颜色模式隔帧处理
    frame_skip = (frame_skip + 1) % 2
    if chars[4] != 0x03 and chars[4] != 0x05 and frame_skip != 0:  # 非黄色和黑色模式执行帧跳过
        # 只更新动画，不做复杂处理
        scan_animation_counter = (scan_animation_counter + 1) % 20

        # 绘制扫描线动画
        scan_roi = (0, scan_roi_y, scan_roi_width, scan_roi_height)
        img.draw_rectangle(scan_roi, color=color[6], thickness=2)

        # 绘制扫描线
        scan_line_y = scan_roi_y + (scan_animation_counter % scan_roi_height)
        img.draw_line(0, scan_line_y, scan_roi_width, scan_line_y, color=color[4], thickness=2)

        # 如果有已检测到的二维码，继续显示
        if qr_detected and last_qr_rect:
            img.draw_rectangle(last_qr_rect, color=(0, 255, 0), thickness=3)
        # 只做简单的扫描窗口移动
        scan_roi_y += scan_step * scan_direction
        if scan_roi_y <= 0:
            scan_roi_y = 0
            scan_direction = 1
        elif scan_roi_y >= 240 - scan_roi_height:
            scan_roi_y = 240 - scan_roi_height
            scan_direction = -1

        lcd.display(img)
        return
    # 创建扫描窗口ROI
    scan_roi = (0, scan_roi_y, scan_roi_width, scan_roi_height)

    # 更新动画计数器
    scan_animation_counter = (scan_animation_counter + 1) % 20

    # 绘制扫描线 - 更美观的扫描效果
    img.draw_rectangle(scan_roi, color=color[6], thickness=2)

    # 绘制扫描线(平滑动画)
    scan_line_y = scan_roi_y
    img.draw_line(0, scan_line_y, scan_roi_width, scan_line_y, color=color[4], thickness=2)

    # 如果检测到二维码，绘制高亮框
    if qr_detected and last_qr_rect:
        img.draw_rectangle(last_qr_rect, color=(0, 255, 0), thickness=3)  # 绿色高亮框
        # 在二维码上方显示"已识别"文字
        img.draw_string(last_qr_rect[0], last_qr_rect[1]-10, "QR Detected", color=(0, 255, 0), scale=1)

    # 处理舵机角度 - 使用新的参数控制更平滑更大范围的移动
    servo_delay += 1
    if servo_delay >= servo_delay_max:  # 只有达到延时才执行舵机移动
        servo_delay = 0
        if is_debug1:
            if angle < max_angle:
                angle += angle_step
                Servo(3, angle)  # 直接传入角度值，函数内部处理正负
            else:
                is_debug1 = 0
        else:
            if angle > min_angle:
                angle -= angle_step
                Servo(3, angle)  # 角度可能为负数，函数内部会处理
            else:
                is_debug1 = 1
    # 根据颜色模式调整参数
    result = None
    if chars[4]==0x03:  # 黄色模式
        # 使用专门的黄色二维码处理函数
        result = process_yellow_qrcode(img, scan_roi, yellow_hsv_thresholds, yellow_lab_thresholds)
    elif chars[4]==0x05:  # 黑色模式
        # 使用专门的黑色二维码处理函数
        result = process_black_qrcode(img, scan_roi)
    else:
        # 其他颜色模式使用标准参数
        result = img.find_qrcodes(roi=scan_roi)
    # 如果找到二维码，停留几帧
    if result:  # 确认result不为None且不为空
        # 设置检测到二维码标志
        qr_detected = True
        # 保存最后一个二维码的位置用于绘制
        if len(result) > 0:
            last_qr_rect = result[0].rect()

        scan_wait_frames += 1
        if scan_wait_frames >= max_wait_frames:
            scan_wait_frames = 0
        # 处理识别到的二维码，直接使用result变量，避免创建新列表
        for res in result:
            rect = res.rect()
            payload = res.payload()

            # 更新最后检测到的二维码区域
            last_qr_rect = rect
            qr_detected = True

            # 绘制框和角标
            img.draw_rectangle(rect, color=color[5], thickness=3)

            # 简化角标绘制，但保留视觉效果
            x, y, w, h = rect
            corner_len = 15  # 角标长度

            # 左上角
            img.draw_line(x, y, x + corner_len, y, color=(0, 255, 0), thickness=3)
            img.draw_line(x, y, x, y + corner_len, color=(0, 255, 0), thickness=3)

            # 右下角
            img.draw_line(x + w, y + h, x + w - corner_len, y + h, color=(0, 255, 0), thickness=3)
            img.draw_line(x + w, y + h, x + w, y + h - corner_len, color=(0, 255, 0), thickness=3)
            # 根据当前模式确定颜色
            color_t = color[4]  # 默认颜色
            if chars[4]==0x01:  # 红
                color_t = color[0]
            elif chars[4]==0x02:  # 绿
                color_t = color[3]
            elif chars[4]==0x03:  # 黄色
                color_t = color[2]
                # 黄色模式下使用闪烁效果，使识别结果更明显
                if (scan_animation_counter % 10) < 5:
                    img.draw_rectangle(rect, color=(255, 255, 0), thickness=4)  # 加粗黄色
                else:
                    img.draw_rectangle(rect, color=(255, 255, 0), thickness=3)  # 普通黄色
            elif chars[4]==0x04:  # 蓝
                color_t = color[5]
            elif chars[4]==0x05:  # 黑色
                color_t = (50, 50, 50)  # 深灰色代表黑色
                # 为黑色二维码添加动态边框效果
                if (scan_animation_counter % 6) < 3:
                    img.draw_rectangle(rect, color=(100, 100, 100), thickness=4)  # 加粗灰色
                else:
                    img.draw_rectangle(rect, color=(0, 0, 0), thickness=3)  # 黑色

            if chars[4] != 0x03 and chars[4] != 0x05:  # 非特殊模式正常绘制
                img.draw_rectangle(rect, color=color_t, thickness=2)
            # 处理二维码内容
            print("QR内容:", payload)
            if chars[4]==1:
                try:
                    selected_keys = ["<>"]
                    include_prefix = True
                    print(qs)
                    S = extract_bracket_data(payload, selected_keys=selected_keys, include_prefix=include_prefix)
                    print(S)
                    if qs is None and S[0][0] == 'A':
                        qs = S[0][2]
                    elif qs2 is None and qs != S[0][2] and S[0][0] == 'B':
                        qs2 = S[0][2]
                    print("str\n", qs)
                    print("str2\n", qs2)
                    if qs != qs2 and qs != None and qs2 != None:
                        s = extract_and_convert_to_s(qs, qs2)
                        print(s)
                        qs=None;
                        qs2=None;
                        Send_QR(s, 0x02)
                        break
                except Exception as e:
                    print("Error processing QR:", e)
            if chars[4]==2:
                try:
                    S = payload
                    print("payload\n", payload)
                    print("fenhou1\n", fenhou1)
                    print("fenhou2\n", fenhou2)
                    if fenhou1 is None:
                        fenhou1 = S
                    elif fenhou2 is None and fenhou1 != S:
                        fenhou2 = S
                    if fenhou1 != fenhou2 and fenhou1 is not None and fenhou2 is not None:
                        s = extract_qr_data(fenhou1, fenhou2)
                        print(s)
                        Send_QR(s, 0x01)
                except Exception as e:
                    print("Error processing QR:", e)
            if chars[4] == 3:
                try:
                    S = payload
                    Send_QR(S, 0x04)
                except Exception as e:
                    print("Error processing QR:", e)
            else:
                scan_wait_frames = (scan_wait_frames + 1) % 10  # 用于扫描线动画
                qr_detected = False  # 重置二维码检测标志
                # 移动扫描窗口 - 更平滑的移动
                scan_roi_y += scan_step * scan_direction
                # 检查是否到达边界 - 平滑转向
                if scan_roi_y <= 0:
                    scan_roi_y = 0
                    scan_direction = 1  # 向下扫描
                elif scan_roi_y >= 240 - scan_roi_height:
                    scan_roi_y = 240 - scan_roi_height
                    scan_direction = -1  # 向上扫描
                # 直接显示原始图像，省略处理后的图像显示
            lcd.display(img)
# --------------二维码识别部分 END -------------------
# ------------------- 巡线(横)10个点 START -----------------
black_h_10 = [(0, 51, -111, 82, -91, 121)]  # 黑线的阈值
#阈值
blackH0 = [(55, 0, 69, -12, -65, 56)]
blackH1 = [(75, 0, 69, -12, -65, 56)]
blackH2 = [(0, 31, 117, -110, 10, 1)]
blackH3 = [(80, 0, 127, -128, -128, 127)]
blackH4 = [(90, 0, 127, -128, -128, 127)]
blackH5 = [(95, 0, 127, -128, -128, 127)]
blackH = [(53, 0)]


roi_10 = [(1, 170, 33, 70), (43, 178, 25, 70), (75, 180, 25, 70), (110, 179, 25, 70),
          (151, 183, 41, 70),  # 中心点
          (203, 178, 36, 70), (250, 180, 30, 70), (290, 170, 30, 70)]  # 右
roi_ding_10 = (85, 5, 140, 30)  # 大方块
roi_ding_12 = (165,35,30,12) #入库辅助线
roi_big_ding=(0,0,320,50)


def video_line_across_2():
    flag1 = [0, 0, 0, 0, 0, 0, 0, 0]
    flag2 = [0, 0, 0]
    flag3 = 0
    blob1 = img.find_blobs(blackH, roi=roi_10[0], pixels_threshold=150)  # 左
    blob2 = img.find_blobs(blackH, roi=roi_10[1], pixels_threshold=50)  # 左
    blob3 = img.find_blobs(blackH4, roi=roi_10[2], pixels_threshold=50)  # 左
    blob4 = img.find_blobs(blackH5, roi=roi_10[3], pixels_threshold=50)  # 左
    blob5 = img.find_blobs(blackH4, roi=roi_10[4], pixels_threshold=50)  # 中
    blob6 = img.find_blobs(blackH4, roi=roi_10[5], pixels_threshold=50)  # 右
    blob7 = img.find_blobs(blackH3, roi=roi_10[6], pixels_threshold=50)  # 右
    blob8 = img.find_blobs(blackH, roi=roi_10[7], pixels_threshold=100)  #右
    blob9 = img.find_blobs(blackH, roi=roi_10[0], pixels_threshold=150)  # 左
    blob10 = img.find_blobs(blackH, roi=roi_10[7], pixels_threshold=150)  # 右
    blob11 = img.find_blobs(blackH3, roi=roi_ding_10, pixels_threshold=220)  # 顶
    blob12 = img.find_blobs(blackH3, roi=roi_ding_12, pixels_threshold=100)

    if blob1:
        flag1[0] = 1  # 左边检测到黑线
        print("左： %d" % blob1[0].pixels())
    if blob2:
        flag1[1] = 1  # 左边检测到黑线
        print("1： %d" % blob2[0].pixels())
    if blob3:
        flag1[2] = 1  # 左边检测到黑线
        print("2： %d" % blob3[0].pixels())
    if blob4:
        flag1[3] = 1  # 中间检测到黑线
        print("3： %d" % blob4[0].pixels())
    if blob5:
        flag1[4] = 1  # 右边检测到黑线
        print("4： %d" % blob5[0].pixels())
    if blob6:
        flag1[5] = 1  # 右边检测到黑线
        print("5： %d" % blob6[0].pixels())
    if blob7:
        flag1[6] = 1  # 右边检测到黑线
        print("6： %d" % blob7[0].pixels())
    if blob8:
        flag1[7] = 1  # 右边检测到黑线
        print("7： %d" % blob8[0].pixels())
    if blob9:
        flag2[0] = 1  # 左
    if blob10:
        flag2[2] = 1  # 右
    if blob11:
        print("11： %d" % blob11[0].pixels())
        flag2[1] = 1  # 中
    if blob12:
        print("12： %d" % blob12[0].pixels())
        flag3 = 1
    data1 = flag1[0] << 7 | flag1[1] << 6 | flag1[2] << 5 | flag1[3] << 4 | flag1[4] << 3 | flag1[5] << 2 | flag1[6] << 1 | flag1[7] << 0
    data2 = flag2[0] << 2 | flag2[1] << 1 | flag2[2]
    data3 = flag3
    Send_Trace(data1, data2, data3)
# ------------------- 停车 ------------------------------
roi_l_s = (0, 108, 43, 15)
roi_r_s = (265, 108, 43, 15)


def stop_car():
    data1 = 0
    blob1 = img.find_blobs(black_h_10, roi=roi_l_s)
    blob2 = img.find_blobs(black_h_10, roi=roi_r_s)
    if blob1 and blob2:
        data1 = 1
    Send_Trace(data1, 0, 0)


# ------------------- 打印roi ------------------------------
def LCD_display():
    #0
    roi=roi_10[0]
    for blob in img.find_blobs(blackH, roi=roi, merge=True):
        img.draw_rectangle(blob.rect())
        img.draw_cross(blob.cx(),blob.cy())
    #1
    roi=roi_10[1]
    for blob in img.find_blobs(blackH, roi=roi, merge=True):
        img.draw_rectangle(blob.rect())
        img.draw_cross(blob.cx(),blob.cy())
    #2
    roi=roi_10[2]
    for blob in img.find_blobs(blackH4, roi=roi, merge=True):
        img.draw_rectangle(blob.rect())
        img.draw_cross(blob.cx(),blob.cy())
    #3
    roi=roi_10[3]
    for blob in img.find_blobs(blackH5, roi=roi, merge=True):
        img.draw_rectangle(blob.rect())
        img.draw_cross(blob.cx(),blob.cy())
    #中心点
    roi=roi_10[4]
    for blob in img.find_blobs(blackH4, roi=roi, merge=True):
        img.draw_rectangle(blob.rect())
        img.draw_cross(blob.cx(),blob.cy())
    #5
    roi=roi_10[5]
    for blob in img.find_blobs(blackH4, roi=roi, merge=True):
        img.draw_rectangle(blob.rect())
        img.draw_cross(blob.cx(),blob.cy())
    #6
    roi=roi_10[6]
    for blob in img.find_blobs(blackH3, roi=roi, merge=True):
        img.draw_rectangle(blob.rect())
        img.draw_cross(blob.cx(),blob.cy())
    #7
    roi=roi_10[7]
    for blob in img.find_blobs(blackH, roi=roi, merge=True):
        img.draw_rectangle(blob.rect())
        img.draw_cross(blob.cx(),blob.cy())
    #ding
    roi=roi_ding_10
    for blob in img.find_blobs(blackH3, roi=roi, merge=True):
        img.draw_rectangle(blob.rect())
        img.draw_cross(blob.cx(),blob.cy())
    roi=roi_ding_12
    for blob in img.find_blobs(blackH3, roi=roi, merge=True):
        img.draw_rectangle(blob.rect())
        img.draw_cross(blob.cx(),blob.cy())
    for rx1 in roi_10:
        img.draw_rectangle(rx1, color=(255, 0, 0), thickness=2)  # 绘制出roi区域
    img.draw_rectangle(roi_ding_10, color=(255, 0, 0), thickness=2)  # 绘制出roi区域
    img.draw_rectangle(roi_ding_12, color=(255, 0, 0), thickness=2)  # 绘制出roi区域

# 将蓝灯引脚IO12配置到GPIO0，K210引脚支持任意配置
fm.register(12, fm.fpioa.GPIO0)
LED_B = GPIO(GPIO.GPIO0, GPIO.OUT)  # 构建LED对象
# 按键KEY用于清屏
fm.register(16, fm.fpioa.GPIO1, force=True)
btn_debug = GPIO(GPIO.GPIO1, GPIO.IN)
data = []
chen=False
line_Patrol1 = False
line_Patrol2 = False
line_Patrol3 = False
line1 = False
QR1 = False
traffic1 = False
LCD1 = True
stop1 = False
a=255
b=0
i=0
j=0
num = 0
#一直拍照
while True:
    img = sensor.snapshot()  # 获取图片
    LED_B.value(0)  # 点亮LED
    if uart.any():#检查UART缓冲区中是否有数据
        data = uart.read(8)#读取8字节的字节
        ColorQr = False
        if len(data) >= 8:
            if (data[0] == 0x55) and (data[1] == 0x02) and (data[7] == 0xBB):
                #print(data[2])
                #print(data[3])#可能跟通信协议有关系，需要对别下
                if data[2] == 0x91:
                    if data[3] == 0x01:  # 舵机调整
                        Servo(data[4], data[5])
                    elif data[3] == 0x06:
                        line_Patrol3 = True
                        print("开始循迹!!!")
                    elif data[3] == 0x07:
                        line_Patrol3 = False
                        print("结束循迹!!!")
                elif data[2] == 0x92:
                    print(data[3])#可能跟通信协议有关系，需要对别下
                    if data[3] == 0x01:
                        inin_sensor_1()  # 二维码
                        QR1 = True
                        line_Patrol3=False
                        print("开始识别二维码！")
                    elif data[3] == 0x02:
                        QR1 = False
                        print("结束识别二维码！")

                    elif data[3] == 0x03:
                        traffic1 = True
                        line_Patrol3=False
                        if FlagOK !=1:
                            FlagOK = 1
                            print("开始识别交通灯")
                            sensor.set_pixformat(sensor.RGB565)
                            sensor.set_brightness(-2)
                            sensor.set_contrast(0)  # 设置摄像头对比度
                            sensor.set_auto_gain(0, 0)
                            time.sleep(1.5)  # 等待交通灯变暗
                        elif FlagOK == 1:
                            print("正在识别")
                    elif data[3] == 0x04:
                        traffic1 = False
                        FlagOK = 2
                        print("结束识别交通灯！")
                    elif data[3] == 0x05:
                        inin_sensor_1()  # 二维码
                        print("彩色")
                    elif data[3] == 0x06:
                        inin_sensor_2()  # 循迹
                        print("黑白")
                    elif data[3] == 0x07:
                        init_sensor_3()  # 彩色二维码初始化
                        ColorQr = True
                        line_Patrol3=False
                        # 重置扫描窗口位置和状态
                        scan_roi_y = 0
                        scan_direction = 1
                        scan_wait_frames = 0
                        scan_animation_counter = 0
                        frame_skip = 0
                        qr_detected = False
                        last_qr_rect = None
                        angle = 0  # 重置舵机角度为中间位置
                        servo_delay = 0  # 重置舵机延时

                        # 黄色模式特殊处理
                        if data[4]==0x03:  # 如果是黄色模式
                            # 完全重置传感器，使用专门的黄色二维码参数
                            sensor.reset()
                            sensor.set_pixformat(sensor.RGB565)
                            sensor.set_framesize(sensor.QVGA)
                            sensor.set_vflip(1)
                            sensor.set_auto_whitebal(False)
                            sensor.set_auto_gain(False)
                            sensor.set_auto_exposure(False, exposure=18000)  # 大幅增加曝光
                            sensor.set_brightness(4)  # 更高亮度
                            sensor.set_contrast(3)
                            sensor.set_saturation(4)  # 增加饱和度以增强色彩
                            # 可选：添加gamma校正使黄色更突出
                            sensor.set_windowing((0, 0, 320, 240))  # 确保使用全分辨率
                            scan_step = 2  # 黄色模式下的扫描步长，从1增加到2
                            servo_delay_max = 1  # 黄色模式舵机移动延时，保持与常规模式一致
                            print("识别黄色二维码！")
                        elif data[4]==0x05:  # 如果是黑色模式
                            # 初始化黑色二维码专用参数
                            init_sensor_black_qr()
                            scan_step = 3  # 黑色模式下的扫描步长
                            servo_delay_max = 1  # 黑色模式舵机移动延时
                            print("识别黑色二维码！")
                        else:
                            # 其他颜色二维码设置
                            scan_step = 4  # 非特殊模式使用更快的扫描速度
                            print("识别彩色二维码！")
                    elif data[3] == 0x08:
                        ColorQr = False
                        print("结束识别彩色二维码！")

    if line_Patrol3:  # 循迹
        video_line_across_2()
    elif stop1:  # 停
        stop_car()
    elif QR1:  # 识别二维码A
        Identify_QR(data)
    elif traffic1:  # 识别交通灯
        Traffical_Check()
    elif ColorQr:  # 识别彩色二维码
        Identify_ColorQR(data)
    elif LCD1:
        pass

    lcd.display(img)
    if btn_debug.value() == 0:
        line_Patrol3 = False
        QR1 = False
        LCD1 = False












































