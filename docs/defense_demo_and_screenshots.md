# 答辩演示脚本与截图点位清单

## 1. 演示目标

本演示用于证明系统已经完成“路线规划 + AIGC 讲解 + 语音交互 + Unity 场景联动”完整闭环。

建议总时长：5 到 8 分钟。

## 2. 演示前 3 分钟准备

### 2.1 启动后端

如果你当前终端在项目根目录，请使用：

python -m uvicorn --app-dir d:/AAA/campus-navigation-system/backend app.main:app --host 0.0.0.0 --port 8000

说明：你之前出现过 No module named app，就是没有指定 app-dir。

### 2.2 快速接口健康确认

- 打开浏览器：http://127.0.0.1:8000/docs
- 看到 Swagger 页面即可
- 执行 GET /health，返回 status=ok

### 2.3 Unity 场景检查

- ApiClient 的 apiBaseUrl 指向 http://127.0.0.1:8000
- RouteHighlighterController 已绑定 nodeAnchors 与 marker
- NarrationBubbleController 已绑定 RouteHighlighterController
- VoiceQAController 已绑定录音按钮与文本输出

## 3. 答辩现场演示脚本（可直接念）

### 阶段 A：课题背景（约 45 秒）

讲稿：

本课题面向校园导览场景，解决传统导览静态、缺少个性化和交互性的问题。系统结合 AIGC、路径规划与虚拟场景交互，实现了个性化路线、动态讲解和语音问答，既可用于招生展示，也可用于校园文化传播。

### 阶段 B：系统架构（约 60 秒）

讲稿：

系统采用前后端分层架构。后端基于 FastAPI，提供路线规划、AIGC 讲解、语音问答等接口。前端采用 Unity3D，实现路线可视化、角色播报和交互按钮。两端通过 HTTP 接口通信，形成路径规划到讲解生成的闭环。

### 阶段 C：功能演示 1 - 路线规划（约 60 秒）

操作：

1. 在 Unity 输入起点 gate_north、终点 stadium。
2. 点击 PlanButton。

讲稿：

当前系统会根据校园图和偏好参数进行加权最短路径规划，返回路径节点、总距离和预计时长。可以看到路径文本已经返回，同时场景中路线高亮和 marker 巡游同步触发。

### 阶段 D：功能演示 2 - 节点自动讲解（约 60 秒）

操作：

1. 保持 marker 巡游。
2. 观察到达每个节点时字幕变化。

讲稿：

当 marker 到达节点时，会触发到站事件。系统优先调用后端单景点讲解接口动态生成个性化文案；若接口异常则自动回退到本地文案，保证演示稳定性。

### 阶段 E：功能演示 3 - 语音问答（约 90 秒）

操作：

1. 点击 StartRecordButton 开始录音。
2. 口述一个问题，例如“图书馆有什么资源？”
3. 点击 StopAndAskButton。

讲稿：

语音输入会进入语音问答链路：ASR 转写后，结合当前景点上下文调用问答模块，返回答案并同步显示在气泡字幕中。当前可配置为 mock ASR 以保证流程稳定，也支持后续接入真实语音识别服务。

### 阶段 F：总结（约 40 秒）

讲稿：

系统已实现核心目标：沉浸式场景、个性化导览、语音交互和可扩展架构。下一步可接入真实校园 GIS 数据、真实 ASR/TTS 与用户行为反馈，实现更高精度的推荐和数字孪生升级。

## 4. 截图点位清单（论文与 PPT 直接用）

建议至少准备 10 张图，按下面顺序命名，便于插入论文。

1. fig01_system_architecture.png
- 内容：总体架构图（Unity 前端、FastAPI 后端、AIGC 服务）
- 对应章节：系统总体设计

2. fig02_api_swagger.png
- 内容：Swagger 文档首页
- 对应章节：系统实现

3. fig03_route_plan_request.png
- 内容：路线规划接口请求参数
- 对应章节：关键模块实现

4. fig04_route_plan_response.png
- 内容：路线规划响应（node_path、distance、minutes）
- 对应章节：算法验证

5. fig05_unity_route_highlight.png
- 内容：Unity 中路线高亮与 marker
- 对应章节：客户端实现

6. fig06_node_auto_narration.png
- 内容：节点到站自动讲解字幕
- 对应章节：交互机制设计

7. fig07_spot_generate_api.png
- 内容：/api/v1/guide/spot-generate 调用结果
- 对应章节：AIGC 模块实现

8. fig08_voice_chat_ui.png
- 内容：录音问答界面与返回文本
- 对应章节：语音交互实现

9. fig09_test_report.png
- 内容：pytest 通过截图（8 passed）
- 对应章节：系统测试

10. fig10_demo_overview.png
- 内容：完整演示界面总览
- 对应章节：实验结果与分析

## 5. 答辩防翻车预案

### 5.1 后端启动失败

现象：No module named app

解决：使用 app-dir 启动命令，不要在根目录直接 app.main:app。

### 5.2 DeepSeek 临时不可用

解决：

- 保留 CHAT 配置不变
- 展示系统的 fallback 机制（模板讲解依然可运行）
- 强调架构支持多模型切换

### 5.3 语音识别无可用 API

解决：

- 保持 ASR_ENGINE=mock
- 演示语音链路仍完整可用
- 答辩中说明已预留真实 ASR 接口

### 5.4 Unity 无路线高亮

解决：

- 检查 nodeAnchors 的 nodeId 与后端返回是否一致
- 检查 LineRenderer 是否绑定

## 6. 评委常见问题速答

Q1：你的创新点是什么？

A：将 AIGC 动态讲解引入校园导览，并与路径规划、节点事件和语音问答形成实时联动，避免了传统静态导览内容。

Q2：为什么采用 FastAPI + Unity？

A：FastAPI 适合快速搭建高性能接口服务，Unity 具备成熟的三维交互和场景渲染能力，两者组合有利于快速实现与扩展。

Q3：没有真实 ASR 是否影响课题完整性？

A：不影响系统架构完整性。当前通过 mock 保证链路可验证，接口与模块均已按真实服务设计，后续可直接替换供应商。

Q4：如何证明系统可扩展？

A：已实现模型通道解耦（Chat 与 ASR 独立配置），并支持多源数据替换（校园节点、路径图、语音服务）。

## 7. 你明天可直接执行的最短流程

1. 启动后端并打开 docs 页面。
2. Unity 点击 PlanButton，演示路径与 marker。
3. 演示节点自动讲解。
4. 演示语音问答。
5. 用 4 句总结收尾：已实现、已测试、可扩展、可落地。
