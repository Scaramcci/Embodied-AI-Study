# F2 核心概念：FK、Jacobian 与 IK

## 1. 两种空间

### Joint space（关节空间）

机器人配置由关节变量组成：

```text
q = [q1, q2, ..., qn]
```

旋转关节通常以 radian 表示，移动关节通常以 metre 表示。数组的第 `i` 项并没有
脱离机器人模型的固定含义；必须同时知道 joint name、joint order、joint type、
unit、zero convention 和 limit。

### Task space（任务空间/笛卡尔空间）

我们希望末端完成的几何任务，例如：

```text
位置 p = [x, y, z]
姿态 R 或 quaternion
```

“腕部到目标点”属于 task-space 目标；“第 2 关节转到 0.7 rad”属于 joint-space
命令。重定向的核心工作之一，就是在这两种表示之间建立受约束的映射。

## 1.1 Base frame 与 end-effector frame

**Frame（坐标系）**不只是一个空间位置，它包含原点和坐标轴方向。一个点的
`[x, y, z]` 数字只有在指定 frame 后才有物理意义。

### Base frame

固定在机器人基座上的参考坐标系，是机器人运动学计算的共同参考：

- 原点通常位于底座或第一个关节附近；
- 轴方向由机器人模型定义，不保证与相机或房间坐标轴一致；
- FK 常输出“末端相对于 base frame 的 pose”；
- 人体/相机目标必须先转换到这个 frame，才能与机器人 FK 结果比较。

### End-effector frame

固定在机器人末端工具上的坐标系，例如腕部法兰、夹爪中心或 tool center point
（TCP）：

- 原点定义“末端位置”究竟指哪里；
- 坐标轴定义夹爪朝向；
- 法兰 frame、夹爪 frame 和 TCP frame 可能不同；
- 如果只给位置、不约束该 frame 的方向，夹爪可能到达目标却朝向错误。

常见 FK 输出 `T_base_ee(q)`：它描述 end-effector frame 相对于 base frame 的
位置和方向。必须在项目中明确变换符号采用哪一种方向约定。

## 2. Forward Kinematics（FK）

```text
robot model + q  --FK-->  link poses / end-effector pose
```

FK 是确定性的模型计算。它回答“给定这些关节变量，模型中的机器人在哪里”。

FK 依赖：

- 机器人拓扑：哪些 link 由哪些 joint 连接；
- link 几何参数和 joint axis；
- base frame 与每个 joint 的零位定义；
- joint order 和单位。

FK 不回答：

- 这个 `q` 是否会碰撞；
- 电机是否有足够力矩到达或保持该姿态；
- 轨迹速度、加速度是否安全；
- 实机是否因为标定误差、背隙或柔性而到达完全相同的位置。

因此，“FK 数值正确”只是几何层正确，不等于动态可行或硬件安全。

## 3. Jacobian

Jacobian 是当前配置附近的局部线性映射：

```text
end-effector velocity ≈ J(q) @ joint velocity
```

这里 `J(q)` 是由当前关节配置决定的矩阵，不是一个固定数字。对于有 `n` 个关节、
只控制三维末端位置的机器人：

```text
q_dot:   shape (n,)   关节速度
J(q):    shape (3,n)
p_dot:   shape (3,)   末端线速度
p_dot = J(q) @ q_dot
```

如果同时控制三维位置和三维角速度，常写成 `6 × n` geometric Jacobian。

对 revolute joint，Jacobian 中的线速度部分可以理解为：

```text
旋转轴 ×（末端位置 - 关节位置）
```

因此它确实包含类似“力臂长度 × 角速度”的关系，但还包含方向、所有关节贡献的
叠加以及当前姿态。不能把整个 Jacobian 简化成一个长度。

单位上，位置 Jacobian 对 revolute joint 的列通常可理解为 metre/radian；乘以
radian/second 后得到 metre/second。radian 在量纲分析中常视为无量纲，但工程上
仍应明确记录。

它连接的是“小变化/速度”，而不是直接把任意目标位置变成关节角。

它有三个关键用途：

1. 数值 IK 根据末端误差迭代修改关节角；
2. 判断某个配置附近哪些末端运动方向容易或困难；
3. 识别奇异位形：Jacobian 丢失秩或病态，某些方向无法产生速度，或者需要极大
   的关节速度。

Jacobian 是**局部**模型。离当前配置很远的目标不能只靠一次线性计算解决，需要
反复更新 `q`、重新计算 FK/Jacobian。

## 4. Inverse Kinematics（IK）

```text
target end-effector pose + robot model + constraints --IK--> candidate q
```

IK 反过来问：“为了让末端接近目标，关节变量可以是什么？”与 FK 不同，IK
通常不是唯一且不保证有解：

- **多解**：同一个腕部位置可能有 elbow-up 和 elbow-down；
- **无解**：目标在 workspace 外，或被 joint limits/碰撞约束排除；
- **局部最优**：数值求解器受初值影响，可能停在不够好的解；
- **奇异附近不稳定**：很小的末端变化可能导致很大的关节变化；
- **冗余**：机器人 DoF 多于任务约束时，有无穷多个候选配置，需要次级目标选择。

一个可靠的 IK 接口不应该只返回数组 `q`，还至少应返回：

```text
success / status
final task error
joint-limit result
iteration count or solver status
```

得到数值后还要用 FK 回代：`FK(q_solution)` 是否真的接近目标。

## 5. Workspace、joint limits 与可执行性

### Workspace

末端在纯几何模型中可能到达的位置集合。目标位于几何 workspace 内，也不代表在
当前 joint limits、碰撞环境和任务姿态要求下可达。

### Joint limits

硬件关节有合法位置范围，还可能有速度、加速度、力矩和温度限制。软件模型中的
limit 必须与真实机器人和控制器一致。

### Kinematically feasible vs executable

```text
几何可达
  -> 满足位置 joint limits
  -> 无自碰撞/环境碰撞
  -> 满足速度与加速度限制
  -> 电机/控制器能够跟踪
  -> 才接近实机可执行
```

F2 主要研究前两层，并明确记录后几层没有被验证。

## 6. 为什么人体关键点不能直接复制成机器人关节角

人体关键点通常是 camera/world frame 中的位置；机器人关节角是机器人特定
kinematic chain 的内部配置。两者存在 embodiment gap：

- **表示不同**：三维点位置不等于关节角；
- **尺寸不同**：人体上臂和机器人 link 长度不同；
- **拓扑不同**：人的肩关节结构与机器人串联关节结构不同；
- **DoF 不同**：人的肩部运动能力不一定对应机器人的关节数量和轴向；
- **约束不同**：机器人有硬限位、碰撞和执行器限制；
- **frame 不同**：人体数据可能在 camera frame，机器人模型在 base frame；
- **任务歧义**：只匹配腕部位置时，肘部形态和腕部姿态可能完全错误。

所以通常先做尺度与 frame 对齐，再把人体信息转换成任务约束，例如腕部位置、
腕部姿态、肘部位置或 arm-plane，最后通过 IK/优化寻找合法机器人配置。

## 7. 审查 AI 生成运动学代码的清单

看到一段能运行的 FK/IK 代码，至少检查：

- 使用的是哪个机器人模型和 base/end-effector frame；
- joint names、order、type、axis 和 unit 是否明确；
- quaternion/Euler 的表示和乘法约定是否明确；
- joint limits 是否真的传给 solver，而不只是事后裁剪；
- 不可达目标是否显式失败；
- IK 解是否经过 FK 回代并报告 task error；
- 轨迹是否出现解分支跳变；
- 是否检查碰撞、速度、加速度；若没有，报告中是否明确说明。

Vibe coding 可以快速生成实现，但这些语义和边界仍需要研究者负责。

## 8. 场景判断记录

### IK/FK 正确但撞桌子

这通常说明求解问题只包含末端跟踪，没有包含机器人几何体与桌面的碰撞约束。
FK/IK 可以在自己的数学定义内完全正确；缺失的是 collision checking 或
collision-aware planning。工程上不能把“task error 很小”当成“可以安全执行”。

### 平滑目标产生关节跳变

常见原因：

- IK 有多个解，逐帧求解时在 elbow-up/elbow-down 等分支间切换；
- 每帧使用不同或固定初值，没有以上一帧解进行 warm start；
- 目标接近奇异位形，小目标变化被放大成大关节变化；
- 角度表示跨过 `-pi/pi`，数值看起来跳变但物理姿态可能连续；
- 噪声、不可达帧或 joint limits 迫使求解器换解。

常见改进：上一帧解作为初值；加入 `||q_t-q_{t-1}||` 连续性代价；固定合理的
解分支；进行 angle unwrapping；在奇异附近使用 damped least squares；记录失败
状态；必要时对整段轨迹联合优化，而不是独立逐帧 IK。

### 相机腕点输入 IK 前的最低检查

- 输入点属于哪个 camera frame、单位、时间戳和置信度；
- 相机到 robot base 的外参变换；
- 人体与机器人的尺度归一化和 root 对齐方式；
- robot model 的 link lengths、拓扑、joint order/axis/zero/limits；
- 目标位置、末端姿态、肘部/arm-plane 中哪些是任务约束；
- workspace、不可达、碰撞和轨迹连续性怎样处理；
- IK 输出是否经 FK 回代，并报告 status/error/limit result。

### 为什么裸 `q` 不能直接发给实机

单独的 `q` 无法证明求解成功、误差可接受、关节未越界、轨迹连续、无碰撞，或
满足速度/加速度限制。它必须先经过独立验证层；实机控制器还应执行限位、限速、
超时拒绝和急停等安全措施。
