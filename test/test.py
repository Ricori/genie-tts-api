import genie_tts as genie
import time

# 首次运行时自动下载所需文件
genie.load_predefined_character('mika')

genie.tts(
    character_name='mika',
    text='どうしようかな……やっぱりやりたいかも……！',
    play=True,  # 直接播放生成的音频
)

genie.wait_for_playback_done()  # 确保音频播放完成