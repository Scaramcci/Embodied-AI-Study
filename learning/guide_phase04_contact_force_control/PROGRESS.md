# Phase 4 学习进度

## P4-1：Contact region 与局部多面体几何

状态：已完成

- 从 fingertip/object cloud 邻域提取接触区域和代表接触点；
- 构造 palm、当前 fingertip、相邻 fingertip、contact point 四顶点单元；
- 验证 global rigid transform invariance 和局部畸变敏感性。

## P4-2：接触阶段与 arm/hand 同步

状态：已完成

- 对比单阈值判断与 hysteresis + minimum dwell time；
- 建立 `approach -> contact -> manipulate -> release` 状态机；
- 验证 arm/hand 共用时间戳和 phase state 的必要性。

## P4-3：目标力与滚动调节

状态：已完成

- 用物体类别查表模拟 semantic target-force prior；
- 使用明确可微的 command + feedback force surrogate；
- 对比无调节、弱正则、合理正则与过强正则的滚动控制。
