# 灰原哀桌面宠物 (Haibara Ai Desktop Pet)（半成品）

基于 MiMo API 的 AI 对话桌面宠物，角色设定为名侦探柯南中的灰原哀（宫野志保）。

![宠物预览](assets/haibara_idle.png)

## 功能特性

- 🤖 **AI 对话**：基于 MiMo-v2.5-pro，灰原哀人设，冷静毒舌但关心你
- 🎨 **手绘形象**：支持自定义角色图片（PNG 透明背景）
- ⏰ **定时提醒**：到点自动提醒，灰原式语气
- 🔧 **快捷工具**：查天气、报时、打开计算器/浏览器
- 🔊 **语音播放**：TTS 语音合成（开发中）
- 💬 **对话气泡**：美观的聊天气泡界面

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/SMZXzbc/haibara-ai-desktop-pet.git
cd haibara-ai-desktop-pet/haibara_desktop_pet
2. 安装依赖
pip install PyQt5 requests openai pygame Pillow

3. 配置 API Key
方法一（推荐）：设置环境变量
# Windows CMD
set MIMO_API_KEY=your_api_key_here

# Windows PowerShell
$env:MIMO_API_KEY="your_api_key_here"

方法二：在 config.json 中填写

{
  "api_key": "your_api_key_here"
}
