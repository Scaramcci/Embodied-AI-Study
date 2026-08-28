# 学习进度

## Unit 1：关节、连杆与运动链

状态：已完成

已完成：

- PyBullet GUI smoke test；
- 成功加载 `kuka_iiwa/model.urdf`；
- 确认 7 个可动关节均为 revolute joint；
- 确认 joint 0 的 child link 为 `lbr_iiwa_link_1`；
- 确认末端为 `lbr_iiwa_link_7`，link index 为 6。

- 已通过滑块确认：joint 1 影响 link 1～7，joint 4 影响 link 4～7，joint 7 只影响 link 7；
- 已能根据运动链判断 joint 5 影响 link 5～7。

## Unit 2：坐标系、旋转表示与齐次变换

状态：进行中

当前任务：运行 `src/unit02_pose_and_frames.py`，观察世界坐标系和末端坐标系，读取末端位置、四元数、欧拉角与齐次变换矩阵。

