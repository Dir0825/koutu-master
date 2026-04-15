# 抠图大师 - AI 背景移除工具

一键去除图片背景，AI 智能抠图

## 本地运行

```bash
pip install -r requirements.txt
python3 server.py
```

然后访问 http://localhost:8080

## 部署到 Railway.app (免费)

1. 把代码推送到 GitHub 仓库
2. 去 [Railway.app](https://railway.app) 用 GitHub 登录
3. 点击 "New Project" → "Deploy from GitHub"
4. 选择你的仓库
5. Railway 会自动检测 Python 项目并部署

## 部署到 Render.com (免费)

1. 去 [Render.com](https://render.com) 用 GitHub 登录
2. 点击 "New" → "Web Service"
3. 连接 GitHub 仓库
4. 设置:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python3 server.py`
5. 点击 "Create Web Service"

注意: Render 免费版服务 15 分钟无活动会休眠

## API

- `GET /api/status` - 检查服务状态
- `POST /api/remove-bg` - 上传图片获取透明背景图
