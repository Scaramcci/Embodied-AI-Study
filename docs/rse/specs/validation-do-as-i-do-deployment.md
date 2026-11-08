# Do as I Do 环境验证

日期：2026-11-06。对应 [计划](plan-do-as-i-do-deployment.md) 与 [实施记录](implement-do-as-i-do-deployment.md)。本地基线 `0e25b56`，服务器源码 `824591b808c342b20079c3b4198a8c2bdf88c74e`，工作分支 `codex/doasido-environment`。

## 实施状态

非受限基础环境、MANO 接入、FFmpeg、公开深度与重力模型、本机展示入口已配置。SAM3/SAM3D 权重等待授权；完整样例复现与教学尚未执行。

## 自动验证

- PASS：hawor/sam3d PyTorch3D GPU KNN 已知距离断言。
- PASS：GPU scatter 求和；左右 MANO 前向有限性和顶点形状。
- PASS：重定向 CLI；官方 MuJoCo 场景在 Warp CUDA 上完成单步并同步。
- PASS：FFmpeg 第 125 帧抽取，FFprobe 视频信息读取。
- PASS：MoGe 单帧 GPU 推理，点云 `(480,854,3)` 全部有限，相机焦距为正。
- PASS：GeoCalib 单帧 GPU 推理，输出 JSON 包含一帧有效重力向量。
- PASS：本机转发 HTTP 200，浏览器三层控件和实际场景出现，播放时帧号推进。
- PASS：本机隧道脚本 bash -n。

证据来自本轮执行，不以历史安装报告替代。服务器日志目录 `/226040255/.setup-doasido/validation-20261106`。

## 实现检查与边界

已有代码修改保留；使用共享盘与独立日志。FFmpeg 包缓存不完整，因此以包装脚本调用已有 HuRo FFmpeg，运行时依赖该环境路径。官方预计算样例未覆盖。受限模型未下载；没有以跳过 SAM 的方式声称端到端完成。

## 人工验收与后续

用户尚未确认视角操作、图层比较及轨迹质量；当前浏览器连通和播放由助手核验。下一步可重新计算已有重建的重定向样例；权限获批后补模型加载、完整 RGB 流程、峰值显存与质量验收。HaWoR/TAPIR 全模型执行和 SAM3D 全部 CUDA 算子仍需在真实流程中验证。
