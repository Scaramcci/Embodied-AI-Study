# Calibration and Sensors

标定目标不是追求最高数学精度，而是保证训练、评估和部署的 observation/action 含义稳定、可追踪。改变相机位置、关节零位或曝光策略都产生新的 calibration/config version。

## 训练前必须保证

| 项目 | 方法 | Pass criteria | 常见失败/排查 |
|---|---|---|---|
| Joint zero/direction | 多个已知姿态对照；正方向低速测试 | leader/follower/模型方向一致；重复加载零位稳定 | 度/弧度、joint order、零位文件错配 |
| Joint range | 物理安全范围内缓慢测量，软限位留裕量 | 命令无法越过软限位；模型范围一致 | 把机械极限当运行极限、夹线 |
| Camera identity | 按 serial/by-id 命名 top/wrist | 重插/重启后不交换 | `/dev/videoN` 漂移、USB hub 供电 |
| Camera placement | 刚性固定并保存照片/量测/config ID | top 覆盖完整工作区；wrist 抓取区可见；运动无碰撞 | 支架振动、遮挡、腕线拉扯 |
| Intrinsics | 固定分辨率/焦距；用标定板估计或保存厂商参数 | 重投影误差满足用途阈值；图像尺寸与参数一致 | 自动裁剪/缩放后仍用旧参数 |
| FPS/timestamp | 单调时钟；记录 capture 与 receive time | 帧率/延迟分布在预设阈值；缺帧有 mask 而非静默复制 | 不同系统时钟、缓存造成旧帧 |
| Lighting/exposure | 固定或记录曝光/白平衡；建立标准灯光 | 颜色与运动模糊稳定；无频闪/严重过曝 | 自动曝光随手臂遮挡漂移 |
| Observation consistency | 冷启动回放同一姿态和色卡/标志物 | shape、顺序、归一化、相机 ID、ROI 一致 | 训练部署 preprocessing 分叉 |

## 高级阶段按需完成

- Camera extrinsics：当 verifier/脚本策略需要像素到 world 几何关系时，标定 `world/base→camera_top`；仅端到端 RGB policy 不必先追求毫米级。
- Hand-eye calibration：需要将 wrist camera 观测精确变换到 tool/base 或做视觉伺服时再做；必须覆盖多姿态并独立验证。
- 多相机硬件同步：若软件时间戳使快速动作严重错位再升级；先量化问题。
- 深度/颜色校正：只有加入深度或颜色是关键 OOD 变量时进入。
- 在线外参估计：支架确有可观测漂移且影响指标时考虑。

## 校准资产

每版保存 `calibration_id`、日期仅作事实记录而非截止计划、设备 serial、分辨率/FPS、内外参、joint zero/direction/range、工具/支架状态、软件 commit、标定原始数据、误差报告、适用 dataset versions。数据 episode 必须引用 calibration ID；标定变更后的数据不可无记录合并。

## Gate

Entry：hardware bring-up 通过。Tasks：完成训练前必需项、小规模静态/动态录制、冷启动重复验证。Exit：两路相机与 proprioception 对齐；缺帧/旧帧可检测；关节与相机配置可重载；回放一致；wrist cable 全范围安全。**Compute/Hardware**：D；标定计算 A；高级视觉标定无需云 GPU。

