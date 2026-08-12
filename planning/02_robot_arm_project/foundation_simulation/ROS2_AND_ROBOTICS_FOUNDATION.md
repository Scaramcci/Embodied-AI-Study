# ROS2 and Robotics Foundation

ROS2 在本项目中是可观察、可替换的机器人软件总线，不是训练框架。MuJoCo baseline 可先用纯 Python，但所有真机接口概念必须能映射到 ROS2。

## 概念到项目接口

| 概念 | 简洁定义 | 本项目练习/用途 | 完成证据 |
|---|---|---|---|
| node | 单一职责进程 | camera、joint state、controller、logger、verifier 分离 | graph 显示清晰所有权 |
| topic | 连续异步消息流 | RGB、joint state、command、events | 频率/延迟/QoS 统计 |
| service | 短请求响应 | 查询校准/状态，不承担长动作 | 超时和错误路径测试 |
| action | 可反馈、可取消的长操作 | go-safe-pose、执行轨迹 | cancel/timeout 实测 |
| launch | 组合进程与参数 | sim/real 两套启动但共享接口 | 参数快照与启动日志 |
| rosbag | 带时间戳消息记录 | 诊断/回放，而非替代正式 dataset | bag info、同步回放 |
| TF | 随时间维护 frame 树 | world→base→tool→camera/object | 无断树；变换可查询 |
| URDF | link/joint/视觉/碰撞模型 | RViz、TF 与仿真模型核对 | joint/axis/limit 审计 |
| RViz | 机器人消息可视化 | 验证模型、frame、轨迹和相机 | 截图及异常案例 |
| joint state | 实测 position/velocity/effort | proprioception 与执行误差 | 单位/顺序/新鲜度断言 |
| controller | 将目标转为稳定运动 | 模拟/真机统一 action 接口 | commanded-vs-actual 曲线 |

Frame 约定：`world` 固定桌面场景；`base` 固定机器人基座；`tool`/`gripper` 随关节；`camera_top` 固定外部相机；`camera_wrist` 随末端。静态变换和动态变换必须明确区分，禁止把像素坐标直接当世界坐标。

## 小型练习路线

### R0 消息闭环

Entry：Linux/Python 环境设计完成。Tasks：joint-command publisher、mock controller、joint-state publisher、logger；测频率、jitter、端到端延迟；断开一个 node 观察失败。Validation：命令和状态带同一关节顺序、单位及单调时间；陈旧命令触发停止。Common failures：QoS 不兼容、双 publisher、时间源混用。Artifacts：node graph、统计和 bag。Exit：能定位数据在哪一跳丢失或延迟。

### R1 URDF / RViz / TF

Entry：R0；robot model 来源锁定。Tasks：加载模型，发布 joint state；显示 world/base/tool/camera；查询点在各 frame 的坐标。Validation：随机姿态与 FK 对照；TF tree 单根、无环、无过期动态变换。Common failures：轴向、parent/child 颠倒、度/弧度、四元数顺序。Artifacts：TF tree、joint table、RViz 图。Exit：能从相机观测路径追到机器人基座 frame。

### R2 action 与安全 controller mock

Entry：R1。Tasks：实现可取消轨迹 action；限位、速度限制、watchdog、safe pose；注入超时/越界。Validation：所有异常产生明确 stop reason，取消不会继续执行缓存动作。Artifacts：action trace、限制测试。Exit：无绕过 safety gate 的命令路径。

### R3 rosbag 回放与数据 schema 桥接

Entry：R2。Tasks：记录双图像占位+joint/action；回放到 preprocessing；导出正式 episode schema。Validation：原始时间戳保留，回放不改变对齐；bag→episode 可重复。Common failures：压缩差异、录制启动边界、frame drop。Artifacts：bag manifest、转换报告。Exit：同一数据可重现 observation tensor 和同步诊断。

## 与 SO-101 的连接

设备到货后只替换 `mock controller/joint state/camera` adapter，不改变上层 observation、action、logger、verifier 接口。若 LeRobot 原生路径不依赖 ROS2，不强行把实时闭环全部重写为 ROS2；ROS2 练习的价值是系统理解和诊断，生产路径以最少桥接为原则。

## Gate

Entry：R0 环境可运行。Tasks：完成 R0–R3 最小练习。Exit：能解释 topic/service/action 选择；TF/URDF 有数值验证；bag 可回放；控制安全异常被测试；输出 artifact 被纳入版本记录。

