import os
import io
import tempfile
import uvicorn
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import genie_tts as genie

# 初始化 FastAPI 应用
app = FastAPI()

# ==========================================
# 阶段一：服务冷启动加载 (极其重要)
# 将模型和参考音频的加载放在全局作用域，
# 这样云函数实例启动时就会加载进内存，而不会在每次用户请求时重复加载。
# ==========================================
print("正在加载 Arimura 模型与参考音频...")

genie.load_character(
    character_name='arimura',
    onnx_model_dir=r"./CharacterModels/v2ProPlus/arimura/tts_models",
    language='ja'
)

genie.set_reference_audio(
    character_name='arimura',
    audio_path=r"./CharacterModels/v2ProPlus/arimura/reference.wav",
    audio_text="多分、先輩が分かりやすいからじゃないすかね。",
    language='ja'
)
print("模型加载完成，服务准备就绪！")

# 定义 API 接收的请求体格式
class TTSRequest(BaseModel):
    text: str

# ==========================================
# 阶段二：定义流式 API 接口
# ==========================================
@app.post("/tts")
def generate_audio_stream(req: TTSRequest):
    """
    接收文本，合成语音，并以音频流的形式返回
    """
    # 1. 创建一个安全的临时文件路径用于存放生成的 WAV
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        temp_audio_path = tmp_file.name

    try:
        # 2. 运行 TTS 推理 (绝不能用 play=True)
        genie.tts(
            character_name='arimura',
            text=req.text,
            play=False, 
            save_path=temp_audio_path
        )

        # 3. 将生成的音频文件读取到内存中
        with open(temp_audio_path, "rb") as f:
            audio_data = f.read()

        # 4. 删除临时文件，防止服务器硬盘被撑爆
        os.remove(temp_audio_path)

        # 5. 将内存中的音频字节流转换为 HTTP 流式响应
        return StreamingResponse(
            io.BytesIO(audio_data), 
            media_type="audio/wav"
        )

    except Exception as e:
        # 异常处理：即使报错也要确保清理临时文件
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
        return {"error": str(e)}

# ==========================================
# 阶段三：启动服务器 (监听 9000 端口对接阿里云 FC)
# ==========================================
if __name__ == "__main__":
    # 获取阿里云 FC 默认端口
    port = int(os.environ.get("FC_SERVER_PORT", 9000))
    uvicorn.run(app, host="0.0.0.0", port=port)