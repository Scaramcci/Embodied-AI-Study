# 每周详细计划：看懂 ACT、完成 LeRobot、读完方法地图并做有限复现

> W1 从 **2026-09-30** 开始；W9 到 **2026-12-01**。每周两篇论文、一个主要工程任务、一份合并汇报。此表只展开当前阶段；后续 VLA 与两个展示项目的顺序见 [总纲](01_具身学习与科研总纲.md)。日期可顺延，不按天安排。

## 使用规则

**主读**：方法核心、一个样本、实验设置和一项关键消融；**对照读**：完整主线、输入输出、实验依据、与主读的差别。不要求两篇都推公式，也不要求每篇都安装仓库。

每周工程按“看输入→跟一次运行→改一个小条件→解释输出”完成。遇到不懂的名词，只补当前步骤必需的内容。已做过的检查直接拿证据复盘，不从头再做。

论文按日历维持；工程按完成情况移动。每周表中的输出是汇报材料，不要求另建很多笔记文件。**复现只承诺有限范围：EgoMimic 小样本训练/离线验证，Track2Act 轨迹预测，VidBot 可供性推理。** 不安排完整重建原论文数据工厂或追平真机指标。

## 周总表

| 周次 | 日期 | 主读 + 对照读 | 唯一主要工程任务 | 周末应留下什么 |
|---|---|---|---|---|
| W1 | 9/30–10/6 | ACT + EgoMimic | 用已有 ACT 追一条训练样本 | 一条样本到 loss 的图，能解释像素和动作标签 |
| W2 | 10/7–10/13 | Track2Act + VidBot | 看 ACT 推理、PushT 执行，再检查 ALOHA 数据迁移 | 一个预测动作如何进入环境的记录 |
| W3 | 10/14–10/20 | Masquerade + Ego2Robot | PiperX 接口确认、相机与小量示教数据检查 | 硬件接口表、一条可读的示范或明确阻塞项 |
| W4 | 10/21–10/27 | VITRA + Being-H0 | PiperX 的 ACT 训练、部署与小规模评估 | 一次真机闭环记录，或尚缺环节清单 |
| W5 | 10/28–11/3 | Being-H0.5 + Qwen-RobotManip | EgoMimic：读人/机器人数据，跑一个 batch | 两域数据如何进入模型的对照 |
| W6 | 11/4–11/10 | LAPA + LAWM | EgoMimic：短训练、恢复、离线验证与受控比较 | checkpoint、预测可视化和限定结论 |
| W7 | 11/11–11/17 | JALA + LDA-1B | Track2Act 官方轨迹推理，回看 W2 论文 | 初始/目标图与预测轨迹、一个失败样例 |
| W8 | 11/18–11/24 | Dream2Flow + DreamGen | VidBot 官方 RGB-D 推理，回看 W2 论文 | 深度/内参/接触/轨迹的对应记录 |
| W9 | 11/25–12/1 | Do as I Do + Being-H0.7 | 收束方法地图、LeRobot 和复现；补一项关键缺口 | 本阶段报告、候选问题和后续 VLA 入口 |

为什么部分论文先读后跑：W2 先建立几何路线的认识；W7–W8 有项目经验后回读并实际运行，形成第二遍理解。W5–W6 的两篇比较阅读服务于人机表示和无动作监督；实际工程仍只维护一个 EgoMimic 项目，不同时安装四个新系统。

## W1：弄清你刚训练的 ACT 到底吃了什么

**阅读：** 主读 [ACT 原论文](https://arxiv.org/abs/2304.13705)，重点看视觉输入、动作块与训练/推理区别；对照读 [EgoMimic](papers/Egomimic/EgoMimic.pdf)，先回答“增加人类示范后，哪些数据和监督不同”。此周不要求理解 EgoMimic 整个实现。

**项目步骤：**

1. 找到已有训练命令、保存的配置、数据集 ID、checkpoint 和评估结果。检查实际的 `input_features`：有图像、状态还是环境状态？若本次没有视觉输入，就加载一条视觉数据或用匹配配置做单 batch 演示，不重新开大训练。
2. 从同一 episode 取一条样本：打开图片，打印 state、action、时间和 padding；对照数据文档确认动作单位。PushT 的动作不能按机械臂关节含义解释。
3. 沿 `LeRobotDataset → DataLoader → preprocessor → ACTPolicy.forward()` 跟一次运行。查看图像维度/数值范围怎样变；不要先人为添加物体检测或 mask。
4. 有图像时在 backbone 前后记录 shape，确认像素变成 feature map，再进入模型。把预测动作块与示范动作块并排看，确认 loss 的对象及 padding；若启用了 VAE，认识 KL 项的作用和训练期额外输入即可。

**验收问题：** 图片里有没有预先标好的物体坐标？哪些是输入、标签、可训练参数？这一张当前图对应哪段未来动作？你必须拿实际样例回答，不背通用介绍。

**本周汇报：** ACT/EgoMimic 一页差异；自己样本的一张图、几个字段和运行入口。原 LeRobot 计划对应 Day 6、Day 8，复用已完成的数据检查。不要安排第二个训练算法。

## W2：让预测的数字真正进入环境

**阅读：** 主读 [Track2Act](papers/Track2Act/Track2Act.pdf)，对照 [VidBot](papers/VidBot/VidBot.pdf)。只先分清“预测点轨迹/接触目标”和“输出实际控制动作”，三维重建细节先标待回读。

**项目步骤：**

1. 用已有 ACT checkpoint 重跑一段 PushT rollout。沿观测、preprocessor、`select_action()`、postprocessor 到 `env.step()`，看一次环境状态和下一张观测怎样改变。
2. 在自己配置中看动作队列、chunk 使用方式及是否开启 temporal ensembling。区分“一次预测多少步”和“多久重新观察”；不要默认每一步都重新算完整 chunk。
3. 把同一观测离线送入模型，比较原图与遮挡/替换图时输出是否变化。只作依赖诊断，不在真机执行扰动动作，也不把输出变化当作视觉理解的充分证明。无图像分支则明确解释它为何不响应。
4. 看一条公开 [ALOHA 仿真示范](https://huggingface.co/datasets/lerobot/aloha_sim_transfer_cube_human)，比较其相机、状态/动作维度与 PushT。做一次前向或短训练检查即可，不新增完整双臂训练任务。

**验收问题：** 离线训练时机器人是否在试错？视频文件解码和在线相机读取有什么共同出口？为什么一段预测很接近标签，连续执行仍可能失败？

**本周汇报：** 一段 rollout 的输入、预测和实际执行记录；Track2Act/VidBot 哪个步骤负责把中间量连到动作。对应原计划 Day 7、Day 9、第二周 ALOHA 迁移。PiperX 提前确认型号与可用排期，但本周不另开硬件开发。

## W3：把 LeRobot 的抽象字段接到 PiperX

**阅读：** 主读 [Masquerade](papers/Masquerade/Masquerade.pdf)，对照 [Ego2Robot](papers/Ego2Robot/Ego2Robot.pdf)。重点看“画面变成机器人”和“得到机器人动作标签”为什么是两件事。这周不安装去人/渲染全套环境。

**项目步骤（实机细节由你后续补）：**

1. 确认 PiperX 确切版本、固件、示教臂模式、相机和连接路径；定位实际使用的驱动/LeRobot 适配。不要套用 SO-101 的串口和电机设置，也不把 ALOHA 名称当成相同硬件。
2. 先读状态和相机画面：关节/夹爪字段是什么、单位是什么、画面用哪个 key、是否同步。用已确认的接口画出 `get_observation → policy → send_action`，不要先研究底层控制器的全部实现。
3. 在实验室人员确认的条件下完成示教检查，录少量测试 episode，立即检查帧、状态、动作、时间和任务描述，再决定是否扩大采集。
4. 选择一个固定场景的简单任务；相机能看到关键交互即可先起步。只有实际接口需要时才做几何标定，不为学习 ACT 额外搭 SLAM。

**不能到实验室时：** 用现有机器人示范检查同样字段，阅读记录与部署入口，完成硬件待核实表。公开数据检查可推进学习，但不能把“读过代码”勾成“已完成 PiperX 接入”。

**本周汇报：** 实际采集样本或明确的接口阻塞；两篇论文分别还给视频增加了什么。对应原计划 Day 10、连接/标定/相机/采集部分，实机动作遵循实验室操作规程。

## W4：完成一个简单的 PiperX ACT 闭环

**阅读：** 主读 [VITRA](papers/Vitra/vitra_paper.pdf)，对照 [Being-H0](papers/BeingH0/BeingH0.pdf)。重点追视频如何变成带状态、动作、指令的样本；比较连续人手动作与离散动作 token，不推网络结构细节。

**项目步骤：**

1. 数据按 episode 划分，检查相机字段、动作含义和归一化。先训练短检查再扩大；采集量和步数依任务及结果调整，不把固定数量当成功保证。
2. 保存配置、权重和 processor/statistics，重新加载检查。确认训练、推理的相机视角和动作表示一致；PushT 权重不能直接替代 PiperX 任务策略。
3. 在监督、限速和可停止条件下测试；做至少 10 次预先定义初始条件的小规模评估，记录成功数/总数和失败阶段。这是入门诊断，不是稳健性能结论。
4. 如果失败集中在一个阶段，只改变一个因素，例如补充对应示范；条件允许再做同协议比较。不得为了完成周计划省掉动作接口核对。

**验收问题：** 相机、状态读取、模型预测和底层执行分别干什么？哪项失败能从数据里提前发现？已有日志能否让你重新运行这次评估？

**本周汇报：** LeRobot 从公开数据到 PiperX 的一张流程图与真实结果。对应原计划实机训练/部署/评估。未完成则保留具体缺项，后续替换一个论文推理周继续，不要求硬件本周一定完成。

## W5：用 EgoMimic 接上人类视频，而不是另学一堆 CV 工具

**阅读：** 主读 [Being-H0.5](papers/BeingH0.5/BeingH0.5.pdf)，对照 [Qwen-RobotManip](papers/Qwen-RobotManip/Qwen-RobotManip.pdf)。本周只重点比较统一动作字段、有效维 mask、相机/世界坐标；其他模型组件停在用途层。

**项目步骤：**

1. 从 [EgoMimic 官方仓库](https://github.com/SimarKareer/EgoMimic)和公开 BowlPlace 样例开始。优先复用你实际已有环境与数据；本地目前只核实到两份导读，没有确认代码、HDF5 或 checkpoint 已就绪。
2. 并排打开一个 robot demo 和 human demo，查看图像、状态、动作块及划分名单。以实际文件核对 [本地项目导读](papers/Egomimic/EgoMimic-main/Learning_doc/01_项目结构与运行逻辑.md)，不照抄其中历史 shape 或“已完成”描述。
3. 对照 `configs → dataset/SequenceDataset → process batch → policy` 跟一个 batch，查清两域哪些字段不同、哪些网络共享、各自监督什么。注意 HDF5 的 split mask 不等于图像分割 mask。
4. 只跑官方 debug/单 batch，不处理原始 Aria 采集、不做完整相机标定，也不接作者的 ALOHA/Eve 真机系统。

**验收问题：** 这里的人类视频是否只是任意互联网 RGB？它额外拥有哪些标签/设备信息？为什么不能把人手的三维位置直接当 PiperX 关节角？

**本周汇报：** 两域样本与代码路径；把它和本周两篇“大规模统一表示”论文做接口对照。EgoMimic 是可运行的桥梁，不作为无需动作信息的互联网视频基线。

## W6：做一次有限训练，区分理解方法和验证论文

**阅读：** 主读 [LAPA](papers/LAPA/LAPA.pdf)，对照 [LAWM](papers/LAWM/LAWM.pdf)。回答：没有可靠人手动作标签时，监督从哪里来？训练时能看未来，部署时为什么不能照搬？本周不安装其全训练栈。

**项目步骤：**

1. 在 EgoMimic 样例上完成短训练、存读 checkpoint 和官方离线验证，打开预测与标签可视化。默认单卡，先测显存，再决定数据规模。
2. 在资源和官方配置支持时，比较 robot-only 与加入 human 数据的设置。固定机器人训练/验证划分，列出模型、动作头和更新次数等是否变化；若架构也变了，就叫“两个配方的教学比较”，不声称隔离了人类数据贡献。
3. 亲自解释一次预测错误，核对是否与时间、坐标、归一化、遮挡或数据量有关。不从验证视频好看推导实际操作成功率。

**最低验收：** 一次有限训练和可恢复的离线验证完成；能解释人类数据在哪一步参与损失。对照不稳定可以保留为排查结果，不要求必须得到收益。

**本周汇报：** 数据范围、配置差异、实际指标、失败和结论边界。明确这不是原论文真机复现，也不把 EgoMimic 的预测视频当仿真 rollout。[官方训练与离线验证入口](https://github.com/SimarKareer/EgoMimic)

## W7：真正跑一次“视频运动表示”的论文模块

**阅读：** 主读 [JALA](papers/JALA/JALA.pdf)，对照 [LDA-1B](papers/LDA-1B/LDA-1B.pdf)。理解有动作/无动作/低质量动作数据分别进入哪些训练目标；不实现全部损失。把上周 EgoMimic 的双域数据作为参照。

**工程主任务：** 回读 W2 的 Track2Act，运行 [官方轨迹预测](https://github.com/homangab/Track-2-Act)。

1. 先用官方权重和示例初始图/目标图，查看实际预处理、推理输出和轨迹可视化。
2. 查明模型预测的是哪些点、多少步、什么坐标；追到可视化前的数组，而不是只播放最终视频。
3. 固定初始图，改变目标图或起始点，先预测可能结果再运行。保留一个失败或不合理输出。
4. 读清“预测轨迹→物体运动→末端计划→残差策略”的后半段接口即可，不重建完整机器人系统。CoTracker 提取已发生轨迹与这里预测未来轨迹不同。

**验收：** 能指出已运行模块的终点、与电机命令之间仍缺哪些步骤。若硬件补课占用本周，则保留读接口/官方输出，推理移到 W9 或取消，状态写清。

## W8：把二维观察和三维目标接起来

**阅读：** 主读 [Dream2Flow](papers/Dream2Flow/Dream2Flow.pdf)，对照 [DreamGen](papers/DreamGen/DreamGen.pdf)。只抓住生成视频用在推理时提出目标，还是训练前造数据；分别需要什么动作/几何转换。本周不训练视频生成模型。

**工程主任务：** 回读 W2 的 VidBot，使用 [官方 RGB-D 示例和预存框](https://github.com/HanzhiC/VidBot)。

1. 跑官方推理，不先安装所有检测、抓取和原始视频重建依赖。
2. 打开一张 RGB、深度和内参，追到接触/目标/轨迹输出。用项目现有几何函数看一个像素怎样对应三维点；只补这里需要的相机知识。
3. 在离线副本中改变一个条件，例如框或深度尺度，观察三维结果变化，保留原始基线。不要把受扰输出送给真机。
4. 对照 Track2Act 和 ACT：前两者的中间表示为什么需要额外桥接，而 ACT 在匹配平台上可直接预测其动作接口？

**验收：** 能区分 RGB、深度、内参、三维轨迹、机器人动作；明确本次没有复现 VidBot 从互联网视频提取训练标签的整套流程。运行困难时保留一个论文推理项目即可，不追加替代仓库。

## W9：收束，避免“又学了一堆，但不知道学了什么”

**阅读：** 主读 [Do as I Do](<papers/Do as  I Do/Do as I do.pdf>)，对照 [Being-H0.7](papers/BeingH0.7/BeingH0.7.pdf)。前者重点是物理重定向生成轨迹；后者重点是训练期未来监督。两者解决不同问题，不强行比较胜负。

**工程主任务：** 不安装新模型，用本周补一个最重要未完成项，优先顺序是 PiperX 闭环→EgoMimic 训练/验证→至少一个几何论文推理。不能一次补三个。

**整理与汇报：**

- 16 篇各完成一张短卡，订正现有 Pipeline 图中自己此前误解的箭头；无需重新美化全图。
- 列出 LeRobot 的实际已完成项：PushT、数据/推理理解、ALOHA 数据检查、PiperX 采集、训练、部署、评估。区分完成、只阅读、阻塞。
- 列出复现的确切范围与结果位置。标明：组件调用、官方推理、有限训练、论文结果复现是不同级别；本轮没有要求最后一级。
- 从真实遇到的问题里留下至多三个候选问题，各写一个观察依据、可能解释和最小对照，交给导师讨论。没有证据的想法标为猜测。

**结束条件：** 你能连续讲清“示范数据→训练→评估/执行”，能解释至少一种人类视频监督和一种几何中间表示，知道下一步做 VLA 会增加什么。若 PiperX 因排期仍未完成，保留一个独立待完成项，不能宣布 LeRobot 实机毕业；其他学习不必全部停住。

## 代码入口与资料索引：按当前周查，不按顺序通读

| 用途 | 本轮核对的入口 | 只看什么 |
|---|---|---|
| 原 LeRobot 进度 | [你的 LEARNING_PLAN.md](https://github.com/Scaramcci/lerobot/blob/main/LEARNING_PLAN.md) | 已勾选第一周不重做；Day 6–10 与实机部分已经合入本计划 |
| ACT 配置 | [configuration_act.py](https://github.com/Scaramcci/lerobot/blob/main/src/lerobot/policies/act/configuration_act.py) | 输入 features、chunk、backbone、VAE 开关；最终以你保存配置为准 |
| ACT 训练/推理 | [modeling_act.py](https://github.com/Scaramcci/lerobot/blob/main/src/lerobot/policies/act/modeling_act.py) | `ACTPolicy.forward`、`select_action`、图像 backbone 路径；其余按需要查 |
| 前后处理 | [processor_act.py](https://github.com/Scaramcci/lerobot/blob/main/src/lerobot/policies/act/processor_act.py) | 默认 processor 的归一化、batch/device、反归一化；数据解码另在 dataset 路径 |
| 相机与录制 | [Cameras](https://huggingface.co/docs/lerobot/cameras)、[模仿学习教程](https://huggingface.co/docs/lerobot/il_robots) | 只读实际相机与机器人适配使用的步骤 |
| PiperX 核对 | [厂商 SDK](https://github.com/agilexrobotics/piper_sdk)、[第三方机器人入口](https://huggingface.co/docs/lerobot/third_party_robots) | 核实型号/固件/通信与适配，不把通用 PiPER 文档视为 PiperX 兼容证明 |
| EgoMimic | [官方仓库](https://github.com/SimarKareer/EgoMimic)及本地 Learning_doc | `pl_train.py`、configs、两域数据、离线 eval；实际以安装版本为准 |
| 方法总图 | [05_论文Pipeline逻辑图绘制说明](05_论文Pipeline逻辑图绘制说明.md) | 遇到路线混淆时查；不是额外待办表 |

代码和远程计划于 2026-09-29 只读核对，周计划按你指定的 9/30 起算。远程 main 会变化，执行时记录当前 commit；本次没有修改 LeRobot 仓库、下载训练数据或运行 GPU/实机。

## 每周只用这一份汇报骨架

```text
本周的问题：
主读/对照论文：各自解决什么，证据与限制是什么？
我实际运行了什么：输入、配置/版本、结果位置。
我能自己解释什么：拿一个样例讲清。
失败/尚未完成：不要省略，也不要写成成功。
下周唯一主要工程任务：
```

每周固定两篇阅读，但不要固定“必须训练出更高分”。能定位一处自己以前说不清的处理过程，并用运行结果解释它，就是实际进步。
