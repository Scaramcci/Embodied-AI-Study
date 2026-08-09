# Progress

此文件是会话中断后的恢复入口。只记录已验证事实；每完成一个子任务立即更新，不用截止日期或工期描述。

## Current Phase

G0 — 基础环境与机器人概念（规划完成，尚未开始实现）

## Current Objective

完成只读开发环境/工作区盘点，并为第一个最小机器人表示与 MuJoCo 闭环练习确定输入、输出和验证，不安装大型依赖。

## Completed

- 创建项目规划控制面与 G0–G8 dependency gates。
- 定义主研究问题、最终架构、failure-driven A/B/C 对照和 Hardware Purchase Gate。
- 将现有 `基础知识补充/` 资料链接为概念预读。

## In Progress

- 无。

## Blocked

- 无。SO-101 尚未确认购买，不阻塞 PRE-HARDWARE 主线。

## Next Actions

1. 阅读 `README_PLAN.md`、`03_PRE_HARDWARE_SIMULATION_PLAN.md` 的 M0–M4、`04_ROS2_AND_ROBOTICS_FOUNDATION.md`。
2. 只读记录 Ubuntu/GPU/driver/Python/Git/磁盘与当前仓库状态。
3. 提出最小环境版本矩阵和 smoke-test 规范；评审后再安装小型依赖。
4. 草拟 v0 joint/frame/observation/action contract，暂不创建大规模代码骨架。

## Important Results

- 尚无实验结果。

## Known Problems

- 硬件购买状态、确切 SO-101 Pro 套件版本和相机型号尚未确认；到 Hardware Purchase Gate 再锁定。

## Files Modified

- `planning/*.md`（项目规划文档）

## Experiments Run

- 无。本轮只做规划。

## Hardware Status

- 已知可用：旧游戏本，Ubuntu 可安装，16GB RAM，GTX1650 4GB。
- 计划/未确认：SO-101 Pro leader/follower、双 RGB camera、M16 RTX4090 Laptop。
- 云端：可按需使用 AutoDL；本轮未使用。

## Dataset Status

- 未创建、未采集。

## Model Status

- 未下载、未训练、无 checkpoint。

## Last Stable Checkpoint

- 不适用；当前稳定点是规划文档集。

## Next Recommended Action

执行 M0 的只读环境盘点，并产出环境设计与 smoke-test 清单。

