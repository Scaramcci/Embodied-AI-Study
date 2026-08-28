# Phase 2 学习进度

## 环境

状态：已完成

- Conda 环境：`eai-retarget`
- Python、NumPy、SciPy、Matplotlib、OpenCV、Open3D、pytest 已安装并验证；
- 当前阶段使用 Windows + CPU，无需 CUDA。

## Unit 1：论文输入接口与数据契约

状态：进行中

当前实验：

- 生成 10 帧 body/hand/object canonical packet；
- 分离数组数据与 metadata；
- 验证 shape、dtype、frame、unit、timestamp、quaternion order、confidence 和 joint order；
- 注入并拦截四类数据契约错误。

完成标准：能够解释为什么“数组 shape 正确”不等于“数据语义正确”，并能读懂验证报告。

