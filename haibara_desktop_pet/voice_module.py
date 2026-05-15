# -*- coding: utf-8 -*-
"""
语音模块
调用 MiMo TTS API 生成语音，使用 pygame 播放音频。
"""
# 需要安装: pip install openai pygame

import os
import tempfile
import threading
from openai import OpenAI
from config_manager import get_api_key, load_config

# 音频播放器初始化状态
_player_ready = False
_pygame = None


def _init_pygame():
    """延迟初始化 pygame mixer"""
    global _player_ready, _pygame
    if _player_ready:
        return True
    try:
        import pygame
        pygame.mixer.init()
        _pygame = pygame
        _player_ready = True
        return True
    except Exception as e:
        print(f"pygame 初始化失败: {e}")
        return False


def get_client():
    """获取 OpenAI 兼容客户端"""
    api_key = get_api_key()
    if not api_key:
        return None
    return OpenAI(
        api_key=api_key,
        base_url="https://token-plan-cn.xiaomimimo.com/v1"
    )


def speak(text, callback=None):
    """
    生成 TTS 音频并播放
    text: 要朗读的文本
    callback: 播放完成后的回调函数
    """
    # 检查是否静音
    config = load_config()
    if config.get("muted", False):
        if callback:
            callback()
        return

    # 在后台线程中执行，避免阻塞 UI
    thread = threading.Thread(target=_speak_thread, args=(text, callback), daemon=True)
    thread.start()


def _speak_thread(text, callback):
    """TTS 工作线程"""
    global _pygame
    client = get_client()
    if not client:
        if callback:
            callback()
        return

    temp_path = None
    try:
        # 调用 MiMo TTS API
        response = client.audio.speech.create(
            model="mimo-v2.5-tts",
            voice="alloy",  # 冷静少女音
            input=text,
            response_format="mp3",
            speed=1.0
        )

        # 保存到临时文件
        temp_fd, temp_path = tempfile.mkstemp(suffix=".mp3")
        os.close(temp_fd)

        response.stream_to_file(temp_path)

        # 使用 pygame 播放
        if _init_pygame():
            _pygame.mixer.music.load(temp_path)
            _pygame.mixer.music.play()

            # 等待播放完成
            while _pygame.mixer.music.get_busy():
                _pygame.time.wait(100)

    except Exception as e:
        print(f"TTS 生成或播放失败: {e}")
    finally:
        # 清理临时文件
        if temp_path and os.path.exists(temp_path):
            try:
                # 停止播放后再删除
                if _pygame and _player_ready:
                    _pygame.mixer.music.stop()
                os.remove(temp_path)
            except:
                pass
        if callback:
            callback()


def stop_playback():
    """停止当前播放"""
    global _pygame
    if _pygame and _player_ready:
        try:
            _pygame.mixer.music.stop()
        except:
            pass


def cleanup():
    """清理资源"""
    global _pygame, _player_ready
    if _pygame and _player_ready:
        try:
            _pygame.mixer.quit()
        except:
            pass
        _player_ready = False
