import modal
import io
import os

os.environ["GENIE_DATA_DIR"] = r"/root/data/GenieData"

# 创建 Modal 应用
app = modal.App("genie-tts-api")

# 定义极其轻量的基础镜像
image = (
    modal.Image.debian_slim(python_version="3.10")
    .pip_install(
        "fastapi",
        "uvicorn",
        "pydantic",
        "genie-tts",
    )
)

# 声明要引用的云盘
model_volume = modal.Volume.from_name("genie-tts-volume", create_if_missing=True)

# 定义 Web 服务
@app.function(
    image=image,
    cpu=8.0,
    memory=8192,
    timeout=300,
    volumes={"/root/data": model_volume},  # 把云盘挂载到容器内的 /root/data 目录下
    min_containers=0,       # 闲置时缩容到 0
    max_containers=1,       # 限制最高并发，防爆刷
    buffer_containers=0,    # 拒绝额外预留
    scaledown_window=15,    # 完工后 15 秒无人理会即刻销毁
)
@modal.asgi_app()
def fastapi_app():
    from fastapi import FastAPI, Security, HTTPException
    from fastapi.responses import StreamingResponse
    from fastapi.security.api_key import APIKeyHeader
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    from typing import Optional
    import genie_tts as genie
    import tempfile
    import os

    app = FastAPI()
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],       # 允许任何前端直接调用
        allow_credentials=True,
        allow_methods=["*"],       # 允许拦截到的 OPTIONS 预检请求通过
        allow_headers=["*"],       # 允许携带 Authorization 等自定义 Header
    )

    # 定义 Header 拦截器，监听 Authorization 字段
    api_key_header = APIKeyHeader(name="Authorization", auto_error=False)
    def verify_api_key(api_key: str = Security(api_key_header)):
        if api_key != f"Bearer nonoka233nonoka233nonoka233nonoka233":
            raise HTTPException(status_code=401, detail="身份验证失败：无效的 Token")
        return api_key

    # 模型冷启动：从云盘加载
    print("正在从云盘加载 Arimura 模型与参考音频...")
    genie.load_character(
        character_name='arimura',
        onnx_model_dir="/root/data/CharacterModels/v2ProPlus/arimura/tts_models",
        language='ja'
    )
    genie.set_reference_audio(
        character_name='arimura',
        audio_path="/root/data/CharacterModels/v2ProPlus/arimura/reference.wav",
        audio_text="多分、先輩が分かりやすいからじゃないすかね。",
        language='ja'
    )
    print("模型加载完成!")

    # OpenAI 兼容的请求体模型
    class OpenAITTSRequest(BaseModel):
        model: str = "tts-1"
        input: str
        voice: str = "arimura"
        response_format: Optional[str] = "wav"
        speed: Optional[float] = 1.0

    class TTSRequest(BaseModel):
        text: str

    # --- 核心推理公共逻辑 ---
    def process_tts(text: str, character: str):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            temp_audio_path = tmp_file.name

        try:
            genie.tts(
                character_name=character,
                text=text,
                play=False,
                save_path=temp_audio_path
            )
            with open(temp_audio_path, "rb") as f:
                audio_data = f.read()
            os.remove(temp_audio_path)

            return StreamingResponse(
                io.BytesIO(audio_data),
                media_type="audio/wav",
                headers={"Content-Disposition": "attachment; filename=speech.wav"}
            )
        except Exception as e:
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
            raise HTTPException(status_code=500, detail=str(e))


    @app.post("/tts", dependencies=[Security(verify_api_key)])
    def custom_tts_endpoint(req: TTSRequest):
        return process_tts(text=req.text, character="arimura")

    @app.get("/v1/models", dependencies=[Security(verify_api_key)])
    def list_models():
        return {
            "object": "list",
            "data": [
                {
                    "id": "arimura",
                    "object": "model",
                    "created": 1700000000,
                    "owned_by": "genie-tts"
                }
            ]
        }
    @app.post("/v1/audio/speech", dependencies=[Security(verify_api_key)])
    def openai_tts_endpoint(req: OpenAITTSRequest):
        return process_tts(text=req.input, character="arimura")
        # return process_tts(text=req.input, character=req.voice)

    @app.get("/health")
    def health_check():
        return {"status": "ok"}

    return app