下一阶段学习计划
========

> 更新日期：2026-08-12
> 
> 当前范围：只学习 `00_common_foundations` 和 `01_teacher_papers`；`02_robot_arm_project` 继续暂停。

1\. 当前结论
--------

*   当前尚未开始系统学习公共基础，也尚未开始 DexTele、ObjRetarget 的第一轮阅读。
*   目前只做过环境配置。由于仓库中还没有版本清单和 smoke-test 证据，F0 暂记为“部分完成、待验证”，不直接标记完成。
*   当前先验证已有环境，然后从 **F1 空间几何** 正式开始；之后依次学习运动学、感知表示、优化轨迹、控制和实验方法。
*   公共基础达到最低 gate 后，再开始两篇老师论文的第一轮阅读；论文理解完成后才进入 E0 合成轨迹实验。
*   不学习 ROS 2、机械臂装配、串口、电机、LeRobot、ACT、实机标定和 sim-to-real。这些属于暂停的第三部分。

2\. 当前状态
--------

状态只按仓库中已有证据填写；没有代码、笔记、图表或可重复命令时，不标记完成。

模块

当前状态

已有信息

还缺的完成证据

F0 环境与工具

部分完成，当前先验证

已配置过环境，但未记录验证证据

manifest、CPU/GPU/优化/PyBullet smoke test

F1 空间几何

未开始，F0 后立即学习

只有计划，没有学习产物

transform 单测、frame 图、四元数错误案例

F2 运动学与重定向

待开始

已定义最小练习

2-link FK、数值 IK、可达/不可达测试

F3 感知与表示

待开始

已限定肩-肘-腕最小输入

skeleton 数据、可视化、字段说明

F4 优化与轨迹

待开始

已确定三类 loss

loss 曲线、轨迹图、消融表

F5 控制概念

待开始

已限定为概念和简化仿真

控制曲线、DexTele 信号流图

F6 论文与实验方法

待开始

已有指标和记录模板

指标单测、实验卡、方法图

P0-P3 论文理解

未开始

只有论文 PDF 和阅读指南

阅读笔记、对比表、方法图、符号/loss 清单

P4 小型实验

未开始

实验日志为空

E0 可重复结果，之后再决定是否做 E1

SO-101 项目

暂停

规划保留

当前不产生待办

3\. 所有必学基础知识
------------

### F0：环境、工具与可复现记录

目标：知道代码究竟在哪个 Python、PyTorch 和 CUDA 组合中运行，并能复现一次结果。

学习内容：

*   Linux：路径、权限、进程、环境变量、标准输入输出、常用诊断命令；
*   Conda：环境创建、激活、导出、删除，`python`/`pip` 所属环境检查；
*   Git：commit、branch、diff、dirty working tree、实验对应的 commit；
*   GPU 软件栈：driver、CUDA runtime、PyTorch CUDA build 三者的区别；
*   基本库：NumPy、SciPy、PyTorch、Matplotlib、pytest、PyBullet；
*   数据交换：NPZ/HDF5 的数组、字段、dtype、shape 和元数据。

实操与验收：

*   建立独立的 `retarget` 环境，不与旧版 FrankMocap 混装；
*   保存 OS、GPU/driver、Python、PyTorch/CUDA 和主要包版本；
*   跑通 NumPy 数组、PyTorch CPU/GPU tensor、SciPy 最小二乘；
*   跑通 PyBullet headless 加载模型；
*   用 pytest 跑通至少一个单元测试；
*   保存 exact command、输出路径、git commit 和 dirty diff。

完成标准：换一个终端，按记录的命令仍能得到相同 smoke-test 结果。

### F1：线性代数、旋转与坐标系

目标：能够无歧义地把人体、相机、物体和机器人数据放到同一坐标系。

学习内容：

*   标量、向量、矩阵、范数、点积、叉积；
*   点与方向向量的区别；world/camera/body/robot frame 的含义；
*   rotation matrix：正交性、行列式、复合顺序；
*   Euler angle 的约定与奇异问题，只需会识别，不用作为核心表示；
*   quaternion：归一化、逆、乘法、`xyzw`/`wxyz`、`q` 与 `-q` 等价；
*   SO(3) 上的旋转误差；
*   homogeneous transform：旋转和平移、复合、求逆、点变换；
*   单位与约定：m/mm、degree/radian、左乘/右乘、行向量/列向量。

实操与验收：

*   NumPy 实现并测试 `compose(T_ab, T_bc)`、`inverse(T)`、`transform_points(T, p)`；
*   验证 `T @ inverse(T)` 和 point round trip 的误差接近数值精度；
*   将相机系中的肩、肘、腕点变换到机器人基座系；
*   构造 `xyzw`/`wxyz`、degree/radian 和乘法顺序错误，并解释错误结果；
*   画一张包含 camera/world/robot frame 的坐标关系图。

完成标准：看到任意 pose 数据时，先问出 frame、单位、旋转表示、乘法约定和时间戳。

### F2：机器人运动学与人体到机器人重定向

目标：理解人体关键点为什么不能直接复制成机器人关节角，并能得到合法关节轨迹。

学习内容：

*   joint、link、DoF、configuration、end effector、joint order；
*   revolute/prismatic joint 与 joint limit；
*   FK：关节角到 link/end-effector pose；
*   Jacobian：关节速度到末端速度的局部映射；
*   IK：解析法与数值法的用途、初值、多解和局部最优；
*   workspace、不可达目标、冗余自由度、奇异位形；
*   人与机器人的尺寸、拓扑、轴向、DoF 差异；
*   尺度归一化、root/frame 对齐、末端目标与肘部/arm-plane 约束。

实操与验收：

*   手算并用 NumPy 实现平面 2-link FK；
*   用数值优化反解 2-link IK，并验证 FK(IK(target))；
*   明确区分可达、边界和不可达目标，不用错误解冒充成功；
*   对一个 3-6 DoF 仿真机械臂求解目标末端轨迹；
*   加入 joint bounds，统计 joint-limit violation；
*   将归一化肩-肘-腕轨迹映射为末端和肘部约束并可视化。

完成标准：能解释同一末端目标为何可能有多个关节解，以及初值、冗余和 joint limit 如何改变结果。

### F3：人体、相机、深度、物体和图表示

目标：读懂两篇论文中的输入与中间表示，并为 E1 准备规范的数据接口。

学习内容：

*   2D keypoint、3D keypoint、置信度、遮挡、丢帧与时间戳；
*   skeleton graph：node、edge、拓扑、位置/旋转/相对几何 feature；
*   camera intrinsics：`fx, fy, cx, cy` 与 pinhole projection；
*   depth 的单位、无效值、RGB-depth 对齐；
*   depth pixel 到 camera-frame 3D point，再到 world/robot frame；
*   point cloud 的 frame、采样与基本可视化；
*   object pose：位置、旋转、目标 ID 和 tracking confidence；
*   contact event：距离/传感阈值与进入、离开接触时刻；
*   FrankMocap/SLAHMR 在论文系统中的位置，只要求理解接口与限制。

实操与验收：

*   定义最小 skeleton 文件：`positions[T,J,3]`、joint names、frame、unit、timestamps、confidence；
*   绘制肩-肘-腕 skeleton sequence，并标出丢帧；
*   画出 skeleton graph，说明 node/edge feature；
*   用给定 intrinsics 将少量 depth pixel 反投影为三维点；
*   将三维点从 camera frame 变换到 world/robot frame；
*   解释 DexTele 和 ObjRetarget 分别需要哪些感知输入。

完成标准：任何数组都能说清 shape、字段、frame、unit、timestamp 和 confidence，缺一项则不进入优化。

### F4：最小二乘、约束优化与轨迹

目标：把重定向写成可检查的优化问题，并用消融判断每个约束的作用。

学习内容：

*   objective/residual、least squares、加权 loss；
*   hard constraint、bounds 与 soft penalty 的区别；
*   regularization、权重尺度、归一化和 trade-off；
*   task tracking loss、orientation loss、joint-limit loss；
*   velocity/acceleration smoothness loss；
*   arm-plane/肘部拟人约束；
*   frame-wise IK 与 trajectory optimization 的区别；
*   优化初值、收敛状态、失败检测和随机种子。

建议先实现：

\[
\\min_{q_{1:T}}
\\sum_t w_p\\lVert FK_p(q_t)-p\_t^\*\\rVert^2

*   w_e\\lVert e(q_t)-e\_t^\*\\rVert^2
*   w_v\\lVert q_t-q\_{t-1}\\rVert^2
*   w_a\\lVert q_t-2q_{t-1}+q_{t-2}\\rVert^2
*   L_{limit}(q_t)
    \]

实操与验收：

*   先只做 tracking baseline；
*   依次加入 joint bounds、velocity smoothness、acceleration smoothness、arm-plane prior；
*   固定输入、机器人模型、seed 和指标，每次只消融一个因素；
*   比较 frame-wise IK 和 trajectory optimization；
*   输出 loss curve、关节位置/速度/加速度图和消融表；
*   记录失败帧、solver status 和不可达目标，不静默丢弃。

完成标准：能从 tracking、平滑性和可执行性三个方面解释权重变化，而不是只报告总 loss 更小。

### F5：控制概念

目标：理解“算出目标轨迹”与“机器人实际跟踪轨迹”不是同一件事，并能读懂 DexTele 的控制部分。

学习内容：

*   position target、actual state、tracking error 和 feedback loop；
*   control frequency、sampling interval、latency、jitter；
*   velocity/acceleration/position limits、saturation 和 stale command；
*   open loop 与 closed loop；
*   force feedback 的信号流、目标力和实测力；
*   MPC 的 state、model、horizon、cost、constraint 和滚动求解；
*   本阶段只做概念和简化仿真，不做 torque/impedance 内环或通用非线性 MPC。

实操与验收：

*   实现一个简化 position-control loop，记录 target/actual/error；
*   比较不同频率、延迟和饱和条件下的跟踪误差；
*   对过期命令和越界目标显式拒绝；
*   画出 DexTele 中 VLM target force、force model、feedback 和 rolling optimization 的信号流。

完成标准：能指出论文中的 retargeting、trajectory optimization 和 low-level control 各自解决什么问题。

### F6：指标、论文阅读与实验方法

目标：把论文理解变成可验证的实验，不让指标定义或实验记录破坏结论。

学习内容：

*   research question、hypothesis、baseline、ablation、trial unit；
*   primary/secondary metric 和实验前决策规则；
*   MPJPE：root alignment 与 scale normalization；
*   quaternion distance：顺序、归一化与符号等价；
*   velocity/acceleration error：真实时间间隔与噪声敏感性；
*   joint-limit violation 和 task success 的分母；
*   reproducibility：配置、seed、代码版本、环境和失败记录；
*   事实、论文主张和个人推断分开记录。

实操与验收：

*   自己实现 MPJPE、quaternion distance、VE、AE、joint-limit violation；
*   为每个指标写手工可计算的小样例和 pytest；
*   整理 DexTele/ObjRetarget 的 input-module-loss-output-evaluation 对比表；
*   将已读论文整理成两张方法流程图与一张符号/loss 表；
*   在运行 E0 前填写 Question、Hypothesis、primary metric 和 decision rule；
*   使用 `01_teacher_papers/EXPERIMENT_LOG.md` 保存有效和失败运行。

完成标准：相同输入和配置可重复得到相同结果，指标定义足以让别人独立重算。

4\. 推荐学习顺序
----------

以下按 **26 个学习单元** 安排；每单元建议 2-3 小时。若每天时间不同，保持顺序，不强行按自然日推进。单元 1 是检查已有环境，不要求重新安装一遍。

单元

学习与实操

当次必须留下的产物

1

F0：核对已有 Conda、Python、Git、CUDA/PyTorch 环境

environment manifest

2

F0：NumPy/SciPy/PyTorch/PyBullet/pytest smoke

命令与完整输出

3

F1：向量、frame、旋转矩阵

手算笔记与数值测试

4

F1：四元数、SO(3) 误差

quaternion 单测

5

F1：齐次变换、复合、求逆

transform 单测与 frame 图

6

F2：joint/link/DoF、2-link FK

FK 代码与手算对照

7

F2：Jacobian、数值 IK

可达/不可达测试

8

F2：冗余、奇异、joint limit

多解和边界可视化

9

F2：人体-机器人差异与归一化

肩-肘-腕映射结果

10

F3：keypoint、时间戳、confidence、skeleton

最小 NPZ/HDF5 schema

11

F3：投影、深度、点云、object pose

反投影与 frame 变换测试

12

F3：skeleton graph 与两篇论文接口

graph 图与字段说明

13

F4：least squares、bounds、penalty

单帧 tracking baseline

14

F4：整段轨迹、平滑项

关节/速度/加速度图

15

F4：arm-plane、权重和消融

固定设置的消融表

16

F5：位置闭环、频率、延迟、饱和

简化控制曲线

17

F5：force feedback 与 MPC 概念

DexTele 控制信号流图

18

F6：五类指标及测试

metrics + pytest 输出

19

P0：两篇论文只看摘要、总图、主表和实验设置

两张粗粒度流程图、术语清单

20

P1：DexTele 输入、骨架图、SAG-GCN 与输出

模块图和符号表

21

P1：DexTele losses、latent optimization、力控与实验

loss/指标表、复现缺口

22

P2：ObjRetarget 输入、初始重定向与 arm constraints

模块图和符号表

23

P2：ObjRetarget object/contact geometry、优化与实验

loss/指标表、复现缺口

24

P3：对比两篇论文并界定最小问题

一页方法对比表

25

F6/P4：写 E0 hypothesis、baseline、指标和决策规则

完整 E0 实验卡

26

P4：运行 E0 合成轨迹

可重复结果、失败记录、下一决策

依赖关系：`F0 -> F1 -> F2 -> F4 -> 论文精读 -> E0` 是主路径；F3、F5、F6 可与基础主路径交替，但不能跳过 P0-P3 直接声称读懂论文。

5\. 当前计划：先完成单元 1-5
------------------

当前只展开最近五个学习单元。先验证已经配好的环境，再进入真正的基础学习；通过 F1 gate 后，再把 F2 拆成当周任务。

### 第 1 次：验证已有环境

*   找到并激活已经配置的环境，不重复安装；
*   记录环境名称、Python 路径、Python/Conda、Git、OS 和 GPU/driver；
*   记录 PyTorch 版本、PyTorch CUDA runtime 与 GPU 是否可用；
*   创建 environment manifest，补全本机与云端分工。

停止条件：已有环境的实际状态可追溯；若缺包，只记录缺口并在第 2 次按需补齐。

### 第 2 次：环境 smoke test

*   运行 NumPy、SciPy least-squares、PyTorch CPU/GPU；
*   运行 PyBullet headless；
*   建立 pytest 入口；
*   把 exact command 和输出保存下来。

停止条件：失败项有明确错误记录；未跑通的项不能标“环境完成”。

### 第 3 次：旋转矩阵与 frame

*   手算一次二维/三维旋转；
*   编写旋转矩阵合法性检查；
*   区分点、方向和不同 frame 中的坐标表达；
*   画 camera/world/robot frame 草图。

停止条件：能解释 `R_ab` 的方向和复合顺序。

### 第 4 次：四元数与姿态误差

*   实现或调用 quaternion normalize/inverse/multiply；
*   验证 `q` 与 `-q` 表示同一旋转；
*   比较 `xyzw` 与 `wxyz` 错误；
*   实现最小 quaternion distance 测试。

停止条件：180°、零旋转、未归一化和符号翻转案例均有测试。

### 第 5 次：齐次变换综合

*   实现 transform compose/inverse/point transform；
*   测试 round trip；
*   把一组肩-肘-腕点从 camera frame 变换到 robot frame；
*   汇总 F1 的单测、图和错误案例。

F1 gate：所有测试通过，且数据约定中明确 frame、unit、rotation convention 和 timestamp。

6\. 每次学习的固定工作流
--------------

1.  开始前写本次问题和唯一的完成条件。
2.  理论学习不超过当次时间的三分之一，随后立刻做最小代码或手算验证。
3.  保存代码、输入、命令、输出图和失败信息。
4.  用测试或数值对照判断是否完成，不能用“视频看完”代替证据。
5.  在本文件状态表中更新进度，并写下一次唯一优先任务。

建议的单次记录：

```
Date / Session:
Question:
What I learned:
Command / Code:
Evidence path:
Result / Failure:
Remaining confusion:
Next single action:

```

7\. 基础阶段与论文阶段总验收
----------------

### 公共基础 gate

满足以下条件后，才把公共基础标记为“足以开始论文精读”，不要求所有主题达到专家水平：

*   能验证坐标变换的复合、求逆和 round trip；
*   能实现 2-link FK，并为仿真机械臂求解可达目标；
*   能显式识别不可达目标、joint-limit violation 和 solver failure；
*   能解释人体骨架不能直接当作机器人关节角；
*   能写出 tracking + joint limit + smoothness + optional arm-plane 的优化问题；
*   能独立计算并测试 MPJPE、姿态误差、VE 和 AE；
*   能说明 position control、force feedback 与 MPC 的边界；
*   能用统一模板记录环境、输入、配置、结果、失败和下一决策。

### 论文理解 gate

*   DexTele 有完整的 input -> representation -> retargeting -> control -> evaluation 流程图；
*   ObjRetarget 有完整的 input -> representation -> optimization -> control -> evaluation 流程图；
*   两篇论文分别有符号表、loss/constraint 表、指标表和复现缺口；
*   能用自己的话在 5 分钟内分别讲清两篇论文，不照读摘要；
*   能解释两篇论文的共同问题、关键差异及 E0 保留/删掉的部分；
*   一页方法对比表已经完成，并能据此写出 E0 实验卡。

只有两个 gate 都通过后，才执行 `01_teacher_papers/MINIMAL_REPRODUCTION.md` 的 E0。E0 完成后再决定是否接入 E1 已提取人体轨迹，不自动启动 SO-101 项目。