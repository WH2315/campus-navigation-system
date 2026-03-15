# Unity 客户端接入说明

本目录提供可直接复制到 Unity 项目的脚本代码。

## 1. 建议 Unity 版本

- Unity 2021 LTS 或 Unity 2022 LTS

## 2. 场景搭建

1) 创建 Canvas
2) 添加以下 UI 组件：
- InputField: StartIdInput（起点）
- InputField: EndIdInput（终点）
- Dropdown: ProfileDropdown
- Dropdown: StyleDropdown
- Button: PlanButton
- Button: GuideButton
- Button: StartRecordButton
- Button: StopAndAskButton
- InputField: CurrentSpotInput（可选，当前景点ID）
- Text: ResultText

3) 创建空对象 Network，并挂载 ApiClient
4) 创建空对象 UIController，并挂载 GuideUIController
5) 创建空对象 VoiceController，并挂载 VoiceQAController
6) 创建空对象 RouteHighlighter，并挂载 RouteHighlighterController
7) 创建空对象 NarrationBubble，并挂载 NarrationBubbleController
8) 在场景中为每个节点建立锚点 Transform（命名建议与 node_id 对应）
9) 在 RouteHighlighterController 中绑定：GuideUIController、LineRenderer、节点锚点映射、可选 marker
10) 在 NarrationBubbleController 中绑定：GuideUIController、VoiceQAController、RouteHighlighterController、字幕文本、可选 AudioSource
11) 确保场景中包含 WavUtility.cs（静态工具类无需挂载）
12) 将 Api Base Url 设为 http://127.0.0.1:8000

## 3. 运行流程

- 点击 PlanButton 调用路线规划
- 路线规划成功后，RouteHighlighterController 自动绘制路线并移动 marker
- marker 到达节点后，会触发 NodeArrived 事件
- 点击 GuideButton 基于路线生成讲解词
- 讲解生成后，NarrationBubbleController 自动触发角色播报字幕
- 若在 NarrationBubbleController 中配置 nodeNarrations（nodeId -> narrationText），则节点到达时自动播报对应景点文案
- 若开启 NarrationBubbleController 的 autoFetchFromBackend，则启动时会自动请求 /api/v1/spots 并用后端 intro 更新讲解映射
- 若开启 useAIGCSpotNarration，则节点到达时会调用 /api/v1/guide/spot-generate 生成个性化讲解
- 点击 StartRecordButton 开始录音
- 点击 StopAndAskButton 上传语音并获取问答结果
- 语音问答返回后，同步触发角色气泡字幕显示

## 4. 可扩展方向

- 将节点 ID 与 3D 场景中的锚点对象绑定
- 添加角色动画与相机轨道
- 接入真实语音识别与语音播报（当前默认 mock ASR）
- 接入地图小窗和路线高亮渲染

## 5. 节点讲解配置示例

在 NarrationBubbleController 的 nodeNarrations 中添加：

- nodeId: gate_north, narrationText: 北门是学校主要出入口，连接城市主干道与校园主轴。
- nodeId: library, narrationText: 图书馆设有自习区、电子阅览室和学术报告厅，是学习中心。
- nodeId: stadium, narrationText: 体育馆承载课程和赛事活动，是校园活力地标。

如果你希望不手填文案：

- 勾选 autoFetchFromBackend
- 设置 apiBaseUrl 为后端地址（默认 http://127.0.0.1:8000）
- 保持后端服务运行，系统会自动拉取景点介绍并用于节点到站讲解

如果你希望每个节点都动态生成讲解词：

- 勾选 useAIGCSpotNarration
- 配置 narrationUserProfile（new_student/parent/visitor/alumni）
- 配置 narrationStyle（formal/friendly/storytelling）
- 配置 narrationLanguage（zh/en）
- 系统会在节点到达时请求后端生成讲解；若失败则自动回退到本地/缓存文案
