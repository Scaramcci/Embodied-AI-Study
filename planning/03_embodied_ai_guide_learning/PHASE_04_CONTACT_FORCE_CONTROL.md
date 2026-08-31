# Phase 4：手—物接触、灵巧手与力调节

> 状态：已完成（2026-08-31）  
> 前置条件：Phase 3 动作重定向与轨迹优化 Gate 通过  
> 优先级：高  
> 建议节奏：3 个核心单元，每单元 60–90 分钟  
> 论文出口：读懂 ObjRetarget 的多面体接触几何与 DexTele 的目标力/滚动优化闭环

## 1. 阶段核心问题

腕部轨迹正确以后，机器人怎样在接触阶段保持有意义的手—物局部几何，并根据目标抓取力持续调整手指命令？

```text
contact event + hand keypoints + object cloud
    -> contact region and representative contact point
    -> palm / fingertip / neighbor / object polyhedral unit
    -> object-relative geometric constraints
    -> contact-phase arm/hand scheduling
    -> target force prior + angle-force surrogate
    -> rolling command refinement and force evaluation
```

始终区分：

| 层级 | 回答的问题 |
|---|---|
| contact event | 当前是否进入或离开接触？ |
| contact point/region | 哪根手指在物体表面哪里接触？ |
| contact geometry | 掌心、指尖和接触点怎样相对排列？ |
| contact force | 接触力大小和方向是什么？ |
| friction/dynamics | 接触后是否会滑动、滚动或失稳？ |

## 2. 与论文的直接对应

### ObjRetarget

- 从五指尖到物体点云的邻近关系提取逐指接触区域 `C_f`；
- 用区域质心 `c_f` 代表接触点，降低单个深度点噪声的影响；
- 每根接触手指构造四顶点单元：palm、当前 fingertip、相邻 fingertip、object contact point；
- 多个局部四面体组成 polyhedral cluster；
- edge 与 hand-local relative pose loss 保留局部接触结构和操作语义；
- non-contact 使用初始化手部轨迹，contact 时切换到几何优化轨迹；
- 本阶段做方法级简化复现，不声称复现完整作者系统。

### DexTele

- VLM 根据物体类别提供目标抓取力先验；
- 历史数据 `(command angle, feedback angle, force)` 训练角度—力预测模型；
- 在线阶段优化新关节命令，使预测力接近目标力，同时惩罚相对上一命令的过大变化；
- 滚动执行形成 `measure/estimate -> optimize -> command -> feedback` 闭环；
- 本阶段使用可微合成 surrogate，不调用 VLM、不连接真实力传感器或灵巧手。

## 3. 学习取舍

### 必学并实验

- contact region、区域质心与单点最近邻的差别；
- palm + current fingertip + adjacent fingertip + contact point 四面体；
- pairwise distance/edge、hand-local relative pose 与 global pose 的关系；
- 为什么局部几何比直接复制人体手指角更适合跨形态重定向；
- contact/non-contact phase 切换与 arm/hand 解耦；
- force target、measured/estimated force、command/feedback angle；
- surrogate model、rolling horizon/online update 与 command smoothness；
- force error、overshoot、oscillation、command change 和稳定时间。

### 概念 + 一个例子

- 摩擦锥、法向/切向力、滑移条件；
- position/force/impedance control 的角色差异；
- MPC 的预测、代价、滚动执行基本结构；
- VLM 目标力只是语义先验，不是安全保证；
- 双臂/双手统一 scheduler 的 phase 和 timestamp 接口。

### 暂不展开

- 完整接触动力学、互补约束与高保真摩擦模型；
- 灵巧手机械结构、触觉阵列、电机和力传感器制作；
- 真机阻抗/力控调参和安全认证；
- 完整非线性 MPC 推导；
- VLM 部署、prompt benchmark 或大模型训练；
- 真实双臂碰撞规划与 ROS 控制系统。

## 4. 环境与统一接口

继续使用 `eai-retarget`：NumPy、SciPy、Matplotlib、Open3D、pytest。P4-3 的简化 surrogate 使用 NumPy/SciPy；只有官方 DexTele 复现才在 `eai-dextele-repro` 中安装 PyTorch/PyG。

统一接口：

```text
timestamp                    [T]           s
hand_keypoints_world         [T,6,3]       palm + five fingertips; m
object_cloud_world           [T,P,3]       m
contact_event                [T,5]         bool
contact_region_mask          [T,5,P]       bool or sparse indices
contact_point_world          [T,5,3]       region centroid; m
hand_R_world / world_R_hand  [T,3,3]
polytope_vertices            [T,5,4,3]
force_target                 [T,5]         declared force unit
force_estimated/measured     [T,5]
hand_command/feedback_q      [T,N_hand]    rad
phase                        [T]           approach/contact/manipulate/release
```

接触点无效时必须使用 valid mask，不能用 `[0,0,0]` 假装接触世界原点。

## 5. 三个核心单元

### P4-1：Contact region 与局部多面体几何

核心问题：怎样把“指尖足够近”升级为可跨全局位姿比较的局部接触结构？

实验：

1. 从物体表面点云中提取每根接触手指附近半径内的 `C_f`；
2. 计算质心 `c_f`，比较单最近点与局部区域；
3. 构造 palm、fingertip、neighbor fingertip、`c_f` 四顶点单元；
4. 计算六条边、hand-local contact coordinate 和基本退化检查；
5. 对整组手/物施加相同刚体变换，验证 pairwise length 和 local pose 不变；
6. 单独扰动指尖/接触点，验证几何 loss 明显增加。

产物：polyhedral cluster 数组、局部/世界可视化、不变量与畸变对照报告。

通过条件：能说明 global rigid motion 为什么不应改变接触语义，以及局部几何为何仍能检测抓取结构被破坏。

### P4-2：接触阶段与 arm/hand 同步

核心问题：为什么同一个优化目标不应从 approach 一直使用到 release？

实验：

- 建立 `approach -> contact -> manipulate -> release` 状态机；
- non-contact 输出初始化 hand retargeting；contact/manipulate 输出 geometry-refined command；
- arm 始终遵循宏观轨迹，但接触阶段降低某些拟人先验权重；
- 注入 contact threshold chatter 和 timestamp offset；
- 使用 hysteresis/minimum dwell time 避免频繁切换。

产物：phase、active controller、切换次数和错误调度图。

### P4-3：目标力与滚动调节

核心问题：怎样根据目标力和当前反馈逐步修改手指命令，同时避免过冲与振荡？

实验：

1. 用一个物体类别到目标力的固定表模拟 VLM 先验；
2. 构造/拟合简化 angle-command + angle-feedback -> force surrogate；
3. 每个控制周期优化下一命令：

```text
||M(command, feedback)-force_target||²
+ lambda ||command-command_prior||²
```

4. 只执行第一步并获取新反馈，再滚动求解；
5. 比较无调节、弱正则、合理正则和过强正则；
6. 记录 force error、overshoot、oscillation、command step 与 settle time。

边界：若使用随机森林，不能无说明地假定它可直接提供普通梯度；教学实验使用明确可微 surrogate，论文代码审计时再核对实际实现。

## 6. 阶段 Gate

- [x] 能区分 contact event、region/point、geometry、force 和 friction；
- [x] 能从点云邻域计算代表接触点并说明质心的优缺点；
- [x] 能构造 palm/fingertip/neighbor/contact 四顶点单元；
- [x] 能解释 pairwise geometry 与 hand-local relative pose 的不变性；
- [x] 能指出世界系 edge vector 并不天然对全局旋转不变；
- [x] 能解释 arm/hand 解耦与 phase scheduler；
- [x] 能写出 target force、surrogate、command regularization 和滚动反馈链；
- [x] 能区分几何接触保持与真实抓取稳定性；
- [x] 能映射到 ObjRetarget hand loss 与 DexTele force adaptation，并明确简化边界。

通过后进入压缩 Phase 5，并继续 DexTele 小规模训练复现。

## 7. 当前入口

Phase 4 Gate 已通过；下一步写阶段总结并进入压缩 Phase 5。
