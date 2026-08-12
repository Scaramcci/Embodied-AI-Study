# 感知与表示

## 人体与手

- 2D keypoint 是像素坐标，不能直接当作三维机器人目标。
- 3D keypoint 必须注明 frame、尺度、时间戳和可信度。
- skeleton graph 的 node 可以包含位置和旋转，edge 表示骨架拓扑或相对几何。
- 人手和机器人灵巧手的关节数、轴向和尺寸不同，需要 retargeting，不能直接复制角度。

## 相机、深度和物体

| 表示 | 最小要求 |
|---|---|
| RGB frame | 分辨率、时间戳、camera ID |
| camera intrinsics | `fx, fy, cx, cy` 与像素坐标约定 |
| depth | 单位、无效值、与 RGB 的对齐方式 |
| point cloud | 每个点所属 frame，从深度到三维的投影公式 |
| object pose | 位置、旋转、目标物 ID、tracking confidence |
| contact event | 距离或传感阈值、进入/离开接触的时间 |

## 与两篇论文的对应

- DexTele：FrankMocap 输出人体和手的三维姿态，再转换为 skeleton graph。
- ObjRetarget：除人体与手外，还需要 RGB-D、物体点云、物体位姿和接触事件。

## 小型实验的简化

小型版只要求肩、肘、腕三个三维点，或者经过尺度归一化的伪 3D 点。物体可以用人工标注的目标点代替，暂不做点云跟踪与接触优化。

这个简化会失去多指接触的论文贡献，但能验证“人体轨迹如何变成机器人可执行轨迹”这个主问题。
