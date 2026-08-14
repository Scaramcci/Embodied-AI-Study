# 人体肩—肘—腕到机器人任务目标

## 研究问题

输入是人体动作观测，输出是机器人合法、连续的关节轨迹。重定向不是复制数组，
而是在不同 embodiment 之间保留任务意图。

## 输入数据

最小人体输入：

```text
shoulder[T, 3]
elbow[T, 3]
wrist[T, 3]
timestamps[T]
confidence[T, 3 joints]
frame = camera/world
unit = metre
```

任何坐标缺少 frame、unit 或时间语义时，都不能直接进入重定向。

## 处理流水线

```text
人体关键点
  -> 质量检查
  -> frame 对齐
  -> root centering
  -> scale normalization
  -> task construction
  -> constrained IK / trajectory optimization
  -> FK、limits、连续性和碰撞检查
  -> 机器人关节轨迹
```

## 1. 质量检查

检查置信度、遮挡、丢帧、突变和时间戳。不可靠观测应当被标记、插值或拒绝，不能
静默当成真实动作。

## 2. Frame 对齐

人体点可能在 camera frame，机器人任务通常在 robot base frame。需要已知的外参
变换和明确的轴向约定：

```text
p_base = T_base_camera * p_camera
```

这一步解决“同一个物理点在两个坐标系中数字不同”的问题，不解决人体与机器人
尺寸差异。

## 3. Root centering

以肩部作为手臂动作的局部 root：

```text
human_elbow_relative = elbow - shoulder
human_wrist_relative = wrist - shoulder
```

这样保留手臂形态与运动方向，同时去掉人体在相机画面中整体站在哪里的影响。之后
再把局部动作放到机器人肩部或 base 中定义的参考位置。

## 4. Scale normalization

人体和机器人臂长不同。常见做法是使用人体与机器人手臂 reach 的比例缩放相对
向量，或先转成无量纲表示再映射到机器人 workspace。

单一全局尺度保持整体运动比例，但不能消除上下臂比例差异。分别缩放每段可能更好
匹配肘部，却会改变腕部轨迹。采用哪一种是实验设计，需要记录并比较。

缩放后的目标仍要做 workspace 和 reachability 检查；不能用缩放把所有不可达帧
静默压到边界上。

## 5. Task construction

人体观测通常不直接生成 robot `q`，而是生成优化目标：

- wrist position：主要末端任务；
- wrist orientation：有可靠手掌/腕姿态时使用；
- elbow position：帮助选择肘部形态；
- arm-plane：用肩、肘、腕定义的平面或法向，保留手臂弯曲方向；
- temporal continuity：当前配置靠近上一帧或整段轨迹平滑。

这些目标可能互相冲突。通常腕部任务优先，肘部/arm-plane 作为次级或软约束，
joint limits 和安全约束保持硬边界。

## 6. IK / trajectory optimization

逐帧 IK 为每一帧单独寻找 `q_t`，速度快但可能换解分支。轨迹优化同时处理
`q_1...q_T`，可直接加入速度、加速度和平滑项，但计算更复杂。

常见流程是：逐帧 IK 生成初始轨迹，再做整段优化。

## 7. 输出与验证

输出至少包含：

```text
q[T, DoF]
timestamps[T]
joint_names / joint_order
unit
solver_status[T]
task_error[T]
limit_violation[T]
```

随后检查 FK 回代、不可达帧、限位、解分支跳变、速度/加速度以及碰撞。失败帧必须
保留状态，不能只删除后报告平均误差。

## 人体信息的层次

```text
人体原始关键点：观测
相对骨段与 arm plane：人体动作表示
腕部/肘部目标：机器人任务意图
robot q：机器人内部配置
```

这四层不能因为 shape 相近而混用。
