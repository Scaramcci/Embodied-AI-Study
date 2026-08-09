# Compute and Deployment

设备：A=旧 GTX1650 4GB/16GB RAM；B=AutoDL RTX 4090 24GB；C=AutoDL A100 40/80GB；D=未来 M16 RTX 4090 Laptop 16GB/64GB。另用 `Local SO-101` 表示必须连接实体设备。

## Compute matrix

| Workload | A 旧本地 | B 云 4090 | C 云 A100 | D 未来 M16 | Local SO-101 | 推荐与原因 |
|---|---|---|---|---|---|---|
| ROS2/RViz/TF | Can run | Can but poor fit | Not needed | Can run | bring-up 必需 | A 足够；设备/GUI/USB 在本地 |
| MuJoCo control | Can run | Can | Not needed | Excellent | 仅真机对照 | A 为主，轻量且易交互 |
| MuJoCo vision/batch | Limited/Can | Recommended | Overkill | Recommended | 否 | 大批量可 B |
| Isaac GUI | Not recommended | 远程 GUI 可但体验受限 | 远程 GUI 可但成本高 | Recommended | 否 | D 的交互 scene/camera/collision 调试最佳 |
| Isaac headless | Limited/not recommended | Recommended | Recommended for very large jobs | Can | 否 | AutoDL 可完成，不要求本地 |
| BC | Can | Recommended for visual | Not needed | Excellent | rollout 需要 | smoke 在 A，正式视觉训练 B/D |
| ACT | smoke/小模型；正式训练不推荐 | Recommended | Can but often unnecessary | Recommended | inference/rollout 需要 | B 训练；本地推理先实测延迟 |
| Diffusion Policy | Not recommended | Recommended | Can | Can/Recommended | rollout 需要 | 采样/训练较重 |
| SmolVLA | 接口 smoke；通常不推荐 | Recommended | Can/Recommended by size | inference/PEFT 视版本可行 | rollout 需要 | 先按具体版本测显存/延迟 |
| Larger VLA | Not recommended | limited by exact model | Recommended 40/80GB when justified | inference 可能受限 | rollout 需要 | 只有明确大模型实验才用 F 级云 GPU |
| Real robot inference | 小模型 Can | 不作为公网实时闭环 | 不作为公网实时闭环 | Recommended for larger local models | 必须 | camera/USB/controller 全部本地 |
| 数据审计/统计 | Can | Can for scale | Not needed | Excellent | 采集需要 | A 足够；大量视频处理可 B |

## 部署分界

云端：训练、headless Isaac、parallel env、数据生成、batch evaluation、checkpoint 产出。传输前后校验 dataset/checkpoint hash，保存环境和配置。真机本地：相机采集、时间同步、policy inference、safety gate、controller、Verifier 快路径、event log。公网中断不得影响急停或产生缓存动作。

## 资源选择 Gate

先在最小设备做 smoke，测峰值显存、RAM、吞吐和 inference P95；只有指标超出设备且影响实验再升级。16GB 是否够不能按营销规格判断；混合精度/量化改变结果时必须记录。A100 80GB 仅在模型/optimizer/序列确实需要时租用，不作为“更快”的默认。

## 迁移到 M16

通过 lock/container、相对数据根、hardware/camera config、checkpoint hash 和 smoke tests 迁移；USB stable IDs 与本机 calibration 分离，不能复制旧机器设备路径。迁移 Gate：相同冻结 episode 的 preprocessing/action 输出一致；仿真 benchmark 在容差内；真机重新做所有 safety/latency 检查。

