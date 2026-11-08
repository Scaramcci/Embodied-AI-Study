# EgoInfinity 部署进度

日期：2026-11-06。计划：[部署计划](plan-egoinfinity-deployment.md)。状态：主环境完成，完整重建等待模型授权和后续验收。

服务器源码 /226040255/EgoInfinity，固定官方 de59610531c08010d63d0493d6a72973eabd402e；初始化部署分支 codex/egoinfinity-deploy。独立环境 egoinfinity 从 huro 克隆，PyTorch 2.7.0+cu128。已有环境未安装或升级包。

已完成：系统 git/patch/EGL/GL 依赖；独立环境；EgoInfinity editable 安装；MoGe 2.0（b942f00）、GeoCalib、MEMFOF、Open3D、Viser；WiLoR 源码补丁及 detector、checkpoint，SAM2、infiller、MoGe-2 权重；MANO 链接；4 秒短片 smoke.mp4；服务器查看脚本与本机 SSH 转发脚本。

验证：CUDA tensor 求和为 8.0；python -m egoinfinity --help 成功；moge.model.v2、geocalib、memfof、viser、open3d、pyrender、third_party.wilor.models、egoinfinity.pipeline.hand_reconstructor 均导入成功。脚本通过 bash -n。

解决问题：MoGe main 已升级 3.0，与 numpy<2 冲突，固定 MoGe 2.0；补 libgl1 修复手部渲染库导入；短片缩放改 scale=-2:480 避免奇数宽度；SSH 重连后继续，安装产物保留。

待完成：SAM3.1 和 SAM3D gated 权重授权及专用 worker 适配；模型前向推理；短片完整重建、网格与位姿检查；Viser 实际结果与本机交互验收。用户确认尚未申请权限；服务器无 HF token。不能把基础 CUDA 和导入测试表述为完整 pipeline 已运行。

日志和冻结依赖在 /226040255/.setup-egoinfinity；激活脚本 /226040255/activate-egoinfinity.sh。使用说明见 [本机查看说明](../../../tutorials/egoinfinity/README.md)。
