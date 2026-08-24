# F3 感知与表示

## 目标

读懂人体到机器人论文中的输入和中间表示，并能审查任何数组的 `shape`、字段、
`frame`、`unit`、`timestamp` 和 `confidence`。

## 学习顺序

| 单元 | 主题 | 最低掌握标准 |
|---|---|---|
| F3.1 | pixel、2D/3D keypoint 与最小数据接口 | 能解释每个字段为什么存在 |
| F3.2 | 相机投影、深度与反投影 | 能说明 2D 点怎样结合 depth 得到相机系 3D 点 |
| F3.3 | 坐标变换、点云与 object pose | 能辨认 camera/world/robot frame |
| F3.4 | skeleton graph 与 contact event | 能解释 node、edge、feature 和接触事件 |
| F3.5 | 论文接口 | 能定位感知模块的输入、输出、假设和失败来源 |

计算策略：不要求大量手算；公式只学输入、输出、物理意义和常见错误，数值计算交给
短脚本验证。

## 当前入口

- [01：从图像到人体关键点](notes/01_keypoints_and_minimum_schema.md)
- [02：深度与反投影](notes/02_depth_and_backprojection.md)
- [学习记录](PROGRESS.md)
