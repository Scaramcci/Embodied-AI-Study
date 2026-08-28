# 学习进度

## Unit 1：关节、连杆与运动链

状态：已完成

已完成：

- PyBullet GUI smoke test；
- 成功加载 `kuka_iiwa/model.urdf`；
- 确认 7 个可动关节均为 revolute joint；
- 确认 joint 0 的 child link 为 `lbr_iiwa_link_1`；
- 确认末端为 `lbr_iiwa_link_7`，link index 为 6。

- 已通过滑块确认：joint 1 影响 link 1～7，joint 4 影响 link 4～7，joint 7 只影响 link 7；
- 已能根据运动链判断 joint 5 影响 link 5～7。

## Unit 2：坐标系、旋转表示与齐次变换

状态：已完成

已完成：

- 读取末端 position、quaternion、Euler RPY 与齐次变换；
- 理解 `q -> FK -> wrist pose`；
- 区分位置误差和姿态误差；
- 使用独立阈值与归一化目标评估位姿误差。

## Unit 3：IK、可达性与 FK 回代

状态：已完成

已完成：

- 比较 position-only IK 与完整位姿 IK；
- 使用 FK 回代检查 position error 和 orientation error；
- 检查 joint limits 与 minimum limit margin；
- 理解 `restPoses` 对冗余 IK 解的软偏好作用；
- 比较正常、工作空间边界和不可达目标；
- 确认 IK 返回数组不等于求解成功。

## Unit 4：从单点 IK 到参考腕部轨迹

状态：已完成

已完成：

- 生成 121 帧合成腕部轨迹并逐帧求 IK；
- 比较独立求解和上一帧连续性参考；
- 计算相邻帧关节变化；
- 构造越过工作空间边界的轨迹；
- 显式保存失败帧、原始索引和 FK 误差；
- 理解单帧成功不保证整段轨迹连续或可执行。

## Unit 5：平滑、位置控制与时间指标

状态：已完成

已完成：

- 比较原始与 Savitzky–Golay 平滑轨迹；
- 固定 60 Hz 轨迹采样和 240 Hz 物理 timestep；
- 计算 FK 误差、速度和加速度；
- 使用 position control 记录 target/actual joint state；
- 比较 2 秒正常执行与 0.5 秒快速执行；
- 区分运动学精度、时间平滑性和控制跟踪精度。

## Unit 6：论文导向综合实验

状态：已完成

已完成：

- 汇总输入约定、IK/FK、失败、平滑和控制指标；
- 重新检查 URDF joint limits；
- 生成 Markdown 综合报告和 JSON 指标；
- 完成 Phase 1 阶段总结与 Gate 检查。

## Phase 1

状态：已完成（Gate 通过）

阶段总结：`PHASE_01_SUMMARY.md`
