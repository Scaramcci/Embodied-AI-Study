# Reproducibility

可复现的最小单位不是一条命令，而是 `code + environment + config + dataset + checkpoint + hardware/calibration + evaluation manifest`。

## 身份链

每个 experiment ID 绑定：Git commit/dirty status、branch、environment lock/container digest、CUDA/driver/OS、dataset version/hash、split version、model/checkpoint hash、merged config、seed、hardware/camera/calibration IDs、evaluation protocol/trial manifest、输出路径。任何缺项都在 EXPERIMENT_LOG 标为未知，不能事后编造。

## Git 与变更

- 主分支保持可运行；功能/实验使用短分支，提交聚焦一个可验证变化。
- 代码、配置、schema 和小型测试进 Git；数据/权重只存 manifest、hash 和可恢复位置。
- 提交前运行与风险相称的 unit/replay/simulation/dry-run tests。
- 核心研究问题、dataset、observation/action、模型族、正式 protocol 的变更先写 DECISIONS。
- 不用未记录的本地修改生成正式结果；若 unavoidable，保存 diff artifact。

## Environment / Docker

先用锁定 Python/系统依赖实现本地开发；容器用于云训练/headless simulator 和跨机复现。USB、相机、低延迟控制的容器化需验证 device/permission/clock，不为“统一”增加真机风险。保存构建文件和 image digest，禁止只写 `latest`。

## Seeds 与不确定性

固定 seed 用于 debug/replay，不等于结果稳定；正式训练记录多个 seed 或数据抽样变化。仿真记录 scene seed；真机记录 trial manifest 和实际 reset 偏差。确定性开关及性能代价要记录。

## Dataset / checkpoint

Dataset immutable；清洗、重标、加入 corrections 都产生新版本和 parent lineage。Checkpoint manifest 含模型 config、训练 dataset、normalization、best-selection rule、指标和 hash；禁止文件名 `best_final.pt` 作为唯一身份。

## M16/云迁移 Gate

在冻结的小 episode 上比较 preprocessing tensor、action denormalization 和离线 policy 输出；运行 MuJoCo benchmark；校验 hash；重新测本地延迟；真机重新完成 serial/camera/safety 检查。Exit：差异在预定义容差或被记录解释，正式实验才可继续。

