# 基于 AIGC 的智能校园虚拟导览系统

本项目是一个可直接运行和二次开发的毕业设计模板，围绕“基于 AIGC 的智能校园虚拟导览系统设计与实现”构建，包含：

- Python FastAPI 后端（导览路线规划、AIGC 讲解生成、问答、语音合成接口）
- Unity3D 客户端脚本（路径请求、讲解展示、语音播放流程）
- 测试、样例数据、论文材料模板与演示脚本

## 1. 项目结构

- backend: 后端服务
- unity: Unity 客户端脚本与接入说明
- docs: 架构文档、文献综述模板、论文提纲、答辩演示脚本

## 2. 功能总览

- 智能路线规划：基于校园图进行最短路径与偏好约束规划
- AIGC 智能讲解：根据路线、用户角色、讲解风格自动生成导览词
- 智能问答：针对景点上下文进行追问与回答
- 语音问答：用户语音输入，ASR 识别后自动调用问答
- 语音播放：提供 TTS 接口（可对接真实语音引擎）
- Unity 交互：输入起终点后自动规划并展示导览内容

## 3. 快速启动（后端）

1) 进入 backend 目录

2) 创建虚拟环境并安装依赖

Windows PowerShell:

python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

3) 配置环境变量

复制 .env.example 为 .env，并填写可选的大模型配置。

4) 启动服务

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

5) 打开接口文档

- Swagger: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## 4. Unity 接入

1) 打开 Unity 项目（URP 或内置渲染管线均可）
2) 将 unity/Assets/Scripts 下脚本拷贝到 Unity 项目 Assets/Scripts
3) 新建 Canvas 并挂载 GuideUIController
4) 绑定输入框、按钮、文本框和 ApiClient
5) 运行后输入起点终点，触发路线规划与讲解生成

详细步骤见 docs/architecture.md 与 unity/README.md。

## 5. 测试

在 backend 目录执行：

pytest -q

## 6. 二次开发建议

- 将校园 3D 模型替换为真实学校场景
- 对接学校 GIS 数据与实时路况
- 接入真实 ASR/TTS（讯飞、Azure、阿里云等）
- 增加多角色导览策略（新生、家长、访客、校友）
- 增加行为日志与推荐反馈闭环
