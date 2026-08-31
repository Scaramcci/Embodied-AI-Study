# 阶段二：人体、手部与物体感知表示

> 2026-08-30 起采用[论文优先加速路线](../../planning/03_embodied_ai_guide_learning/ACCELERATED_PAPER_FIRST_ROUTE.md)：中心化、缺失值、异常和通用插值降为可选；主线直接转向 object local/world cloud、palm/fingertips、contact geometry，并并行开始论文粗读。

## 当前状态：加速版 Phase 2 已完成

```powershell
python learning\guide_phase02_perception_representation\src\p2a_hand_object_geometry.py
```

P2-A 与 P2-B 已完成：物体 local/world cloud、掌心/五指尖、最近表面距离、接触事件和时间错位
失败案例均已验证。下一步进入 Phase 3 动作重定向与轨迹优化。

本目录用于完成 `Embodied-AI-Guide-main` 论文导向路线的 Phase 2。重点不是训练大型视觉模型，
而是理解并验证感知模块交给动作重定向模块的数据。

## 当前任务：Unit 1——论文输入接口与数据契约

感知数组只有数值是不够的。进入后续重定向、轨迹优化或接触计算前，至少要明确：

- `shape`：时间、关节、左右手、物体和坐标维分别在哪一维；
- `dtype`：浮点数、布尔 mask、整数索引分别怎样保存；
- `semantic order`：第 `j` 个元素对应哪个关节或关键点；
- `frame`：坐标属于 camera、world、human-root、hand-local 还是 object frame；
- `unit`：位置使用米还是毫米，时间使用秒还是帧号；
- `timestamp`：各帧真实采样时刻是否严格递增；
- `quaternion order`：四元数采用 `xyzw` 还是 `wxyz`；
- `confidence / valid`：低置信度和缺失观测不能伪装成正常的零坐标。

Unit 1 的第一个实验生成 10 帧合成数据，并用 schema validator 检查正确样本。随后依次注入
四类常见错误：`m/mm` 单位错误、`xyzw/wxyz` 约定错误、非递增时间戳和 joint order 错误。

## 运行方法

在项目根目录执行：

```powershell
conda activate eai-retarget
python learning\guide_phase02_perception_representation\src\unit01_schema_contract.py
```

运行后会生成：

- `data/unit01_valid_packet.npz`：10 帧 canonical 数组；
- `data/unit01_metadata.json`：数组之外不能丢失的语义元数据；
- `outputs/unit01_validation_report.json`：正确样本与错误注入的验证结果。

运行自动测试：

```powershell
pytest learning\guide_phase02_perception_representation\tests -q
```

## 本次观察任务

运行脚本后先观察：

1. 正确 packet 是否显示 `PASS`；
2. 四个错误样本是否都显示 `REJECTED`；
3. 每条拒绝理由是在检查数值本身，还是在检查描述数值的 metadata；
4. 为什么 `[T,J,3]` 仍不足以说明一组 3D 关节数据可直接使用。

详细概念见 [Unit 1 笔记](notes/unit01_data_contract.md)。

## Unit 1 第二部分：confidence、valid 与数值检查

```powershell
python learning\guide_phase02_perception_representation\src\unit01_validity_and_numeric_checks.py
```

该实验允许 `valid=False` 的缺失观测使用 `NaN`，但拒绝有效观测中的 `NaN`。它还会注入越界
confidence、非单位四元数和错误 shape，区分连续可靠度、离散可用性和数值合法性。

## Unit 1 第三部分：模型 adapter

```powershell
python learning\guide_phase02_perception_representation\src\unit01_adapter_pipeline.py
```

该实验模拟一个上游人体姿态模型使用 `mm`、`ms`、`wxyz` 和自定义 joint order，adapter 对数值和
轴顺序进行真实转换，再交给 canonical validator。它也会验证缺少必需关节时必须明确失败。

## Unit 2 第一部分：相机投影与深度反投影

```powershell
python learning\guide_phase02_perception_representation\src\unit02_camera_roundtrip.py
```

该实验将 camera-frame 三维点投影到像素，使用像素和 Z-depth 反投影，再用
`world_T_camera` 转到 world frame，最后通过逆变换和重投影检查整个闭环误差。

## Unit 2 第二部分：约定错误为什么会躲过重投影

```powershell
python learning\guide_phase02_perception_representation\src\unit02_convention_failures.py
```

该实验分别注入 `mm/m`、欧氏距离/Z-depth 和变换方向错误。它说明像素重投影只能检查点是否
位于同一条相机射线上，不能单独证明三维尺度、深度定义或 world frame 正确。

## Unit 2 第三部分：深度图到点云

```powershell
python learning\guide_phase02_perception_representation\src\unit02_depth_image_to_cloud.py
```

该实验生成一张小型 Z-depth 图，将每个像素反投影为相机系三维点，并保存深度图/点云对照图。
它直接比较光轴中心与偏轴像素的 Z-depth 和欧氏 range。

Unit 2 已完成，阶段总结见 [Unit 2 总结](notes/unit02_summary.md)。

## Unit 3 第一部分：上肢骨架图

```powershell
python learning\guide_phase02_perception_representation\src\unit03_skeleton_graph.py
```

该实验把左右 `shoulder-elbow-wrist` 关键点构造成节点与有向边，生成 `[position, quaternion]`
节点特征和 `p_child-p_parent` 边特征，并验证边特征对全局平移不变。

## Unit 3 第二部分：中心化与尺度归一化

```powershell
python learning\guide_phase02_perception_representation\src\unit03_skeleton_normalization.py
```

该实验以关节几何中心作为 `center`，以平均骨长作为 `scale`，验证归一化骨架对整体平移和统一
尺寸缩放不变，并使用保留的 center/scale 重建米制坐标。

## 加速 Phase 2A：手—物任务几何

```powershell
python learning\guide_phase02_perception_representation\src\p2a_hand_object_geometry.py
```

该实验把物体局部点云通过 `world_T_object` 放入 world frame，并在同一 world frame 中表示
掌心和五个指尖，为接触距离计算建立几何输入。

## 加速 Phase 2B：接触距离与时间错位

```powershell
python learning\guide_phase02_perception_representation\src\p2b_contact_events.py
```

该实验模拟手的 approach/contact/release，计算五个指尖到物体表面的最近距离并以 8 mm 阈值
生成接触事件；随后故意把物体流错开 5 帧，展示“frame 相同但 timestamp 错误”仍会造成接触误判。
