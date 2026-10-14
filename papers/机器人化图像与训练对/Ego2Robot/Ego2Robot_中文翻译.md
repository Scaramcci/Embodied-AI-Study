# Ego2Robot：从第一人称人类数据大规模合成机器人训练数据

原文：Ego2Robot: Scalable Robot Data Synthesis from Egocentric Human Data。对应所提供的 arXiv:2608.02580v1，2026 年 8 月 3 日。

作者：Ye Wang、Pei Lin、Xiong-Hui Chen、Haoqi Yuan、Zhixuan Liang、Yiyang Huang、Anzhe Chen、Zixing Lei、Jie Zhang、Tao Zhang、Haoyang Li、Tong Zhang、Chenxi Xiao、Ziyuan Jiao、Qin Jin。前三位为共同贡献，Qin Jin 为通讯作者。机构包括中国人民大学 AIM3 实验室、阿里巴巴 Qwen 团队、上海科技大学、北京通用人工智能研究院和北京航空航天大学。

> 阅读说明：按便于个人阅读的中文技术文章翻译，保留正文和全部技术附录，合并断行及重复叙述。VLA 是视觉-语言-动作模型，VLM 是视觉语言模型，EEF 是末端执行器，IK/FK 是逆/正运动学，TCP 是工具中心点。embodiment/morphology 按语境译为“机器人形态”或“平台”。文中的“我们”指论文作者。参考文献保留英文，便于查找。

## 摘要

要学习有泛化能力的机器人操作策略，需要规模大且多样的示范数据。第一人称人类操作视频具有丰富的场景和任务多样性。此前工作已经证明，把这些视频的动作重定向到机器人，再渲染成机器人格式的数据，可以在小规模、单任务上训练出有效策略。然而，这种方法能否在大规模 VLA 预训练中带来收益，还没有得到充分研究。

我们提出 Ego2Robot：一个可扩展流程，通过动作重定向、机器人手臂视觉合成，以及多层质量清洗，把第一人称人类操作视频转换成机器人训练数据。它既支持整理好的数据集，也支持自然环境中的视频，最终生成覆盖 15 种机器人形态、共 18,561 小时的数据，是作者所知截至本文最大的第一人称人类到机器人合成数据集。

为了评估泛化，我们扩展 RoboTwin 2.0，把视觉外观、场景布局、机器人形态和任务语义拆成独立扰动轴。实验表明，合成数据与机器人数据联合预训练，可以在多种扰动下持续改善 OOD 泛化，收益也在真实机器人部署中得到验证。

关键词：机器人数据合成、第一人称数据、泛化评估。

## 1. 引言

近年来，VLA 模型通过大规模机器人示范预训练，在操作任务上取得明显进展。但它们的泛化仍根本受制于可用机器人数据的规模和多样性。即使有 Open X-Embodiment、DROID、AgibotWorld 等大规模项目，采集示范仍昂贵且耗费人力，还受到硬件可用性、遥操作成本和交互多样性的限制。

第一人称人类视频提供了另一条路径。相比机器人遥操作，人手交互可以在大量不同物体、环境和任务变体中采集，包含单靠机器人很难获得的操作先验。但人类和机器人形态差异很大，不能直接把人类视频当机器人训练数据。

一种有希望的方法是把人手动作重定向到机器人运动学，再把画面中的人手替换成渲染机器人。这已在小规模单任务中有效，尚未充分探索它能否作为大规模预训练数据，尤其能否改善 OOD 泛化。

本文的假设是：即使形态不同，人类操作视频仍包含可迁移的交互规律，只要正确对齐，就能补充机器人数据。我们据此提出 Ego2Robot，用动作对齐、视觉对齐和多层清洗形成端到端数据合成流程。它支持带手部标注的数据集和纯视频，把约 1,940 小时、四个来源的第一人称视频转到 15 种机器人形态，最终得到 18,561 小时有效训练数据。

【图 1：Ego2Robot 总流程】路径 A 输入带手部姿态标注的数据集 ANT、EgoDex、ViTRA、EgoVerse；路径 B 输入无姿态标注的 Ego Play 视频，先估计手部姿态。随后共同执行重定向平滑、手臂分割、去手修复、基座搜索和 IK、深度合成，并进行流程内、统计和 VLM 语义一致性三层清洗。15 形态、四来源，数据量约扩展 9.6 倍。

我们还构建了 RoboTwin 2.0 上的独立扰动评估。此前把多种分布变化合成一个总分，很难知道预训练究竟改善了视觉稳健性、形态迁移还是语义理解。新的协议将四类因素分开，能细致归因。实验显示，合成数据具有与机器人数据互补的价值，视觉、形态、语义扰动下的提升最明显。这说明它主要改善了不变性和跨分布稳健性，而不只是增加轨迹覆盖。

本文贡献是：支持 15 形态的完整合成流程；18,561 小时合成数据集；拆分视觉、场景、形态、语义的泛化基准；以及合成与机器人数据联合训练改善 OOD 泛化的系统证据。

## 2. 相关工作

**机器人数据扩展与人类数据学习。** 大规模机器人数据集和便携采集系统增加了示范，但采集成本和硬件扩展仍限制多样性。人类视频提供更广来源，催生了视觉预训练、奖励学习、运动先验和点追踪等方法，不过它们通常仍靠机器人数据跨越形态差异。

更直接的路线，一类在人类或第一人称视频和机器人数据上联合训练，另一类通过重定向与渲染、或形态遮罩，把人类示范转成机器人格式。重定向渲染此前主要用于有限规模或单任务。本文把它扩到 18,561 小时、15 形态，并系统研究 VLA 预训练与 OOD 泛化收益。

**机器人数据增强。** 仿真和数字孪生能合成示范；RoviAug、Mirage、OXE-AugE 通过视频修复和图像编辑缩小机器人到机器人的视觉差异。本文面向差异更大的第一人称人类到机器人领域，利用人手视频生成 15 形态数据，并沿多种独立扰动评测。

**泛化基准。** RoboTwin、LIBERO、CALVIN、RLBench、SIMPLER 等通常同时改变多个因素，难以定位失败原因。ManiSkill2/3 和 RoboCasa 支持多个机器人配置，但缺乏标准化跨形态评测。Colosseum、LIBERO-Plus、LIBERO-PRO 将扰动分解，显示 VLA 在单一变化下也明显下降，但主要限于单臂。RoboTwin 2.0 和 EBench 支持双臂，但报告仍多为组合结果。本文同时支持独立扰动、双臂和跨形态评测。

## 3. Ego2Robot 数据合成流程

给定人手操作的第一人称视频，流程依次执行动作对齐、视觉对齐和质量清洗。动作对齐把手部姿态转换为末端轨迹并平滑；视觉对齐分割并去除人臂、搜索机器人基座、求解 IK，并做深度渲染；质量清洗在轨迹、帧和整段示范层面过滤样本。

路径 A 接受已有手部姿态标注的数据。路径 B 先用 WiLoR 逐帧重建，用 DynHaMR 做时序优化；长视频还通过 Qwen3.5 分割成带自然语言说明的独立子任务。得到手部姿态后，两路径进入相同流程，可以为 15 形态并行生成数据。

### 3.1 动作对齐

**人手到平行夹爪。** 每个检测到手的帧，根据 21 个关键点提取紧凑夹爪表示。虚拟指尖由食指尖和中指尖加权：

$$p_{vf}=0.7p_{index}+0.3p_{middle}. \tag{1}$$

TCP 是拇指尖与虚拟指尖中点，夹爪开口是二者距离：

$$p_{tcp}=\frac{p_{thumb}+p_{vf}}2,\qquad w=\|p_{thumb}-p_{vf}\|. \tag{2}$$

方向由右手正交坐标系 $R=[x\ y\ z]$ 表示。抓取轴 $z$ 沿拇指与虚拟指尖连线，$d=p_{vf}-p_{wrist}$ 为手腕到指尖方向。二者张成夹爪平面，$y$ 为法向，$x$ 为接近轴：

$$z=\frac{s(p_{thumb}-p_{vf})}{w},\quad
 y=\frac{z\times d}{\|z\times d\|},\quad x=y\times z. \tag{3}$$

右手 $s=+1$、左手 $s=-1$，使两只手具有一致抓取轴方向，映射到同一夹爪坐标定义。

**时序平滑。** 逐帧检测会产生高频噪声。位置和宽度使用 Savitzky-Golay 滤波，方向使用高斯加权 SLERP，在保留动作结构的同时平滑轨迹。

**速度对齐。** 人手通常比机器人遥操作快，训练按来源降低采样帧率：ANT、EgoDex 为原来的 60%（约慢 1.7 倍），EgoVerse 45%（约慢 2.2 倍），ViTRA 25%（约慢四倍）。这里保留作者给出的降速解释。

### 3.2 视觉对齐

目标是让同一场景的视频，从“人手操作”变成“机器人手臂操作”。

**手臂分割。** SAM 3 为每帧生成具有时序一致性的手臂掩码。

**去除人手。** ProPainter 根据掩码做时序一致的视频修复，重建人臂后的背景。

**机器人基座搜索。** 人手轨迹不带机器人基座，而机器人到机器人迁移有源基座可参考。我们必须寻找 $T_{base}=(t,R)\in SE(3)$，让目标形态能在运动学上实现重定向轨迹。

给定 $N$ 个末端目标位姿，选代表性关键帧集合 $\mathcal K$，覆盖位置最大位移或姿态显著变化，优化 IK 可行比例：

$$T^*_{base}=\arg\max_{T_{base}}\frac1{|\mathcal K|}
\sum_{k\in\mathcal K}\mathbf1[\mathrm{IK}(T^{-1}_{base}T^{ee}_k)\text{ 可行}]. \tag{4}$$

候选基座在轨迹中心附近网格搜索，范围受机器人最大可达距离 $r_{max}$ 约束。每个候选在所有关键帧求解 MuJoCo IK，选择可行率最高者。每种形态独立搜索，因为臂长关节配置不同。

**IK 和渲染。** 固定优化后的基座，逐帧求 IK，从原视频相机视角渲染机器人。

**深度合成。** 将机器人与修复背景按深度排序合成：

$$I_{final}(u,v)=\begin{cases}
I_{robot}(u,v),&D_{robot}(u,v)<D_{scene}(u,v)\ \land\ M_{robot}(u,v)=1,\\
I_{inpaint}(u,v),&\text{其他情况}.
\end{cases} \tag{5}$$

场景深度来自深度传感器或单目估计。每个视频分别生成 Panda、UR5e、ARX-L5、xArm7、Sawyer、Kinova Gen3、IIWA、Jaco、FR3、UR10e、ViperX、WidowX、Piper、YAM、Aloha-Agilex 共 15 形态的训练流。

### 3.3 三层质量清洗

**L1：流程内部。** 标记 IK 失败、自碰撞、异常动作、工作空间覆盖不足等帧。

**L2：统计过滤。** 移除极端动作、不连续突变，以及无效帧过多的轨迹。

**L3：VLM 一致性。** 审核合成视频中的机器人行为，是否与原始操作意图在语义上相容。

四组输入是 ANT（内部采集、带手部标注的抓取放置数据，7 小时）、EgoDex（732 小时）、ViTRA（249 小时）、EgoVerse（954 小时），合计约 1,940 小时。经过 15 形态生成和清洗，最终为 18,561 小时。

每个样本包含合成机器人视频帧、对应相机系末端动作、相机参数和文本指令。第一人称相机位置多样且未知，世界系动作需要逐视频标定，跨源动作空间容易不一致。相机系相对末端动作直接在观察者坐标系中表达位移，可以自然统一不同相机设置和机器人形态。

## 4. 如何评估泛化

既要知道合成数据改善哪些能力，也要知道哪些能力仍受域差异限制，就需要独立扰动。RoboTwin 2.0 的多因素同时随机化只给一个 OOD 总分，混合了视觉、空间、形态和语义变化。

我们扩展 11 个独立 RoboTwin 条件，支持相机系相对末端控制，并增加外部 EBench 的七个 Isaac Sim 精密桌面任务。EBench 头部相机更高，更接近人类第一人称视角。

【图 2：四维十二种评测设置】虚线框表示从原随机化中拆出的独立因素，实线框表示新增因素，灰框表示外部 EBench。

四维具体为：

- **视觉外观：** 背景纹理、光照、机器人颜色。前两者独立控制；颜色对所有机器人连杆随机改变色相，测试对未见外观的视觉不变性。
- **场景布局：** 桌高 ±4 cm、干扰物、相机位置每轴最多偏移 5 cm。独立测量常见空间布置变化。
- **机器人形态：** 默认 Aloha-Agilex 换成 UR5-WSG、ARX-X5、Franka Panda，IK 对齐初始末端，零样本测试，不做目标形态专用微调。
- **任务语义：** 50 项任务使用该任务训练未见的物体实例；另有 505 条口语化改写指令，测试新外观及语言表达变化。

## 5. 实验

### 5.1 实验设置

架构采用 Qwen3.5-4B 主干和 DiT 动作头，在相机系相对末端表示中预测 32 步动作块，使用八次扩散训练计算。附录进一步明确，推理采用四步欧拉积分。

所有预训练配置相同：八 GPU，每 GPU 批量 12，学习率从 $10^{-5}$ 余弦衰减到 $10^{-6}$，bf16，200K 步。每种配置处理相同约 19.2M 帧，数据集大小不同不会造成训练样本数量不公平。微调加载预训练权重，用 ColorJitter，训练 50K 步。

比较四方案：仅机器人数据，来自 DROID、AgibotWorld 和 InternData，约 6,565 小时；以及 Ego2Robot 合成（简称 Ego2R）与机器人按 1:3、3:1、1:1 混合。比例均为 **Ego2R : Robot**。

各模型在 RoboTwin Clean 的 50 任务、每任务 50 示范上微调，每个扰动条件下每任务评测 50 次。EBench 单独微调。真实实验用 ARX ACone，五项长时序任务。

### 5.2 主要结果

**表 1：成功率 %。** Visual、Scene、Embody、Task 是 RoboTwin 对应维度平均，EBench 为外部基准平均。

|预训练|Clean|随机化|视觉|场景|形态|任务|EBench|
|---|---:|---:|---:|---:|---:|---:|---:|
|仅机器人|62.2|50.9|61.4|52.9|23.8|46.2|39.6|
|Ego2R+Robot 1:3|61.4|51.0|61.2|52.5|21.9|49.5|47.4|
|Ego2R+Robot 3:1|64.1|49.2|62.7|54.3|28.2|51.6|51.7|
|Ego2R+Robot 1:1|68.1|53.5|67.3|56.9|27.2|54.1|49.8|

相对仅机器人，1:3 的变化依次为 -0.8、+0.1、-0.2、-0.4、-1.9、+3.3、+7.8 点；3:1 为 +1.9、-1.7、+1.3、+1.4、+4.4、+5.4、+12.1；1:1 为 +5.9、+2.6、+5.9、+4.0、+3.4、+7.9、+10.2。

**表 2：独立扰动成功率 %。**

|预训练|背景|光照|机器人颜色|桌高|杂物|相机|ARX|UR5|Franka|新物体|改写语言|
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
|仅机器人|66.6|58.2|59.4|60.1|48.3|50.4|44.1|20.2|7.0|29.3|63.1|
|1:3|65.0|58.3|60.3|58.6|49.3|49.6|43.7|17.6|4.5|36.8|62.2|
|3:1|65.5|60.9|61.8|62.0|49.2|51.6|47.6|31.4|5.6|40.0|63.1|
|1:1|70.3|65.8|65.8|62.4|52.0|56.3|51.2|25.0|5.3|39.6|68.5|

这些结果带来以下结论。

**联合训练提高 OOD 泛化。** 1:1 在七列中五列最好，Randomized 为 53.5，比仅机器人高 2.6 点，同时 Clean 达 68.1。1:3 总体收益较小，3:1、1:1 更明显，但不是所有测试都提高，例如 3:1 的组合随机化低于基线。

**视觉外观收益最大。** 1:1 的背景、光照、颜色分别约提高四、八、六点。第一人称场景多样性帮助背景光照，多形态渲染帮助机器人外观不变性。

**场景布局有中等改善。** 相机位置扰动约提高六点，与第一人称视频中自然变化的头部姿态和视角有关。

**多形态数据帮助迁移。** ARX 从 44 到 51（1:1），UR5 在 3:1 达约 31，预训练见到 15 种形态直接有益。但 Franka 仍低于约 7%，反映它与微调形态的较大运动学差异。

**任务语义持续改善。** 新物体从 29 到 40，3:1 约提高 11 点，来自人类视频中的丰富物体交互；改写指令在 1:1 达约 69，受益于更广语言表达。

**EBench 的较高视角进一步验证收益。** 3:1 最好，为 51.7，比机器人基线高 12.1。当目标相机视角更接近第一人称来源时，联合训练收益可能更明显。

### 5.3 消融

为了隔离流程的作用，这组实验的预训练只用人类来源数据，不含机器人数据，随后仍在 RoboTwin Clean 微调。

【图 3：流程价值与形态数量】原始第一人称数据在 RoboTwin Randomized 仅 28.1%；经过合成、只用一种机器人形态为 31.7%，提高 3.6 点，证明动作和视觉对齐有效。

机器人形态从一增加到十五，表现逐步由 31.7 到 33.5。再混入原始第一人称视频，达到 37.3%。原始人手可视作第十六种“形态”，具有稍不同的外观和动作分布，进一步丰富预训练。

### 5.4 真实机器人实验

在 ARX ACone 上测试水果放篮子、积木放抽屉、折毛巾、扫垃圾、插螺钉五项长任务。每任务采集 20 遥操作示范，另录约每场景七分钟的人手自由操作 Ego Play，再由流程转成 ACone 专属合成示范。

比较：Robot-only 用仅机器人预训练，在遥操作示范上微调；Mix 用 1:1 联合预训练，在相同示范上微调；Mix + Ego2R Play 再把遥操作和合成自由操作按 1:1 混合微调。图中还展示 Scratch 从头训练对照。

【图 4：真实平台结果】Mix + Ego2R Play 五项都最好，放积木相对 Robot-only 约提高 14 点，插螺钉约提高 13 点。仅混合预训练已经改善表现，Ego Play 再持续提高。图中精确柱高未全部印数字，不在译文中臆造数值。

【图 5：真实执行序列】展示五任务在 ACone 上的关键帧。

这些结果表明，随手记录的第一人称操作视频，通过合成流程也能变成有效训练信号。

> 计分说明：正文和图使用“成功率”表述；附录明确采用子步骤部分计分、每任务满分 100。读取图中数值时应结合这个协议，不能一概视为完整任务成功比例。

## 6. 局限

首先，人手姿态重定向到平行夹爪会丢失细粒度手指运动。扩展到多指灵巧手，可能迁移更多技能。

其次，视觉对齐依赖视频修复和深度合成，在严重遮挡或复杂光照下可能产生伪影。提高渲染保真度，例如使用生成模型，可能进一步缩小视觉域差异。

最后，评测主要局限于 RoboTwin 2.0 的任务范围，扩到更多任务和形态会增强结论的一般性。

## 7. 结论

Ego2Robot 把第一人称人手操作视频大规模转换为 15 种机器人形态的数据。独立扰动评测显示，合成与机器人数据互补，视觉、形态和语义变化下收益最明显。真实机器人上，合成数据加少量遥操作示范可以实现有效多任务部署。作者希望推动利用海量人类操作视频，扩展机器人学习。

---

## 附录 A：合成流程的具体实现

### A.1 无标注视频的手部姿态估计（路径 B）

**逐帧重建。** WiLoR 检测人手并回归 MANO 参数 $(\theta,\beta,t)$，每帧得到 21 关键点和手部网格。用 SAM 3 的手部掩码过滤：如果超过 80% 的投影关键点落在掩码外，该帧丢弃。

**跨帧关联。** WiLoR 的 YOLO 检测器给出框及初始左右标签。选择左右手检测分数之和最高的帧作为种子，双向传播。每帧的新检测分配给上一帧图像空间手腕位置最近的手，使用欧氏距离；多个检测竞争同一只手时保留最高分。

关联后去除手腕三维速度超过 $\max(4\times\mathrm{median\ velocity},0.003\ \mathrm m/\mathrm{frame})$ 的跳变帧，认为其属于误检测。

**时序优化。** DynHaMR 在完整序列上联合优化 MANO 姿态和形状：

$$\mathcal L_{dyn}=\mathcal L_{data}+\lambda_{smooth}\mathcal L_{smooth}+\lambda_{bio}\mathcal L_{bio}. \tag{6}$$

数据项约束与 WiLoR 一致，平滑项惩罚手腕位置与手指角度加速度，生物力学项约束关节范围。重建手部距离相机的深度限制在 0.05-0.4 m。

**缺失处理。** 连续缺失超过十帧时，用机器人初始关节配置填补，在边界平滑过渡。过渡长度：

$$n=\max(5,\min(90,\lceil0.6n_{pos}+0.4n_{rot}\rceil)),\quad
n_{pos}=\frac{\Delta p}{3.25\ \mathrm{mm}},\quad
n_{rot}=\frac{\Delta\theta}{1.08^\circ}.$$

这对应在固定过渡速度下完成位移/转角需要的帧数。缺失不超过十帧时，位置线性插值，方向 SLERP。

### A.2 子任务分割（路径 B）

长连续视频先每 60 秒切段，将片段交给 Qwen3.5，提示内容为：

```text
你正在观看第一人称操作视频（时长 {duration} 秒）。
任务：{task_desc}。
按完整任务目标分割视频，每个子任务应是独立且完整的目标。
为每个子任务写一条简短英文动作指令，长度 5-12 个词。
只输出 JSON 数组：
[{"description": ..., "start_time": ..., "end_time": ...}, ...]
```

返回的时间边界和描述作为训练指令。这里只翻译提示含义，JSON 字段保持代码形式。

### A.3 动作对齐细节

左右手符号直接由身份确定。构造法向的手腕指尖向量直接取 MANO 关键点。

**退化方向。** 夹爪宽度小于 0.01 m，拇指与虚拟指尖几乎重合，姿态会退化，此时沿用最近有效姿态。$z$ 与 $d$ 近乎平行、叉积约为零时，同样处理。

**速度过滤。** 位置逐帧位移 $v_t=\|p_t-p_{t-1}\|$ 的阈值为：

$$\tau_t=\max(5\cdot\mathrm{median}(\{v_s\}_s),0.9/\mathrm{fps}). \tag{7}$$

旋转使用类似阈值，下限为 $10.0/\mathrm{fps}$ rad/frame。超阈值帧通过相邻帧插值替换，重复两轮。

**平滑参数。** 位置和夹爪开口的 Savitzky-Golay 窗口是 $\min(21,n)$，多项式阶数是 $\min(3,\mathrm{window}-1)$。方向用高斯加权 SLERP，$\sigma=10$ 帧，核大小 21。插值前做四元数半球修正：若 $q_t\cdot q_{t-1}<0$，把 $q_t$ 取负，避免等价四元数符号翻转带来的跳变。

### A.4 视觉对齐细节

**分割。** SAM 3 使用文本提示 `person`，以中间帧为时间传播锚点。长视频按 400 帧处理，相邻段重叠 50 帧，重叠掩码按位或合并。后处理包括：不超过三帧的缺失，用相邻掩码插值；面积低于局部中位数一半的帧，用最近有效掩码替换，局部窗口 11；用 5×5 椭圆核做形态学闭运算。

**修复。** ProPainter 使用 fp16，参数 `neighbor_length=10`、`ref_stride=10`、`subvideo_length=80`、`mask_dilation=4`，RAFT 迭代 20 次。

**基座候选。** 以可达距离 $r$ 缩放，在相机坐标系生成：

|变量|候选|
|---|---|
|左右偏移|$r\times\{0.3,0.4,0.5,0.6,0.8,1.0,1.2\}$；左右臂符号相反|
|前后偏移|$r\times\{-0.1,0.0,0.1,0.3,0.5,0.7,0.9\}$|
|上下偏移|$r\times\{0.4,0.2,0.0,-0.2,-0.4\}$|
|俯仰|30°、45°、60°|
|偏航|-45°、-20°、0°、20°、45°|
|滚转|-15°、0°、15°|

离相机小于 0.20 m、轨迹点距基座超过 $0.9r$、或小于 0.08 m 的候选被排除。剩余候选评分：

$$S=FR(T_{base})-5.0|\bar\rho-0.65|. \tag{8}$$

$FR$ 是最多 20 个关键帧上的 IK 可行率，使用 mink、quadprog 后端、100 次迭代、$10^{-5}$ 阈值。$\bar\rho$ 是末端到基座平均距离除以 $r$：

$$\bar\rho=\frac1{|\mathcal K|}\sum_{k\in\mathcal K}\frac{\|T_{base}^{-1}p_k^{ee}\|}{r}.$$

惩罚最小时，机器人在最大可达距离的约 65% 处操作，以保留运动学余量。每臂独立保留前五候选，再联合检查全部 25 个左右组合，选择最终基座。

**深度合成的实际规则。** 正文给了统一深度排序，但实现分机械臂主体与夹爪。通过 MuJoCo 每几何体分割掩码区分：机械臂主体总是叠到修复场景，因为假设它在相机和工作空间之间，不会被场景物体遮挡；夹爪逐像素比较深度。若场景更近、且像素不在膨胀人手掩码中，则隐藏夹爪。

场景深度由 Depth Anything V3 估计，机器人由 MuJoCo 渲染。人手掩码用 5×5 核膨胀一次，防止显露原手臂轮廓处的修复边缘。

$$I_{out}(u,v)=\begin{cases}
I_{sim}(u,v),&(u,v)\in M_{arm}\cup M_{gripper\_vis},\\
I_{inpaint}(u,v),&\text{其他情况},
\end{cases} \tag{9}$$

其中 $M_{gripper\_vis}$ 是从夹爪掩码中，减去“场景深度小于机器人深度且不在人手掩码内”的像素。

### A.5 清洗条件

L1 中一帧有效须同时满足：检测到人手；IK 跟踪误差小于 0.05 m；渲染机器人可见，像素数大于零；MuJoCo 接触检查没有自碰撞。若双臂交叉接触数大于一，或机器人掩码超过图像面积 70%，也标无效。

**稳定性侵蚀。** 两段无效帧之间，如果有效连续段短于 $\lfloor0.3\times\mathrm{fps}\rfloor$ 帧，也整段标无效。

L2 做两项事后统计检查。第一，对每个数据集、每个动作维，排除此前无效帧后计算 Q1/Q99，区间 $[Q1-3(Q99-Q1),Q99+3(Q99-Q1)]$ 外标异常。第二，在状态动作轨迹计算残差、加速度和 jerk，根据该数据集逐维分布设阈值，超阈值标异常。两过滤后，无效帧比例超过 60% 的示范整段丢弃。

L3 用 Qwen3.5，以 4 fps 抽取合成视频，加子任务描述进行审核。提示含义为：

```text
判断操作视频是否符合文字描述。
这是机器人操作数据集，“手”指机器人夹爪/末端执行器。
不少任务用假物体、玩具或仿真物体代替真实物体，这属于正常情况。
任务描述：{description}。
判断机器人动作是否符合任务。
标记重大不匹配：动作类型错误、物体类别错误、目标位置错误、执行失败。
容忍玩具、轻微外观变化、小的空间偏差和不同抓取方式。
用 JSON 回答：
{"is_consistent": true/false, "confidence": 0.0-1.0, "reasoning": "..."}
```

判断不一致的示范被丢弃。

### A.6 颜色随机化

每个渲染机器人采用可复现的 HSV 随机颜色：$H\sim U(0,1)$，$S\sim U(0.3,1)$，$V\sim U(0.4,1)$，同一机器人所有连杆统一使用该颜色。

### A.7 支持的机器人

**表 3：形态、自由度、夹爪开口和可达距离。** 可达距离按论文定义保留。

|机器人|自由度|夹爪 mm|可达距离 m|
|---|---:|---:|---:|
|Panda|7|0-80|1.272|
|Kinova Gen3|7|0-85|1.337|
|IIWA|7|0-85|1.411|
|Sawyer|7|14-79|1.420|
|FR3|7|0-80|1.272|
|xArm7|7|0-85|1.290|
|UR5e|6|0-85|1.236|
|UR10e|6|0-85|1.627|
|Jaco|6|0-125|1.200|
|ViperX|6|15-87|0.911|
|WidowX|6|11-55|0.787|
|ARX-L5|6|0-88|0.855|
|Piper|6|0-70|0.883|
|YAM|6|4-75|0.866|
|Aloha-Agilex|6|7-102|0.853|

【图 6】15 种机器人的三维模型。

## 附录 B：评测实现细节

### B.1 扰动参数

原始 Randomized 同时替换背景纹理、随机光照、桌高和杂物。我们拆开这些因素，再加入相机偏移、机器人颜色、改写指令和新物体。

背景从纹理库随机替换桌面和地面；光照随机位置和强度；所有机器人连杆统一施加 $[0^\circ,360^\circ)$ 色相变化。桌高 ±4 cm；杂物三至五个，随机姿态；头部相机每轴最多偏移 5 cm。

语义包括人工与大模型生成的 505 条口语指令。未见物体测试使用 50 个新任务，同类别但外观几何不同，分七组：

|任务组|数量|具体组合|
|---|---:|---|
|移到垫子或锅|10|瓶/杯/碗到垫子；杯/瓶/马克杯/苹果/印章/药瓶/碗到锅|
|放篮子|11|肥皂、马克杯、香水、茶盒、玩具车、苹果、瓶、杯、咖啡盒、酱料罐、汉堡|
|放支架|4|杯、马克杯、瓶、苹果|
|放秤上|3|瓶、杯、马克杯|
|放柜子|3|苹果、印章、碗|
|双臂 A 放到 B|12|cup-left-bottle、mug-right-apple、bottle-left-cup、seal-right-mug、mug-left-cup、apple-left-mug、bottle-right-apple、seal-left-cup、mug-left-bottle、apple-right-cup、cup-right-seal、bottle-left-apple|
|移开|7|杯、瓶、苹果、马克杯、印章、碗、药瓶|

双臂组合保留英文代码中的 left/right，避免把任务名里的臂侧信息误解成额外空间关系。

默认 Aloha-Agilex 用一个双臂 URDF。替代形态用两个独立单臂 URDF，在工作空间中心两侧对称放置。臂基座间距 ARX-X5 为 0.6 m，UR5-WSG 为 0.59 m，Franka 为 0.65 m。IK 对齐初始末端，头部加两腕共三个相机外参跨形态对齐。

### B.2 五十项训练评测任务

下面保留任务代码并给出中文名称，方便对照代码和逐任务表。

|代码|中文|
|---|---|
|adjust_bottle|调整瓶子|
|beat_block_hammer|用锤敲积木|
|blocks_ranking_rgb|按 RGB 颜色排列积木|
|blocks_ranking_size|按大小排列积木|
|click_alarmclock|按闹钟|
|click_bell|按铃|
|dump_bin_bigbin|小桶内容倒入大桶|
|grab_roller|抓滚筒|
|handover_block|交接积木|
|handover_mic|交接麦克风|
|hanging_mug|挂马克杯|
|lift_pot|抬锅|
|move_can_pot|罐子移到锅|
|move_pillbottle_pad|药瓶移到垫子|
|move_playingcard_away|移开扑克牌|
|move_stapler_pad|订书机移到垫子|
|open_laptop|打开笔记本电脑|
|open_microwave|打开微波炉|
|pick_diverse_bottles|抓取多样瓶子|
|pick_dual_bottles|双臂抓瓶|
|place_a2b_left|左侧 A 到 B 放置|
|place_a2b_right|右侧 A 到 B 放置|
|place_bread_basket|面包放篮子|
|place_bread_skillet|面包放煎锅|
|place_burger_fries|汉堡与薯条放置|
|place_can_basket|罐子放篮子|
|place_cans_plasticbox|多个罐子放塑料盒|
|place_container_plate|容器放盘子|
|place_dual_shoes|双臂放鞋|
|place_empty_cup|放空杯|
|place_fan|放风扇|
|place_mouse_pad|鼠标放垫子|
|place_object_basket|物体放篮子|
|place_object_scale|物体放秤|
|place_object_stand|物体放支架|
|place_phone_stand|手机放支架|
|place_shoe|放鞋|
|press_stapler|按订书机|
|put_bottles_dustbin|瓶子放垃圾桶|
|put_object_cabinet|物体放柜子|
|rotate_qrcode|旋转二维码|
|scan_object|扫描物体|
|shake_bottle|摇瓶子|
|shake_bottle_horizontally|水平摇瓶子|
|stack_blocks_three|叠三积木|
|stack_blocks_two|叠两积木|
|stack_bowls_three|叠三碗|
|stack_bowls_two|叠两碗|
|stamp_seal|盖章|
|turn_switch|拨开关|

任务步数上限从 400 到 1700，多数为 400；开微波炉 1500，排列积木与叠三积木 1200，叠碗 900-1200，挂杯 900，叠两积木、交接积木、罐子入塑料盒 800，瓶子入垃圾桶 1700。新任务默认 1000。

### B.3 统计协议

每任务 50 次，二值成功。Visual 为背景、光照、机器人颜色平均；Scene 为桌高、杂物、相机平均；Embodiment 为 ARX、UR5、Franka 平均；Task 为新物体、改写语言平均。

### B.4 EBench 桌面任务

七项是收集咖啡豆、翻杯并收集饼干、把框靠在笔筒上、安装齿轮、插销入孔、玻璃杯放玻璃盒、拧紧螺母。相机比 RoboTwin 高，接近第一人称视角。

## 附录 C：模型细节

Qwen3.5-4B 输入每个时间点两至三张 RGB 视图和结构文本，得到联合视觉语言隐藏序列 $H\in\mathbb R^{L\times d}$。相机内参 $K\in\mathbb R^{3\times3}$ 和外参 $T_{wc}\in SE(3)$ 通过 mRoPE 位置编码注入视觉特征，帮助理解相机与场景的三维关系。

上下文生成器使用八个可学习 query，把 $H$ 压缩成条件特征 $C$；DiT 通过交叉注意力关注 $C$，用流匹配生成 32 步动作块。每次前向八次训练采样、推理四步。

### C.1 结构化提示

```text
embodiment: {type}_{model}
instruction: {task_description}
```

形态字段同时表示来源和机器人型号，例如 `robot_aloha` 为真实机器人，`h2r_arx` 为 ARX 合成，`human_ego` 为原始人类数据。训练以 15% 概率把形态字段改成 `None`，指令从不丢弃。

### C.2 相机系相对末端动作

每步七维：三维位移 $\Delta p$、三维旋转向量 $\Delta\omega$、一维夹爪。末端到相机变换为 $T_{ce}=T_{wc}^{-1}T_{we}$，旋转部分为 $R_{ce}$，增量变换：

$$\Delta p^{cc}=R_{ce}\Delta p^{ee},\qquad
\Delta R^{cc}=R_{ce}\Delta R^{ee}R_{ce}^{\top}. \tag{10}$$

作者表示，这自然统一不同相机和形态的数据，不需要额外显式外参标定。

> 原文表述提示：这一段文字称“基座系增量”，公式却用末端系 $ee$ 上标；正文又强调相机参数作为样本内容，附录说“不需显式标定”。理解时可以区分“不额外逐视频标定世界坐标系”和“完全不需要任何相机几何信息”。译文保留原公式及原文主张，不擅自将坐标定义改成一致版本。

### C.3 流匹配

令干净动作为 $a_0$，噪声为 $\epsilon\sim\mathcal N(0,I)$：

$$a_t=(1-t)a_0+t\epsilon,\qquad t\in[0,1]. \tag{11}$$

$$\mathcal L=\mathbb E_{t,a_0,\epsilon}\|v_\theta(a_t,t,c)-(\epsilon-a_0)\|^2. \tag{12}$$

$c$ 为视觉语言条件。推理用四步欧拉，步长 1/4。

> 这里从干净动作到噪声定义路径，目标速度是“噪声减动作”；Qwen-RobotManip 从噪声到动作定义路径，目标速度相反。两篇采用相反时间方向，不能直接混用符号。

## 附录 D：训练细节

### D.1 预训练

八张 A100，每 GPU 批量 12；主干学习率 $10^{-5}\to10^{-6}$ 余弦衰减，预热 5K 步；动作头学习率十倍，为 $10^{-4}\to10^{-5}$。AdamW，$\beta_1=0.9,\beta_2=0.95$；bf16、ZeRO-1；200K 步，约 19.2M 帧；每次前向八次扩散训练采样；不做图像增强。

### D.2 数据与比例

机器人数据：DROID 约 511 小时，Franka 上丰富物体场景的真实遥操作；AgibotWorld 约 2,404 小时，180 项人形操作任务；InternData 约 3,650 小时，Franka、人形、ALOHA 仿真。合计约 6,565 小时。

第一人称数据：ANT 7、EgoDex 732、ViTRA 249、EgoVerse 954 小时，共约 1,940。15 形态合成清洗后为 18,561。

1:3、3:1、1:1 是通过每来源采样权重实现的训练混合比例。所有配置总训练帧数一样。

【图 7：数据组成饼图】机器人总量约 6,565 小时，Ego2R 总量约 18,561；扇区表示来源的训练采样权重，不是简单的原始时长占比。

### D.3 微调

加载预训练权重，八 A100，每 GPU 批量 12，主干和动作头学习率、预热、优化器、bf16 同预训练；改为 ZeRO-2，加入 ColorJitter，每前向八次扩散训练采样。

|目标|数据|步数|动作块与重规划|
|---|---|---:|---|
|RoboTwin Clean|50 任务×50 示范，2,500 段|50K|块长 20，每 16 步重规划|
|EBench Table Top|7 任务×400 示范，2,800 段|50K|块长 32|
|真实机器人|遥操作与 Ego2R 1:1|50K|块长 32|

### D.4 消融配置

图 3 全部只用人类来源预训练，不混机器人，然后在 RoboTwin Clean 微调：

|配置|时长|形态|
|---|---:|---|
|原始第一人称|约 1,940 小时|已按流程质量过滤，不渲染机器人|
|Ego2R 一形态|约 1,237|ARX-L5|
|Ego2R 五形态|约 6,187|Aloha-Agilex、ARX-L5、FR3、ViperX、xArm7|
|Ego2R 十形态|约 12,374|Aloha-Agilex、ARX-L5、FR3、IIWA、Jaco、Piper、UR5e、ViperX、YAM、xArm7|
|Ego2R 十五形态|约 18,561|全部十五|
|十五形态 + 原始第一人称|约 20,501|合成加原始人类数据|

## 附录 E：真实机器人实验细节

### E.1 平台与任务

ARX ACone 双臂，每臂六自由度、平行夹爪，头部加两腕 RGB 相机，15 Hz 控制，每 32 步重规划。

- 放水果：三步，依次把三个水果放篮子。
- 放积木：四步，开抽屉、放两块积木、关抽屉。
- 折毛巾：两次连续折叠。
- 扫垃圾：四步，拿扫帚、扫、倒垃圾、放回扫帚。
- 插螺钉：四步，对两颗螺钉分别进行双臂交接和插入。

### E.2 数据

每任务 20 遥操作示范，共 100；五场景约 35 分钟 Ego Play。路径 B 的 WiLoR、DynHaMR、Qwen3.5 与 Ego2R 生成 675 段 ACone 合成示范。微调中遥操作与合成数据按 1:1 采样。

### E.3 可视化

【图 8：自由操作视频到机器人合成】上排原始第一人称人手视频，下排 ACone 叠到修复背景后的对应帧。

### E.4 计分

每任务 20 次，采用子步骤部分计分，任务满分 100。

**表 4：每一步分值。**

|任务|第一步|第二步|第三步|第四步|
|---|---:|---:|---:|---:|
|放水果|33.3|33.3|33.3|—|
|放积木|25|25|25|25|
|折毛巾|50|50|—|—|
|扫垃圾|25|25|25|25|
|插螺钉|25|25|25|25|

## 附录 F：补充实验

### F.1 与 π0.5 比较

π0.5 在相同 RoboTwin 末端设置中评估，使用 OpenPI 和相机系相对末端动作。它的主干及预训练数据与本文不同。

【图 9】沿背景、光照、颜色、桌高、杂物、相机、ARX、UR5、Franka、新任务和改写语言，比较 π0.5、仅机器人和 1:1 合成混合模型。合成混合在几乎所有设置优于仅机器人，但 Franka 不在此收益模式中。

### F.2 逐任务结果

**表 5：RoboTwin 各任务成功率 %。** 每格为 **Clean / Randomized**。任务中文对照见 B.2，混合比例仍是 Ego2R : Robot。

|任务|π0.5|仅机器人|1:3|3:1|1:1|
|---|---|---|---|---|---|
|adjust_bottle|62 / 18|94 / 77|92 / 79|100 / 72|89 / 91|
|beat_block_hammer|48 / 16|63 / 27|64 / 56|57 / 18|65 / 71|
|blocks_ranking_rgb|74 / 16|56 / 60|64 / 63|49 / 43|78 / 60|
|blocks_ranking_size|32 / 0|30 / 22|46 / 21|43 / 7|52 / 16|
|click_alarmclock|44 / 56|96 / 93|100 / 87|100 / 85|100 / 100|
|click_bell|32 / 40|100 / 95|100 / 94|100 / 93|100 / 100|
|dump_bin_bigbin|72 / 70|54 / 73|72 / 69|81 / 76|86 / 72|
|grab_roller|94 / 46|98 / 71|68 / 48|91 / 64|89 / 63|
|handover_block|16 / 0|5 / 2|18 / 4|39 / 9|36 / 9|
|handover_mic|26 / 4|69 / 13|86 / 34|83 / 17|97 / 23|
|hanging_mug|10 / 4|14 / 16|14 / 9|12 / 9|10 / 10|
|lift_pot|8 / 2|93 / 28|84 / 14|95 / 44|93 / 44|
|move_can_pot|28 / 0|47 / 50|30 / 40|42 / 85|47 / 65|
|move_pillbottle_pad|60 / 44|63 / 60|68 / 69|41 / 67|74 / 82|
|move_playingcard_away|90 / 52|74 / 58|88 / 92|88 / 42|92 / 63|
|move_stapler_pad|22 / 6|23 / 19|34 / 21|30 / 13|43 / 31|
|open_laptop|68 / 20|77 / 61|74 / 56|64 / 46|75 / 58|
|open_microwave|26 / 8|77 / 59|42 / 29|37 / 32|50 / 25|
|pick_diverse_bottles|56 / 18|60 / 37|58 / 53|71 / 50|70 / 50|
|pick_dual_bottles|82 / 14|91 / 59|80 / 77|83 / 55|97 / 54|
|place_a2b_left|60 / 10|40 / 55|58 / 42|54 / 48|73 / 44|
|place_a2b_right|58 / 14|42 / 49|52 / 41|53 / 51|64 / 53|
|place_bread_basket|68 / 44|75 / 55|72 / 64|76 / 59|79 / 62|
|place_bread_skillet|86 / 46|76 / 41|76 / 50|80 / 61|87 / 53|
|place_burger_fries|90 / 78|96 / 83|98 / 81|97 / 88|96 / 88|
|place_can_basket|40 / 0|49 / 25|38 / 9|34 / 15|34 / 16|
|place_cans_plasticbox|94 / 74|90 / 68|54 / 68|97 / 59|70 / 59|
|place_container_plate|96 / 58|86 / 76|92 / 79|93 / 73|93 / 81|
|place_dual_shoes|54 / 12|50 / 30|34 / 27|35 / 17|35 / 19|
|place_empty_cup|74 / 56|73 / 74|86 / 83|88 / 78|88 / 66|
|place_fan|36 / 30|48 / 54|48 / 24|41 / 50|39 / 46|
|place_mouse_pad|18 / 0|41 / 34|22 / 36|30 / 25|29 / 33|
|place_object_basket|24 / 4|65 / 50|76 / 28|77 / 51|69 / 48|
|place_object_scale|58 / 44|38 / 46|40 / 33|52 / 45|40 / 47|
|place_object_stand|94 / 40|70 / 75|80 / 77|87 / 71|82 / 82|
|place_phone_stand|40 / 4|65 / 49|48 / 63|70 / 61|75 / 45|
|place_shoe|64 / 24|84 / 84|78 / 84|63 / 58|75 / 76|
|press_stapler|42 / 32|86 / 71|82 / 62|76 / 70|83 / 62|
|put_bottles_dustbin|14 / 2|25 / 20|42 / 32|41 / 19|50 / 39|
|put_object_cabinet|22 / 0|41 / 20|30 / 19|39 / 36|43 / 29|
|rotate_qrcode|50 / 2|31 / 17|54 / 16|54 / 36|69 / 37|
|scan_object|62 / 38|62 / 37|66 / 46|66 / 46|56 / 33|
|shake_bottle|96 / 72|91 / 75|88 / 89|99 / 75|96 / 87|
|shake_bottle_horizontally|98 / 74|98 / 81|84 / 87|99 / 84|97 / 92|
|stack_blocks_three|68 / 16|14 / 23|14 / 28|10 / 13|28 / 23|
|stack_blocks_two|80 / 56|75 / 70|82 / 75|77 / 56|95 / 61|
|stack_bowls_three|38 / 36|50 / 41|40 / 43|48 / 50|47 / 45|
|stack_bowls_two|82 / 44|76 / 78|66 / 73|73 / 67|72 / 72|
|stamp_seal|32 / 2|35 / 42|46 / 30|34 / 30|44 / 42|
|turn_switch|56 / 40|55 / 42|40 / 42|53 / 41|50 / 48|
|平均|54.9 / 27.7|62.2 / 50.9|61.4 / 51.0|64.1 / 49.2|68.1 / 53.5|


## 参考文献（原文保留，便于检索）

```text
[1] B. Zitkovich, T. Yu, S. Xu, P. Xu, T. Xiao, F. Xia, J. Wu, P. Wohlhart, S. Welker, A. Wahid,
     et al. Rt-2: Vision-language-action models transfer web knowledge to robotic control. In
     Conference on Robot Learning, pages 2165–2183. PMLR, 2023.

 [2] M. J. Kim, K. Pertsch, S. Karamcheti, T. Xiao, A. Balakrishna, S. Nair, R. Rafailov, E. Foster,
     G. Lam, P. Sanketi, et al. Openvla: An open-source vision-language-action model. arXiv
     preprint arXiv:2406.09246, 2024.

 [3] K. Black, N. Brown, D. Driess, A. Esmail, M. Equi, C. Finn, N. Fusai, L. Groom, K. Hausman,
     B. Ichter, et al. pi 0: A vision-language-action flow model for general robot control. arXiv
     preprint arXiv:2410.24164, 2024.

 [4] P. Intelligence, K. Black, N. Brown, J. Darpinian, K. Dhabalia, D. Driess, A. Esmail, M. Equi,
     C. Finn, N. Fusai, et al. pi {0.5}: a vision-language-action model with open-world general-
     ization. arXiv preprint arXiv:2504.16054, 2025.

 [5] J. Bjorck, F. Castañeda, N. Cherniadev, X. Da, R. Ding, L. Fan, Y. Fang, D. Fox, F. Hu,
     S. Huang, et al. Gr00t n1: An open foundation model for generalist humanoid robots. arXiv
     preprint arXiv:2503.14734, 2025.

 [6] A. O’Neill, A. Rehman, A. Maddukuri, A. Gupta, A. Padalkar, A. Lee, A. Pooley, A. Gupta,
     A. Mandlekar, A. Jain, et al. Open x-embodiment: Robotic learning datasets and rt-x models:
     Open x-embodiment collaboration 0. In 2024 IEEE International Conference on Robotics and
     Automation (ICRA), pages 6892–6903. IEEE, 2024.

 [7] A. Khazatsky, K. Pertsch, S. Nair, A. Balakrishna, S. Dasari, S. Karamcheti, S. Nasiriany,
     M. K. Srirama, L. Y. Chen, K. Ellis, et al. Droid: A large-scale in-the-wild robot manipulation
     dataset. arXiv preprint arXiv:2403.12945, 2024.

 [8] Q. Bu, J. Cai, L. Chen, X. Cui, Y. Ding, S. Feng, S. Gao, X. He, X. Hu, X. Huang, et al. Agibot
     world colosseo: A large-scale manipulation platform for scalable and intelligent embodied
     systems. arXiv preprint arXiv:2503.06669, 2025.

 [9] C. Chi, Z. Xu, C. Pan, E. Cousineau, B. Burchfiel, S. Feng, R. Tedrake, and S. Song. Universal
     manipulation interface: In-the-wild robot teaching without in-the-wild robots. arXiv preprint
     arXiv:2402.10329, 2024.

[10] T. Z. Zhao, V. Kumar, S. Levine, and C. Finn. Learning fine-grained bimanual manipulation
     with low-cost hardware. arXiv preprint arXiv:2304.13705, 2023.

[11] P. Wu, Y. Shentu, Z. Yi, X. Lin, and P. Abbeel. Gello: A general, low-cost, and intuitive
     teleoperation framework for robot manipulators. In 2024 IEEE/RSJ International Conference
     on Intelligent Robots and Systems (IROS), pages 12156–12163. IEEE, 2024.

[12] R. Hoque, P. Huang, D. J. Yoon, M. Sivapurapu, and J. Zhang. Egodex: Learning dexterous
     manipulation from large-scale egocentric video. arXiv preprint arXiv:2505.11709, 2025.

[13] R. Punamiya, S. Kareer, Z. Liu, J. Citron, R.-Z. Qiu, X. Cai, A. Gavryushin, J. Chen, D. Li-
     conti, L. Y. Zhu, et al. Egoverse: An egocentric human dataset for robot learning from around
     the world. arXiv preprint arXiv:2604.07607, 2026.

[14] M. Lepert, J. Fang, and J. Bohg. Phantom: Training robots without robots using only human
     videos. In Conference on Robot Learning, pages 4545–4565. PMLR, 2025.

[15] S. Kareer, D. Patel, R. Punamiya, P. Mathur, S. Cheng, C. Wang, J. Hoffman, and D. Xu.
     Egomimic: Scaling imitation learning via egocentric video. In 2025 IEEE International Con-
     ference on Robotics and Automation (ICRA), pages 13226–13233. IEEE, 2025.



[16] T. Chen, Z. Chen, B. Chen, Z. Cai, Y. Liu, Z. Li, Q. Liang, X. Lin, Y. Ge, Z. Gu, et al.
     Robotwin 2.0: A scalable data generator and benchmark with strong domain randomization
     for robust bimanual robotic manipulation. arXiv preprint arXiv:2506.18088, 2025.

[17] N. M. M. Shafiullah, A. Rai, H. Etukuru, Y. Liu, I. Misra, S. Chintala, and L. Pinto. On
     bringing robots home. arXiv preprint arXiv:2311.16098, 2023.

[18] L. Pei, H. Yuzhe, L. Wanlin, X. Chenxi, and J. Ziyuan. Dexmove: Learning tactile-guided
     non-prehensile manipulation with dexterous hands. In The Fourteenth International Con-
     ference on Learning Representations, 2026. URL https://openreview.net/forum?id=
     dT3ZciXvNX.

[19] S. Nair, A. Rajeswaran, V. Kumar, C. Finn, and A. Gupta. R3m: A universal visual represen-
     tation for robot manipulation. arXiv preprint arXiv:2203.12601, 2022.

[20] I. Radosavovic, T. Xiao, S. James, P. Abbeel, J. Malik, and T. Darrell. Real-world robot
     learning with masked visual pre-training. In Conference on Robot Learning, pages 416–426.
     PMLR, 2023.

[21] Y. J. Ma, S. Sodhani, D. Jayaraman, O. Bastani, V. Kumar, and A. Zhang. Vip: Towards
     universal visual reward and representation via value-implicit pre-training. arXiv preprint
     arXiv:2210.00030, 2022.

[22] A. S. Chen, S. Nair, and C. Finn. Learning generalizable robotic reward functions from” in-
     the-wild” human videos. arXiv preprint arXiv:2103.16817, 2021.

[23] C. Wang, L. Fan, J. Sun, R. Zhang, L. Fei-Fei, D. Xu, Y. Zhu, and A. Anandkumar. Mimicplay:
     Long-horizon imitation learning by watching human play. arXiv preprint arXiv:2302.12422,
     2023.

[24] M. Xu, Z. Xu, Y. Xu, C. Chi, G. Wetzstein, M. Veloso, and S. Song. Flow as the cross-domain
     manipulation interface. arXiv preprint arXiv:2407.15208, 2024.

[25] J. Ren, P. Sundaresan, D. Sadigh, S. Choudhury, and J. Bohg. Motion tracks: A unified repre-
     sentation for human-robot transfer in few-shot imitation learning. In 2025 IEEE International
     Conference on Robotics and Automation (ICRA), pages 8802–8810. IEEE, 2025.

[26] R. Zheng, D. Niu, Y. Xie, J. Wang, M. Xu, Y. Jiang, F. Castañeda, F. Hu, Y. L. Tan, L. Fu, et al.
     Egoscale: Scaling dexterous manipulation with diverse egocentric human data. arXiv preprint
     arXiv:2602.16710, 2026.

[27] H. Luo, Y. Feng, W. Zhang, S. Zheng, Y. Wang, H. Yuan, J. Liu, C. Xu, Q. Jin, and Z. Lu.
     Being-h0: vision-language-action pretraining from large-scale human videos. arXiv preprint
     arXiv:2507.15597, 2025.

[28] H. Luo, Y. Wang, W. Zhang, S. Zheng, Z. Xi, C. Xu, H. Xu, H. Yuan, C. Zhang, Y. Wang,
     et al. Being-h0. 5: Scaling human-centric robot learning for cross-embodiment generalization.
     arXiv preprint arXiv:2601.12993, 2026.

[29] Q. Li, Y. Deng, Y. Liang, L. Luo, L. Zhou, C. Yao, L. Zeng, Z. Feng, H. Liang, S. Xu, et al.
     Scalable vision-language-action model pretraining for robotic manipulation with real-life hu-
     man activity videos. arXiv preprint arXiv:2510.21571, 2025.

[30] T. Zhang, S. Xia, Y. Wang, and Q. Jin. Easymimic: A low-cost framework for robot imitation
     learning from human videos. arXiv preprint arXiv:2602.11464, 2026.

[31] A. Mandlekar, S. Nasiriany, B. Wen, I. Akinola, Y. Narang, L. Fan, Y. Zhu, and D. Fox.
     Mimicgen: A data generation system for scalable robot learning using human demonstrations.
     arXiv preprint arXiv:2310.17596, 2023.



[32] S. Nasiriany, A. Maddukuri, L. Zhang, A. Parikh, A. Lo, A. Joshi, A. Mandlekar, and Y. Zhu.
     Robocasa: Large-scale simulation of everyday tasks for generalist robots. arXiv preprint
     arXiv:2406.02523, 2024.

[33] L. Y. Chen, C. Xu, K. Dharmarajan, M. Z. Irshad, R. Cheng, K. Keutzer, M. Tomizuka,
     Q. Vuong, and K. Goldberg. Rovi-aug: Robot and viewpoint augmentation for cross-
     embodiment robot learning. arXiv preprint arXiv:2409.03403, 2024.

[34] L. Y. Chen, K. Hari, K. Dharmarajan, C. Xu, Q. Vuong, and K. Goldberg. Mirage: Cross-
     embodiment zero-shot policy transfer with cross-painting. arXiv preprint arXiv:2402.19249,
     2024.

[35] G. Ji, H. Polavaram, L. Y. Chen, S. Bajamahal, Z. Ma, S. Adebola, C. Xu, and K. Goldberg.
     Oxe-auge: A large-scale robot augmentation of oxe for scaling cross-embodiment policy learn-
     ing. arXiv preprint arXiv:2512.13100, 2025.

[36] Y. Mu, T. Chen, Z. Chen, S. Peng, Z. Lan, Z. Gao, Z. Liang, Q. Yu, Y. Zou, M. Xu, et al.
     Robotwin: Dual-arm robot benchmark with generative digital twins. In Proceedings of the
     computer vision and pattern recognition conference, pages 27649–27660, 2025.

[37] B. Liu, Y. Zhu, C. Gao, Y. Feng, Q. Liu, Y. Zhu, and P. Stone. Libero: Benchmarking knowl-
     edge transfer for lifelong robot learning. Advances in Neural Information Processing Systems,
     36:44776–44791, 2023.

[38] O. Mees, L. Hermann, E. Rosete-Beas, and W. Burgard. Calvin: A benchmark for language-
     conditioned policy learning for long-horizon robot manipulation tasks. IEEE Robotics and
     Automation Letters, 7(3):7327–7334, 2022.

[39] S. James, Z. Ma, D. R. Arrojo, and A. J. Davison. Rlbench: The robot learning benchmark &
     learning environment. IEEE Robotics and Automation Letters, 5(2):3019–3026, 2020.

[40] X. Li, K. Hsu, J. Gu, K. Pertsch, O. Mees, H. R. Walke, C. Fu, I. Lunawat, I. Sieh, S. Kir-
     mani, et al. Evaluating real-world robot manipulation policies in simulation. arXiv preprint
     arXiv:2405.05941, 2024.

[41] J. Gu, F. Xiang, X. Li, Z. Ling, X. Liu, T. Mu, Y. Tang, S. Tao, X. Wei, Y. Yao, et al. Maniskill2:
     A unified benchmark for generalizable manipulation skills. arXiv preprint arXiv:2302.04659,
     2023.

[42] S. Tao, F. Xiang, A. Shukla, Y. Qin, X. Hinrichsen, X. Yuan, C. Bao, X. Lin, Y. Liu, T.-k.
     Chan, et al. Maniskill3: Gpu parallelized robotics simulation and rendering for generalizable
     embodied ai. arXiv preprint arXiv:2410.00425, 2024.

[43] W. Pumacay, I. Singh, J. Duan, R. Krishna, J. Thomason, and D. Fox. The colosseum: A bench-
     mark for evaluating generalization for robotic manipulation. arXiv preprint arXiv:2402.08191,
     2024.

[44] S. Fei, S. Wang, J. Shi, Z. Dai, J. Cai, P. Qian, L. Ji, X. He, S. Zhang, Z. Fei, et al.
     Libero-plus: In-depth robustness analysis of vision-language-action models. arXiv preprint
     arXiv:2510.13626, 2025.

[45] X. Zhou, Y. Xu, G. Tie, Y. Chen, G. Zhang, D. Chu, P. Zhou, and L. Sun. Libero-pro: To-
     wards robust and fair evaluation of vision-language-action models beyond memorization. arXiv
     preprint arXiv:2510.03827, 2025.

[46] S. A. Laboratory. Ebench: Elemental mobile manipulation benchmark, 2026. URL https:
     //internrobotics.github.io/EBench-doc/. Preprint coming soon.



[47] R. A. Potamias, J. Zhang, J. Deng, and S. Zafeiriou. Wilor: End-to-end 3d hand localization
     and reconstruction in-the-wild. In Proceedings of the Computer Vision and Pattern Recognition
     Conference, pages 12242–12254, 2025.
[48] C. Si, Y. Liu, B. Ai, J. Xie, R. A. Potamias, C. Zheng, and H. Su. Anyhand: A large-scale
     synthetic dataset for rgb (-d) hand pose estimation. arXiv preprint arXiv:2603.25726, 2026.

[49] Z. Yu, S. Zafeiriou, and T. Birdal. Dyn-hamr: Recovering 4d interacting hand motion from a
     dynamic camera. In Proceedings of the Computer Vision and Pattern Recognition Conference,
     pages 27716–27726, 2025.
[50] Q. Team. Qwen3. 5: Accelerating productivity with native multimodal agents, february 2026.
     URL https://qwen. ai/blog.
[51] N. Carion, L. Gustafson, Y.-T. Hu, S. Debnath, R. Hu, D. Suris, C. Ryali, K. V. Alwala,
     H. Khedr, A. Huang, et al. Sam 3: Segment anything with concepts. arXiv preprint
     arXiv:2511.16719, 2025.
[52] S. Zhou, C. Li, K. C. Chan, and C. C. Loy. Propainter: Improving propagation and transformer
     for video inpainting. In Proceedings of the IEEE/CVF international conference on computer
     vision, pages 10477–10486, 2023.
[53] E. Todorov, T. Erez, and Y. Tassa. Mujoco: A physics engine for model-based control. In 2012
     IEEE/RSJ international conference on intelligent robots and systems, pages 5026–5033. IEEE,
     2012.

[54] K. Zakka. Mink: Python inverse kinematics based on MuJoCo, Feb. 2026. URL https:
     //github.com/kevinzakka/mink.
[55] Y. Tian, Y. Yang, Y. Xie, Z. Cai, X. Shi, N. Gao, H. Liu, X. Jiang, Z. Qiu, F. Yuan, et al.
     Interndata-a1: Pioneering high-fidelity synthetic data for pre-training generalist policy. arXiv
     preprint arXiv:2511.16651, 2025.
```
