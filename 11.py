import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import struct
import random

def add_noise_to_image(pixels, noise_level=0.05):
    """
    添加随机噪声到图像中。
    :param pixels: 像素数据
    :param noise_level: 噪声比例，默认值为 5%
    :return: 添加噪声后的像素数据
    """
    height = len(pixels)
    width = len(pixels[0])
    num_noisy_pixels = int(height * width * noise_level)

    noisy_pixels = set()
    while len(noisy_pixels) < num_noisy_pixels:
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        noisy_pixels.add((y, x))

    for y, x in noisy_pixels:
        if isinstance(pixels[y][x], tuple):  # 24bit 图像
            r, g, b = pixels[y][x]
            r = (r + random.randint(-30, 30)) % 256
            g = (g + random.randint(-30, 30)) % 256
            b = (b + random.randint(-30, 30)) % 256
            pixels[y][x] = (r, g, b)
        else:  # 8bit 灰度图像
            idx = pixels[y][x]
            idx = (idx + random.randint(-30, 30)) % 256
            pixels[y][x] = idx

    return pixels

# 读取BMP图片文件
def read_bmp(filename):
    with open(filename, 'rb') as f:
        bmp_header = f.read(54)
        width, height = struct.unpack('ii', bmp_header[18:26])
        bpp = struct.unpack('H', bmp_header[28:30])[0]  # 每像素位数
        if bpp == 24:
            image_type = '24bit'
            pixels = []
            for y in range(height):
                row = []
                for x in range(width):
                    b, g, r = struct.unpack('BBB', f.read(3))
                    row.append((r, g, b))
                pixels.append(row)
        elif bpp == 8:
            image_type = '8bit'
            palette = f.read(1024)  # 256*4 = 1024 bytes
            pixels = []
            for y in range(height):
                row = []
                for x in range(width):
                    idx = struct.unpack('B', f.read(1))[0]
                    row.append(idx)
                pixels.append(row)
        else:
            raise ValueError('Unsupported BMP format')
        return bmp_header, pixels, width, height, image_type

# 写入BMP图片文件
def write_bmp(filename, bmp_header, pixels, image_type):
    with open(filename, 'wb') as f:
        f.write(bmp_header)
        if image_type == '24bit':
            for row in pixels:
                for pixel in row:
                    f.write(struct.pack('BBB', pixel[2], pixel[1], pixel[0]))
        elif image_type == '8bit':
            palette = bytearray(1024)
            for i in range(256):
                palette[i*4:i*4+3] = struct.pack('BBB', i, i, i)
            f.write(palette)
            for row in pixels:
                for pixel in row:
                    f.write(struct.pack('B', pixel))

# 字符串转换为二进制
def str_to_bin(message):
    binary = ''.join(format(ord(c), '08b') for c in message)
    return binary

# 二进制转换为字符串
def bin_to_str(binary):
    chars = [chr(int(binary[i:i+8], 2)) for i in range(0, len(binary), 8)]
    return ''.join(chars)

# 嵌入消息到像素数据中
def embed_message(pixels, message):
    binary_message = str_to_bin(message)
    print("嵌入信息的二进制结果是{}".format(binary_message))
    binary_message += '00000000'  # 添加终止符
    height = len(pixels)
    width = len(pixels[0])
    index = 0
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[y][x]
            if index < len(binary_message):
                r = (r & 0xFE) | int(binary_message[index])
                index += 1
            if index < len(binary_message):
                g = (g & 0xFE) | int(binary_message[index])
                index += 1
            if index < len(binary_message):
                b = (b & 0xFE) | int(binary_message[index])
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
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[y][x]
            binary_message += str(r & 1)
            binary_message += str(g & 1)
            binary_message += str(b & 1)
            if '00000000' in binary_message:
                break
    binary_message = binary_message[:binary_message.index('00000000')]

    # 补充被删掉的0
    if len(binary_message) % 8 != 0:
        binary_message += '0' * (8 - (len(binary_message) % 8))

    print("得到信息的二进制结果是{}".format(binary_message))
    return bin_to_str(binary_message)

# 计算可嵌入消息的最大长度
def calculate_max_message_length(pixels):
    height = len(pixels)
    width = len(pixels[0])
    max_bits = height * width * 3
    return max_bits // 8

# 嵌入消息到像素数据中（针对8位灰度图像）
def embed_message_gray(pixels, message):
    binary_message = str_to_bin(message)
    binary_message += '00000000'  # 添加终止符
    index = 0
    for y in range(len(pixels)):
        for x in range(len(pixels[0])):
            idx = pixels[y][x]  # 灰度值作为索引
            if index < len(binary_message):
                idx = (idx & 0xFE) | int(binary_message[index])
                index += 1
            pixels[y][x] = idx
            if index >= len(binary_message):
                break
        if index >= len(binary_message):
            break
    return pixels

# 从像素数据中提取嵌入的消息（针对8位灰度图像）
def extract_message_gray(pixels):
    binary_message = ''
    for row in pixels:
        for pixel in row:
            binary_message += str(pixel & 1)
            if '00000000' in binary_message:
                break
        if '00000000' in binary_message:
            break
    binary_message = binary_message[:binary_message.index('00000000')]

    # 补充被删掉的0
    if len(binary_message) % 8 != 0:
        binary_message += '0' * (8 - (len(binary_message) % 8))

    return bin_to_str(binary_message)

# GUI应用程序
class LSBSteganographyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LSB Steganography")

        self.menu_frame = tk.Frame(root)
        self.menu_frame.pack(fill=tk.X)

        self.read_button = tk.Button(self.menu_frame, text="读取图片", command=self.open_image)
        self.read_button.pack(side=tk.LEFT)

        self.save_button = tk.Button(self.menu_frame, text="存储图片", command=self.save_image)
        self.save_button.pack(side=tk.LEFT)

        self.embed_button = tk.Button(self.menu_frame, text="嵌入", command=self.embed)
        self.embed_button.pack(side=tk.LEFT)

        self.extract_button = tk.Button(self.menu_frame, text="提取", command=self.extract)
        self.extract_button.pack(side=tk.LEFT)

        self.noise_button = tk.Button(self.menu_frame, text="添加噪声", command=self.add_noise)
        self.noise_button.pack(side=tk.LEFT)

        self.image_frame = tk.Frame(root)
        self.image_frame.pack()

        self.original_image_label = tk.Label(self.image_frame, text="原图")
        self.original_image_label.grid(row=0, column=0)

        self.processed_image_label = tk.Label(self.image_frame, text="处理后的图")
        self.processed_image_label.grid(row=0, column=2)

        self.info_frame = tk.Frame(root)
        self.info_frame.pack()

        self.max_length_label = tk.Label(self.info_frame, text="显示计算出来的可嵌入信息的最大长度")
        self.max_length_label.grid(row=0, column=0)

        self.message_entry = tk.Entry(self.info_frame)
        self.message_entry.grid(row=1, column=0)

        self.output_label = tk.Label(self.info_frame, text="")
        self.output_label.grid(row=1, column=1)

        self.original_image = None
        self.processed_image = None
        self.pixels = None
        self.bmp_header = None
        self.image_type = None

        self.width = None
        self.height = None

    def open_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.bmp_header, self.pixels, self.width, self.height, self.image_type = read_bmp(file_path)
            self.original_image = Image.open(file_path)
            self.original_image.thumbnail((self.width, self.height))
            self.original_image_tk = ImageTk.PhotoImage(self.original_image)
            self.original_image_label.configure(image=self.original_image_tk)
            self.processed_image = None
            self.processed_image_tk = None
            self.processed_image_label.configure(image=None)
            max_length = calculate_max_message_length(self.pixels)
            self.max_length_label.configure(text=f"可嵌入信息的最大长度: {max_length} 字节")

    def save_image(self):
        if self.processed_image:
            file_path = filedialog.asksaveasfilename(defaultextension=".bmp", filetypes=[("BMP files", "*.bmp")])
            if file_path:
                write_bmp(file_path, self.bmp_header, self.pixels, self.image_type)
                messagebox.showinfo("保存图片", "图片已保存")

    def embed(self):
        message = self.message_entry.get()
        if not message:
            messagebox.showwarning("输入错误", "请输入要嵌入的信息")
            return
        max_length = calculate_max_message_length(self.pixels)
        if len(message) > max_length:
            messagebox.showwarning("输入错误", f"信息过长！最大长度为 {max_length} 字节")
            return
        
        if self.image_type == '24bit':
            self.pixels = embed_message(self.pixels, message)
        else:
            self.pixels = embed_message_gray(self.pixels, message)

        output_path = "output.bmp"
        write_bmp(output_path, self.bmp_header, self.pixels, self.image_type)

        self.processed_image = Image.open(output_path)
        self.processed_image.thumbnail((self.width, self.height))
        self.processed_image_tk = ImageTk.PhotoImage(self.processed_image)
        self.processed_image_label.configure(image=self.processed_image_tk)
        messagebox.showinfo("嵌入信息", "信息已嵌入图片")

    def extract(self):
        if not self.pixels:
            messagebox.showwarning("提取错误", "请先读取图片")
            return
        
        if self.image_type == '24bit':
            extracted_message = extract_message(self.pixels)
        else:
            extracted_message = extract_message_gray(self.pixels)
            
        self.output_label.configure(text=f"提取的信息: {extracted_message}")
        messagebox.showinfo("提取信息", f"提取的信息: {extracted_message}")

    def add_noise(self):
        if not self.pixels:
            messagebox.showwarning("错误", "请先读取图片")
            return
        
        noise_level = 0.05  # 噪声水平设为5%
        self.pixels = add_noise_to_image(self.pixels, noise_level)

        output_path = "output.bmp"
        write_bmp(output_path, self.bmp_header, self.pixels, self.image_type)

        self.processed_image = Image.open(output_path)
        self.processed_image.thumbnail((self.width, self.height))
        self.processed_image_tk = ImageTk.PhotoImage(self.processed_image)
        self.processed_image_label.configure(image=self.processed_image_tk)
        messagebox.showinfo("添加噪声", "已添加随机噪声")

if __name__ == "__main__":
    root = tk.Tk()
    app = LSBSteganographyApp(root)
    root.mainloop()

