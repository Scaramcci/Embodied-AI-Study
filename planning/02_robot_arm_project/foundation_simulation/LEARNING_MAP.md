# Learning Map

学习顺序由接口依赖决定：机器人语言 → 软件与坐标 → 仿真闭环 → 数据 → 模仿学习 → 硬件/teleop → 真机策略 → 长时序验证与恢复。已熟悉的 Python、PyTorch、Transformer 和基础 CV 只在接口处补齐。

## 路径与掌握层级

| 知识 | What | Why / 项目使用处 | 掌握标准 |
|---|---|---|---|
| joint / DOF | joint 是可动连接；DOF 是独立运动变量数 | 定义 SO-101 state/action 与限位 | 必须实操：读取、命名、绘制、限幅每个关节 |
| pose / frame | pose 是位置与方向；frame 是表达它的坐标基准 | 世界、基座、末端、相机、物体变换 | 必须实操：画 frame 树，做点/姿态变换并验证 |
| TF | 带时间的 frame 变换树 | 融合相机、机器人与目标 | 必须实操：发布/查询 TF、诊断断树和时间错误 |
| FK / IK | FK: joint→末端 pose；IK: 目标 pose→joint 解 | 验证模型、脚本策略、可达性 | FK 必须实验；IK 能调用、检查多解/不可达，不要求推导复杂算法 |
| joint/task space | 关节变量空间与笛卡尔任务空间 | 区分 policy 输出与 controller 接口 | 必须能转换、比较约束和故障模式 |
| trajectory | 带时间的状态/动作序列 | teleop、action chunk 和执行平滑 | 必须检查速度、加速度、连续性与回放 |
| controller | 低层误差调节与安全执行 | 把目标关节/速度变成稳定运动 | 理解 position/velocity/torque；实操 position 控制与限幅；不需自研伺服驱动 |
| policy | 根据 observation 预测目标/action | ACT/SmolVLA Actor | 必须实操训练、rollout、区分 policy error 与 controller error |
| frequency / latency | 控制采样率与从观测到动作生效的延迟 | 时序错位会破坏模仿学习和安全 | 必须测量分布、记录 dropped frame，做延迟故障注入 |
| proprioception | 机器人内部状态，如关节和夹爪 | 视觉模糊时提供运动状态 | 必须同步记录、归一化和回放 |
| observation/state/action | observation 是可测输入；state 是系统内部描述；action 是控制命令 | 数据 schema 与策略接口的根 | 必须写出 shape、单位、frame、频率、范围、时间语义 |
| action chunk | 一次预测一段动作 | ACT 平滑与吞吐，但可能降低反馈速度 | 必须比较 chunk 长度、重规划频率和中断机制 |
| closed loop | 执行动作后重新观察再决策 | 对抗误差与扰动 | 必须在仿真和真机展示扰动后的纠正 |
| episode | 从 reset 到终止的一段交互 | 数据、切分、统计的基本单元 | 必须定义边界、终止原因、成功/失败标签 |
| BC / covariate shift | 监督拟合专家动作；rollout 偏离会进入未见状态 | 解释失败驱动采集为何必要 | 必须跑 baseline、比较离线 loss 与在线成功，识别分布漂移 |
| ACT | Transformer action-chunking imitation policy | 首个有代表性的视觉模仿 baseline | 必须训练、部署、评估；架构推导只需到能改输入/输出和诊断 |
| teleoperation | 人类实时控制 follower | 采集 demonstrations 和 corrections | 必须安全操作、标记干预、发现延迟/饱和/操作者偏差 |
| calibration | 建立传感器/执行器数值与物理现实的对应 | 训练和部署一致性 | 必须完成关节/方向/范围/相机一致性；高级手眼标定按需 |
| Sim2Real | 将仿真训练/测试迁移到真机 | 可选增加数据或研究对比 | 概念必知；只有证据表明有价值才实操大规模随机化 |
| VLA | 视觉语言输入到机器人动作的策略 | 后期语言条件扩展 | 先理解接口和延迟；主线稳定后实操 SmolVLA，不先追大模型 |
| verifier | 独立判断子目标是否满足 | 防止 Actor 自我宣告成功 | 必须先用确定性规则/轻分类器，测 precision/recall 和误判代价 |
| recovery | 根据失败状态选择重试、重观测、重抓或人工介入 | 长时序任务不中断 | 必须有边界、次数限制、安全回退和独立成功率 |
| task state / memory | 已完成项、当前子目标、对象状态和历史 | 保持顺序，避免重复动作 | 必须实现可序列化状态机和状态转移日志 |

## 学习模块 Gate

### L0 机器人表示与控制

Entry：能读 Python 配置和张量。Tasks：关节命名/单位/限位；二维/三维 frame 变换；FK；position loop；频率/延迟测量。Artifacts：术语卡、frame 图、FK 数值测试、控制曲线。Exit：能解释同一 pose 在不同 frame 的差异；限位或时间戳错误能被测试捕获。

### L1 ROS2 与机器人软件

Entry：L0。Tasks：node/topic/service/action/launch/rosbag；URDF/RViz/TF；joint state 与 controller 接口。Artifacts：最小 graph、bag、TF tree、URDF 截图和诊断记录。Exit：能从 topic 时序追到控制效果，而非只会运行 launch。

### L2 闭环仿真

Entry：L0；ROS2 可并行但非 MuJoCo 硬前置。Tasks：reset/step、observation/action、简单抓放、扰动和指标。Artifacts：固定种子 rollout、轨迹、视频、失败日志。Exit：能稳定复现成功和至少三种故障。

### L3 数据与模仿学习

Entry：L2。Tasks：episode schema、同步审计、sim demonstrations、BC/ACT、在线评估、covariate shift。Artifacts：versioned dataset manifest、审计报告、checkpoint、实验记录。Exit：能独立解释 dataset→train→rollout→failure。

### L4 Hardware Purchase Gate

Entry：L3。Tasks：阅读 LeRobot SO-101 数据、训练、部署路径；映射到本项目 schema。Exit：能说明 observation/state/action/policy/controller，跑通 closed-loop simulated robot 和基础 imitation policy，并独立追踪 LeRobot pipeline。达到后即可采购 SO-101，不需等待 Isaac/VLA/全部仿真完成。

### L5–L7 真机、研究与长时序

Entry：分别对应 G3、G5、G6。必须实操安全 bring-up、同步数据、ACT rollout、故障挖掘、公平对照、Verifier/Recovery。Exit 以 [项目路线图](../ROADMAP.md) 的 Gate 为准。

## 只需概念 vs 必须操作

只需概念：复杂动力学推导、torque control 内环实现、高级优化 IK、全套 SLAM、Isaac 扩展开发、基础 VLA 预训练。必须操作：frame/TF、FK 数值验证、控制频率/限幅、MuJoCo 闭环、数据同步/回放、teleop、标定、ACT 训练部署、真机安全、失败标注、定量验证和恢复。
