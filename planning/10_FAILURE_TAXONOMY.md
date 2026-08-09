# Failure Taxonomy

标签可多选，并分 `task/policy/perception/control/system/verifier/safety` 根因层。检测规则和 metric 版本化；“unknown”是有效类别，不强迫事后猜测。

| Failure | Detection | Possible cause | Recovery | Targeted recollection | Metric |
|---|---|---|---|---|---|
| grasp miss | 闭合后夹爪/图像无对象，lift 前后位置不随工具 | approach 偏差、遮挡、数据稀疏 | reobserve→reposition→regrasp | 从 miss 前状态示范多方向对准 | miss / grasp attempts |
| partial grasp | 接触但对象姿态不稳/夹持过浅 | 夹爪中心偏、闭合时机 | 放回/松开，重新居中 | 收集边缘、旋转物体纠正 | partial / grasps |
| object slip | lift/move 后对象相对夹爪下移或掉落 | 抓力/摩擦、速度、腕姿态 | 减速；安全放回或 regrasp | 高风险运输姿态与平滑动作 | slips / transports |
| wrong object | 夹持对象 ID ≠ subgoal | grounding、遮挡、distractor | 安全放回，重观察 | 相似物体/distractor corrections | wrong-object / attempts |
| object occlusion | 关键对象不可见/置信不足 | 手臂/杂物遮挡、相机布局 | 移到观察位/换视角 | 遮挡状态与 reobserve | occluded decisions / trials |
| collision | 碰撞事件/异常电流/几何距离 | 路径、外参、动作跳变 | 立即停止→安全撤离/人工 | 只在仿真或安全监督下收集绕行 | collisions / trial |
| unreachable pose | IK/限位/持续跟踪误差判定不可达 | 目标超工作空间、frame 错 | 重规划接近方向/请求 reset | 边界目标及可达替代策略 | unreachable requests |
| placement offset | 对象终态在目标区外或姿态不符 | release pose、视觉误差、滚动 | regrasp/reposition | 目标边界/不同入射方向 | distance/angle; failure rate |
| dropped object | 对象脱离夹爪并落到非目标区 | slip、碰撞、过快 | 停止；定位；可达才 regrasp | 掉落前状态和平缓运输 | drops / trial |
| incorrect subgoal | 执行对象/区域/顺序与 task state 不符 | planner/memory/语言 grounding | 停止，回滚未确认状态 | 相邻顺序与 distractor 对比 | wrong subgoals / task |
| verifier error | 与人工/离线 gold verdict 不同 | 阈值、视角、状态错位 | unknown→重观察/人工；不盲目推进 | hard negatives/positives | precision/recall/FNR/FPR |
| camera failure | 丢帧、冻结、交换、过曝、旧帧 | USB/带宽/命名/曝光 | 停止 chunk，恢复传感或介入 | 不作为 policy 纠正数据混入 | failures / frames/trials |
| timing failure | action/observation 延迟或错位超阈值 | 缓冲、负载、时钟 | 停止并刷新队列 | 系统修复，不伪装成示范 | latency/jitter/drop rate |
| policy oscillation | 关节/末端反复换向且无进展 | OOD、chunk 聚合、噪声 | 中断→safe pose/reobserve | 从振荡起点示范平滑退出 | oscillations; reversals |
| action saturation | 命令持续触及 position/velocity limit | policy OOD、归一化、目标不可达 | clamp+stop/replan，不继续积累 | 边界状态；先排除单位错误 | saturated steps / steps |

## 标注与诊断规则

每个事件记录开始/结束 frame、当前 subgoal、primary/secondary labels、检测证据、人工确认、恢复动作、是否导致任务终止。先区分系统故障（camera/timing/servo）与策略能力故障；系统坏数据不计作 failure-targeted 学习收益。故障原因可为 `unknown`，后续修订必须保留原标签和审计轨迹。

## Gate

Entry：pilot rollouts 存在。Tasks：两名标注者或同一标注者复核子集；计算一致性；将定义落到事件 schema。Exit：常见失败覆盖、互斥/多标签规则明确、同一事件可重现定位、verifier 与人工 gold 分开。taxonomy 变更必须在 DECISIONS 和 dataset version 中记录。

