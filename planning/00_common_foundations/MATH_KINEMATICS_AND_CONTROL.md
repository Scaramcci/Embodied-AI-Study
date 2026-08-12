# 数学、运动学与控制

## 掌握层级

| 主题 | 要掌握的内容 | 论文中的用途 | 实操标准 |
|---|---|---|---|
| 向量与坐标系 | 点和向量的区别，坐标表达依赖 frame | 人体、相机、物体、机器人统一表达 | 手算并编程验证 transform |
| 旋转 | rotation matrix、quaternion、SO(3) 误差 | DexTele 的 quaternion loss，ObjRetarget 的腕部姿态 | 发现四元数顺序和符号等价问题 |
| 齐次变换 | compose、inverse、point transform | RGB-D 点云和机器人基座系对齐 | round-trip 误差接近数值精度 |
| FK | joint configuration 到 link/end-effector pose | 重定向 loss 和机器人执行 | 2-link 手算，多自由度调库后检查 |
| Jacobian/IK | 局部速度映射、可达性、多解与奇异 | 人体轨迹到机器人关节角 | 不可达目标显式失败，不返回假解 |
| 约束优化 | objective、bounds、soft penalty、regularization | joint limit、arm-plane、contact geometry | 能写出目标函数并做单项消融 |
| 轨迹 | position/orientation sequence、velocity、acceleration | 动作连续性和执行稳定性 | 画出轨迹并检测跳变 |
| 位置控制 | target/actual/error、频率、延迟、饱和 | 把优化轨迹变成可执行命令 | 简化闭环会收敛，过期命令会终止 |
| 力反馈/MPC | state、model、target、rolling optimization | DexTele 自适应抓取 | 先能解释信号流，暂不复现实机力控 |

## 建议的最小练习

1. 将一个相机坐标系中的手腕点变换到机器人基座系。
2. 对 2-link 手臂实现 FK 和数值 IK。
3. 对一段目标手腕轨迹求解关节序列，依次加入 joint limit 和 smoothness penalty。
4. 比较单帧求解与轨迹级求解的速度、加速度和关节跳变。

## 只需概念理解

- 完整刚体动力学推导；
- torque/impedance 内环实现；
- 通用非线性 MPC 求解器；
- 多指接触力学的完整接触模型。

当小型实验确实需要时再加深。
