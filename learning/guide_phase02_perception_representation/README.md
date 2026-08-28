# 阶段二：人体、手部与物体感知表示

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

