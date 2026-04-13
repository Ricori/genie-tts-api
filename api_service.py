import genie_tts as genie
import os

os.environ["GENIE_DATA_DIR"] = r"./GenieData"

if __name__ == "__main__":
  genie.start_server(
      host="0.0.0.0",  # 主机地址
      port=9000,  # 端口
      workers=1  # 工作进程数
  )