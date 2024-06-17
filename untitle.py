def process_file(input_file, output_file):
    # 读取文件内容
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 初始化变量
    event_count = 0
    max_correlation_line = None
    max_correlation_value = float('-inf')
    result_lines = []

    # 遍历每一行
    for i, line in enumerate(lines):
        # 提取相关性概率值
        parts = line.strip().split('||')
        correlation = float(parts[-1])
        
        # 更新最大相关性概率和对应的行
        if correlation > max_correlation_value:
            max_correlation_value = correlation
            max_correlation_line = line

        # 每127行是一个事件，处理下一个事件
        if (i + 1) % 127 == 0:
            result_lines.append(max_correlation_line)
            max_correlation_value = float('-inf')
            max_correlation_line = None
            event_count += 1
    
    # 将结果写入新的文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(result_lines)
    
    print(f"处理完成，总共处理了 {event_count} 个事件。结果已保存到 {output_file} 文件中。")

# 输入文件路径和输出文件路径
input_file = 'C:/Users/dell/Documents/WeChat Files/wxid_dq39zs7wrvvi22/FileStorage/File/2024-06/predict_modify.txt'
output_file = 'output.txt'

# 处理文件
process_file(input_file, output_file)
