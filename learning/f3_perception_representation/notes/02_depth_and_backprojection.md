# F3.2 深度如何把二维像素变成三维点

## 1. 核心问题

二维关键点 `[u,v]` 只确定从相机出发的一条视线。要确定这条视线上的具体三维点，
还需要该像素的深度 `Z`。

```text
2D pixel [u,v] + depth Z + camera intrinsics
  -> camera-frame 3D point [X,Y,Z]
```

这个过程叫 back-projection（反投影）。

## 2. 相机内参分别做什么

针孔相机常用四个内参：

- `fx`：水平方向焦距，控制横向像素偏移对应多大的空间方向变化；
- `fy`：竖直方向焦距；
- `cx`：图像主点的横坐标，通常接近图像中心；
- `cy`：图像主点的纵坐标。

反投影公式是：

```text
X = (u - cx) * Z / fx
Y = (v - cy) * Z / fy
Z = depth(u,v)
```

不要求手算；需要理解每一项的作用：先计算像素相对主点的偏移，再利用焦距和深度
换成相机坐标系中的真实尺度。

## 3. 一个直觉例子

如果 wrist pixel 恰好位于主点：

```text
u = cx, v = cy
```

那么 `X=0, Y=0`，这个点位于相机正前方；depth 决定它在前方多远。

如果两个 wrist pixel 相同但 depth 不同，它们在图像中重合，三维位置却不同。这就是
为什么只有 `[u,v]` 无法确定三维位置。

## 4. depth 不是拿来就能用

至少要检查：

- unit：depth 是 metre、millimetre，还是设备的整数刻度；
- invalid value：`0`、`NaN` 或特殊最大值可能表示没有测量结果；
- RGB-depth alignment：RGB 的 `[u,v]` 是否对应 depth 图中的同一个像素；
- timestamp：RGB、depth 和 keypoint 是否来自同一时刻；
- noise/occlusion：腕部边缘可能混入背景深度。

## 5. 反投影的结果仍不是机器人命令

反投影得到的是：

```text
p_camera = [X,Y,Z]
```

它通常还要经过：

```text
p_camera
  -> camera-to-robot 坐标变换
  -> 人机尺度和任务目标构造
  -> 可达性与约束检查
  -> IK
  -> robot joint command q
```

## 本课检查题

同一个 wrist pixel `[u,v]`，第一帧 depth 是 `0.8 m`，第二帧 depth 是 `1.2 m`。
为什么它们的二维位置相同，三维位置却不同？反投影后得到的坐标属于哪个 frame？
