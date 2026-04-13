import genie_tts as genie

# 第一步：加载角色语音模型
genie.load_character(
    character_name='arimura',  # 替换为您的角色名称
    onnx_model_dir=r"./CharacterModels/v2ProPlus/arimura/tts_models",  # 包含 ONNX 模型的文件夹
    language='ja',  # 替换为语言代码，例如 'en', 'zh', 'jp'
)

# 第二步：设置参考音频（用于情感和语调克隆）
genie.set_reference_audio(
    character_name='arimura',  # 必须与加载的角色名称匹配
    audio_path=r"./CharacterModels/v2ProPlus/arimura/reference.wav",  # 参考音频的路径
    audio_text="多分、先輩が分かりやすいからじゃないすかね。",  # 对应的文本
)

# 第三步：运行 TTS 推理并生成音频
genie.tts(
    character_name='arimura',  # 必须与加载的角色匹配
    text="どうしようかな……やっぱりやりたいかも……！",  # 要合成的文本
    play=True,  # 直接播放音频
    #save_path="<OUTPUT_AUDIO_PATH>",  # 输出音频文件路径
)

genie.wait_for_playback_done()  # 确保音频播放完成

print("Audio generation complete!")