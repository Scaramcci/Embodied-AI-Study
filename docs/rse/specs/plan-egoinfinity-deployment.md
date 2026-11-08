# EgoInfinity 服务器部署计划

日期：2026-11-06。状态：执行中。用户已授权连续部署，最后在本机交互查看。
依据：[调研](research-egoinfinity-deployment.md)。

## 目标和范围
服务器完成 RGB 到手—物重建，本机经 SSH 隧道访问 Viser。先验证基础重建，机器人重定向、Flow3R 和 FP++ 增强不作为首轮验收要求。

## 当前状态与实施方式
官方固定版本 de59610531c08010d63d0493d6a72973eabd402e。defaults.yaml:27 默认关闭 worker；必须开启 phase1.args.with_sam3d_worker。服务器已有 CUDA 12.8、可用 huro 环境及 MANO。克隆到独立 egoinfinity 环境，不修改已有模型环境。

## 阶段
- [ ] 源码放 /226040255/EgoInfinity；conda create -n egoinfinity --clone huro；验证 python -c 'import torch; print(torch.ones(8,device="cuda").sum())'。
- [ ] 在独立环境 pip install -e /226040255/EgoInfinity；安装 MoGe、GeoCalib、MEMFOF；bash scripts/setup_weights.sh；链接既有 MANO，执行 python -m egoinfinity --help。
- [ ] 独立检查 SAM3.1、SAM3D 权重授权和模型加载；缺少授权时保留明确阻塞状态，不以跳过网格作为完整成功。
- [ ] 用短片执行 process，设置 phase1.args.with_sam3d_worker=true；检查 PKL、非空手数据、PLY 和物体位姿。
- [ ] 启动 --load-cache 查看器，建立 SSH localhost 转发；本机验证 HTTP 响应，用户检查交互。

## 验收
自动：CUDA 运算、依赖导入、命令入口、模型加载、产物内容、查看器 HTTP。人工：本机视角操作、时间滑块、手物对齐质量。
安装日志和版本存于 /226040255/.setup-egoinfinity。以真实短片集成检查为主，不为包安装编写模拟测试。
