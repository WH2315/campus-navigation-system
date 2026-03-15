# Unity 联调检查清单（可逐项验收）

## 0. 前置状态确认

- 后端服务已启动：`http://127.0.0.1:8000/docs` 可打开
- Python 测试通过：`8 passed`
- Unity 场景已导入以下脚本：
  - ApiClient.cs
  - GuideUIController.cs
  - VoiceQAController.cs
  - RouteHighlighterController.cs
  - NarrationBubbleController.cs
  - WavUtility.cs

## 1. Inspector 绑定检查

### 1.1 Network

- ApiClient 挂在 Network 对象
- Api Base Url = `http://127.0.0.1:8000`

### 1.2 Guide UI

- GuideUIController 挂在 UIController 对象
- 已绑定：StartIdInput、EndIdInput、ProfileDropdown、StyleDropdown、PlanButton、GuideButton、ResultText

### 1.3 Voice QA

- VoiceQAController 挂在 VoiceController 对象
- 已绑定：StartRecordButton、StopAndAskButton、CurrentSpotInput、ResultText

### 1.4 Route Highlighter

- RouteHighlighterController 挂在 RouteHighlighter 对象
- 已绑定：GuideUIController、LineRenderer
- nodeAnchors 已配置（nodeId 与 Transform 一一对应）
- 可选 marker 已绑定（用于巡游演示）

### 1.5 Narration Bubble

- NarrationBubbleController 挂在 NarrationBubble 对象
- 已绑定：GuideUIController、VoiceQAController、RouteHighlighterController
- 已绑定：speakerLabelText、bubbleText、transcriptText
- 可选 narratorAudioSource、placeholderNarrationClip 已绑定

## 2. API 连接验收（不进 Unity）

### 2.1 健康检查

- 请求：GET `/health`
- 预期：200，`status=ok`

### 2.2 路线规划

- 请求：POST `/api/v1/route/plan`
- 示例：`start_id=gate_north`，`end_id=stadium`
- 预期：返回 `node_path`、`total_distance`、`estimated_minutes`

### 2.3 节点文案源

- 请求：GET `/api/v1/spots`
- 预期：返回 `spots[]`，每个 spot 含 `node_id` 和 `intro`

### 2.4 单景点讲解

- 请求：POST `/api/v1/guide/spot-generate`
- 预期：返回 `title`、`script`

## 3. Unity 功能验收

### 3.1 路线规划与高亮

- 操作：输入起点/终点，点 PlanButton
- 预期：
  - ResultText 显示路线成功
  - LineRenderer 绘制路径
  - marker 沿路径移动

### 3.2 节点到站自动讲解

- 操作：等待 marker 到达节点
- 预期：
  - 气泡字幕自动显示对应节点讲解
  - speakerLabelText 更新为讲解角色

### 3.3 节点 AIGC 动态讲解

- 条件：NarrationBubbleController 勾选 `useAIGCSpotNarration`
- 操作：执行路线巡游
- 预期：
  - 到站时调用 `/api/v1/guide/spot-generate`
  - 返回成功时显示动态讲解词
  - 失败时回退到本地/缓存文案

### 3.4 语音问答链路

- 操作：点击 StartRecordButton 录音，再点击 StopAndAskButton
- 预期：
  - 上传音频到 `/api/v1/session/voice-chat`
  - 返回 transcript + answer
  - transcriptText 和 bubbleText 同步更新

## 4. DeepSeek + Mock ASR 推荐配置

在 backend/.env 使用：

- CHAT_API_KEY=你的DeepSeekKey
- CHAT_BASE_URL=https://api.deepseek.com/v1
- CHAT_MODEL=deepseek-chat
- ASR_ENGINE=mock

说明：

- 文本生成、问答、节点个性化讲解走 DeepSeek
- 语音识别先走 mock，保证演示流程完整

## 5. 常见问题排查

### 5.1 提示 No module named app

- 启动命令需指定 app-dir：
  - `python -m uvicorn --app-dir d:/AAA/campus-navigation-system/backend app.main:app --host 0.0.0.0 --port 8000`

### 5.2 Unity 里没有画路线

- 检查 nodeAnchors 中 nodeId 是否和后端返回完全一致（区分大小写）
- 检查 LineRenderer 是否绑定

### 5.3 到站不触发讲解

- 检查 NarrationBubbleController 是否绑定 RouteHighlighterController
- 检查 autoNarrateOnNodeArrival 是否开启

### 5.4 语音按钮点击无反应

- 检查麦克风权限
- 检查 VoiceQAController 的 UI 引用绑定
- 检查后端 `/api/v1/session/voice-chat` 是否可访问

## 6. 最终验收标准（答辩可用）

- 路线规划成功并可视化
- marker 巡游与节点自动讲解可联动
- 语音提问可返回答案并显示字幕
- 后端接口可稳定返回 200
- 演示过程中无阻断性报错
