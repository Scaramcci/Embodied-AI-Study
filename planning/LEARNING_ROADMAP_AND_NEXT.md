# Embodied AI Learning Roadmap and Current Plan

这是本项目的学习执行入口，也是持续更新的活文档。它同时回答两个问题：

1. **整体规划（Roadmap）**：从机器人基础到真实 SO-101 长时序操作系统，需要依次掌握什么；
2. **当前计划（Current Plan）**：现在只做哪些任务、做到什么程度才算完成、完成后往哪里推进。

完成一个学习任务后，在对应条目记录证据，并更新“当前计划”。不要只因为看完课程、代码不报错或模型 loss 下降就标记完成。

## 1. Final Learning Outcome

最终能够独立构建、解释、调试和评估以下完整 embodied AI loop：

```text
language task
    -> Planner / task decomposition
    -> observation (RGB + robot state + time)
    -> Actor / policy
    -> safety Controller
    -> robot or simulator
    -> Verifier
    -> success: update task state
    -> failure: Recovery or human intervention
    -> targeted correction data
    -> retraining and evaluation
```

最终不以“机械臂偶尔成功一次”为目标，而以安全、可重复、可诊断、可量化、可从失败中恢复的完整系统为目标。

## 2. Overall Roadmap

### Phase 0 — Environment and reproducibility

**Learn**

- Conda environment 与系统 Python 的边界；
- package version、environment manifest、seed 和日志的作用；
- NVIDIA driver、CUDA runtime 和 CUDA Toolkit 的区别。

**Build**

- Conda `Robot` Python 3.11 仿真环境；
- NumPy、SciPy、Matplotlib、pytest、MuJoCo、Gymnasium；
- 可重建的 `environment.yml`；
- MuJoCo CPU/headless smoke test。

**Exit evidence**

- [x] `Robot` 环境存在且使用 Python 3.11；
- [x] 核心 Python packages 可以导入且无依赖冲突；
- [x] MuJoCo 运行 1000 steps，状态 finite 且结果 deterministic；
- [x] 环境配置已记录在 `environment.yml`；
- [ ] MuJoCo GUI 在宿主桌面可见并可正常运行；
- [ ] ROS 2 Jazzy 使用系统环境安装并通过基础 smoke test。

### Phase 1 — Minimal robotics foundations

**Learn**

- link、joint、DOF、revolute/prismatic joint；
- degree、radian、joint order、direction 和 limits；
- position、orientation、pose；
- world/base/tool/camera frames；
- rotation matrix 与 homogeneous transformation；
- Forward Kinematics；
- position control、control frequency、latency、timeout；
- observation、state、action 和 controller 的区别。

**Build**

- 2D/3D transform compose、inverse、point transform；
- 2-link arm Forward Kinematics；
- 简单离散 position-control loop；
- target、actual、error 曲线；
- degree/radian、frame direction、joint order、stale timestamp 的失败测试。

**Exit evidence**

- 能手算并用 NumPy 验证坐标变换；
- FK 在零位、边界和错误单位测试中表现符合预期；
- controller 能在限幅内收敛；
- 能定位并解释上述四类典型错误。

### Phase 2 — MuJoCo closed-loop simulation

**Learn**

- MJCF/URDF 的用途和边界；
- `qpos`、`qvel`、actuator、contact；
- physics timestep 与 control period；
- reset、observe、act、step、log 的闭环结构。

**Build**

- 单关节 position-control simulation；
- 2–3 DOF 简化机械臂；
- joint/velocity limits 与 safety stop；
- 固定 seed、扰动、延迟、噪声和 timeout；
- rollout log、控制曲线和短视频。

**Exit evidence**

- 闭环受扰动后重新收敛；
- 越界或 timeout 会安全停止；
- 日志包含 observation、action、timestamp、seed、stop reason；
- 同一 seed 可以复现轨迹。

### Phase 3 — ROS 2 and robot interfaces

**Learn**

- node、topic、publisher/subscriber；
- service、action、QoS；
- TF2、URDF、rosbag；
- timestamp、message frequency、latency 和 watchdog。

**Build**

```text
command publisher
    -> safety controller mock
    -> simulated joint
    -> joint state publisher
    -> logger / rosbag
```

**Exit evidence**

- 能从 command topic 追踪到 state feedback；
- 能测量频率、延迟和丢帧；
- rosbag replay 产生一致 observation；
- TF tree 只有一个根、无环，transform query 正确；
- action 可取消且 watchdog 对过期 command 生效。

### Phase 4 — Data pipeline and scripted demonstrations

**Learn**

- episode、trajectory、observation/action schema；
- camera/state synchronization；
- dataset version、split、normalization 和 audit；
- scripted policy 与 teleoperation data 的差异。

**Build**

- 明确的 observation/action schema；
- scripted pick-and-place demonstrations；
- episode recorder、loader 和 replay；
- 缺帧、不同步、越界、异常终止的数据检查；
- 固定的 train/validation/test split。

**Exit evidence**

- dataset 可以被记录、加载、回放和审计；
- schema 中单位、shape、range、order、timestamp 均明确；
- 数据错误会被测试主动发现，而不是在训练时才暴露。

### Phase 5 — Imitation learning baseline

**Learn**

- Behavior Cloning、covariate shift、closed-loop evaluation；
- training/validation loss 与真实 rollout success 的区别；
- checkpoint、config、seed 和 evaluation manifest；
- ACT 的 action chunking。

**Build**

1. 小型 BC baseline；
2. dataset -> train -> checkpoint -> rollout -> failure report；
3. 固定场景与固定 trial protocol；
4. pipeline 稳定后再训练 ACT baseline。

**Exit evidence**

- checkpoint 可以从 manifest 恢复；
- closed-loop rollout 有量化结果；
- 失败按 taxonomy 记录；
- 结果不是只依赖单次成功展示。

### Phase 6 — SO-101 hardware bring-up

**Learn**

- motor ID、direction、joint limit 和 calibration；
- serial/USB、camera、control frequency；
- leader/follower teleoperation；
- emergency stop 与真实硬件风险边界。

**Build**

1. 确认硬件型号和采购清单；
2. 建立真实 joint table；
3. 电机 ID、标定、软限位和急停；
4. 低速单关节测试；
5. leader/follower teleoperation；
6. top + wrist 双相机；
7. 小规模真实数据采集和回放审计；
8. ACT dry-run 与受控 rollout。

**Exit evidence**

- 急停和限幅经过实际测试；
- teleoperation 稳定且双相机数据同步；
- policy 输出先通过 offline replay 和 dry-run；
- 固定测试协议下有可重复的真实 baseline。

### Phase 7 — Failure-driven learning

**Learn**

- covariate shift 与真实失败状态；
- intervention/correction trajectory；
- 公平的数据预算和受控实验；
- failure taxonomy 与 uncertainty reporting。

**Main comparison**

- A：基础 demonstrations；
- B：基础数据 + N 条随机成功 demonstrations；
- C：基础数据 + N 条 failure-targeted corrections/interventions。

**Exit evidence**

- A/B/C 使用相同新增轨迹预算；
- 报告 overall/subgoal success、recovery rate、interventions、failure frequency；
- 报告 OOD 表现和单位新增数据收益；
- 保存多个 seed/批次及不确定性，而非只展示最好结果。

### Phase 8 — Long-horizon task, verifier and recovery

**Learn**

- task decomposition、state machine、memory；
- 独立 verifier 与 actor 自报成功的区别；
- retry、replan、recovery、human intervention；
- long-horizon error accumulation。

**Build**

```text
Planner -> Actor -> Controller -> Verifier
                    |              |
                    | failure      | success
                    v              v
              Recovery/Human   Task State update
```

**Exit evidence**

- 多物体有序任务可以从局部失败继续；
- Task State 只接受 verifier evidence 更新；
- recovery 和人工介入都有结构化日志；
- 使用固定 long-horizon protocol 报告结果。

### Phase 9 — Optional extensions and release

仅在主线稳定后考虑：

- SmolVLA 或其他 language-conditioned policy；
- Isaac 并行仿真、高保真传感或 domain randomization；
- Sim2Real 专项实验；
- cloud training/container；
- OOD、消融、复现报告、视频和 portfolio。

这些扩展不能替代前面的闭环、数据质量、安全和评估 Gate。

## 3. Current Plan

### Current phase

**Phase 1 — Minimal robotics foundations**，同时补齐 Phase 0 尚未完成的 GUI/ROS smoke。

### Current objective

理解并亲自实现：一个 action 如何经过 joint/frame 约定、限位、控制周期和物理系统，最终产生新的 observation。

### Do now — ordered task list

- [ ] **Task 1 — Joint/frame contract v0**
  - 建立 2-link arm joint table：name、order、type、unit、positive direction、min/max；
  - 定义 world、base、link、tool frames；
  - 写清楚 transform 记号表示“从哪个 frame 到哪个 frame”。

- [ ] **Task 2 — NumPy transform exercises**
  - 实现 rotation matrix；
  - 实现 homogeneous transform；
  - 实现 compose、inverse、point transform；
  - 测试 identity、90-degree rotation、inverse round trip；
  - 加入故意写反 frame direction 的失败测试。

- [ ] **Task 3 — 2-link Forward Kinematics**
  - 手算一个已知姿态；
  - 用 NumPy 实现 FK；
  - 测试 zero pose、90-degree pose、joint limits；
  - 加入 degree/radian 混用测试。

- [ ] **Task 4 — Discrete position-control loop**
  - 定义 target、actual、error、control period；
  - 加入 velocity/action limit；
  - 画 target/actual/error；
  - 注入 delay 和 stale timestamp；
  - 明确 convergence 与 safety stop 条件。

- [ ] **Task 5 — MuJoCo single-joint closed loop**
  - 将 Task 4 controller 接入 MuJoCo；
  - 完成 reset -> observe -> act -> limit -> step -> log；
  - 固定 seed，并保存 rollout evidence。

- [ ] **Task 6 — Complete environment smoke tests**
  - 在宿主桌面运行 MuJoCo GUI；
  - 单独安装 ROS 2 Jazzy，不装进 Conda `Robot`；
  - 运行 talker/listener 与 RViz/TF smoke。

### Current exit gate

全部满足后才进入 2–3 DOF MuJoCo closed-loop phase：

- [ ] 能解释 joint、pose、frame、action、controller；
- [ ] transform 与 FK tests 全部通过；
- [ ] 四类故意注入的错误会被测试发现；
- [ ] position loop 在正常条件收敛，在越界/超时时安全停止；
- [ ] MuJoCo single-joint rollout 可复现；
- [ ] 每项结果都有代码、测试、图或命令输出作为 evidence。

### Not now

当前不安装或开展：

- PyTorch 和正式 neural policy training；
- LeRobot `.[all]`；
- ACT、Diffusion Policy 或大型 VLA；
- Isaac Sim；
- CUDA Toolkit；
- 真实机械臂自动 rollout。

## 4. Study Record

每完成一项，在此追加记录。不要删除历史记录。

| Date | Phase / Task | What was learned | Evidence | Result / Problem | Next action |
|---|---|---|---|---|---|
| 2026-08-11 | Phase 0 — `Robot` environment | Conda isolation；最小 simulation packages | `environment.yml`；package import、pip check、MuJoCo 1000-step smoke | CPU/headless tests passed；GUI/ROS pending | Start Task 1 joint/frame contract |

## 5. How to Update This File

当一个任务完成后，按以下顺序更新：

1. 检查 exit evidence，不凭主观感觉标记完成；
2. 把对应 checkbox 从 `[ ]` 改为 `[x]`；
3. 在 Study Record 追加日期、学到的内容、证据和问题；
4. 若当前 phase 的 exit gate 全部通过，将 Current phase 推进一阶段；
5. 重写 Do now，使其只包含下一批最小、可验证任务；
6. 新发现的 blocker 写入 `BLOCKERS.md`，方向性变化写入 `DECISIONS.md`；
7. 不删除历史失败，不把计划任务写成已经完成的事实。

每次继续学习时，优先打开本文件的 **Current Plan** 和最新一条 **Study Record**，再决定下一步。

## 6. Related Project Documents

- `README_PLAN.md`：项目目标、阶段依赖和总 Gate；
- `01_LEARNING_MAP.md`：按知识依赖组织的学习地图；
- `04_ROS2_AND_ROBOTICS_FOUNDATION.md`：ROS 2 和机器人基础；
- `05_SIMULATION_STACK.md`：MuJoCo/Isaac 的职责；
- `09_BASELINE_POLICIES.md`：BC、ACT、Diffusion、VLA 层级；
- `16_EVALUATION_PROTOCOL.md`：正式评估规则；
- `20_REPRODUCIBILITY.md`：环境、数据、模型和实验身份；
- `24_CURRENT_MACHINE_AND_NEXT_STEPS.md`：当前机器边界和近期路线；
- `PROGRESS.md`：整个研究项目的恢复上下文；
- `BLOCKERS.md`：阻塞及已尝试方案；
- `DECISIONS.md`：方向性决定。
