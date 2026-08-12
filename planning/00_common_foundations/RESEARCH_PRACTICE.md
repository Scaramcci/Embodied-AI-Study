# 论文与实验方法

## 论文阅读输出

每篇论文最终要回答：

1. 输入、中间表示和输出分别是什么？
2. 人与机器人在尺寸、拓扑、自由度和视角上的差异如何处理？
3. 方法中哪些是学习模块，哪些是几何、优化或控制模块？
4. 主要 loss、constraint 和 metric 各自衡量什么？
5. 消融实验能否支持作者对模块作用的解释？
6. 完整复现需要哪些未公开数据、权重、硬件或标定？
7. 小型实现保留了哪个科学问题，又删掉了哪些论文贡献？

## 指标

| 指标 | 用途 | 容易出错的地方 |
|---|---|---|
| MPJPE | 关键点/关节位置误差 | 是否先做 root alignment、scale normalization |
| Quaternion distance | 姿态误差 | `q` 与 `-q` 等价，四元数顺序 |
| Velocity error | 一阶运动差异 | 必须使用真实时间间隔 |
| Acceleration error | 平滑性与抖动 | 对噪声敏感，不能随意平滑后不记录 |
| Joint-limit violation | 可执行性 | 单位、joint order 和 tolerance |
| Task success | 真实任务结果 | 成功定义、试验分母和无效试验 |

## 实验规则

- 实验前写 hypothesis、primary metric 和决策规则。
- 固定输入轨迹和机器人模型，再更改 loss 或约束。
- 消融只删除一个可解释因素，不同时更换数据、模型和指标。
- 失败运行保留错误和配置，不只记录最好结果。
- 事实、论文主张和自己的推断分开写。

## 最小实验记录

```text
Experiment ID:
Question / Hypothesis:
Input trajectory:
Robot model:
Method / Ablation:
Environment / Commit:
Primary metric:
Result and denominator:
Failure cases:
Interpretation:
Next decision:
```
