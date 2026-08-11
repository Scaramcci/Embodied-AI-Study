# Progress

此文件是会话中断后的恢复入口。只记录已验证事实；每完成一个子任务立即更新，不用截止日期或工期描述。

## Current Phase

G0 — 基础环境与机器人概念（M0 盘点/设计完成，环境尚未实施）

## Current Objective

建立隔离的 ROS 2 Jazzy 与 MuJoCo/ML 环境，运行最小 smoke tests，然后开始 joint/frame/transform 实操。

## Completed

- 创建项目规划控制面与 G0–G8 dependency gates。
- 定义主研究问题、最终架构、failure-driven A/B/C 对照和 Hardware Purchase Gate。
- 将现有 `基础知识补充/` 资料链接为概念预读。
- 完成 M0 只读机器盘点：Ubuntu 24.04.4、i7-9750H、16GB RAM、452GB 可用磁盘、GTX 1650 4GB。
- 在宿主机验证 NVIDIA driver 580.173.02 与 `nvidia-smi` 正常；确认沙箱内 GPU/USB 检测不可靠。
- 形成系统 ROS 2 Python 与 Conda simulation/ML Python 的环境边界、版本策略和 smoke-test contract。

## In Progress

- 无。

## Blocked

- 无。SO-101 尚未确认购买，不阻塞 PRE-HARDWARE 主线。

## Next Actions

1. 按 `24_CURRENT_MACHINE_AND_NEXT_STEPS.md` 创建 Python 3.11 `embodied-sim` 环境并保存 exact manifest。
2. 运行 MuJoCo headless/GUI 和 transform smoke tests。
3. 使用系统 Python 路径安装并验证 ROS 2 Jazzy、RViz、TF 和 talker/listener。
4. 草拟 v0 joint/frame contract，并完成 transform/FK 数值测试。

## Important Results

- 尚无实验结果。

## Known Problems

- 硬件购买状态、确切 SO-101 Pro 套件版本和相机型号尚未确认；到 Hardware Purchase Gate 再锁定。

## Files Modified

- `planning/*.md`（项目规划文档）

## Experiments Run

- 无。本轮只做规划。

## Hardware Status

- 已验证可用：Ubuntu 24.04.4 旧游戏本，i7-9750H、16GB RAM、GTX1650 4GB、NVIDIA driver 580.173.02。
- 计划/未确认：SO-101 Pro leader/follower、双 RGB camera、M16 RTX4090 Laptop。
- 云端：可按需使用 AutoDL；本轮未使用。

## Dataset Status

- 未创建、未采集。

## Model Status

- 未下载、未训练、无 checkpoint。

## Last Stable Checkpoint

- 不适用；当前稳定点是规划文档集。

## Next Recommended Action

执行 `24_CURRENT_MACHINE_AND_NEXT_STEPS.md` 的 Stage A：建立最小环境并跑 smoke tests。
