# 使用 Python 3.10 官方精简版镜像
FROM python:3.10-slim

# 设置时区为上海，并配置非交互式
ENV TZ=Asia/Shanghai
ENV DEBIAN_FRONTEND=noninteractive

# 设置容器内的工作目录
WORKDIR /app

# 安装必要的系统底层依赖
# build-essential: 提供 gcc 编译器，用于编译 jieba_fast 等 C 扩展
# python3-dev: 提供 Python C API 头文件
# libsndfile1 和 ffmpeg: 音频处理/格式转换必备
# libgomp1: ONNX Runtime 底层多线程计算依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libsndfile1 \
    libgomp1 \
    ffmpeg \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# 先复制 requirements.txt，利用 Docker 缓存机制加速重复构建
COPY requirements.txt .

# 安装 Python 依赖 (使用了阿里云 pip 镜像源加速下载)
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 下载模型
RUN wget --progress=dot:giga -O models.zip "https://file.kvv.me/genie-tts-api.zip"
# 解压并删除压缩包
RUN unzip models.zip && rm models.zip

# 目录下的所有代码和模型文件复制到容器的 /app 目录下
COPY . /app

# 暴露阿里云 FC 默认监听的 9000 端口
EXPOSE 9000

# 容器启动时执行的命令
CMD ["python", "app.py"]