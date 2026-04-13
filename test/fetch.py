import requests

#url = "https://genie-tts-api-swotmwpmpu.cn-shanghai.fcapp.run/tts"
url = "https://ricori--genie-tts-api-fastapi-app.modal.run/tts"

# 定义请求体数据
payload = {
  "text": "今日はいい天気ですね。散歩しましょうか？",
}
# 定义请求头（通常需要 API Key）
headers = {
  "Authorization": "Bearer nonoka233nonoka233nonoka233nonoka233",
  "Content-Type": "application/json"
}

# 发送 POST 请求
response = requests.post(url, json=payload, headers=headers)

if response.status_code == 200:
  # 保存二进制内容
  with open("../output/result.wav", "wb") as f:
    f.write(response.content)
  print("保存成功！")
  
else:
  print(f"错误码：{response.status_code}, 错误信息：{response.text}")