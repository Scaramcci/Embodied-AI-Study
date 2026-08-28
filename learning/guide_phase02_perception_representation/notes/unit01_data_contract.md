# Unit 1：数据契约为什么是感知流水线的第一关

## 1. 本单元在整条链路中的位置

```text
RGB / RGB-D
  -> 感知模型原始输出
  -> adapter 转换
  -> canonical packet + metadata
  -> schema validator
  -> 动作重定向 / 接触计算
```

DexTele 和 ObjRetarget 可以使用不同的上游模型，但下游代码不能靠猜测理解数组。
因此我们先定义一个稳定的 canonical representation，再让每个真实模型通过 adapter 转成它。

## 2. 三个容易混淆的层级

| 层级 | 示例 | 本阶段怎样处理 |
|---|---|---|
| raw observation | RGB、depth、相机 timestamp | 保留采集信息，不直接当机器人目标 |
| model output | 2D/3D keypoints、mask、object pose | 了解其接口与误差，不训练大型模型 |
| canonical representation | 统一命名、坐标系、单位和时间轴的数组 | 本阶段重点实现与验证 |

canonical 不代表数据一定准确；它表示数据的语义已经明确，能够被一致地检查和消费。

## 3. 为什么 metadata 不是注释

例如同一个数组：

```text
body_position.shape = [T, J, 3]
```

仍然无法回答：

- 第 `j` 个关节是谁；
- 三个数属于哪个坐标系；
- 数值单位是米还是毫米；
- 每个 `t` 对应什么真实时刻；
- 遮挡关节是无效、低置信度，还是恰好位于原点。

这些信息会直接改变距离、速度、骨架边、重定向目标和接触判断，所以必须进入数据契约并接受验证。

## 4. 本实验的核心结论

validator 能检查“约定是否自洽”，但不能证明感知结果是真实世界的真值。后续仍需检查重投影误差、
时间同步误差、轨迹连续性和任务结果。它与 Phase 1 的 IK 后再做 FK 验证类似：上游函数返回一个数组，
不等于该数组已经满足下游任务要求。

