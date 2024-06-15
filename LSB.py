import struct

# 读取BMP图片文件
def read_bmp(filename):
    with open(filename, 'rb') as f:
        # 读取BMP文件头
        bmp_header = f.read(54)
        # 提取图像宽度和高度
        width, height = struct.unpack('ii', bmp_header[18:26])
        pixels = []
        # 逐行读取像素数据
        for y in range(height):
            row = []
            for x in range(width):
                b, g, r = struct.unpack('BBB', f.read(3))
                row.append((r, g, b))
            pixels.append(row)
        return bmp_header, pixels

# 写入BMP图片文件
def write_bmp(filename, bmp_header, pixels):
    with open(filename, 'wb') as f:
        # 写入BMP文件头
        f.write(bmp_header)
        # 逐行写入像素数据
        for row in pixels:
            for pixel in row:
                f.write(struct.pack('BBB', pixel[2], pixel[1], pixel[0]))

# 将字符串转换为二进制
def str_to_bin(message):
    binary = ''.join(format(ord(c), '08b') for c in message)
    return binary

# 将二进制转换为字符串
def bin_to_str(binary):
    chars = [chr(int(binary[i:i+8], 2)) for i in range(0, len(binary), 8)]
    return ''.join(chars)

# 嵌入消息到像素数据中
def embed_message(pixels, message):
    binary_message = str_to_bin(message) + '00000000'  # 添加终止符
    height = len(pixels)
    width = len(pixels[0])
    index = 0
    # 遍历每个像素进行嵌入
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[y][x]
            if index < len(binary_message):
                r = (r & 0xFE) | int(binary_message[index])  # 嵌入到红色通道
                index += 1
            if index < len(binary_message):
                g = (g & 0xFE) | int(binary_message[index])  # 嵌入到绿色通道
                index += 1
            if index < len(binary_message):
                b = (b & 0xFE) | int(binary_message[index])  # 嵌入到蓝色通道
                index += 1
            pixels[y][x] = (r, g, b)
            if index >= len(binary_message):
                return pixels
    return pixels

# 从像素数据中提取嵌入的消息
def extract_message(pixels):
    binary_message = ''
    height = len(pixels)
    width = len(pixels[0])
    # 遍历每个像素提取信息
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[y][x]
            binary_message += str(r & 1)  # 提取红色通道最低有效位
            binary_message += str(g & 1)  # 提取绿色通道最低有效位
            binary_message += str(b & 1)  # 提取蓝色通道最低有效位
            if '00000000' in binary_message:  # 检查终止符
                break
    binary_message = binary_message[:binary_message.index('00000000')]
    return bin_to_str(binary_message)

# 计算可嵌入消息的最大长度
def calculate_max_message_length(pixels):
    height = len(pixels)
    width = len(pixels[0])
    max_bits = height * width * 3  # 每个像素3个字节，每个字节1个比特位可用
    return max_bits // 8  # 转换为字节数

# 主程序
bmp_header, pixels = read_bmp('./可供选用的图片/24位真彩图/test1.bmp')  # 读取输入BMP文件
max_length = calculate_max_message_length(pixels)  # 计算最大可嵌入信息长度
print(f'可嵌入信息的最大长度: {max_length} 字节')

# 获取用户输入并进行长度控制
message = input(f'请输入要嵌入的信息（不超过 {max_length} 字节）: ')
if len(message) > max_length:
    raise ValueError('信息过长！')

# 将信息嵌入到像素数据中
pixels = embed_message(pixels, message)
write_bmp('output.bmp', bmp_header, pixels)  # 写入嵌入信息后的BMP文件

# 读取嵌入信息后的BMP文件并提取信息
bmp_header, pixels = read_bmp('output.bmp')
extracted_message = extract_message(pixels)
print(f'提取的信息: {extracted_message}')
