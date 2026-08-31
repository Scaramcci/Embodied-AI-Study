# Unit 2 总结：相机模型、深度与坐标变换

## 1. 本单元解决的问题

Unit 2 建立了从图像观测到世界系三维几何的最小链路：

```text
camera-frame 3D point
    -> pinhole projection
pixel [u,v] + Z-depth
    -> back-projection
camera-frame 3D point
    -> world_T_camera
world-frame 3D point
```

这条链路是后续人体关键点、物体点云和手—物距离计算的几何基础。

## 2. 相机系与世界系

常用相机光学坐标约定：

```text
+x：图像右方
+y：图像下方
+z：镜头向前
```

世界系是系统选择的固定参考系，可以位于机器人底座、实验桌、动作捕捉场地或仿真原点，
不存在唯一的“绝对世界系”。

变换命名遵循 `target_T_source`：

```text
p_world  = world_T_camera @ p_camera
p_camera = camera_T_world @ p_world
camera_T_world = inverse(world_T_camera)
```

`world_T_camera` 左上角 `3×3` 是相机轴在世界系中的朝向，右上角三维向量是相机光心在世界系中的位置。

## 3. 相机内参与针孔投影

```text
K = [[fx,  0, cx],
     [ 0, fy, cy],
     [ 0,  0,  1]]
```

- `fx, fy`：像素焦距；
- `cx, cy`：主点；
- `K` 描述怎样成像，不描述相机位于世界中的哪里。

投影：

```text
u = fx X/Z + cx
v = fy Y/Z + cy
```

反投影：

```text
X = (u-cx)Z/fx
Y = (v-cy)Z/fy
p_camera = [X,Y,Z]
```

## 4. Z-depth 与欧氏 range

对于相机系点 `[X,Y,Z]`：

```text
Z-depth = Z
range   = sqrt(X^2 + Y^2 + Z^2)
```

只有位于光轴上的点 `X=Y=0` 才满足 `range=Z`。本单元深度图实验中：

```text
中心像素：Z=0.8 m，range=0.8 m
偏轴像素：Z=0.8 m，range=0.820652 m
```

若传感器提供的是 range，应沿单位射线放置点，不能直接把 range 填入要求 Z-depth 的公式。

## 5. 三个错误实验

### mm 被当成 m

三维误差达到约 `2011.54 m`，但像素重投影误差为零。原因是投影只依赖 `X/Z` 和 `Y/Z`，
同时缩放 `X,Y,Z` 不改变像素。

修正：根据明确的 `depth_scale` 转换数值，而不是只修改单位标签。

### range 被当成 Z-depth

三维误差约 `0.013646 m`，像素误差仍为零。错误点仍在同一条相机射线上，只是沿射线的位置错误。

修正：确认传感器的深度定义；range 输入需要使用归一化射线。

### 变换方向用反

把 `camera_T_world` 当作 `world_T_camera` 使用，世界系三维误差约 `2.835472 m`。

修正：乘矩阵前检查 `target_T_source` 的 source 是否与输入点的 frame 一致，并用相机原点等已知点验证外参。

## 6. Round trip 能证明什么

正确实验的三维和像素 round-trip error 都接近机器精度，证明实现内部数学一致。但内部一致不等于现实正确：

- 错误尺度可以在投影中相消；
- 错误变换与其错误逆变换可能互相抵消；
- 一个像素只确定一条射线，不确定射线上的三维位置。

可靠验证需要联合检查：

```text
重投影误差
+ depth unit / depth definition
+ 已知人体或物体尺度
+ frame 与外参方向
+ 标定或外部测量
```

## 7. 与目标论文的关系

- 人体/手部关键点必须从 camera frame 转换到统一 frame 后，才能构造骨架图和重定向目标；
- ObjRetarget 使用 RGB-D 恢复物体表面点云，深度单位或定义错误会直接破坏手—物距离和接触事件；
- 不同时间的相机或物体 pose 必须明确 `target_T_source`，否则轨迹虽然数值连续，也可能位于错误坐标系。

## 8. Unit 2 Gate

- [x] 能区分相机内参 `K` 与相机外参；
- [x] 能解释 camera frame、world frame 和 `target_T_source`；
- [x] 能完成投影、Z-depth 反投影和 frame round trip；
- [x] 能区分 Z-depth 与欧氏 range；
- [x] 能说明为什么零像素重投影误差不保证三维尺度正确；
- [x] 能识别并修正 depth scale 和变换方向错误；
- [x] 能把完整深度图反投影成 camera/world point cloud。

结论：Unit 2 Gate 通过，可以进入 Unit 3 的人体上肢、手部关键点与骨架图。

