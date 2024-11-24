import pyttsx3
import speech_recognition as sr
from aip import AipSpeech
import pyaudio
import wave

# 百度 API 配置
APP_ID = '你的APP_ID'
API_KEY = '你的API_KEY'
SECRET_KEY = '你的SECRET_KEY'

client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

# 录制语音
def record_audio(file_path):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    RECORD_SECONDS = 5
    WAVE_OUTPUT_FILENAME = file_path

    p = pyaudio.PyAudio()

    print("开始录音...")
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    frames = []

    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("录音结束")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

# 使用百度 API 转换语音到文本
def baidu_speech_to_text(file_path):
    with open(file_path, 'rb') as fp:
        audio_data = fp.read()
    result = client.asr(audio_data, 'wav', 16000, {'dev_pid': 1537})  # 1537 代表普通话
    if 'result' in result:
        print("语音识别结果：", result['result'][0])
        return result['result'][0]
    else:
        print("识别失败：", result)
        return None

def text_to_speech(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("请说话...")
        audio = recognizer.listen(source)
    try:
        # 使用Google Web API识别语音
        text = recognizer.recognize_google(audio, language="zh-CN")
        print("识别结果：", text)
        return text
    except sr.UnknownValueError:
        print("未能识别语音")
    except sr.RequestError as e:
        print(f"无法请求结果；{e}")

speech_to_text()
text_to_speech("你好！这是一个从文本到语音的示例。")
audio_file = "record.wav"
record_audio(audio_file)
baidu_speech_to_text(audio_file)