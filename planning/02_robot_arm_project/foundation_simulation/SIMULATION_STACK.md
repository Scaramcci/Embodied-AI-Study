# Simulation Stack

## 选择原则

MuJoCo 是必需的学习与接口验证栈；Isaac Sim/Lab 是有明确规模或传感需求时的可选实验栈。仿真必须服务于闭环、数据或研究问题，不能因为画面真实而自动增加贡献。

| 栈 | 最适合 | 本项目角色 | 必需性 |
|---|---|---|---|
| MuJoCo | 轻量动力学、接触、简单控制、快速测试 | FK/控制、抓放、schema、BC/ACT 仿真 baseline、故障注入 | 必须 |
| Isaac Sim | 高保真场景、RTX RGB/depth、资产/相机交互调试 | 需要更复杂视觉、相机布局或传感随机化时使用 | 可选 |
| Isaac Lab | GPU 并行环境、RL/批量数据/评估 | 大规模 domain randomization、RL 或并行实验 | 可选且需明确假设 |

优先用 MuJoCo：机器人基础、简单 position controller、closed loop、reach/grasp/place、observation/action contract、sim demonstrations、快速回归和基础 ACT。值得引入 Isaac：GPU 并行环境显著减少批量实验成本；需要 RGB/depth sensor 或 domain randomization；需要更高保真碰撞/相机布置调试；研究设计明确依赖大规模仿真。

## Local GUI vs AutoDL headless

| 工作流 | 优势 | 局限 | 推荐设备 |
|---|---|---|---|
| Local interactive GUI | scene/camera/collision 调试即时；便于观察异常 | GTX1650 4GB 对 Isaac GUI 不合适 | MuJoCo 用 A；Isaac GUI 用未来 E |
| Remote/headless | 并行环境、RL、数据生成、batch evaluation；可弹性租 4090/A100 | 无本地交互；需离屏渲染、日志和资产同步 | AutoDL B/F |

Isaac 不必须本地运行。AutoDL 可以承担 headless Isaac、RL、parallel environments、data generation 和 batch evaluation；未来 M16 的主要增益是 GUI、scene/camera/collision 调试与较大模型真机本地推理。

## 接口一致性

两种 simulator 必须实现同一最小 contract：`reset(scene_config, seed)`、`observe()`、`step(action)`、`termination`、event log。关节顺序、单位、action 范围、相机命名、时间戳和成功谓词由 simulator-independent 配置定义；严禁为迁移静默改变 policy 输入。

## 验证与常见失败

- 验证：模型零位/轴向/限位、控制响应、相机外参、接触事件、固定 seed、real-time factor、跨 simulator schema。
- 失败：资产尺度错误、collision mesh 不合理、timestep/控制频率混淆、接触参数调到只适配单场景、headless 图像与 GUI 不一致、随机化覆盖测试集。
- 输出：资产来源/许可/版本、sim config、渲染/物理参数、已知差异、基准场景结果。

## Gate

### MuJoCo Gate

Entry：模型和 action contract 草案。Tasks：完成闭环、简单操作、数据记录、扰动/故障注入。Exit：固定评估场景可重复；动作限制生效；轨迹和视频可审计；能解释仿真与真机差异。

### Isaac Admission Gate

Entry：MuJoCo baseline 已稳定。Tasks：书面提出 Isaac 能改变的指标/吞吐/视觉假设，并估计资产迁移成本。Exit：小型试验显示附加价值才扩展；否则在 DECISIONS 记录不采用。Isaac 不是 Hardware Purchase Gate 前置。

