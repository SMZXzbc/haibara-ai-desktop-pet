from PIL import Image
import os

# 读取图片
img = Image.open(r'C:\Users\ice\Desktop\20190719083819_2eGvB.jpeg')

# 转换为 RGBA（支持透明）
img = img.convert('RGBA')

# 裁剪掉右下角签名（保留上半部分约88%）
w, h = img.size
crop_box = (0, 0, w, int(h*0.88))  # 去掉底部12%的签名区域
img = img.crop(crop_box)

# 调整大小为 200x250
img = img.resize((200, 250), Image.Resampling.LANCZOS)

# 保存到 assets/
os.makedirs('assets', exist_ok=True)
img.save('assets/haibara_idle.png')
img.save('assets/haibara_talk.png')
img.save('assets/haibara_think.png')
img.save('assets/haibara_tired.png')
img.save('assets/haibara_serious.png')

print('图片处理完成！已保存到 assets/ 文件夹')