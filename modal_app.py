import modal
import io
import os

os.environ["GENIE_DATA_DIR"] = r"/root/data/GenieData"

# 创建 Modal 应用
app = modal.App("genie-tts-api")

# 1. 定义极其轻量的基础镜像（只装依赖）
image = (
    modal.Image.debian_slim(python_version="3.10")
    .pip_install(
        "fastapi",
        "uvicorn",
        "pydantic",
        "genie-tts",
    )
)

# 2. 声明要引用的云盘
model_volume = modal.Volume.from_name("genie-tts-volume", create_if_missing=True)

# 3. 定义 Web 服务
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
    from pydantic import BaseModel
    import genie_tts as genie
    import tempfile
    import os

    app = FastAPI()

    # 定义 Header 拦截器，监听 Authorization 字段
    api_key_header = APIKeyHeader(name="Authorization", auto_error=False)
    def verify_api_key(api_key: str = Security(api_key_header)):
        if api_key != f"Bearer nonoka233nonoka233nonoka233nonoka233":
            raise HTTPException(status_code=401, detail="身份验证失败：无效的 Token")
        return api_key

    # 指向挂载的云盘目录 /root/data/...
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

    class TTSRequest(BaseModel):
        text: str

    @app.post("/tts", dependencies=[Security(verify_api_key)])
    def generate_audio_stream(req: TTSRequest):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            temp_audio_path = tmp_file.name

        try:
            genie.tts(
                character_name='arimura',
                text=req.text,
                play=False,
                save_path=temp_audio_path
            )

            with open(temp_audio_path, "rb") as f:
                audio_data = f.read()

            os.remove(temp_audio_path)

            return StreamingResponse(
                io.BytesIO(audio_data),
                media_type="audio/wav"
            )

        except Exception as e:
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
            return {"error": str(e)}

    @app.get("/health")
    def health_check():
        return {"status": "ok"}

    return app