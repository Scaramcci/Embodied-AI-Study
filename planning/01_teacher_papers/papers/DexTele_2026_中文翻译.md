# DexTele：基于动作重定向与自适应力控制的双臂灵巧遥操作系统

> 原文：*DexTele: A Dual-Arm Dexterous Teleoperation System Based on Motion Retargeting and Adaptive Force Control*  
> 作者：Yuanchuan Lai、Qing Gao、Ziyan Liang、Xianfeng Cheng、Junjie Hu、Zhaojie Ju  
> arXiv:2607.05883v1，2026-07-07  
> 说明：本文为学习用中文全译稿。公式编号、图表编号与参考文献编号均与原文一致；论文图片请对照同目录原始 PDF，参考文献保留英文书目信息以便检索。

## 摘要

在双臂灵巧遥操作中，动作重定向的跨平台泛化能力与抓取的交互适应能力至关重要。然而，不同机器人的结构差异以及被抓物体的多样性，使双臂灵巧遥操作难以同时实现精确动作重定向与柔顺抓取。为解决这些问题，本文提出一种基于动作重定向和自适应力控制的双臂灵巧遥操作系统 DexTele。

首先，系统设计了一个基于视觉的动作重定向模块，根据人体图像生成初步机器人动作。该模块通过动作图编码器与潜在空间优化，实现精确、便捷的跨平台动作重定向。其次，系统设计自适应抓取模块以实现柔顺抓取。该模块结合视觉—语言模型（VLM）与模型预测控制（MPC），预测目标物体所需的抓取力，并进行基于梯度的在线优化。大量实验表明，DexTele 能够实现精确动作重定向和柔顺抓取，并可泛化到多种机器人平台。项目页面：<https://github.io/DexTele>。

## I. 引言

机器人遥操作使人类操作者能够远程控制机器人完成复杂任务。动作重定向是其中的关键环节，它把人体动作映射到机器人，使机器人自然、准确地复现人的运动。现有系统常通过直接映射实现动作重定向，这在简单任务中效果尚可 [1], [2]，但扩展到多种机器人平台时便显现局限。这些方法通常只面向单一平台，缺少跨平台泛化能力，容易在结构不同的机器人上产生重定向误差，影响操作的自然性与可靠性。

在灵巧手遥操作中，手部动作不仅要复现人的手势，还要适应与物体交互的特性，才能保证操作准确、安全 [3], [4]。自适应抓取因此格外重要：机器人可以根据物体属性调整动作，保证操作过程的稳定性和安全性。总体而言，跨平台泛化能力、重定向精度和自适应抓取共同决定遥操作系统是否实用可靠。

如图 1(a) 所示，现有重定向方法通常依赖成对的人—机器人数据集训练监督映射模型 [5]–[7]。这种方法虽然能提高特定场景中的精度，但每增加一个机器人平台，都需要额外采集成对数据，因而限制了泛化能力。在手部遥操作方面，主流方法常使用位置控制或固定力阈值 [8]–[10]，如图 1(b) 所示，无法灵活适应多种物体。由此产生两个主要问题：动作重定向方法难以跨机器人平台泛化；手部控制方法不能为不同物体提供自适应抓取。

要克服这些局限，需要一个统一遥操作系统，同时支持高效跨平台重定向与灵巧操作中的自适应抓取。对此可以沿两个方向解决。第一，把跨平台重定向重新表示为基于图的跨拓扑映射问题，在统一图结构中描述人和机器人之间的结构关系。把得到的特征嵌入潜在空间后进行优化，只需使用人体动作数据，无须额外成对数据集，即可在不同机器人平台间完成动作重定向。第二，把手部抓取从固定阈值控制提升为结合语义推理与动态优化的智能策略：VLM 理解物体属性，MPC 主动生成力控制，从而在复杂物体交互场景中提高灵巧手的稳定性与适应性。

基于上述思路，我们提出图 1(c) 所示的 DexTele。DexTele 使用带双流输入—输出设计的空间注意力门控图卷积网络（Spatial Attention Gated Graph Convolutional Network，SAG-GCN），在共享中间表示的同时分别处理手臂和手部动作，从而提高不同机器人平台上的重定向精度。与此同时，自适应抓取模块使用 VLM 推断物体类别并推荐合适的抓取力，再将结果送入 MPC 进行在线优化，生成兼顾安全性、稳定性和前瞻性的自适应抓取策略。大量仿真和真实实验表明，DexTele 能够实现精确动作重定向与柔顺抓取，并可泛化到多个机器人平台。

本文贡献如下：

- 提出 DexTele，用于解决遥操作中的跨平台动作重定向与自适应抓取问题。它既能在不同机器人上精确重定向动作，也能稳定、灵活地抓取物体，从而弥补现有方法的不足。
- 提出基于视觉的动作重定向模块。该模块使用 SAG-GCN 建模人—机器人拓扑，并以双流输入—输出结构分别处理手臂与手部动作，实现精确的跨平台动作重定向。
- 提出用于柔顺抓取的自适应抓取模块。该模块结合 VLM 与 MPC，预测合适的抓取力并在线优化，从而稳定、自适应地抓取物体。

**图 1：** 遥操作系统示意图。(a) 以往的动作重定向工作；(b) 以往的力控制工作；(c) 本文提出的灵巧遥操作流程。

## II. 相关工作

### A. 人到机器人动作重定向

人—机器人动作重定向旨在把人体动作映射到运动学结构和自由度不同的机器人上，实现高保真动作复现。VR 头显、数据手套和基于标记点的光学系统等传统动作捕捉方法 [14], [15] 精度较高，但设备笨重、成本高，也会影响操作者舒适度。为解决这些问题，基于视觉的非接触方法凭借低成本、易部署的特点受到关注 [16]。本文沿用这一思路，采用标准 RGB 相机和三维人体姿态估计算法 FrankMocap [30] 捕捉人的手臂—手部姿态，用于生成机器人动作。

当前人—机器人动作重定向主要关注单个身体部位，如手或手臂 [17], [20]，限制了实际应用。一些研究使用基于运动学的方法进行手臂—手部联合重定向，具备跨平台适应能力，但难以高保真复现动作。Li 等人 [18] 提出了由运动学驱动、可适应不同平台的手臂重定向方法；Qin 等人 [19] 提出了类似方法，但也存在精度限制。另一些方法依赖成对的人—机器人数据。Zeng 等人 [21] 开发了带自适应力控制的遥操作系统，在训练平台上有效；Li 等人 [22] 为 Shadow 灵巧手提出基于视觉的端到端框架，精度较高，但只适用于该机器人。

为克服这些局限，SAG-GCN 把人体动作和基于 URDF 的机器人模型编码为动作图，并进行潜在空间优化。它进一步采用双流输入—输出设计，分别处理手臂和手部，同时共享中间表示，从而在多个机器人平台上实现精确且可扩展的动作重定向。

### B. 基于力反馈的自适应灵巧抓取

复杂环境中的灵巧抓取与操作是实现人类水平机器人操作的核心。然而，物体在材质、形状和质量上的差异，使系统难以确定合适的抓取力并在执行过程中动态调节；这仍是自适应抓取的关键挑战。传统方法常采用位置控制或开环力控制 [23], [24]，虽然能完成基本拾取与放置任务，却难以安全处理易碎、可变形物体，也难以适应外部扰动。一些研究使用力传感器进行闭环控制，或通过阻抗控制增强稳定性 [25], [26]，但通常需要准确建模手—物交互动力学，部署复杂，也限制了多物体场景中的泛化。

近期研究把机器学习与 MPC 结合，通过学习关节角与接触力之间的映射实现力预测和调节。例如，Xu 等人 [27] 使用 GelSight 触觉反馈在线调整；Shi 等人 [28] 用高斯过程建模状态—力关系，并将其纳入带安全约束的 MPC；Tian 等人 [29] 把深度强化学习与力反馈结合，用于多指自适应抓取控制。这些方法虽然能够在线控制和预测力，但多数依赖离线训练，或缺少对目标力的智能感知以及针对具体任务的适应能力。

为解决上述问题，本文提出一种力自适应抓取策略，把 VLM 推理与基于 MPC 的力调节结合起来。VLM 负责理解任务，MPC 负责实时优化，使系统能够平滑、自适应地抓取多种物体，包括训练时未见过的物体。

## III. 双臂灵巧遥操作系统

### A. DexTele 概览

DexTele 是一个结合视觉动作重定向与自适应抓取的双臂灵巧遥操作系统，总体流程如图 2 所示。系统使用 FrankMocap 捕捉人的三维手臂和手部动作。数据经过处理后，由于手臂与手部的动作特性不同，捕捉结果被分为相互独立的手臂动作和手部动作。

这些动作由 SAG-GCN 处理，其输入与输出阶段分别处理手臂和手部。随后，系统根据动作尺度与类型采用相应优化方法，以提高重定向精度。重定向得到的机器人手臂关节角直接用于控制；灵巧手关节角则进入结合 VLM 推理和基于 MPC 的力调节的自适应抓取模块。抓取时，VLM 分析外部相机图像，推断目标物体所需的抓取力。系统再结合灵巧手的实时力反馈，通过 MPC 动态优化关节指令和施加的力。

**图 2：** 双臂灵巧遥操作系统概览。首先用 FrankMocap 捕捉人体动作，并处理为三维身体和手部姿态；再把提取出的手部和手臂动作分别重定向为机器人手和手臂的相应动作。机器人手臂角度直接发送给机器人；灵巧手角度先经自适应抓取模块调整，再执行真实抓取。

### B. 动作重定向

#### 动作重定向问题定义

本文把动作重定向表示为潜在空间优化问题。给定人体骨架图序列 $D=\{G_k\}$，编码器 $f_\phi$ 把 $G_k$ 映射为潜在向量 $z$，解码器 $f_\psi$ 输出机器人关节角 $\theta$，再由前向运动学 $K(\cdot)$ 转换为重定向轨迹 $S$。优化目标是最小化重定向损失；约束 $\theta_{\mathrm{lower}}$ 和 $\theta_{\mathrm{upper}}$ 保证预测关节角处于机械限位内：

$$
\theta=\arg\min_{\phi,\psi}L_{\mathrm{ret}}\bigl(D,S=K(\theta)\bigr), \tag{1}
$$

$$
\text{s.t.}\quad \theta_{\mathrm{lower}}\leq\theta\leq\theta_{\mathrm{upper}}. \tag{2}
$$

为衡量重定向机器人动作与目标人体示范之间的差异，本文定义复合目标函数：

$$
L_{\mathrm{ret}}=
\lambda_{ee}L_{ee}+\lambda_{\mathrm{ori}}L_{\mathrm{ori}}
+\lambda_{\mathrm{norm}}L_{\mathrm{norm}}+\lambda_dL_d
+\lambda_{\mathrm{fin1}}L_{\mathrm{fin1}}+\lambda_{\mathrm{fin2}}L_{\mathrm{fin2}}. \tag{3}
$$

各项依次对应末端执行器位置损失 $L_{ee}$、末端执行器方向损失 $L_{\mathrm{ori}}$、手臂法向量损失 $L_{\mathrm{norm}}$、动力学损失 $L_d$、指尖方向损失 $L_{\mathrm{fin1}}$ 和手指角度损失 $L_{\mathrm{fin2}}$。相应权重 $\lambda_{ee}$、$\lambda_{\mathrm{ori}}$、$\lambda_{\mathrm{norm}}$、$\lambda_d$、$\lambda_{\mathrm{fin1}}$ 和 $\lambda_{\mathrm{fin2}}$ 分别设为 1000、100、1000、1000、100 和 100，以平衡各项贡献，保证重定向结果准确、自然并符合物理规律。

#### 动作重定向架构

本文的动作重定向网络采用对称编码器—解码器结构，编码器和解码器均包含三层，如图 3 所示。编码器前两层采用双流结构，以处理手臂与手部动作之间的尺度差异；第三层负责特征融合。解码器采用镜像结构，高效整合特征。双流输入—输出结构分别处理粗粒度手臂动作和细粒度手部动作，使网络能针对不同尺度学习特征；第三层融合这些特征，协调手臂—手部动作，提高重定向精度和整体任务效率。

重定向网络的核心由两个模块构成：空间基本块（Spatial Basic Block，SBB）与门控残差块（Gated Residual Block，GRB），具体结构见图 4。SBB 作为特征提取器，通过拼接与消息传播处理节点特征和边属性，高效编码骨架拓扑，以支持实时动作重定向。GRB 引入注意力机制和门控残差结构，增强特征选择性与稳定性，同时减少噪声累积。

#### 动作重定向网络

动作重定向网络采用基于 SAG-GCN 的端到端编码器—解码器，把人体动作映射为机器人动作。人体和机器人骨架均表示为加权图，以描述关节拓扑和空间约束。第 $k$ 帧的骨架表示为 $G_k=(V_k,E_k,W_k)$，其中 $V_k=\{v_{k,1},\ldots,v_{k,N}\}$ 是关节节点，$E_k\subseteq V_k\times V_k$ 定义连接关系，$W_k\in\mathbb{R}^{N\times N}$ 是前向传播过程中学习得到的动态注意力矩阵。节点 $v_{k,i}$ 的特征为 $h_{k,i}=[p_{k,i},q_{k,i}]$，其中位置 $p_{k,i}\in\mathbb{R}^3$，四元数 $q_{k,i}\in\mathbb{R}^4$；边特征 $e_{k,ij}=p_{k,j}-p_{k,i}$ 编码局部几何关系。

在特征编码阶段，网络对位置进行归一化、保持旋转不变，从而既处理人和机器人骨架之间的尺度差异，又保证物理一致性。归一化位置为：

$$
\bar p_{k,i}=\frac{p_{k,i}-c_k}{s_k},\qquad
c_k=\frac{1}{N}\sum_{j=1}^{N}p_{k,j},\qquad
s_k=\sqrt{\frac{1}{N}\sum_{j=1}^{N}\lVert p_{k,j}-c_k\rVert_2^2}. \tag{4}
$$

其中 $c_k$ 是几何中心，$s_k$ 是全局尺度。归一化位置与旋转信息拼接为节点输入，再通过空间注意力处理。由空间—姿态相似度计算的注意力权重用于引导邻域信息聚合：

$$
m_{k,i}=\sum_{j\in\mathcal{N}(i)}\alpha_{k,ij}\,
\varphi\left([\bar p_{k,i},q_{k,i},\bar p_{k,j},q_{k,j},e_{k,ij}]\right), \tag{5}
$$

其中 $\varphi(\cdot)$ 表示采用 Swish 激活函数的两层全连接消息编码器，$\alpha_{k,ij}$ 是学习得到的注意力系数。

聚合消息与残差特征通过门控残差单元融合，得到更新后的节点表示：

$$
g_{k,i}=\sigma(W_gh_{k,i}+b_g), \tag{6}
$$

$$
h'_{k,i}=g_{k,i}\odot m_{k,i}+(1-g_{k,i})\odot Uh_{k,i}. \tag{7}
$$

其中 $g_{k,i}$ 是控制融合比例的门控向量，$\sigma(\cdot)$ 是 sigmoid 函数，$U$ 是维度映射矩阵。该门控机制减轻深层特征传播中的噪声累积，提高网络稳定性。

**图 3：** SAG-GCN 结构概览。编码器通过空间基本块和门控残差块对捕捉到的人体手臂与手部动作进行特征提取；提取的特征再利用目标函数在潜在空间中优化；最后，解码器把优化表示转换到机器人关节空间，完成动作重定向。

**图 4：** 空间基本块与门控残差块的结构。

### C. 自适应抓取

为灵活抓取不同物体，本文设计了图 5 所示的自适应抓取模块，将 VLM 推理与基于 MPC 的力调节结合起来。其核心流程依次包括目标物体识别、目标抓取力估计和关节指令在线优化，由此建立从视觉感知到自适应力调节的闭环映射。

#### VLM 驱动的目标力推断

抓取开始时，一旦灵巧手产生力信号，外部相机会拍摄机器人抓取图像。系统把图像与预先定义的识别指令一起输入 VLM，快速进行语义理解，并输出物体类别与建议的目标抓取力。与依赖传感器或启发式阈值确定抓取力的传统方法相比，该方法利用大模型的知识库，直接把物体类别映射为所需的力。例如，当物体被识别为“水瓶”时，模型可以推断建议目标抓取力约为 300 g，为后续自适应力优化提供量化参考。

在这里，VLM 的主要优势是能够根据知识驱动的判断为目标力提供先验估计。在复杂多物体环境中，手动标定或固定阈值往往难以兼顾抓取稳定性与物体安全。VLM 借助语义感知和先验知识，根据视觉输入生成合理目标力，为自适应力控制提供有效初值。

#### 关节角—力预测模型构建

确定目标力后，系统根据机器人手的关节角估计受力，以便在闭环优化过程中评价抓取性能。本文采用数据驱动策略，在历史动作—力数据上训练关节角—力预测模型：

$$
\mathcal{D}=\{(\theta_1^k,\theta_2^k,F^k)\}_{k=1}^{M}, \tag{8}
$$

其中 $\theta_1\in\mathbb{R}^6$ 表示关节角指令，$\theta_2\in\mathbb{R}^6$ 表示实际关节角反馈，$F\in\mathbb{R}^6$ 是相应的六维力传感器测量值。构建模型时，把控制角和反馈角拼接为输入：

$$
x=[\theta_1,\theta_2]\in\mathbb{R}^{12}. \tag{9}
$$

模型输出定义为预测力 $\hat F\in\mathbb{R}^6$。本文使用随机森林回归器，在训练效率与推理速度之间取得平衡，同时捕捉关节角与力之间的非线性映射。

训练完成后，模型 $M$ 无须依赖实时力传感器读数即可快速预测力，并作为后续基于梯度优化的可微替代模型。它相当于 MPC 优化器中的近似力学模型，使系统能在指令空间中直接推断力响应，无须显式动力学模型即可在线调节抓取力。

#### 基于 MPC 原理的自适应力优化

抓取执行期间，系统根据实时反馈持续细化关节指令，使输出力平滑收敛到目标值。一个受 MPC 启发的在线优化模块把力预测模型嵌入基于梯度的迭代环路，形成轻量级闭环控制机制。

在每个控制周期中，把上一个关节指令 $\theta_1^{\mathrm{prior}}$ 与当前实际关节角 $\theta_2$ 输入模型，得到预测力 $\hat F$。优化问题写为：

$$
L(\theta_1)=\lVert M(\theta_1,\theta_2)-F_{\mathrm{target}}\rVert^2
+\lambda\lVert\theta_1-\theta_1^{\mathrm{prior}}\rVert^2, \tag{10}
$$

第一项使预测力接近目标力，第二项正则化过大的关节指令变化。权重 $\lambda$ 用于平衡响应速度与平滑性。

系统把关节角 $\theta_1$ 视为可微变量，并使用 Adam 优化器通过梯度下降更新：

$$
\theta_1^*=\arg\min_{\theta_1}L(\theta_1). \tag{11}
$$

得到的 $\theta_1^*$ 用于下一个控制步骤，从而实现具有 MPC 类似特性的滚动优化。该方法在保持动作连续性的同时，自适应补偿力偏差，保证抓取稳定且可控。

**图 5：** 自适应抓取模块流程。当灵巧手产生力信号时，系统采集外部相机的当前图像，并与识别指令一起输入 VLM。VLM 输出目标抓取力和物体类别。MPC 模块再根据当前力信号和重定向关节角实时调整灵巧手关节角，使抓取力达到目标值。

## IV. 实验

### A. 实验设置

为评估视觉动作重定向系统在多个机器人平台上的可部署性，我们在 RMC-DA、YuMi 和 Unitree H1 三种机器人上开展人体动作重定向实验。RMC-DA 同时在真实和虚拟环境中评估，YuMi 与 Unitree H1 则在虚拟环境中测试。

RMC-DA 的两条手臂各有 6 个自由度，并配备带力传感器的因时（Inspire Robotics）灵巧手，每只手有 6 个自由度。YuMi 的每条手臂有 7 个自由度，安装与 RMC-DA 相同的灵巧手。Unitree H1 使用 5 自由度手臂，并配备 12 自由度灵巧手。

训练与评估使用两个数据集。第一个是高质量开源人体姿态数据集 Sign [35]。第二个是自建数据集：我们使用 FrankMocap 从 CSL-Daily 手语图像数据集 [31] 的单帧图像中提取三维人体姿态。两个数据集均为每条手臂的三个主要关节提供位置和四元数旋转数据，并为每只手的 16 个关节提供位置数据。基于 CSL-Daily 构建的数据集包含三名示范者完成的 151 类复杂上肢动作，覆盖多种日常肢体运动。

图神经网络用 PyTorch Geometric [32] 实现，在 NVIDIA RTX 4090 GPU 和 Intel Core i7-11700KF CPU 上使用 Adam 优化器训练，固定学习率为 $10^{-4}$。

### B. 动作重定向对比实验

#### 1）手臂动作重定向

手臂动作重定向对比实验使用 Sign 和 CSL-Daily 数据集，将本文方法与 NLO [35]、VMR [37] 和 ATP [38] 三个基线比较。手臂动作采用四项指标：平均逐关节位置误差 MPJPE [33]、四元数距离 Quat [34]、速度误差 VE 和加速度误差 AE [36]。MPJPE 衡量预测关节位置与真实值之间的平均距离，Quat 衡量关节方向的旋转差异，VE 和 AE 则分别通过关节位置的一阶与二阶导数评价动作的时间平滑性。如表 I 和表 II 所示，本文方法在两个数据集的所有指标上均优于基线，具有更高的位置精度、更好的一致旋转以及更平滑的运动动态。

#### 2）手部动作重定向

手部动作重定向使用与手臂实验相同的数据集和基线。性能通过三点法 [1] 计算的手指关节角误差（Fin Angle）衡量。如表 I 和表 II 所示，本文方法在所有手指和两个数据集上都取得最低误差，说明它能够更精确、更一致地重定向多样化手部动作。

**表 I：Sign 数据集上的手臂与手指动作重定向性能**

| 方法 | MPJPE（m） | Quat（rad） | VE（m/s） | AE（m/s²） | 拇指（rad） | 食指 | 中指 | 无名指 | 小指 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| NLO [35] | 0.0948 | 0.1670 | 0.0590 | 2.1420 | 0.2200 | 0.2542 | 0.0863 | 0.1609 | 0.1289 |
| VMR [37] | 0.0853 | 0.1578 | 0.0358 | 1.1056 | 0.2133 | 0.2631 | 0.0811 | 0.1571 | 0.1263 |
| ATP [38] | 0.1021 | 0.1834 | 0.0425 | 2.4312 | 0.2046 | 0.2749 | 0.1034 | 0.1497 | 0.1351 |
| 本文方法 | **0.0785** | **0.1503** | **0.0304** | **0.8212** | **0.1967** | **0.2471** | **0.0732** | **0.1476** | **0.1223** |

**表 II：CSL-Daily 数据集上的手臂与手指动作重定向性能**

| 方法 | MPJPE（m） | Quat（rad） | VE（m/s） | AE（m/s²） | 拇指（rad） | 食指 | 中指 | 无名指 | 小指 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| NLO [35] | 0.1038 | 0.1771 | 0.0622 | 1.9560 | 0.2200 | 0.2542 | 0.0863 | 0.1609 | 0.1289 |
| VMR [37] | 0.0963 | 0.1622 | 0.0471 | 1.3296 | 0.2133 | 0.2631 | 0.0811 | 0.1571 | 0.1263 |
| ATP [38] | 0.9381 | 0.1778 | 0.0527 | 1.6319 | 0.2169 | 0.2566 | 0.0901 | 0.1568 | 0.1369 |
| 本文方法 | **0.0882** | **0.1550** | **0.0388** | **0.9421** | **0.1833** | **0.2182** | **0.0766** | **0.1385** | **0.1310** |

### C. 动作重定向消融实验

我们在 CSL-Daily 数据集上对双流架构及其关键模块进行消融。变体包括单流结构（Single Graph）、移除 GRB、以线性结构替换 SBB，以及只保留手部流或手臂流。

如表 III 所示，Single Graph 使局部与全局特征相互干扰，增大位置和角度误差；移除 GRB 会削弱特征融合与注意力机制，降低末端执行器精度；用线性结构替换 SBB 后，模型难以表达非线性依赖，MPJPE 和 Quat 误差上升；只保留单流虽然能维持该部位的精度，却丢失互补信息，影响整体协调。这些结果表明，分别建模手部和手臂动作、再通过 GRB 融合，对于生成协调且自然的重定向动作非常重要。

**表 III：动作重定向消融实验**

| 方法 | MPJPE（m） | Quat（rad） | Fin Angle（rad） |
|---|---:|---:|---:|
| Ours (Full) | **0.0882** | **0.1550** | **0.1495** |
| Single Graph | 0.1333 | 0.1821 | 0.1947 |
| w/o GRB | 0.1513 | 0.1939 | 0.2020 |
| w/o SBB | 0.1566 | 0.2035 | 0.2239 |
| w/o Hand | 0.1139 | 0.1630 | — |
| w/o Arm | — | — | 0.1729 |

### D. 多机器人动作重定向实验

我们在 YuMi、Unitree H1 和 RMC-DA 三个平台上可视化所提出视觉引导动作重定向方法的跨平台泛化能力。如图 6 所示，同一组人体动作样本被用于仿真与真实环境，在各平台上均能稳定复现。

除可视化外，我们还在 CSL-Daily 数据集上使用 MPJPE、Quat、Fin Angle、速度误差和加速度误差进行定量评估，结果见表 IV。所有平台均取得较低的位置与旋转误差，并保持平滑运动动态，说明该方法在多个机器人平台上具有较好的鲁棒性和适用性。

系统还评估了实时遥操作性能：遥操作期间运行速度约为 10 帧/秒，其中 FrankMocap 处理每帧人体姿态耗时 0.08 秒，重定向模块处理每帧耗时不超过 0.02 秒。

**图 6：** 多机器人平台上的动作重定向演示。从上到下六行依次为：人类示范者、示范者人体网格渲染、仿真中的 YuMi、仿真中的 Unitree H1、仿真中的 RMC-DA，以及真实环境中的 RMC-DA。

**表 IV：跨平台机器人性能**

| 指标 | YuMi | Unitree H1 | RMC-DA |
|---|---:|---:|---:|
| MPJPE（m） | 0.1024 | 0.0877 | 0.0882 |
| Quat（rad） | 0.1735 | 0.1422 | 0.1550 |
| Fin Angle（rad） | 0.1486 | 0.1845 | 0.1495 |
| 速度误差（m/s） | 0.0431 | 0.0622 | 0.0388 |
| 加速度误差（m/s²） | 0.8376 | 1.1329 | 0.9421 |

### E. 自适应抓取性能评估

#### 1）自适应抓取性能

视觉推理采用 Doubao-seed-1-6-vision-250815 模型。在实验设置下，平均推理延迟约为 0.2–0.3 秒，足以满足机器人抓取的实时响应要求。本文在八种形状和材质不同的日常物体上验证自适应抓取模块，可视化结果见图 7。

除可视化外，表 V 给出了八类物体的定量抓取结果。VLM 能够为每个物体准确推断目标抓取力。对刚性与可变形物体进行抓取时，力偏差（Dev）和振荡幅值（Osc）均保持在 10% 以内。所有物体都被牢固抓取，没有出现滑落或损坏。

为更直观地说明自适应抓取模块的作用，我们可视化了启用和关闭该模块时抓取水瓶过程中的力变化，如图 8 所示。关闭自适应模块后，手指力不受控制；启用该模块后，系统会自动调整抓取角度以达到目标力，并平滑收敛。结果说明，把 VLM 推理与基于 MPC 的力调节结合起来，可以对不同物体实现精确、低振荡且安全的柔顺抓取。

**图 7：** 八类不同物体的抓取结果，展示系统对不同质地和形状的自适应力控制。

**图 8：** 抓取水瓶时的力曲线。五条不同颜色的曲线分别对应五根手指施加的力。

**表 V：自适应抓取性能**

| 物体 | VLM 目标力（g） | 力偏差（%） | 力振荡（%） | 是否牢固抓取 |
|---|---:|---:|---:|:---:|
| 水瓶 | 300 | 5.3 | 4.2 | 是 |
| 啤酒罐 | 270 | 7.1 | 6.5 | 是 |
| 纸盒 | 60 | 4.9 | 6.1 | 是 |
| 塑料芒果 | 150 | 7.6 | 3.2 | 是 |
| 海绵块 | 50 | 6.0 | 2.5 | 是 |
| 毛绒玩具 | 200 | 4.8 | 7.2 | 是 |
| 抹布 | 50 | 8.1 | 8.4 | 是 |
| 纸杯 | 30 | 5.9 | 7.5 | 是 |

#### 2）抓取成功率评估

我们在八类日常物体上评估自适应抓取模块（AGM）。一次成功抓取定义为：稳定持握，且没有滑落或明显变形。如表 VI 所示，加入 AGM 后可靠性显著提高，八类物体的平均成功次数从每 10 次中的 5.13 次上升到 9.13 次。对纸杯和毛绒玩具等可变形物体，自适应力调节能防止过度挤压和结构损伤；对塑料芒果和海绵块等容易滑落的物体，快速调整则减少了滑移与意外松脱。结果表明，在遥操作中加入 AGM 能显著提升抓取稳定性和安全性。

**表 VI：抓取成功率**

| 物体 | 使用 AGM | 不使用 AGM |
|---|---:|---:|
| 水瓶 | 9/10 | 7/10 |
| 啤酒罐 | 9/10 | 6/10 |
| 塑料芒果 | 10/10 | 4/10 |
| 纸盒 | 9/10 | 5/10 |
| 海绵块 | 8/10 | 4/10 |
| 毛绒玩具 | 10/10 | 5/10 |
| 抹布 | 9/10 | 6/10 |
| 纸杯 | 9/10 | 4/10 |

## V. 结论

本文提出 DexTele，将动作重定向与自适应力控制整合在一个系统中。实验结果表明，所设计的 SAG-GCN 视觉动作重定向模块能够准确、高效地进行跨平台动作重定向。自适应抓取模块把 VLM 与 MPC 结合起来，使系统能够推断目标物体所需的抓取力，并进行基于梯度的在线优化，实现柔顺抓取。该系统已在 RMC-DA、YuMi 和 Unitree H1 等多个机器人平台上验证，表现出较强的泛化能力和实时性能。

不过，系统仍有一些局限。第一，实时性能受到姿态估计算法限制。第二，当前重定向算法只适用于机器人上半身动作。未来工作将采用更轻量、更准确的姿态估计方法，并把重定向算法扩展到机器人全身动作。

## 参考文献

> 为保证作者名、论文题名、期刊或会议名称及检索信息准确，本节沿用原文书目，不翻译题名。

[1] S. Li, N. Hendrich, H. Liang, et al., “A dexterous hand-arm teleoperation system based on hand pose estimation and active vision,” *IEEE Trans. Cybern.*, vol. 54, no. 3, pp. 1417–1428, 2022.  
[2] A. Sivakumar, K. Shaw, and D. Pathak, “Robotic telekinesis: Learning a robotic hand imitator by watching humans on YouTube,” arXiv:2202.10448, 2022.  
[3] Z. Fu, T. Z. Zhao, and C. Finn, “Mobile Aloha: Learning bimanual mobile manipulation with low-cost whole-body teleoperation,” arXiv:2401.02117, 2024.  
[4] X. Cheng, J. Li, S. Yang, et al., “Open-television: Teleoperation with immersive active visual feedback,” arXiv:2407.01512, 2024.  
[5] C. Zeng, S. Li, Y. Jiang, et al., “Learning compliant grasping and manipulation by teleoperation with adaptive force control,” in *Proc. IEEE/RSJ IROS*, 2021, pp. 717–724.  
[6] S. Li, et al., “Vision-based teleoperation of Shadow dexterous hand using end-to-end deep neural network,” in *Proc. IEEE ICRA*, 2019, pp. 416–422.  
[7] S. Baek, A. Kim, J. Y. Choi, et al., “Human motion retargeting to a full-scale humanoid robot using a monocular camera and human pose estimation,” *Int. J. Control Autom. Syst.*, vol. 22, no. 9, pp. 2860–2870, 2024.  
[8] C. Zeng, S. Li, Z. Chen, et al., “Multifingered robot hand compliant manipulation based on vision-based demonstration and adaptive force control,” *IEEE Trans. Neural Netw. Learn. Syst.*, vol. 34, no. 9, pp. 5452–5463, 2022.  
[9] T. Kim and J.-H. Lee, “TeachMe: Three-phase learning framework for robotic motion imitation based on interactive teaching and reinforcement learning,” in *Proc. IEEE RO-MAN*, 2019, pp. 1–8.  
[10] S. Patel, T. Garg, G. Patel, et al., “Motion retargeting and machine learning for humanoid robotics,” in *ISDCS*, 2020, pp. 1–5.  
[11] Z. Deng, Y. Jonetzko, L. Zhang, et al., “Grasping force control of multi-fingered robotic hands through tactile sensing for object stabilization,” *Sensors*, vol. 20, no. 4, p. 1050, 2020.  
[12] Q. Tang, H. Yang, W. Wang, et al., “Grasp compliant control using adaptive admittance control methods for flexible objects,” in *ICIRA*, 2023, pp. 515–525.  
[13] S. Cortinovis, G. Vitrani, M. Maggiali, et al., “Control methodologies for robotic grippers: A review,” *Actuators*, vol. 12, no. 8, p. 332, 2023.  
[14] B. Fang, F. Sun, H. Liu, and C. Liu, “3D human gesture capturing and recognition by the IMMU-based data glove,” *Neurocomputing*, vol. 277, pp. 198–207, 2018.  
[15] D. Shi, S. Jin, C. Yang, et al., “Exploring the synergistic effects of teleoperation scaling ratio and learning from demonstration,” *IEEE Trans. Autom. Sci. Eng.*, 2025.  
[16] M. Zhang, Q. Gao, Y. Lai, et al., “HR-GCN: 2D–3D whole-body pose estimation with high-resolution graph convolutional network from a monocular camera,” *IEEE Sens. J.*, 2025.  
[17] C. Zeng, et al., “Learning compliant grasping and manipulation by teleoperation with adaptive force control,” in *Proc. IEEE/RSJ IROS*, 2021, pp. 717–724.  
[18] L. S. Li, J. Jiang, P. Ruppel, et al., “A mobile robot hand-arm teleoperation system by vision and IMU,” in *Proc. IEEE/RSJ IROS*, 2020, pp. 10900–10906.  
[19] C. Lu, et al., “Mobile-TeleVision: Predictive motion priors for humanoid whole-body control,” in *Proc. IEEE ICRA*, 2025, pp. 5364–5371.  
[20] Z. Yang, S. Bien, S. Nertinger, et al., “An optimization-based scheme for real-time transfer of human arm motion to robot arm,” in *Proc. IEEE/RSJ IROS*, 2024, pp. 12220–12225.  
[21] T. Kim and J.-H. Lee, “C-3PO: Cyclic-three-phase optimization for human-robot motion retargeting based on reinforcement learning,” in *Proc. IEEE ICRA*, 2020, pp. 8425–8432.  
[22] S. Choi, M. J. Song, H. Ahn, and J. Kim, “Self-supervised motion retargeting with safety guarantee,” in *Proc. IEEE ICRA*, 2021, pp. 8097–8103.  
[23] H. Liang, et al., “PointNetGPD: Detecting grasp configurations from point sets,” in *Proc. IEEE ICRA*, 2019, pp. 3629–3635.  
[24] Q. Lu, M. Van der Merwe, B. Sundaralingam, and T. Hermans, “Multifingered grasp planning via inference in deep neural networks: Outperforming sampling by learning differentiable models,” *IEEE Robot. Autom. Mag.*, vol. 27, no. 2, pp. 55–65, 2020.  
[25] T. Wimbock, C. Ott, and G. Hirzinger, “Analysis and experimental evaluation of the intrinsically passive controller (IPC) for multifingered hands,” in *Proc. IEEE ICRA*, 2008, pp. 278–284.  
[26] M. Li, H. Yin, K. Tahara, and A. Billard, “Learning object-level impedance control for robust grasping and dexterous manipulation,” in *Proc. IEEE ICRA*, 2014, pp. 6784–6791.  
[27] Z. Xu and Y. She, “LeTac-MPC: Learning model predictive control for tactile-reactive grasping,” *IEEE Trans. Robot.*, 2024.  
[28] L. Shi, C. Mucchiani, and K. Karydis, “Online modeling and control of soft multi-fingered grippers via Koopman operator theory,” in *Proc. IEEE CASE*, 2022, pp. 1946–1952.  
[29] D. Tian, X. Lin, and Y. Sun, “Adaptive motion planning for multi-fingered functional grasp via force feedback,” in *Proc. IEEE-RAS Humanoids*, 2024, pp. 835–842.  
[30] Y. Rong, T. Shiratori, and H. Joo, “FrankMocap: A monocular 3D whole-body pose estimation system via regression and integration,” in *ICCV*, 2021, pp. 1749–1759.  
[31] H. Zhou, W. Zhou, W. Qi, et al., “Improving sign language translation with monolingual data by sign back-translation,” in *CVPR*, 2021, pp. 1316–1325.  
[32] M. Fey and J. E. Lenssen, “Fast graph representation learning with PyTorch Geometric,” in *ICLR Workshop on Representation Learning on Graphs and Manifolds*, 2019.  
[33] R. Villegas, J. Yang, D. Ceylan, et al., “Neural kinematic networks for unsupervised motion retargetting,” in *CVPR*, 2018, pp. 8639–8648.  
[34] R. Greer, N. Deo, and M. Trivedi, “Trajectory prediction in autonomous driving with a lane heading auxiliary loss,” *IEEE Robot. Autom. Lett.*, vol. 6, no. 3, pp. 4907–4914, 2021.  
[35] H. Zhang, et al., “Kinematic motion retargeting via neural latent optimization for learning sign language,” *IEEE Robot. Autom. Lett.*, vol. 7, no. 2, pp. 4582–4589, 2022.  
[36] J. Li, S. Bian, C. Xu, et al., “D&D: Learning human dynamics from dynamic camera,” in *ECCV*, 2022, pp. 479–496.  
[37] Y. Lai, Z. Ju, and Q. Gao, “Motion retargeting using graph neural network for vision-guided dexterous robot teleoperation,” in *i-CREATe*, 2024, pp. 1–6.  
[38] Y. Qin, et al., “AnyTeleop: A general vision-based dexterous robot arm-hand teleoperation system,” in *Robotics: Science and Systems (RSS)*, 2023.
