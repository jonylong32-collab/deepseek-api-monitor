# DeepSeek API Monitor

DeepSeek API Monitor 是一个本地运行的 DeepSeek API 用量与余额监控桌面应用。项目由 FastAPI 后端和 React/Vite 前端组成，可在浏览器中调试，也可以通过 PyInstaller 打包成 Windows 桌面程序。

## 功能

- 查看 DeepSeek 账户余额和余额变动趋势
- 导入 DeepSeek 用量导出的 CSV/ZIP 文件
- 按模型统计请求数、Token 用量和每日趋势
- 本地加密保存 API Key，不把密钥写进仓库
- 支持自动刷新、导出 CSV、系统托盘和 WebView 桌面窗口

## 技术栈

- 后端：Python、FastAPI、Uvicorn、Pydantic、Requests、Cryptography
- 前端：React、TypeScript、Vite、Recharts、Lucide React
- 桌面端：pywebview、pystray、Pillow、PyInstaller

## 项目结构

```text
backend/              FastAPI 服务、桌面入口和数据解析逻辑
frontend/             React + Vite 前端
backend/.env.example  后端环境变量示例
DeepSeek监控.spec      PyInstaller 打包配置
icon.ico              Windows 应用图标
```

## 本地开发

### 1. 安装后端依赖

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
copy .env.example .env
```

编辑 `backend/.env`，填入你的 DeepSeek API Key：

```env
DEEPSEEK_API_KEY=your_api_key_here
HOST=0.0.0.0
PORT=8000
```

应用也支持在设置面板中保存 API Key。密钥会保存在本机应用数据目录，并用 Fernet 加密。

### 3. 启动后端

```bash
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 4. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端默认运行在 `http://127.0.0.1:5173`，并把 `/api` 请求代理到后端。

## 构建与打包

先构建前端：

```bash
cd frontend
npm run build
```

将 `frontend/dist` 的产物复制到 `backend/app/static` 后，再回到项目根目录执行：

```bash
pyinstaller DeepSeek监控.spec
```

打包产物会生成在 `dist/`，该目录不会提交到 Git。

## 验证

```bash
cd backend
python verify.py

cd ../frontend
npm run build
```

## 安全说明

- 不要提交真实的 `.env`、API Key、WebView 用户数据或打包产物
- `backend/.env.example` 只保留占位符
- API Key 本地保存时会加密，仓库中不包含真实凭据

## License

MIT
