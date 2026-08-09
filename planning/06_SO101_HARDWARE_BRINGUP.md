# SO-101 Hardware Bring-up

禁止设备到货即录大规模数据。所有运动从不使能检查、单电机低速、无负载到 leader/follower 逐级推进；任何异常返回上一个稳定 Gate。

## 准入

Entry：Hardware Purchase Gate 通过；官方硬件/软件版本与供应商清单归档；工作区清空；急停/断电路径、关节限位和安全位已书面定义；相机不会进入运动包络。

## Bring-up 检查表

| 步骤 | Tasks | Pass criteria | 失败时安全动作 |
|---|---|---|---|
| 1 Mechanical inspection | 核对型号/零件/紧固件、关节自由度、夹爪、运输损伤 | 无裂纹/松动/卡滞；运动包络明确 | 不上电，拍照并联系供应商 |
| 2 Power & safety | 核对电压/极性/电源容量；布置物理断电；低速/低力限制 | 断电可单动作触达并实测；线材无拉扯 | 立即断电，不尝试软件修复硬件风险 |
| 3 Serial/USB | 记录端口、serial/by-id、权限、断连行为 | leader/follower 唯一稳定识别；重插映射不变 | 停止使能，排查线缆/供电/权限 |
| 4 Servo inspection | 单独检测电机通信、温度/电压/错误状态 | 每个 servo 健康，未出现异常温升/错误 | 断电隔离问题电机 |
| 5 Motor ID | 对照物理标签、软件 joint order 和总线 ID | ID 唯一且与 joint table 一一对应 | 禁止广播动作；逐个核对 |
| 6 Direction/range | 不使能核对方向；单关节低速小幅运动 | 正命令方向正确；软限位在机械限位内 | 急停，修正配置并重新从 dry-run 开始 |
| 7 Calibration | leader/follower 分别采样零位/范围/对应关系 | 校准版本保存；重复姿态误差在预设阈值内 | 不覆盖旧标定；定位漂移来源 |
| 8 Basic joint tests | 单关节→组合关节→安全位，记录目标/实测 | 无突跳/振荡/饱和；停止后无缓存运动 | 断电并检查映射、频率、增益/模式 |
| 9 Leader/follower | 低速小幅 teleop；逐步扩大安全范围 | 映射一致、延迟稳定、松手/断连进入安全状态 | 立即停止 follower，保留日志 |
| 10 Camera setup | 固定 top/wrist，相机命名按 serial/path；测 FPS/丢帧 | `camera_top`/`camera_wrist` 重插不交换；帧率稳定 | 停止运动；修复带宽/命名/供电 |
| 11 Wrist cable | 全工作空间缓慢扫过，检查线缆弯折/拉力/遮挡 | 无拉扯、卡入、碰撞或显著关节负载 | 缩小范围并重新布线 |
| 12 E-stop fault tests | 运动中断电/软件停止/USB 断连/陈旧命令 | 每种故障均在规定状态停止，stop reason 有日志 | 不进入下一步，直到可重复通过 |
| 13 Test checklist | 重启、重插、加载标定、safe pose、双相机、短 teleop | 全部可从冷启动重复；操作员能口述和执行急停 | 回退到对应失败项 |

## 必存 Artifact

硬件 BOM/序列号（公开版脱敏）、接线和工作区照片、motor ID/joint/方向/范围表、电源信息、标定文件与版本、相机 stable IDs、线缆布置图、急停步骤、每个 pass 的日志/视频、已知限制。标定不可只存在操作者记忆或某台机器缓存中。

## 完成 Gate

Exit：leader/follower 均稳定检测；所有 servo IDs 正确；校准可重载；teleoperation 稳定；两相机稳定命名并记录；无不安全运动；急停、断连和过期命令路径均实测；冷启动清单通过。通过后只允许进入小规模数据质量验证，仍不允许立即批量采集。

**Compute/Hardware**：D；训练不在此 Gate 内。旧 GTX1650 足以承担设备控制、记录和基础可视化，若 I/O/编码瓶颈则先降低显示负担而非迁移实时控制到公网。

