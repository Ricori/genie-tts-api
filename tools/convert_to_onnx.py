import genie_tts as genie

genie.convert_to_onnx(
    torch_pth_path=r"./models/arimura_e24_s408.pth",  # 替换为您的 .pth 文件
    torch_ckpt_path=r"./models/arimura-e48.ckpt",  # 替换为您的 .ckpt 文件
    output_dir=r"./Output"  # 保存 ONNX 模型的目录
)