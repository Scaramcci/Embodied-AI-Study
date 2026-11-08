# Do as I Do 非受限环境配置

日期：2026-11-06。计划：[部署计划](plan-do-as-i-do-deployment.md)。本轮范围：用户授权先配置除 SAM3/SAM3D 受限权重以外的部分。

## 已配置

- 本机和服务器使用分支 `codex/doasido-environment`。服务器原有子模块修改保存于 `/226040255/.setup-doasido/validation-20261106/existing-changes.patch`。
- Do as I Do 的左右手 MANO 目录链接到服务器 HuRo 已有的对应模型；没有复制或下载新的授权模型。
- `sam3/bin/ffmpeg` 和 `ffprobe` 添加包装入口，执行现有 `huro/bin` 的对应程序。离线 conda 安装因缓存缺包未完成，未执行包事务；改用现有二进制，避免改动 Python 依赖。
- 服务器 `/226040255/.setup-doasido/view-result.sh` 启动官方回放；本机 `tutorials/do-as-i-do/view-server.sh` 建立 18081 → 8081 的 SSH 转发。
- 保留官方预计算样例；没有执行完整重定向或 RGB 重建。SAM3/SAM3D 权重等待用户的权限申请通过。

## 本轮验证

- hawor、sam3d 的 PyTorch3D GPU KNN 通过已知距离断言；hawor 的 GPU scatter 求和通过。
- 左右 MANO GPU 前向通过，均输出 `(1, 778, 3)`，顶点均为有限值。
- DROID、lietorch、SAM3D 渲染器依赖导入通过；这些导入不代表各自所有 CUDA 内核已验收。
- 重定向 CLI `launch.py --help` 成功。
- FFmpeg 抽取第 125 帧成功；FFprobe 读取视频为 1280×720、172 帧。
- 服务器回放加载 MANO、IK、物理轨迹三层；跳过预热后有 1000 帧。本机 HTTP 返回 200，浏览器展示三层开关，点击播放后帧号推进；再次点击停止。

日志、检查脚本与冻结依赖输出位于 `/226040255/.setup-doasido/validation-20261106/`。浏览器操作由助手验证，用户尚未进行教学式人工验收。

## 后续

权限通过后下载并加载 SAM3/SAM3D，完成真实短片流程和峰值显存检查。首个完整样例完成后，再逐阶段讲解。

使用入口：[本机查看说明](../../../tutorials/do-as-i-do/README.md)。

## GPU 仿真验收补充

官方 whisking 场景已通过 `mujoco_warp.put_model`、`put_data(nworld=1)`、`step` 和 `warp.synchronize()`；日志包含 `MUJOCO_WARP_GPU_STEP_PASS`。首次编译约数分钟，后续可复用内核缓存。这是仿真单步环境检查，不是完整优化轨迹的质量验证。

## 公开模型验收补充

MoGe v1（配置指定 Ruicheng/moge-vitl）与 GeoCalib pinhole 权重已缓存并完成第 125 帧的 GPU 推理。MoGe 点云形状 `(480,854,3)` 且全部有限；相机内参四值有效且焦距为正。GeoCalib 输出一帧有效重力向量，JSON 有限性检查通过。HF Xet 下载长时间无进展后终止本轮下载进程，改 `HF_HUB_DISABLE_XET=1` 成功；该变量只设置在本轮检查脚本中。

五个环境的 pip freeze 已保存。检查脚本均已退出，仅保留查看器与本机 SSH 展示隧道运行。HaWoR 整段视频前向、TAPIR 跟踪和完整重定向优化留到样例复现阶段；不要把局部环境测试描述为整条流水线成功。
