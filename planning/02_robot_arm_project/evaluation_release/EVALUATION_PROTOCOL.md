# Evaluation Protocol

正式 protocol 在首次主对比前冻结并版本化。一次 trial 是从标准 reset 到 success 或明确 termination 的完整任务尝试；重试属于同一 trial，不能选择性删除。

## 指标

| 指标 | 定义 |
|---|---|
| Overall task success | 全部有序 subgoals 经 verifier/gold 确认的 trials / 总 trials |
| Per-subgoal success | 每类 pick/place predicate 成功数 / 尝试数 |
| Grasp / placement success | 正确稳定抓取；最终对象在目标区并释放 |
| Long-horizon completion | 完成 subgoal 数 / 任务要求数，同时报告 full completion |
| Recovery success | recovery 后当前 subgoal 成功 / recovery attempts |
| Intervention count | 每 task 人工接管次数及占比；另报 duration/steps |
| Completion time | reset 到 termination 的 wall-clock，含 recovery；仅作系统性能指标 |
| Collision/safety | 每 trial 碰撞、急停、饱和、系统 abort |
| OOD success | 预定义 OOD strata 下 overall/per-subgoal success |
| Data efficiency | 相对 base 每新增 N 轨迹/等价控制步的成功率增益 |

Verifier 结果用于在线控制，但正式结果建议由离线人工/gold protocol 复核；二者差异用于 verifier metric。

## Scene split

- Training：采集允许的对象实例、位置区域、光照和布局；mining pool 属于 training distribution 但与 test 清单隔离。
- Validation：调阈值、chunk、checkpoint selection；scene IDs 与训练 episode 隔离。
- Test-ID：与训练分布同类但冻结的对象布局组合，不用于采集/故障挖掘。
- Test-OOD：预注册 strata：新位置区域、对象身份/实例、distractor、光照、相机小扰动、clutter、未见排列。每个 OOD 只改变声明变量，避免无法归因。

## 执行规则

为各条件使用相同 trial manifest、reset protocol、对象/相机/标定版本和安全限制；顺序随机化或配对以降低漂移；记录环境和操作者；无论成功/失败/abort 都入表。checkpoint 和阈值在看 test 前锁定。报告分母、缺失、系统故障与排除原因；系统故障不静默重跑，而是单列并按预定义规则处理。

## 统计与报告

二项成功率报告样本数、点估计和区间；配对场景优先配对分析；长时序同时给总体和子目标条件概率；多次训练报告 seed/数据采样变化。不要用 completion time 替代成功，不根据单段视频下结论。

## Gate

Entry：canonical task、taxonomy、dataset split、verifier gold protocol 已定义。Tasks：pilot 检查可执行性，冻结 `evaluation_protocol_version`。Exit：另一个执行者可依据 manifest 复现 reset/判定；每个指标有明确分子分母；ID/OOD 不泄漏；排除规则预先写明；所有主结论有 quantitative evidence。

