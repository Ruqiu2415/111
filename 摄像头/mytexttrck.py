"""
 交通灯识别 & 二维码识别 & 循迹
"""
import math
import sensor, image, time, lcd
import binascii
import re
from Maix import GPIO
from machine import Timer, PWM, UART
from fpioa_manager import fm
angle = 0
# 交通灯
FlagOK = 0
# 直线检测（官方）
is_debug = False
is_debug1 = 1
# 0: 红：(255，0，0)  1:橙: (255，125，0)  2:黄：(255，255，0)
# 3: 绿：(0，255，0)  4:青: (0, 255, 255)  5:蓝：(0，0，255)  6:紫: (255, 0, 255)
# 颜色表
color = [(255, 0, 0), (255, 125, 0), (255, 255, 0), (0, 255, 0), (0, 255, 255), (0, 0, 255), (255, 0, 255)]

DISTORTION_FACTOR = 1  # 设定畸变系数
IMG_WIDTH = 240
IMG_HEIGHT = 320


# --------------感光芯片配置  START -------------------
# 二维码
def inin_sensor_1():
    sensor.reset()
    sensor.set_vflip(1)
    sensor.set_brightness(-2)  # 设置摄像头亮度
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QVGA)
    sensor.set_contrast(100)  # 设置摄像头对比度
    sensor.set_brightness(0)
    #lcd.rotation(1)    # LCD屏旋转90°
    #sensor.set_auto_gain(False)  # 必须关闭此功能，以防止图像冲洗…


# 循迹
def inin_sensor_2():
    sensor.reset()
    sensor.set_vflip(1)
    sensor.set_pixformat(sensor.GRAYSCALE)  # 设置像素格式为灰色
    sensor.set_framesize(sensor.QVGA)
    #sensor.set_contrast(2)  # 设置摄像头对比度
    sensor.set_brightness(-30)  # 设置摄像头亮度
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


def Servo(symbol, angle):
    print("sy: %d" % symbol)
    print("angle: %d" % angle)
    if symbol == 43:
        if angle > 35:
            angle = 35
        pass
        print("+and %d" % angle)
    elif symbol == 45:
        if angle > 80:
            angle = 80
        angle = -angle
        print("-and %d" % angle)
    tim_pwm = Timer(Timer.TIMER0, Timer.CHANNEL0, mode=Timer.MODE_PWM)
    S1 = PWM(tim_pwm, freq=50, duty=0, pin=17)
    S1.duty((angle + 90) / 180 * 10 + 2.5)

init_sensor()  # 开机初始化
#inin_sensor_1()

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
    if len(src) == 1:
        src += ' *'
    print(src)
    print([len(src)])
    print(fx)
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
is_need_send_data = False  # 是否需要发送数据的信号标志
QR_num = 0
QR_Flag = False


def uart_time_trigger(tim):
    global is_need_send_data, QR_Flag, QR_num
    if QR_Flag:
        QR_num += 1
    if QR_num >= 200:  # 10秒计时
        QR_Flag = False
        QR_num = 0

    is_need_send_data = True


tim1 = Timer(Timer.TIMER1, Timer.CHANNEL1, mode=Timer.MODE_PERIODIC, period=50, callback=uart_time_trigger)

LINE_COLOR_THRESHOLD = [(0, 134)]
# LIGHT_LINE_COLOR_THRESHOLD = [(9, 88)]
# LINE_COLOR_THRESHOLD = [(0, 52, -19, 0, -1, 14)]
# LINE_COLOR_THRESHOLD = [(0, 32, -23, 16, -5, 28)]


# --------------交通灯识别 START -------------------
# 红
thresholds1 = [(70, 9, 25, 127, 14, 105)]
#[(100, 54, 9, 127, -128, 127)]
##[(70, 9, 25, 127, 14, 105)]
# 绿
thresholds2 = [(100, 0, -128, -20, -128, 127)]
##[(100, 0, -111, -16, -6, 30)]
#[(100, 0, -128, -20, -128, 127)]

# 黄
thresholds3 = [(100, 83, -33, 127, 18, 105)]
#[(95, 100, 127, -128, 5, 127)]
##[(100, 83, -33, 127, 18, 105)]


traffic_light = ['红色', '绿色', '黄色']


def Traffical_Check():
    global FlagOK
    red = 0
    yellow = 0
    green = 0
    if FlagOK == 1:
        print("进入方法")
        for i in range(10):
            img1 = sensor.snapshot()
            # 图像预处理步骤
            img1.lens_corr(1.8)  # 畸变矫正
            img1.histeq()  # 直方图均衡化
            img1.mean(1)  # 均值滤波

            blobr = img1.find_blobs(thresholds1, pixels_threshold=200, area_threshold=200, roi=(0, 0, 313, 112))
            if blobr:
                red += 1
                print("red： %d" % red)
            bloby = img1.find_blobs(thresholds3, pixels_threshold=200, area_threshold=200, roi=(0, 0, 313, 112))
            if bloby:
                yellow += 1
                print("yellow： %d" % yellow)
            blobb = img1.find_blobs(thresholds2, pixels_threshold=200, area_threshold=200, roi=(0, 0, 313, 112))
            if blobb:
                green += 1
                print("blobb： %d" % green)
        m = max1(red, yellow, green)
        print("m： %d" % m)
        print(traffic_light[m - 1])
        Send_Traffical(m)

    if FlagOK == 2:
        # inin_sensor_1()
        FlagOK = 0


# --------------交通灯是识别 END -------------------


#二维码算法处


def is_prime(x):
    if x <= 1:
        return False
    for i in range(2, x):
        if x % i == 0:
            break
    else:
        return True
    return False


def translateNum(num):
    s = str(num)
    a = b = 1
    for i in range(2, len(s) + 1):
        a, b = (a + b if "10" <= s[i - 2:i] <= "25" else a), a
    return a


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

"""感性区域##"""
# 调整后的roi2，添加中间区域(80, 60, 180, 120)
roi2 = [
    (0, 0, 340, 240),        # 全图覆盖
    (80, 60, 180, 120),       # 新增中间区域ROI ★核心修改★
    (0, 0, 320, 140),
    (0, 100, 320, 140),
    (0, 0, 320, 180),
    (0, 0, 180, 240),
    (150, 0, 180, 240)
]  # 上下全区域+中间增强

roihd = [(0, 0, 320, 180), (0, 60, 320, 180), (0, 40, 320, 180), (0, 0, 340, 240)]  # 上下中全局 # 上下中全局滑动ROI
# 已识别二维码记录，避免重复识别
seen_qr_codes = set()
def extract_plate_string(qr_tab):
    """提取并检查车牌字符串格式"""
    start = qr_tab.find('<')
    end = qr_tab.find('>')
    if start != -1 and end != -1 and end > start:
        plate_string = qr_tab[start + 1:end]
        if len(plate_string) == 6 and (plate_string[0].isalpha() and plate_string[1].isdigit() and
                                       plate_string[2].isdigit() and plate_string[3].isalpha() and
                                       plate_string[4].isdigit() and plate_string[5].isdigit()):
            return plate_string
    return None

def extract_bracket_data(qr_tab):
    """提取方括号、尖括号、大括号内的内容"""
    bracket_data = {"[]": "", "<>": "", "{}": ""}
    for i in range(len(qr_tab) - 3):
        if qr_tab[i] == '[' and qr_tab[i + 3] == ']':
            bracket_data["[]"] += qr_tab[i + 1] + qr_tab[i + 2]
        elif qr_tab[i] == '<' and qr_tab[i + 3] == '>':
            bracket_data["<>"] += qr_tab[i + 1] + qr_tab[i + 2]
        elif qr_tab[i] == '{' and qr_tab[i + 3] == '}':
            bracket_data["{}"] += qr_tab[i + 1] + qr_tab[i + 2]
    return bracket_data

def Identify_QR(chars):
    # 扫描所有ROI区域
    for roi in roi2:
        img.draw_rectangle(roi, color=color[6], thickness=2)  # 绘制扫描区域框
        for code in img.find_qrcodes(roi):  # 扫描二维码
            qr_code_id = str(code.rect())  # 唯一标识符（矩形框）
            if qr_code_id in seen_qr_codes:
                continue  # 如果二维码已经识别过，跳过

            seen_qr_codes.add(qr_code_id)  # 记录已识别二维码

            # 保持原有数据处理逻辑
            qr_tab = code.payload()
            print("原始数据:", qr_tab)
            plate_string = extract_plate_string(qr_tab)
            bracket_data = extract_bracket_data(qr_tab)
            formula_string = bracket_data["<>"] + bracket_data["{}"] + bracket_data["[]"]
            print("chars[5]:", chars[5])
            # 判断二维码类型并设置对应的处理内容
            s = ""
            index = 0
            if plate_string:
                s = plate_string
                index = 1
                print("车牌:", s)
            elif formula_string:
                s = formula_string
                index = 2
                print("烽火台激活码:", s)

            # 绘制二维码矩形框
            img.draw_rectangle(code.rect(), color=color[6], thickness=2)

            # 根据二维码的类型执行相应的操作
            if chars[5] == 16 and index == 1:
                print("车牌！")
                Send_QR(s, 0x02)
                break;
            elif chars[5]==16 and index ==2:
                print("烽火台激活码")
                Send_QR(s, 0x04)
                break;
            elif chars[5]==24 and index==1:
                print("车牌")
                Send_QR(s,0x02)
                break;
            elif chars[5] == 24 and index == 2:
                print("烽火台激活码！")
                Send_QR(s, 0x04)
                break;
            elif chars[5] & 0x04 == 0x04 and index == 3:  # 第三张二维码
                print("第三个二维码！")
                Send_QR(s, 0x03)
                break;
            elif chars[5] == 0 and index == 26:  # 单个二维码
                print("单个二维码！")
                Send_QR(s, 0x03)
                break;
            elif chars[5] == 0 and index == 56:  # 静态B第一个
                print("B1")
                Send_QR(s, 0x02)
                break;
            elif chars[5] == 0 and index == 7:  # 静态B第二个
                print("B2")
                Send_QR(s, 0x04)
                break;
# --------------彩色二维码识别部分() START ----------
roi5 = [(0, 0, 340, 240), (0, 0, 320, 140), (0, 100, 320, 140), (0, 0, 320, 180), (0, 0, 180, 240), (150, 0, 180, 240)]

#thresholdRed = [(40, 71, 36, 80, -14, 42)]
thresholdRed = [(52, 96, 6, 41, -7, 18)]  #[(45, 71, 12, 115, -33, 75)]

#thresholdBlue = [(82, 41, -10, 1, -44, -3)]
thresholdBlue = [(82, 41, -10, 1, -44, -11)]

#thresholdGreen = [(18, 76, -66, -17, 3, 48)]
thresholdGreen = [(72, 53, -28, -3, -19, 14)]

#thresholdYello = [(54, 91, 33, -12, 72, 41)]
thresholdYello = [(100, 46, -32, -3, -3, 127)]
temp = 0

#nums=[1,1,1,0]
def get_color(th):
    color_t = (0, 0, 0)
    #a_value负数为绿色，正数为红色
    if (th.a_value() >= -128 and th.a_value() < -50 and th.b_value() < 0):
        color_t = color[0]
    elif (th.a_value() >= 50 and th.a_value() <= 127 and th.b_value() < 0):
        color_t = color[3]
    elif (th.b_value() >= 50 and th.b_value() <= 127 and th.a_value() < 0):
        color_t = color[5]
    return color_t


def Identify_ColorQR(chars):
    img_rgb = sensor.snapshot()
    img_rgb.lens_corr(1.2)  #畸变矫正方法来修复图像失真问题
    img_gry = img_rgb.copy()
    img_gry.to_grayscale()  #将RGB图像转换为灰度图像
    img_gry.laplacian(1, sharpen=True, invert=False)
    img_gry.histeq(adaptive=True, clip_limit=30)
    img_gry.gamma_corr(gamma=2.0)
    result = img_gry.find_qrcodes()

    global QR_j
    global flag
    global s
    global count
    color1 = ""
    print("chars[4]:")
    print(chars[4])
    if chars[4] == 0x01:  #红
        color1 = color[0]
    elif chars[4] == 0x02:  #绿
        roi3 = roi2[2]
        color1 = color[3]
    elif chars[4] == 0x03:  #蓝
        color1 = color[5]
    elif chars[4] == 0x04:  #黄
        color1 = color[2]

    s = ""
    qrcode_result = []
    for res in result:
        i = 0
        if qrcode_result != []:
            for qrc in qrcode_result:
                if qrc.get("payload") == res.payload():
                    i = 1
                    break
            if i == 0:
                tmp = {"rect": res.rect(), "payload": res.payload()}
                qrcode_result.append(tmp)
        else:
            tmp = {"rect": res.rect(), "payload": res.payload()}
            qrcode_result.append(tmp)
    img_rgb.laplacian(1, sharpen=True, invert=False)  #图像锐化
    img_rgb.histeq(adaptive=True, clip_limit=30)  #自适应直方图均衡
    img_rgb.gamma_corr(gamma=2.5)  #伽玛校正
    for qrc in qrcode_result:
        his = img_rgb.get_histogram(roi=qrc.get("rect"))
        stat = his.get_statistics()
        th = his.get_threshold()
        #print(th)
        color_t = get_color(th)
        qrc["color"] = color_t
        if (color1 == qrc.get("color")):
            print(color_t)
            print(qrc.get("color"))
            img_rgb.draw_rectangle(qrc.get("rect"), color=color_t, thickness=3)
            qr_Tab = qrc.get("payload")
            l = len(qr_Tab)
            left, right, count = 0, 0, 0
            num1 = 0
            num2 = 0
            s = ""

###########################################################################################################
            for i in range(l):
                if (qr_Tab[i] == '<'):
                    while len(s) < 6:
                        if (qr_Tab[i] >= '0' and qr_Tab[i] <= '9') or (qr_Tab[i] >= 'A' and qr_Tab[i] <= 'Z'):
                            s += qr_Tab[i]
                        i += 1
            Send_QR(s, 0x02)  # 串口
        break
    #lcd.display(img_gry)
# --------------二维码识别部分 END -------------------
# ------------------- 巡线(横)10个点 START -----------------
black_h_10 = [(0, 60, -120, 90, -100, 130)]  # 调整亮度和色度范围
blackH0 = [(60, 0, 75, -15, -70, 60)]  # 调整亮度和色度范围
blackH1 = [(80, 0, 75, -15, -70, 60)]  # 调整亮度和色度范围
blackH2 = [(0, 35, 120, -115, 15, 5)]  # 调整亮度和色度范围
blackH3 = [(85, 0, 130, -130, -130, 130)]  # 调整亮度和色度范围
blackH4 = [(95, 0, 130, -130, -130, 130)]  # 调整亮度和色度范围
blackH5 = [(100, 0, 130, -130, -130, 130)]  # 调整亮度和色度范围

# black_h_10 = [(6, 65)]  # 黑线的阈值
#roi_10 = [(0, 130, 30, 60), (55, 130, 15, 60),  (85, 130, 20, 80),(115,170,30,60),
#(165, 140, 30, 60),  # 中心点
#(220, 130, 30, 60), (275, 120, 20, 80), (298, 130, 30, 60)]  # 右
#roi_di_10 = (0, 100, 320, 75)  # 面积
#roi_di_l_10 = (0, 119, 30, 40)
#roi_di_r_10 = (290, 119, 30, 40)
#roi_ding_10 = (105, 5, 100, 30)  # 大方块

roi_10 = [(1, 170, 33, 70), (43, 178, 25, 70), (75, 180, 25, 70), (110, 179, 25, 70),
          (151, 183, 41, 70),  # 中心点
          (203, 178, 36, 70), (250, 180, 30, 70), (290, 170, 30, 70)]  # 右
roi_ding_10 = (85, 5, 140, 30)  # 大方块
roi_ding_12 = (165, 35, 30, 12)  #入库辅助线
roi_big_ding = (0, 0, 320, 50)
def video_line_across_2():
    flag1 = [0, 0, 0, 0, 0, 0, 0, 0]
    flag2 = [0, 0, 0]
    flag3 = 0
    blob1 = img.find_blobs(blackH4, roi=roi_10[0], pixels_threshold=150)  # 左
    blob2 = img.find_blobs(blackH3, roi=roi_10[1], pixels_threshold=50)  # 左
    blob3 = img.find_blobs(blackH4, roi=roi_10[2], pixels_threshold=50)  # 左
    blob4 = img.find_blobs(blackH5, roi=roi_10[3], pixels_threshold=50)  # 左
    blob5 = img.find_blobs(blackH4, roi=roi_10[4], pixels_threshold=50)  # 中
    blob6 = img.find_blobs(blackH4, roi=roi_10[5], pixels_threshold=50)  # 右
    blob7 = img.find_blobs(blackH3, roi=roi_10[6], pixels_threshold=50)  # 右
    blob8 = img.find_blobs(blackH3, roi=roi_10[7], pixels_threshold=100)  #右
    blob9 = img.find_blobs(blackH5, roi=roi_10[0], pixels_threshold=150)  # 左
    blob10 = img.find_blobs(blackH3, roi=roi_10[7], pixels_threshold=150)  # 右
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
    data1 = flag1[0] << 7 | flag1[1] << 6 | flag1[2] << 5 | flag1[3] << 4 | flag1[4] << 3 | flag1[5] << 2 | flag1[
        6] << 1 | flag1[7] << 0
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
    roi = roi_10[0]
    for blob in img.find_blobs(blackH4, roi=roi, merge=True):
        img.draw_rectangle(blob.rect())
        img.draw_cross(blob.cx(), blob.cy())
    #1
    roi = roi_10[1]
    for blob in img.find_blobs(blackH3, roi=roi, merge=True):
        img.draw_rectangle(blob.rect())
        img.draw_cross(blob.cx(), blob.cy())
    #2
    roi = roi_10[2]
    for blob in img.find_blobs(blackH4, roi=roi, merge=True):
        img.draw_rectangle(blob.rect())
        img.draw_cross(blob.cx(), blob.cy())
    #3
    roi = roi_10[3]
    for blob in img.find_blobs(blackH5, roi=roi, merge=True):
        img.draw_rectangle(blob.rect())
        img.draw_cross(blob.cx(), blob.cy())
    #中心点
    roi = roi_10[4]
    for blob in img.find_blobs(blackH4, roi=roi, merge=True):
        img.draw_rectangle(blob.rect())
        img.draw_cross(blob.cx(), blob.cy())
    #5
    roi = roi_10[5]
    for blob in img.find_blobs(blackH4, roi=roi, merge=True):
        img.draw_rectangle(blob.rect())
        img.draw_cross(blob.cx(), blob.cy())
    #6
    roi = roi_10[6]
    for blob in img.find_blobs(blackH3, roi=roi, merge=True):
        img.draw_rectangle(blob.rect())
        img.draw_cross(blob.cx(), blob.cy())
    #7
    roi = roi_10[7]
    for blob in img.find_blobs(blackH3, roi=roi, merge=True):
        img.draw_rectangle(blob.rect())
        img.draw_cross(blob.cx(), blob.cy())
    #ding
    roi = roi_ding_10
    for blob in img.find_blobs(blackH3, roi=roi, merge=True):
        img.draw_rectangle(blob.rect())
        img.draw_cross(blob.cx(), blob.cy())
    roi = roi_ding_12
    for blob in img.find_blobs(blackH3, roi=roi, merge=True):
        img.draw_rectangle(blob.rect())
        img.draw_cross(blob.cx(), blob.cy())
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

line_Patrol1 = False
line_Patrol2 = False
line_Patrol3 = False
line1 = False
QR1 = False
ColorQr = False
traffic1 = False
LCD1 = True
stop1 = False
a = 255
b = 0
i = 0
j = 0
num = 0
#cnn=[(1,2,1),(2,8,2),(1,2,1)]
while True:
    img = sensor.snapshot()  # 获取图片
    LED_B.value(0)  # 点亮LED
    if uart.any():
        data = uart.read(8)
        ColorQr = False
        if len(data) >= 8:
            if (data[0] == 0x55) and (data[1] == 0x02) and (data[7] == 0xBB):
                print(data[2])
                print(data[3])
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
                    if data[3] == 0x01:
                        inin_sensor_1()  # 二维码
                        QR1 = True
                        line_Patrol3 = False
                        print("开始识别二维码！")
                    elif data[3] == 0x02:
                        QR1 = False
                        print("结束识别二维码！")
                    elif data[3] == 0x03:
                        traffic1 = True
                        line_Patrol3 = False
                        if FlagOK != 1:
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
                        inin_sensor_1()  # 二维码
                        ColorQr = True
                        line_Patrol3 = False
                        print("识别彩色二维码！")
                    elif data[3] == 0x08:
                        ColorQr = False
                        print("结束识别彩色二维码！")

    if line_Patrol3:  # 循迹
        video_line_across_2()
    elif stop1:  # 停
        stop_car()
    elif QR1:  # 识别二维码
        Identify_QR(data)
    elif traffic1:  # 识别交通灯
        Traffical_Check()
    elif ColorQr:  # 识别彩色二维码
        Identify_ColorQR(data)
    elif LCD1:
        pass
    LCD_display()
    lcd.display(img)
    if btn_debug.value() == 0:
        line_Patrol3 = False
        QR1 = False
        LCD1 = False
