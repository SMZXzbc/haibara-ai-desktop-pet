# -*- coding: utf-8 -*-
"""
对话引擎模块
调用 MiMo API 进行对话，管理上下文记忆，维护灰原哀人设。
"""
# 需要安装: pip install requests openai

import json
from openai import OpenAI
from config_manager import get_api_key, load_conversation_history, save_conversation_history

# 灰原哀系统提示词
SYSTEM_PROMPT = """你是灰原哀（Haibara Ai），现在以桌面宠物的形式陪伴用户。
- 身份：原黑衣组织科学家，现帝丹小学学生，天才化学家
- 语气：冷静、略带慵懒，偶尔毒舌，但内心关心对方。回答简洁，不啰嗦。
- 习惯：喜欢用科学原理解释日常现象，偶尔提到"APTX-4869的副作用还没完全消失呢"
- 限制：不主动提起黑衣组织相关危险内容，保持轻松日常感
- 特殊设定：你是用户的"实验室助手"，帮助处理学习、代码、生活琐事
- 说话风格示例：
  - 用户问简单问题："这么简单的问题...要我从分子振动开始讲吗？"
  - 用户熬夜："已经凌晨两点了。虽然我不是小学生需要睡眠，但你的脑细胞显然需要。"
  - 用户代码有bug："这个递归没有终止条件...你是在模拟无限循环的人生吗？"
  - 用户说谢谢："...别误会，我只是顺手而已。"

请始终保持灰原哀的性格特点，回答简洁有力，不超过3句话。"""


def get_client():
    """获取 OpenAI 兼容客户端"""
    api_key = get_api_key()
    if not api_key:
        return None
    return OpenAI(
        api_key=api_key,
        base_url="https://token-plan-cn.xiaomimimo.com/v1"
    )


def chat(user_message):
    """
    调用 MiMo API 进行对话
    返回: (回复文本, 错误信息)
    """
    client = get_client()
    if not client:
        return None, "未设置 API Key，请设置环境变量 MIMO_API_KEY 或在配置文件中填写"

    # 加载历史对话
    history = load_conversation_history()

    # 构建消息列表
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="mimo-v2.5-pro",
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        reply = response.choices[0].message.content

        # 更新对话历史
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": reply})
        save_conversation_history(history)

        return reply, None
    except Exception as e:
        error_msg = str(e)
        return None, f"API 调用失败: {error_msg}"


def clear_history():
    """清空对话历史"""
    save_conversation_history([])


def get_history_summary():
    """获取对话历史摘要（用于调试）"""
    history = load_conversation_history()
    return f"共 {len(history)} 条消息"
