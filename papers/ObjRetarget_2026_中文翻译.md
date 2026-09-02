# ObjRetarget：融合拟人化手臂约束与多面体手部建模的物体感知动作重定向框架

> 原文：*ObjRetarget: An Object-Aware Motion Retargeting Framework with Anthropomorphic Arm Constraints and Polyhedral Hand Modeling*  
> 作者：Yuanchuan Lai、Qing Gao、Ziyan Liang、Junjie Hu、Zhaojie Ju  
> arXiv:2607.03828v1，2026-07-04  
> 说明：本文为学习用中文全译稿。公式编号、图表编号与参考文献编号均与原文一致；论文图片请对照同目录原始 PDF，参考文献保留英文书目信息以便检索。

## 摘要

从人类操作视频中学习机器人灵巧操作，需要在保持稳定手—物接触的同时，将人的意图可靠地重定向为机器人可执行动作。这仍是具身智能中的一项关键挑战。现有重定向方法往往忽略显式接触建模，或依赖强化学习，因而在准确性和泛化能力上受到限制。为此，我们提出 ObjRetarget：一种从人类视频学习机器人灵巧操作的人到机器人动作重定向框架。该框架将拟人化手臂轨迹约束与结构化手—物几何建模结合起来。

对于手臂运动，系统先用从人类视频中提取的参考轨迹完成初始化，再加入拟人化约束和冗余感知优化，从而生成自然、准确的动作。对于手部操作，ObjRetarget 使用多面体簇表示多指接触，并借助几何不变量保持接触结构，以提升稳定性。真实机器人实验表明，ObjRetarget 在多项灵巧操作任务中提高了操作成功率和接触稳定性，并能较好地泛化到不同示范者、物体位姿和任务设置。项目页面：<https://github.io/ObjRetarget>。

## I. 引言

从人类操作视频中学习机器人灵巧操作，需要把人的意图可靠地重定向为机器人可执行动作，同时在整个操作过程中维持稳定的手—物接触。这是具身智能和灵巧操作研究中的核心问题，因为成功的操作不仅取决于动作模仿，还取决于是否保留具有物理意义的接触关系 [1]–[3]。如图 1(a) 所示，现有动作重定向方法主要关注自由空间中的姿态或关节映射，使机器人复现示范中的运动学动作 [4], [5]。然而，对于物体交接、接触转换和持续手—物交互的建模仍然不足，特别是在依赖手部直接映射的方法中 [6], [7]，如图 1(b) 所示。在真实操作中，机器人不仅要复现精细手指动作，还要协调大尺度手臂运动，使抓取、搬运和物体操作既保持物理稳定，又符合自然行为。这要求系统同时推理接触几何、动作连续性和任务相关约束。

然而，多数现有方法把手臂和手视为一个统一系统，忽略了二者在动作尺度、功能角色和精度要求上的根本差异 [8]。手臂主要产生大尺度全局动作，决定物体接近、空间定位和整体运动轨迹；手则执行精细且对接触敏感的动作，直接影响抓取稳定性和操作成功率。忽略这种差异，往往会使全局运动平滑性与局部接触稳定性发生冲突，因此难以在物体转移、建立接触和维持接触等任务中同时获得鲁棒性与自然性。与此同时，许多交互感知方法依赖强化学习进行端到端优化 [9], [10]。这类方法虽然能够隐式学习接触行为，但泛化能力通常有限；当物体几何形状、初始位姿或任务条件改变时，性能可能下降。这些局限说明，稳定且可泛化的重定向不仅要复现示范动作，还要显式建模手与臂的动作差异，并把物体交互约束纳入重定向过程。

为解决上述问题，我们提出面向物体交互的灵巧操作人到机器人重定向框架 ObjRetarget，如图 1(c) 所示。该流程首先从示范视频中提取关节轨迹和物体点云信息，建立人类参考计划；随后通过初始重定向，将人的动作转换为粗略机器人轨迹，供后续优化使用。在此基础上，ObjRetarget 显式建模手臂与手的不同运动特性。

对于手臂，系统通过拟人化动作约束和任务自适应优化细化参考轨迹，使全局动作在适应物体初始位姿变化的同时，仍遵循人类运动模式，从而提高动作的自然性和准确性。对于手部操作，系统构造多面体簇，把每个手指—物体接触表示为局部几何单元，并利用几何不变量约束保持接触结构和操作语义，以增强抓取稳定性与交互可靠性。大量真实机器人实验表明，ObjRetarget 能够显著提高多项灵巧操作任务的成功率和接触稳定性，同时保持自然且可解释的机器人动作。

本文的主要贡献如下：

- 提出 ObjRetarget，一种手—臂解耦的人到机器人重定向框架。它显式分离手臂的全局运动与对接触敏感的手部操作，在统一流程中生成物体感知动作。
- 提出由参考轨迹引导、带拟人化动作约束的手臂优化策略，使机器人在不同物体位姿和任务条件下生成稳定且符合人类动作特征的手臂轨迹。
- 提出多面体簇手部建模方法，把多指接触表示为局部几何单元，并通过几何约束保持手—物接触结构。

**图 1：** 动作重定向框架示意图。(a) 通过逆运动学完成手臂重定向；(b) 通过直接映射完成手部重定向；(c) 本文提出的、融合多面体手部建模与拟人化手臂约束的流程。

## II. 相关工作

### A. 物体感知灵巧操作

物体感知灵巧操作受到多接触约束和复杂手—物几何关系的影响，因而具有较高难度。强化学习和模型预测控制被广泛用于学习交互策略 [11], [12]，但强化学习通常需要大量交互轨迹、漫长训练过程和精心设计的奖励函数，其性能也容易受到物体几何形状与初始条件变化的影响 [13], [14]。另一些方法引入显式接触模型或触觉感知来提高稳定性 [15], [16]，但它们往往依赖准确的接触建模或专用触觉硬件，从而限制了可扩展性和跨物体泛化能力。因此，在不依赖重训练过程或精确物体模型的情况下，实现稳定且可泛化的灵巧操作仍然困难。

为克服这些局限，ObjRetarget 不依赖自主策略学习，而是利用视频中的人类操作先验。它以带几何不变量的多面体簇建模手—物交互，并使用示范中的参考轨迹引导手臂运动。该结构化、由人类信息引导的形式避免了大规模训练和显式物体模型，能够在不同物体和任务场景中实现稳定交互并改善泛化性能。

### B. 人到机器人动作重定向

人到机器人动作重定向旨在把人类示范迁移到具有不同运动学结构和自由度的机器人平台，以高保真地复现动作。传统方法依赖解析运动学、优化或基于约束的规划，通常通过关节空间映射适配手臂和手部姿态 [17]–[19]；较新的工作则使用深度学习或潜在表示减小运动学差异，提高重定向精度 [20]–[22]。这些方法在自由空间模仿和轨迹跟踪中表现良好。

不过，多数方法假设无物体或弱接触场景，重点在于几何一致性或关节误差最小化，并未显式建模手—物交互。此外，许多方法把手臂和手当作统一系统 [23], [24]，忽略二者的不同作用：手臂控制大尺度运动，而手负责精确、对接触敏感的操作。这种简化会削弱全局动作与局部交互之间的协调，导致复杂任务中的性能下降。

ObjRetarget 将手臂层面的全局运动与手部层面的精细操作分开处理。手臂运动由参考轨迹引导，并通过任务相关约束进行细化，生成既保留人类特征、又能物理执行并支持稳定物体交互的动作。同时，重定向过程显式考虑手—物接触，保证交互过程中的多指操作稳定而准确。

### C. 从人类示范中学习

人类示范视频为机器人灵巧操作提供了丰富先验，使系统可以将人的物体感知动作重定向到机器人。传统模仿学习方法通过轨迹回放、行为克隆或端到端视觉运动学习，把人类视频或动作捕捉数据映射为机器人控制策略 [25]–[28]。这类方法虽然能用于技能习得，但通常关注自主策略学习，并忽略细粒度手—物交互，因此难以实现精确动作映射和稳定抓取。

OKAMI [31] 和 ORION [32] 等单视频重定向方法利用人类示范生成可执行机器人动作。OKAMI 为技能学习模仿人形机器人动作，但由于缺少显式手—物建模，在多阶段操作和持续接触控制方面存在困难。ORION 使用开放世界物体图推断以物体为中心的动作，改善了跨物体和跨布局泛化，但没有建模细粒度手—物接触。这些工作显示了视频驱动操作的潜力，也说明结构化、物体感知重定向仍有必要。ObjRetarget 用多面体簇建模手—物接触，并通过人类参考轨迹引导手臂运动，从而生成接触一致、拟人且可泛化的动作，供后续技能学习使用。

## III. ObjRetarget

### A. 物体感知动作重定向框架

我们提出 ObjRetarget：一种面向物体交互、从人类操作视频学习机器人操作的动作重定向框架。如图 2(a) 所示，给定一段 RGB-D 操作视频，系统首先使用 SLAHMR [29] 姿态估计器重建人体动作。SLAHMR 是一种通过迭代优化恢复人体动作序列的算法。随后，系统通过视觉—语言模型识别被操作物体，并跟踪物体位姿，以估计其随时间变化的空间轨迹。各部分信息经过整合，得到时间同步的人体关节姿态序列、物体点云位姿序列和人—物交互距离。系统通过对交互距离设置阈值来检测接触事件，从而区分自由运动阶段与物理交互阶段。

在手臂层面（图 2(b)），ObjRetarget 采用两阶段策略生成全局动作。系统先根据人体关节姿态序列生成初始重定向轨迹，提供可行且结构一致的动作先验；再结合物体位姿信息和拟人化动作约束细化轨迹，从而得到既与示范一致、又能适应具体任务设置的可执行手臂轨迹。在手部层面（图 2(c)），ObjRetarget 使用接触感知的分阶段重定向机制。非接触阶段沿用初始化得到的手部动作；检测到接触后，则启用基于多面体簇的几何一致性优化，以保持局部接触结构和操作语义。

图 2(d) 展示了负责协调手臂和手部轨迹的统一时间调度器。它同步全局手臂运动与精细手部操作，保证双臂协调执行。通过这种手—臂解耦形式，ObjRetarget 能在复杂物体交互任务中实现自然、稳定且可泛化的灵巧操作。

**图 2：** 物体感知动作重定向框架概览。(a) 从 RGB-D 视频中提取人体三维身体和手部姿态，同时检测并跟踪任务相关物体以生成参考计划；(b) 根据物体位姿和拟人化约束细化手臂轨迹；(c) 使用多面体簇在接触点优化手部动作；(d) 通过统一时间调度器同步手臂与手部动作，实现协调双臂执行。

### B. 拟人化手臂约束

为在复杂物体交互任务中得到稳定、自然且可泛化的机器人执行轨迹，ObjRetarget 使用两阶段手臂动作生成策略。首先，根据我们此前的重定向工作 [30] 生成参考轨迹，以提供可行且结构化的初始动作。随后，在拟人化动作约束与任务目标引导下，通过优化框架细化轨迹，使动作在满足任务要求的同时保持拟人化运动模式。

#### 通过动作重定向完成运动初始化

初始化轨迹虽然不一定是最终执行结果，但它提供了结构有效且接近最优的起点，可以显著提高后续优化的收敛稳定性。

设包含 $T$ 帧的人体动作序列为骨架图集合 $D=\{G_k\}_{k=1}^{T}$。每一帧的图 $G_k=(V_k,E_k,W_k)$ 由关节节点 $V_k$、骨架连接关系 $E_k$ 和动态注意力权重 $W_k$ 构成。编码器 $f_\psi(\cdot)$ 将每个骨架图嵌入潜在空间，得到紧凑表示 $z_k=f_\psi(G_k)$；解码器再把它解码为机器人关节配置 $\theta_k=f_\phi(z_k)\in\mathbb{R}^{n}$，其中 $n$ 是机器人关节数，且 $\theta_k$ 满足关节限位。

通过前向运动学得到相应的机器人末端执行器位姿 $S_k=\mathrm{FK}(\theta_k)$，其中 $S_k$ 同时编码末端执行器的位置与方向。重定向过程通过最小化以下参考损失进行优化：

$$
L_{\mathrm{ref}}(S_k,S_k^h)=L_{\mathrm{pos}}+\lambda_{\mathrm{ori}}L_{\mathrm{ori}}+\lambda_{\mathrm{tip}}L_{\mathrm{tip}}. \tag{1}
$$

该损失分别衡量相对于人类示范 $S_k^h$ 的末端位置误差 $L_{\mathrm{pos}}$、方向误差 $L_{\mathrm{ori}}$ 和指尖一致性误差 $L_{\mathrm{tip}}$；$\lambda_{\mathrm{ori}}$ 与 $\lambda_{\mathrm{tip}}$ 用于调节各项权重。对编码器和解码器参数 $(\psi,\phi)$ 的优化写为：

$$
\min_{\psi,\phi}\sum_{k=1}^{T}L_{\mathrm{ref}}(S_k,S_k^h), \tag{2}
$$

$$
\text{s.t.}\quad \theta_{\min}\leq\theta_k\leq\theta_{\max}. \tag{3}
$$

得到的机器人轨迹 $S=\{S_k\}_{k=1}^{T}$ 作为宏观手臂参考轨迹，为后续几何一致性优化提供有效初始化。

#### 任务自适应手臂平面正则化

在人类运动中，由肩、肘、腕构成的平面随时间平滑变化，其法向方向与动作方向及任务语义密切相关。相比之下，具有冗余自由度的机器人如果只受到末端执行器约束，往往会产生不符合人类习惯的肘部构型，例如肘部翻转、抖动或异常抬高。

现有方法通常通过直接匹配人类示范中的手臂平面法向量来促进拟人化运动，但这实际上把手臂平面当作刚性姿态目标，会限制机器人在受约束操作场景中的运动灵活性。为了既保持拟人化结构又允许动作自适应，本文把手臂平面表示为软几何约束。

如图 3 所示，设时刻 $t$ 的机器人肩、肘、腕位置分别为 $p_s(t)$、$p_e(t)$、$p_w(t)$。瞬时手臂平面单位法向量定义为：

$$
n_{\mathrm{arm}}^{\mathrm{robot}}(t)=
\frac{(p_e(t)-p_s(t))\times(p_w(t)-p_e(t))}
{\lVert(p_e(t)-p_s(t))\times(p_w(t)-p_e(t))\rVert}. \tag{4}
$$

本文不直接使用人类示范，而是根据当前动作趋势自适应构造参考弯曲方向：

$$
n_{\mathrm{arm}}^{\mathrm{ref}}(t)=
\frac{(p_w(t)-p_s(t))\times\dot p_w(t)}
{\lVert(p_w(t)-p_s(t))\times\dot p_w(t)\rVert}, \tag{5}
$$

其中 $\dot p_w(t)$ 表示手腕速度方向。任务自适应手臂平面损失定义为：

$$
L_{\mathrm{plane}}(t)=w(t)\left(1-n_{\mathrm{arm}}^{\mathrm{robot}}(t)\cdot n_{\mathrm{arm}}^{\mathrm{ref}}(t)\right). \tag{6}
$$

自适应权重 $w(t)$ 在手臂进行大幅、快速运动时增强该先验，在精细接触操作时自动减弱先验，以避免干扰任务精度。这一形式只惩罚相对于符合人类习惯的弯曲趋势的较大偏差，同时保留利用冗余自由度的灵活性。

**图 3：** 任务自适应手臂平面正则化示意图。(a) 由肩—肘—腕三角形定义的单位法向量 $n_{\mathrm{arm}}^{\mathrm{robot}}$；(b) 根据手腕运动方向构造的参考法向量 $n_{\mathrm{arm}}^{\mathrm{ref}}$；(c) 机器人构型中的手臂平面及其法向量。

#### 面向任务的末端执行器跟踪损失

为保证轨迹细化过程中的任务精度，ObjRetarget 加入标准的末端执行器位姿跟踪目标。设时刻 $t$ 的腕部位姿为 $x_w(t)=[p_w(t),R_w(t)]$，其中 $p_w(t)\in\mathbb{R}^3$ 是手腕位置，$R_w(t)\in SO(3)$ 是以旋转矩阵表示的手腕方向。类似地，参考腕部位姿为 $x_w^{\mathrm{ref}}(t)=[p_w^{\mathrm{ref}}(t),R_w^{\mathrm{ref}}(t)]$，其中 $p_w^{\mathrm{ref}}(t)$ 和 $R_w^{\mathrm{ref}}(t)$ 分别是第 $t$ 帧的目标位置与方向。任务跟踪损失定义为：

$$
L_{\mathrm{task}}(t)=\lVert p_w(t)-p_w^{\mathrm{ref}}(t)\rVert^2
+\lambda_R\left\lVert\varphi\left(R_w^{\mathrm{ref}}(t)^\top R_w(t)\right)\right\rVert^2. \tag{7}
$$

其中，$\varphi(\cdot)$ 把 $SO(3)$ 上的旋转误差映射到其李代数表示，$\lambda_R$ 调整方向项相对于位置项的权重。该损失只关注任务精度，不加入额外先验，因此可用于不同场景。

#### 总体优化目标

结合任务约束与拟人化正则项，手臂轨迹优化写为：

$$
\min_{q(t)}\sum_t\left[
L_{\mathrm{task}}(t)+\lambda_pL_{\mathrm{plane}}(t)
+\lambda_s\lVert q(t)-q(t-1)\rVert^2
\right], \tag{8}
$$

其中 $q(t)$ 表示时刻 $t$ 的机器人关节配置，$\lambda_p$ 和 $\lambda_s$ 分别控制拟人化正则项和时间平滑项。

### C. 多面体手部建模

#### 手—物接触表示

为了准确描述多指操作过程中人手与物体之间的细粒度几何关系，ObjRetarget 引入物体感知的手—物接触表示。给定 RGB-D 输入视频，系统首先提取手部关键点和物体表面点云。手部关键点包括五个指尖和掌心，共六个点，用于表示整体手部构型；物体表面则由深度点云重建。

系统根据手部关键点与物体点之间的空间邻近关系，逐指检测接触，以确定哪些手指与物体发生有效接触。对于发生接触的手指 $f$，系统提取物体表面的局部接触区域 $C_f$，并把该区域的质心作为代表性接触点：

$$
c_f=\frac{1}{|C_f|}\sum_{o\in C_f}o, \tag{9}
$$

其中 $|C_f|$ 是接触区域中的点数，$o$ 表示物体表面点。该设计能够在复杂交互场景中稳健提取多指接触信息，为结构化几何建模提供可靠输入。

#### 多面体簇构建

获得逐指接触信息后，ObjRetarget 构建多面体簇，以建模多指协作时的局部几何关系。对于发生接触的手指 $f$，局部四面体单元 $T_f$ 由四个顶点定义：掌心、手指 $f$ 的指尖关键点、相邻手指的指尖，以及相应的物体接触点 $c_f$。当多根手指同时接触物体时，这些四面体共同形成多面体簇，表示协同操作下的局部手—物几何结构。这种形式把复杂多指接触关系转换为一组稳定、紧凑的几何单元，从而得到可解释、可优化的高维接触约束。

核心思想是：人类操作不要求精确复现绝对位姿，真正需要保留的是稳定的局部几何关系与接触语义。因此，多面体簇被用作软几何约束，为后续几何一致性优化提供结构化基础。

#### 几何不变量优化

在多面体簇建模的基础上，ObjRetarget 把手部动作重定向表示为几何不变量约束下的非线性优化问题。总体几何一致性损失定义为：

$$
L=\sum_f w_f\,L(T_f), \tag{10}
$$

其中 $f$ 表示手指索引，$w_f$ 是权重系数，$L(T_f)$ 是第 $f$ 个四面体的几何一致性损失，由边长不变量和相对位姿不变量组成：

$$
L(T_f)=L_{\mathrm{edge}}(T_f)+\lambda L_{\mathrm{pose}}(T_f). \tag{11}
$$

边长损失约束局部四面体几何结构：

$$
L_{\mathrm{edge}}(T_f)=
\sum_{(i,j)\in E_f}
\left\lVert (p_i^r-p_j^r)-(p_i^h-p_j^h)\right\rVert^2, \tag{12}
$$

其中 $E_f$ 是四面体的边集合，$p^r$ 和 $p^h$ 分别表示机器人与人类示范中的顶点位置。

仅保持几何结构并不能区分操作语义不同的情况，因此本文进一步加入相对位姿不变量。系统以手部关键点建立局部坐标系，对物体接触点的相对位置施加约束：

$$
L_{\mathrm{pose}}(T_f)=
\left\lVert
R_r^\top(c_f^r-p_0^r)-R_h^\top(c_f^h-p_0^h)
\right\rVert^2, \tag{13}
$$

其中 $p_0$ 是掌心参考点，$R_r,R_h\in SO(3)$ 分别表示机器人和人类示范的手部局部坐标系。该项消除了全局平移和旋转影响，同时保持接触方向及其相对于手的空间分布，从而有效保留操作语义。

最终，手部动作重定向写为以下约束优化问题：

$$
q^*=\arg\min_q\sum_f w_fL(T_f(q)), \tag{14}
$$

$$
\text{s.t.}\quad q_{\min}\leq q\leq q_{\max}, \tag{15}
$$

其中 $q_{\min}$、$q_{\max}$ 是关节限位，$q^*$ 是使边长损失和位姿损失之和最小的优化关节配置。

### D. 手臂—手部同步执行

得到优化后的手臂与手部控制指令后，ObjRetarget 使用统一时间调度器协调双臂与双手。手臂执行手臂层优化得到的拟人化重定向指令，以保证轨迹符合物理约束且平滑。手部则采用接触感知策略：当手—物交互距离大于阈值 $\delta$、即没有检测到接触时，系统执行初始化手部重定向指令。阈值 $\delta$ 设为 $0.05\,\mathrm{cm}$，这一数值根据物体跟踪系统的精度确定，用于可靠地区分真实接触与自由运动。一旦发生接触，手部控制便切换到多面体簇优化指令，以保持局部接触结构和操作语义。接触解除后，系统重新执行初始化手部指令。一次操作中如果发生多次接触事件，这一循环会自动重复。通过这种手臂与手部同步方式，调度器能保证复杂物体交互任务稳定、自然且可泛化地执行。

## IV. 实验

### A. 实验设置

为系统评估 ObjRetarget 在真实操作场景中的稳定性与泛化能力，我们在 RealMan 双臂机器人平台上开展了一系列日常灵巧操作实验。任务涵盖抓取、放置、连续倾倒控制和可动部件物体交互，以便在不同交互复杂度和运动约束下进行评估。具体任务包括：

1. 依次把两个纸盒放到托盘上（Sequential Place）；
2. 抓取毛绒玩具并放入篮中（Soft Place）；
3. 把药盒放入打开的抽屉并关闭抽屉（Drawer Close）；
4. 把芒果从桌面转移到水果篮（Fruit Place）；
5. 拿起瓶子，将水倒入容器，再把瓶子放回（Pour Water）；
6. 双手分别抓住苹果和柠檬，再同步放置（Bimanual Place）。

实验使用 RealMan 双臂机器人。每条手臂具有 6 个自由度，并配备一只 6 自由度因时（Inspire）灵巧手。视觉感知与实验记录采用 Intel RealSense D435i 深度相机。机器人通过关节空间位置控制持续跟踪轨迹，以保证双臂动作平滑、同步且稳定。

每个任务重复 20 次。每次试验中，物体位姿在相机视野与机器人可达工作空间的交集内随机初始化；实验桌面含有干扰物体。该设置用于评估系统在现实感知不确定性下的鲁棒性。

我们将 ObjRetarget 与 OKAMI [31]、ORION [32] 比较。ORION 原本为平行夹爪设计，其末端执行器轨迹无法直接用于灵巧手。为保证公平比较，我们将其夹爪轨迹转换为手掌轨迹，并在逆运动学求解器中加入手部姿态和关节约束，使其能在相同任务设置下稳定完成多指抓取与放置。

所有实验均使用 PyTorch 深度学习框架，在配备 NVIDIA RTX 4090 GPU 和 Intel Core i7-11700KF CPU 的系统上运行。

**图 4：** ObjRetarget 在六项真实灵巧操作任务上的可视化。每项任务上排为人类示范，下排为机器人执行。从左到右依次是：(a) 依次放置两个纸盒；(b) 将毛绒玩具放入篮中；(c) 将药盒放入抽屉并关上抽屉；(d) 将芒果放入水果篮；(e) 拿起瓶子倒水并放回；(f) 双手抓取苹果和柠檬并同步放置。

**表 I：任务成功率（%）**

| 任务（每项 20 次） | OKAMI [31] | ORION [32] | 本文方法 |
|---|---:|---:|---:|
| Soft Place | 13 | 12 | 17 |
| Pour Water | 12 | 12 | 16 |
| Fruit Place | 14 | 13 | 16 |
| Drawer Close | 10 | 8 | 13 |
| Sequential Place | 12 | 9 | 14 |
| Bimanual Place | 13 | 8 | 15 |
| 平均成功率 | 61.6% | 50.8% | 75.8% |

### B. 动作重定向对比实验

#### 1）多方法比较

我们在全部任务上系统比较 ObjRetarget、OKAMI 和 ORION，以评估复杂灵巧操作场景中的执行稳定性与任务完成能力。ObjRetarget 的执行结果见图 4。所有实验均在工作空间内随机初始化物体位姿，要求各方法在不同空间构型和视觉观测下自主完成任务。该设置能够更真实地评估方法在杂乱、不确定环境中的鲁棒性与泛化能力。

如表 I 所示，ObjRetarget 在所有任务中均取得最高成功率，尤其在倒水、关闭抽屉、连续放置和双手放置等对接触敏感或包含多个阶段的任务中优势明显。结果表明，结构化手—物建模提高了接触稳定性，统一的手臂运动约束则改善了时间一致性和协调性。OKAMI 在较简单的放置任务中表现相近，但在需要持续接触或分阶段转换的操作中性能下降。ORION 总体表现最低，说明如果缺少显式动作与接触建模，就难以维持稳定抓取和协调的手腕动作。

#### 2）跨示范者泛化

为进一步评估系统对个体差异的鲁棒性，我们在跨示范者条件下测试 ObjRetarget。三名手部尺寸、动作习惯和操作风格不同的示范者执行同一组任务。在不修改模型结构或参数的情况下，系统把所有人的示范映射到同一机器人平台执行。

如图 5 所示，ObjRetarget 对不同个体的示范都能保持稳定性能。操作风格和手部形态的变化虽然会造成任务结果的轻微差异，但三项任务在所有示范者上仍保持较高且接近的成功率，说明系统不依赖某一种特定动作风格。

**图 5：** 使用多名示范者的视频对 ObjRetarget 进行性能评估。

### C. 消融实验

#### 1）手—物几何一致性模块

为评估结构化接触建模对任务稳定性与成功率的贡献，我们比较三种设置：移除基于人类示范的初始化（W/o Init Retarget）、进一步移除手—物几何一致性（W/o Hand Geometry），以及完整 ObjRetarget。评估指标包括：物体滑移距离 [33]，即物体相对于手部接触坐标系的累计位移，用于反映接触稳定性；几何一致性 [34]，由局部手—物接触的归一化边长误差和相对位姿误差计算，用于衡量接触结构保持程度；任务成功率，即成功完成任务的试验比例。

**表 II：手—物几何一致性消融实验**

| 方法 | 物体滑移距离（m，越低越好） | 几何一致性（越低越好） | 任务成功率（%，越高越好） |
|---|---:|---:|---:|
| W/o Init Retarget | 0.025 | 0.183 | 65.0 |
| W/o Hand Geometry | 0.045 | 0.275 | 53.3 |
| 本文方法 | **0.012** | **0.081** | **75.8** |

如表 II 所示，完整 ObjRetarget 获得最低几何误差和物体滑移距离，以及最高成功率。移除初始化会减慢收敛并降低稳定性；进一步移除几何一致性会导致明显滑移、接触失败和姿态坍塌。

#### 2）手臂初始化与拟人化约束消融

我们评估初始化重定向和任务自适应手臂平面正则化对动作精度与自然性的影响。比较三种设置：W/o Init Retarget（移除初始化重定向先验）、W/o Arm-Plane Opt（移除手臂平面正则化）和完整 ObjRetarget。评估采用四项指标：用于衡量空间精度的平均逐关节位置误差 MPJPE [35]；用于衡量方向精度的末端执行器四元数距离 Quat [36]；用于衡量整体轨迹形状相似性的 Fréchet 距离；以及反映执行可靠性的任务成功率。

**表 III：手臂初始化与拟人化约束消融实验**

| 方法 | MPJPE（m，越低越好） | Quat（rad，越低越好） | Fréchet（m，越低越好） | 任务成功率（%，越高越好） |
|---|---:|---:|---:|---:|
| W/o Init Retarget | 0.125 | 0.275 | 0.313 | 60.8 |
| W/o Arm-Plane Opt | 0.103 | 0.337 | 0.251 | 57.5 |
| 本文方法 | **0.088** | **0.192** | **0.124** | **75.8** |

如表 III 所示，完整 ObjRetarget 在所有指标上表现最好，生成的轨迹与人类示范高度一致。移除初始化后，搜索空间增大，MPJPE 和 Fréchet 距离上升；移除手臂平面正则化则会产生不自然的肘部动作与振荡，使轨迹一致性下降。

## V. 结论

本文提出 ObjRetarget：一种人到机器人动作重定向框架。它将多面体手部建模与拟人化手臂约束结合起来，把手臂层面的全局运动与对接触敏感的手部操作解耦，以实现稳定、自然且可泛化的灵巧操作。该框架在 RMC-DA 双臂机器人平台上完成了多项精细操作验证，包括抓取、倾倒、物体转移、关闭抽屉、连续放置和双手协调。实验结果表明，多面体手部簇表示能够有效保持手—物接触结构和操作语义，而由参考轨迹引导的手臂优化能够保证全局动作准确且符合拟人化特征。

尽管如此，当前框架仍存在局限：复杂手—物交互中的动态反馈尚未被充分利用，并且该方法目前只适用于上肢操作。未来工作将整合自适应力反馈，并把 ObjRetarget 扩展到机器人全身操作，以构建更通用、更具柔顺性的灵巧操作系统。

## 参考文献

> 为保证作者名、论文题名、期刊或会议名称及检索信息准确，本节沿用原文书目，不翻译题名。

[1] H. Xiong, Q. Li, Y. C. Chen, et al., “Learning by watching: Physical imitation of manipulation skills from human videos,” in *Proc. IEEE/RSJ Int. Conf. Intell. Robot Syst. (IROS)*, 2021, pp. 7827–7834.  
[2] Y. Qin, Y. H. Wu, S. Liu, et al., “DexMV: Imitation learning for dexterous manipulation from human videos,” in *Proc. Eur. Conf. Comput. Vis. (ECCV)*, 2022, pp. 570–587.  
[3] Y. Liu, W. C. Shin, Y. Han, et al., “ImMimic: Cross-domain imitation from human videos via mapping and interpolation,” arXiv:2509.10952, 2025.  
[4] L. S. Li, J. Jiang, P. Ruppel, et al., “A mobile robot hand-arm teleoperation system by vision and IMU,” in *Proc. IEEE/RSJ IROS*, 2020, pp. 10900–10906.  
[5] S. Li, N. Hendrich, H. Liang, et al., “A dexterous hand-arm teleoperation system based on hand pose estimation and active vision,” *IEEE Trans. Cybern.*, vol. 54, no. 3, pp. 1417–1428, 2022.  
[6] A. Sivakumar, K. Shaw, and D. Pathak, “Robotic telekinesis: Learning a robotic hand imitator by watching humans on YouTube,” arXiv:2202.10448, 2022.  
[7] D. Antotsiou, G. Garcia-Hernando, and T.-K. Kim, “Task-oriented hand motion retargeting for dexterous manipulation imitation,” in *ECCV Workshops*, 2018.  
[8] M. Zhang, Q. Gao, Y. Lai, et al., “HR-GCN: 2D–3D whole-body pose estimation with high-resolution graph convolutional network from a monocular camera,” *IEEE Sens. J.*, 2025.  
[9] L. Yang, X. Huang, Z. Wu, et al., “OmniRetarget: Interaction-preserving data generation for humanoid whole-body loco-manipulation and scene interaction,” arXiv:2509.26633, 2025.  
[10] H. Weng, Y. Li, N. Sobanbabu, et al., “HDMI: Learning interactive humanoid whole-body control from human videos,” arXiv:2509.16757, 2025.  
[11] O. A. Andrychowicz, B. Baker, M. Chociej, et al., “Learning dexterous in-hand manipulation,” *Int. J. Robot. Res.*, vol. 39, no. 1, pp. 3–20, 2020.  
[12] A. Gupta, C. Eppner, S. Levine, et al., “Learning dexterous manipulation for a soft robotic hand from human demonstrations,” in *Proc. IEEE/RSJ IROS*, 2016, pp. 3786–3793.  
[13] W. Yang and W. Jin, “ContactSDF: Signed distance functions as multi-contact models for dexterous manipulation,” *IEEE Robot. Autom. Lett.*, 2025.  
[14] A. Rajeswaran, K. Lowrey, E. V. Todorov, et al., “Towards generalization and simplicity in continuous control,” in *NeurIPS*, vol. 30, 2017.  
[15] S. Calinon, “A tutorial on task-parameterized movement learning and retrieval,” *Intell. Serv. Robot.*, vol. 9, no. 1, pp. 1–29, 2016.  
[16] Z. Si, Z. Zhu, A. Agarwal, S. Anderson and W. Yuan, “Grasp stability prediction with sim-to-real transfer from tactile sensing,” in *Proc. IEEE/RSJ IROS*, 2022, pp. 7809–7816.  
[17] Y. Liang, et al., “Dynamic movement primitive based motion retargeting for dual-arm sign language motions,” in *Proc. IEEE ICRA*, 2021, pp. 8195–8201.  
[18] X. Xing, K. Maqsood, C. Zeng, et al., “Dynamic motion primitives-based trajectory learning for physical human–robot interaction force control,” *IEEE Trans. Ind. Inform.*, vol. 20, no. 2, pp. 1675–1686, 2023.  
[19] T. He, Z. Luo, W. Xiao, et al., “Learning human-to-humanoid real-time whole-body teleoperation,” in *Proc. IEEE/RSJ IROS*, 2024, pp. 8944–8951.  
[20] X. B. Peng, et al., “Learning agile robotic locomotion skills by imitating animals,” arXiv:2004.00784, 2020.  
[21] S. Li, et al., “Vision-based teleoperation of Shadow dexterous hand using end-to-end deep neural network,” in *Proc. IEEE ICRA*, 2019, pp. 416–422.  
[22] H. Zhang, et al., “Kinematic motion retargeting via neural latent optimization for learning sign language,” *IEEE Robot. Autom. Lett.*, vol. 7, no. 2, pp. 4582–4589, 2022.  
[23] B. Zheng, D. Liang, Q. Huang, et al., “Frame-by-frame motion retargeting with self-collision avoidance from diverse human demonstrations,” *IEEE Robot. Autom. Lett.*, 2024.  
[24] H. Zhang, et al., “Kinematic motion retargeting via neural latent optimization for learning sign language,” *IEEE Robot. Autom. Lett.*, vol. 7, no. 2, pp. 4582–4589, 2022.  
[25] S. Ross, G. Gordon, and D. Bagnell, “A reduction of imitation learning and structured prediction to no-regret online learning,” in *AISTATS*, 2011, pp. 627–635.  
[26] C. Finn, T. Yu, T. Zhang, et al., “One-shot visual imitation learning via meta-learning,” in *CoRL*, 2017, pp. 357–368.  
[27] M. Shridhar, L. Manuelli, and D. Fox, “CLIPort: What and where pathways for robotic manipulation,” in *CoRL*, 2022, pp. 894–906.  
[28] S. Zhu, R. Kaushik, S. Kaski, et al., “Imitation-guided multimodal policy generation from behaviourally diverse demonstrations,” in *Proc. IEEE/RSJ IROS*, 2023, pp. 1675–1682.  
[29] V. Ye, G. Pavlakos, J. Malik, and A. Kanazawa, “Decoupling human and camera motion from videos in the wild,” in *CVPR*, 2023.  
[30] Anonymous, “DexTele: A dual-arm dexterous teleoperation system based on motion retargeting and adaptive force control,” in *Proc. IEEE ICRA*, 2026, to appear.  
[31] J. Li, Y. Zhu, Y. Xie, et al., “OKAMI: Teaching humanoid robots manipulation skills through single video imitation,” arXiv:2410.11792, 2024.  
[32] Y. Zhu, A. Lim, P. Stone, and Y. Zhu, “Vision-based manipulation from single human video with open-world object graphs,” arXiv:2405.20321, 2024.  
[33] G. Garcia-Hernando, S. Yuan, S. Baek, et al., “First-person hand action benchmark with RGB-D videos and 3D hand pose annotations,” in *CVPR*, 2018, pp. 409–419.  
[34] S. Song, A. Zeng, J. Lee, et al., “Grasping in the wild: Learning 6-DoF closed-loop grasping from low-cost demonstrations,” *IEEE Robot. Autom. Lett.*, vol. 5, no. 3, pp. 4978–4985, 2020.  
[35] R. Villegas, J. Yang, D. Ceylan, et al., “Neural kinematic networks for unsupervised motion retargetting,” in *CVPR*, 2018, pp. 8639–8648.  
[36] R. Greer, N. Deo, and M. Trivedi, “Trajectory prediction in autonomous driving with a lane heading auxiliary loss,” *IEEE Robot. Autom. Lett.*, vol. 6, no. 3, pp. 4907–4914, 2021.  
[37] H. Alt and M. Godau, “Computing the Fréchet distance between two polygonal curves,” *Int. J. Comput. Geom. Appl.*, vol. 5, no. 1–2, pp. 75–91, 1995.
