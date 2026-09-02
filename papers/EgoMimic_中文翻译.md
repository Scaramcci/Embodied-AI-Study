# EgoMimic：通过第一人称视频扩展模仿学习

> 原文：*EgoMimic: Scaling Imitation Learning via Egocentric Video*  
> 作者：Simar Kareer、Dhruv Patel、Ryan Punamiya、Pranay Mathur、Shuo Cheng、Chen Wang、Judy Hoffman、Danfei Xu  
> arXiv:2410.24221v1，2024-10-31  
> 说明：本文为学习用中文全译稿。章节、公式、算法、图表编号与参考文献编号均与原文一致；论文图片请对照同目录原始 PDF，参考文献保留英文书目信息以便检索。

**图 1：** EgoMimic 将“人体具身数据”——与三维手部轨迹配对的第一人称视频——开发成一种可扩展的模仿学习数据源。操作者只需佩戴 Project Aria 眼镜并用自己的双手执行操作任务，就可以在任何地方、无须机器人地采集此类数据。EgoMimic 弥合人体具身数据（左）与传统机器人遥操作数据（右）在运动学、数据分布和外观上的差异，从而学习统一策略。实验发现，与仅使用机器人数据相比，人体具身数据可将任务表现提高 34%–228%，并使策略能够泛化到新物体乃至新场景。

## 摘要

模仿学习所需示范数据的规模与多样性是一项重大挑战。本文提出 EgoMimic：一个通过人体具身数据扩展机器人操作学习的全栈框架，具体使用与三维手部跟踪配对的人类第一人称视频。EgoMimic 通过四项设计实现这一目标：(1) 使用符合人体工学的 Project Aria 眼镜采集人体具身数据；(2) 构建低成本双臂操作平台，以缩小人体数据与机器人数据之间的运动学差距；(3) 使用跨域数据对齐技术；(4) 设计在人类数据与机器人数据上联合训练的模仿学习架构。

与以往只从人类视频中提取高层意图的方法不同，本文把人类数据与机器人数据同等视为具身示范数据，并使用两种数据学习统一策略。EgoMimic 在多项具有挑战性的长时序、单臂和双臂真实操作任务中显著优于现有模仿学习方法，同时能够泛化到全新场景。最后，实验显示出良好的扩展趋势：增加一小时人手数据所带来的收益，显著高于增加一小时机器人数据。视频和补充材料见 <https://egomimic.github.io/>。

## I. 引言

端到端模仿学习在复杂操作任务上已经表现出显著能力，但在面对新场景和新任务时仍然较为脆弱。受到计算机视觉和自然语言处理近期成功的启发，本文提出一个假设：若要让学习策略获得广泛泛化能力，就必须大幅扩展训练数据规模。相邻领域可以利用互联网数据，但机器人领域尚不存在等价的数据来源。

为了扩展机器人数据，近期出现了多种数据采集系统。例如，ALOHA [1], [2] 和 GELLO [3] 使用直观的主从控制采集遥操作数据；另一些工作开发了手持式夹爪，使人们无需机器人本体即可采集数据 [4]。尽管取得了进展，这些系统仍然需要专用硬件，也需要示范者主动投入精力。本文假设，实现互联网规模机器人数据的关键一步是被动数据采集。正如互联网最初并不是为了整理大模型训练数据而建立的一样，理想的机器人数据系统应当允许用户在没有刻意采集意图的情况下产生传感运动行为数据。

人类视频，尤其是第一人称视角视频，是扩展被动数据的理想来源。它与机器人数据较为接近：第一人称相机提供视觉观测，三维手部跟踪提供动作信息，设备上的 SLAM 提供定位。能够采集这类信息的消费级设备——包括扩展现实（XR）设备和带相机的智能眼镜——为大规模被动数据采集带来新机会。尽管近期工作已经开始使用人类视频，但通常只从视频中提取高层意图，用于构建指导低层条件策略的规划器 [5], [6]。因此，系统性能仍受限于只用遥操作数据训练的低层策略。

本文主张：若要真正利用人类数据扩展机器人性能，就不应把人类视频仅仅视为需要单独处理的辅助数据源。相反，应利用第一人称人体数据与机器人数据之间的内在相似性，把二者视为连续具身数据谱系中地位相同的组成部分。要无缝地从两类数据学习，需要全栈创新：从统一两类数据的数据采集系统，到能够实现跨具身策略学习的模仿学习架构。

为此，本文把人类数据作为机器人操作的一等数据源。该系统是使用可穿戴智能眼镜产生的被动数据训练操作策略的重要一步。EgoMimic（图 1）同时采集人类第一人称视频和机器人遥操作数据，并据此联合训练操作策略，具体包括：

1. 基于 Project Aria 眼镜 [7] 的人体数据采集系统，可获取第一人称视频、三维手部跟踪和设备 SLAM。丰富的信息使人类第一人称数据能够被转换成与机器人模仿学习兼容的形式。
2. 能力充分且成本较低的双臂机器人，尽量减小其与人体具身数据之间的运动学差距和相机到相机的差距。系统把 Project Aria 眼镜同时作为机器人的主要传感器，从硬件上缩小视场角、动态范围等设备差异。
3. 为缓解数据分布差异，分别归一化并对齐人类和机器人的动作分布；同时通过视觉遮罩缩小人类手臂与机器人机械臂之间的外观差距。
4. 统一的模仿学习架构：使用共同的视觉编码器和策略网络，在手部数据与机器人数据上联合训练。尽管人类与机器人的动作空间不同，模型仍强制学习共享表示，使性能可以随人体具身数据增加而扩展，并优于分别处理两类数据的方法。

EgoMimic 在三个具有挑战性的真实长时序操作任务上进行评估：连续物体入碗、衣物折叠和食品装袋（图 5）。结果表明，EgoMimic 在所有场景中都显著改善任务表现，相对提升最高达到 200%。它还能泛化到只在人类数据中出现过的物体和场景。扩展性实验进一步表明，在已有一定机器人数据的基础上，增加一小时人手数据明显优于增加一小时机器人数据。

## II. 相关工作

### A. 模仿学习

模仿学习（Imitation Learning，IL）已被用于多种接触丰富的操作任务 [8]–[10]。近期发展产生了像素到动作的模仿学习模型，它们直接把原始视觉输入映射为机器人低层控制 [1], [11]。这类视觉模仿学习模型表现出较强的反应式策略能力 [5], [12]；RT-1 和 RT-2 等工作还表明，扩大模型和数据规模可以带来较强泛化能力 [13], [14]。但是这些方法仍然耗费大量人力和资源，例如 RT-1 使用 13 台机器人，历时 17 个月采集数据 [13]。EgoMimic 利用可扩展的人体具身示范，其潜在规模和多样性可能超过只由机器人示范构成的数据集。

### B. 从视频示范中学习

为了满足像素到动作模仿学习算法的数据需求，许多近期工作利用高度可扩展的人类数据。不同工作在不同抽象层面使用人类数据：有些利用互联网规模的人类视频预训练视觉表示 [15]–[17]；有些通过预测点轨迹、在像素空间中生成中间状态或预测可供性，更显式地理解场景动力学 [6], [18]–[21]；还有近期工作使用手部轨迹预测近似机器人动作预测 [5]。

这些方法虽然利用了人手数据，却通常使用彼此独立的模块处理人类数据与机器人数据。EgoMimic 充分利用 Aria 眼镜提供的机载 SLAM 等丰富信息，把人类和机器人数据统一起来并同等对待，使用单一端到端策略在两类数据上联合训练。

### C. 数据采集系统

许多方法被用于扩展机器人数据。Space Mouse 等低成本设备可以对机械臂进行灵敏、精细的遥操作 [10], [11], [22]–[24]；另一些工作使用 VR 头显改善控制直观性 [25]–[29]。ALOHA 和 GELLO 等系统通过主从遥操作接口 [1], [3] 或外骨骼 [30], [31]，提高了低成本精细双臂任务的数据采集体验。

还有一些工作试图采集包含三维动作跟踪等丰富信息的人体具身数据，但现有系统存在权衡：信息丰富的系统往往缺乏便携性，例如使用固定相机 [5], [32]–[34]；或者不够符合人体工学，例如要求使用手持夹爪 [4], [35] 或穿戴式相机 [36], [37]。这些条件限制了数据采集的被动扩展能力。EgoMimic 同样采集第一人称视频和三维手部跟踪，但采用符合人体工学的 Project Aria 眼镜 [7]。VR 头显等可穿戴采集方式通常记录手部位置以遥操作机器人，而 EgoMimic 在采集人体数据时完全不需要机器人。随着类似消费级设备逐渐普及，这种系统有望实现被动扩展 [38]。

### D. 跨具身策略学习

跨具身学习的进展表明，在包含多种机器人具身形态的数据集上训练的大模型通常具有更好的泛化能力 [39]。一些方法通过观测重投影 [40]、动作抽象 [41] 和以具身形态为条件的策略 [42] 弥合具身差距，近期工作也把跨具身学习视为域适应问题 [43]。EgoMimic 主张在人类到机器人的迁移学习中，把人类数据视为另一种具身形态的数据。

## III. EgoMimic

EgoMimic 是一个采集并学习人体第一人称具身数据和机器人数据的全栈框架。下面依次介绍人体与机器人数据采集的硬件系统（III-A）、两种数据的处理与对齐（III-B），以及统一策略架构（III-C）。所有设计都服务于一个目标：使人体具身数据能够像机器人遥操作数据一样适合机器人学习。

### A. 数据采集系统与硬件设计

#### 用于第一人称示范采集的 Aria 眼镜

理想的人体数据系统需要在能够被动扩展的同时，获取丰富的场景信息。这样的系统应当可穿戴、符合人体工学、具有宽视场角，并能跟踪手部位置和设备位姿等信息。EgoMimic 基于 Project Aria 眼镜 [7] 构建系统。Aria 是用于采集多模态第一人称数据的头戴式设备，采用仅重 75 克的眼镜形态，可以长时间佩戴并进行被动数据采集。

本文使用正面的宽视场 RGB 相机采集视觉观测，并使用两个单色场景相机估计设备位姿和跟踪手部（示例见图 2）。特别是，即使手部移出主 RGB 相机视野，侧向场景相机仍可继续跟踪。这显著缓解了一个自然行为造成的问题：在连续操作任务中，人通常会提前转动头部和视线，使其先于手部指向后续目标。

围绕 Project Aria 已经开展了大规模数据采集工作 [44], [45]，学术界也可通过研究合作计划获取设备。未来，EgoMimic 可以让使用者把自行采集的数据无缝合并到这些大数据集中。总体而言，该系统实现了既被动又信息丰富的人体数据采集，有助于扩展机器人操作数据。

#### 低成本双臂操作平台

为了有效利用第一人称人体具身数据，机器人应当能够以近似人类手臂的方式运动。以往工作常使用 Franka Emika Panda 等桌面机械臂 [46]。这些机器人能力很强，但在运动学结构上与人类手臂差异明显；较大的质量和惯量还要求其出于安全考虑缓慢谨慎运动，难以达到人类执行操作任务的速度。

为此，作者参考 ALOHA [1] 构建了轻量、灵活且低成本的双臂平台。机器人由两条 6 自由度 ViperX 300 S 从臂组成，每条手臂配备 Intel RealSense D405 腕部相机；双臂倒置安装在可调高度支架上作为躯干（图 2），在运动学上近似人体上半身。ViperX 手臂外形纤细，尺寸接近人臂，因此较为灵活。除 ViperX 手臂外，整个支架的装配成本低于 1,000 美元，作者计划公开物料清单。系统还构建了类似 ALOHA 的主臂装置，用于采集机器人遥操作数据。

由于方法要从人类和机器人第一人称数据中共同学习视觉策略，对齐视觉观测空间十分重要。除了后处理对齐，作者还直接匹配相机硬件：在机器人躯干顶部接近人眼的位置安装另一副 Aria 眼镜作为主要视觉传感器（图 2）。这样可以缩小由相机设备造成的观测域差距，包括视场角、曝光水平和动态范围差异。

**图 2：** 人体数据系统使用 Aria 眼镜采集第一人称 RGB 视频，并利用侧面的 SLAM 相机定位设备和跟踪双手。机器人由两条 ViperX 从臂构成，配备 Intel RealSense D405 腕部相机，并由两条 WidowX 主臂控制。机器人使用相同的 Aria 眼镜作为主要视觉传感器，以缩小相机到相机的差距。

### B. 数据处理与域对齐

为了使用人类数据和机器人数据训练统一策略，EgoMimic 需要弥合三个关键差距：(1) 统一动作坐标系；(2) 对齐动作分布；(3) 缩小视觉外观差距。

#### 原始数据流

按照 III-A 所述硬件设置，系统流式记录原始传感器数据。人和机器人佩戴的 Aria 眼镜都产生第一人称 RGB 图像流；机器人还产生两个腕部相机图像流。对于本体感知，系统使用 Aria Machine Perception Service（MPS）[47] 估计双手的三维位姿：

$$
{}^{H}p\in SE(3)\times SE(3).
$$

机器人本体感知包括两个末端执行器位姿：

$$
{}^{R}p\in SE(3)\times SE(3),
$$

以及包含夹爪开合关节的机器人关节位置：

$$
{}^{R}q\in \mathbb{R}^{2\times7}.
$$

对于遥操作机器人数据，系统还采集关节空间动作：

$$
{}^{R}a^q\in \mathbb{R}^{2\times7}.
$$

**表 I：人类与机器人数据流对比**

| 来源 | 类型 | 数据 |
|---|---|---|
| 人类 $D_H$ | 图像 | 第一人称视角 |
| 人类 $D_H$ | 本体感知 | 三维手部位姿 ${}^{H}p$ |
| 人类 $D_H$ | 动作 | 归一化手部轨迹 ${}^{H}a^p$ |
| 机器人 $D_R$ | 图像 | 第一人称视角 + 腕部视角 |
| 机器人 $D_R$ | 本体感知 | 末端位姿 ${}^{R}p$、关节位置 ${}^{R}q$ |
| 机器人 $D_R$ | 动作 | 末端动作 ${}^{R}a^p$、关节动作 ${}^{R}a^q$ |

#### 统一人类—机器人数据坐标系

机器人动作和本体感知数据通常使用固定参考系，例如相机坐标系或机器人基座坐标系。但第一人称手部数据来自持续运动的相机，这一固定参考系假设不再成立。为统一坐标系并联合训练策略，本文把人手轨迹和机器人末端轨迹都变换到以相机为中心的稳定参考系。

沿用动作分块预测思想 [1], [11]，系统为人手和机器人末端构造动作块 $a^p_{t:t+h}$。为简化符号，以下用单臂描述，双臂情况可直接推广。原始轨迹是三维位姿序列：

$$
[p_t^{F_t},p_{t+1}^{F_{t+1}},\ldots,p_{t+h}^{F_{t+h}}],
$$

其中 $F_i$ 是估计 $p_i$ 时的相机坐标系。机器人的 $F_i$ 保持固定，而人体第一人称数据中的 $F_i$ 随头部运动不断变化。目标是把轨迹中每个位置都变换到当前观测相机坐标系 $F_t$，构造 $a^p_{t:t+h}$。这样，策略预测动作时无需考虑未来相机如何运动。

对于人体数据，系统使用 MPS 视觉惯性 SLAM 得到 Aria 眼镜在世界坐标系中的位姿 $T_{F_i}^{W}\in SE(3)$，动作轨迹变换为：

$$
{}^{H}a_i^p=
\left[(T_{F_t}^{W})^{-1}T_{F_i}^{W}p_i^{F_i},
\quad i\in\{t,t+1,\ldots,t+h\}\right].
$$

图 2 左上给出了示例轨迹。机器人数据则通过手眼标定获得固定相机坐标系，并以类似方式变换。统一参考系后，无论动作监督来自人类视频还是机器人遥操作示范，策略都可以共同学习。

#### 对齐人类—机器人位姿分布

即使通过硬件设计和数据处理进行了对齐，采集到的人手位姿与机器人末端位姿仍呈现不同分布。这些差异来自人体生物力学、任务执行方式，以及人和机器人测量精度的差异。若不缩小这种差距，策略可能分别学习两个数据域的表示 [48], [49]，从而无法利用增加的人类数据扩展性能。

为此，本文分别对两个来源的末端（或手部）位姿和动作进行高斯归一化，如图 3 所示。与 [49] 的发现一致，这项简单技术在实验中有效（IV-B）；作者计划进一步探索动作量化等方法 [13]。

#### 缩小视觉外观差距

即使两类数据使用相同传感硬件，人手与机械臂之间仍存在很大的视觉外观差距。以往工作尝试在视觉观测中遮挡或移除操作主体 [50], [51]。EgoMimic 使用 SAM [52] 同时遮挡人手和机器人，再叠加一条红线表示末端执行器方向（图 3）。SAM 的点提示由机器人末端位姿和人手位姿投影到图像平面后产生。

**图 3：** (a) 动作归一化：人手和机器人位姿分布不同，尤其体现在 $y$（左右）方向。模型输入前，分别对人手和机器人位姿数据进行高斯归一化。(b) 视觉遮罩：为了缩小人手与机械臂的外观差距，使用 SAM 对两者施加黑色遮罩，再在图像中叠加红线。

### C. 人类—机器人联合策略训练

现有方法通常采用分层架构：用人类数据训练高层策略，再由其条件化一个输出机器人动作的低层策略 [5], [6]。但这种架构天然受低层策略能力限制，因为只由机器人数据训练的低层策略并不能直接从大量人类数据中受益。EgoMimic 提出一个简单的统一架构（图 4），从统一数据中学习并促进共享表示。模型以 ACT [1] 为基础，但设计也可以用于其他基于 Transformer 的模仿学习算法。

统一架构中的关键问题是选择机器人动作空间。机器人末端位姿在语义上比机器人关节位置更接近人手位姿，但对于本文使用的机器人，通过笛卡尔控制器（例如差分逆运动学）使用末端位姿控制并不容易，因为 6 自由度 ViperX 手臂的解冗余度较低。实验中，机器人轨迹经常遇到奇异点或不平滑解。因此，系统最终使用关节空间控制，即用预测关节动作 $\hat a^q_{t:t+h}$ 控制机器人，同时使用位姿空间预测学习人类—机器人联合表示。需要指出，这种同时预测位姿和关节动作的设计与所用硬件有关；更适合末端空间控制的机器人可以不再预测关节空间动作。

除两个浅层输入头和输出头外，策略的其他参数全部共享。输入头先变换视觉与本体感知嵌入，再送入策略 Transformer；Transformer 处理这些特征后，两个输出头分别把隐表示转换为位姿预测或关节空间预测。位姿损失通过 ${}^{H}a^p$ 和 ${}^{R}a^p$ 同时监督人类与机器人数据，而关节动作损失只用机器人数据 ${}^{R}a^q$ 监督。两个分支之间只隔着一个线性层，这迫使模型为两个数据域学习联合表示。算法 1 总结了训练过程，表 I 总结了训练数据。

**图 4：** 人类—机器人联合策略学习架构。模型使用共享视觉编码器和 ACT 编码器处理归一化的人手数据与机器人数据；两类数据都输出位姿预测，机器人数据还输出关节动作预测。模型使用遮罩图像缩小人类—机器人的外观差距，并为机器人输入腕部相机视图。

**算法 1：人类—机器人联合策略学习**

输入：人类数据集 $D_H$，机器人数据集 $D_R$。

1. 初始化共享 Transformer 编码器 $f_{enc}(\cdot)$、位姿解码器 $f^p(f_{enc}(\cdot))$ 和关节解码器 $f^q(f_{enc}(\cdot))$。
2. 对迭代 $n=1,2,\ldots$：
3. 人类数据：从 $D_H$ 采样 $(I_t,p_t,a^p_{t:t+h})$。
4. 由 $f^p(f_{enc}(I_t,p_t))$ 预测 $\hat a^p_{t:t+h}$。
5. 计算 $L_p^H=\operatorname{MSE}(\hat a^p_{t:t+h},a^p_{t:t+h})$。
6. 机器人数据：从 $D_R$ 采样 $(I_t,p_t,q_t,a^p_{t:t+h},a^q_{t:t+h})$。
7. 由 $f^q(f_{enc}(I_t,p_t,q_t))$ 预测 $\hat a^q_{t:t+h}$。
8. 由 $f^p(f_{enc}(I_t,p_t,q_t))$ 预测 $\hat a^p_{t:t+h}$。
9. 计算 $L_q^R=\operatorname{MSE}(\hat a^q_{t:t+h},a^q_{t:t+h})$。
10. 计算 $L_p^R=\operatorname{MSE}(\hat a^p_{t:t+h},a^p_{t:t+h})$。
11. 使用 $L_p^H+L_p^R+L_q^R$ 更新 $f_{enc}$、$f^p$ 和 $f^q$。
12. 结束循环。

## IV. 实验

实验验证三个关键假设：

- **H1：** EgoMimic 能利用人体具身数据，提升复杂操作任务中的域内表现。
- **H2：** 人类数据帮助 EgoMimic 泛化到新物体与新场景。
- **H3：** 在已有足够初始机器人数据的情况下，继续采集人类数据比继续采集机器人数据更有价值。

### A. 实验设置

#### 任务

实验选择三个真实世界长时序任务，要求精确对齐、复杂运动和双臂协调（图 5）。

**连续物体入碗（Continuous Object-in-Bowl）：** 机器人拾取一个约 6 厘米长的小毛绒玩具，放入碗中；随后拿起碗，把玩具倒回桌面，并在 40 秒内连续重复。实验从 3 个碗和 5 个玩具中随机选择，并把它们随机放置在桌面 $45\text{ cm}\times60\text{ cm}$ 的范围内。该任务考察精细操作、空间泛化和长时序执行鲁棒性。每次玩具被放入碗中或碗被成功倒空，获得一个分数点（Pts）。实验覆盖 9 种碗—玩具—位置组合，共进行 45 次评估轨迹。

**衣物折叠（Laundry）：** 这是一个双臂任务。T 恤以随机位置放在 $90\text{ cm}\times60\text{ cm}$ 范围内，旋转范围为 $\pm30^\circ$。机器人必须使用双臂依次折叠右袖、左袖，再把整件衣服对折。每完成一个阶段得到分数点；所有阶段均成功的轨迹被计为成功，并据此计算成功率（SR）。实验覆盖 8 种衬衫—位置组合，共进行 40 次评估。

**食品装袋（Groceries）：** 机器人把 3 包薯片放入购物袋。它先用左臂抓住袋子提手上侧以撑开袋口，再用右臂逐一拾取薯片并放入袋中。该任务要求高精度操作——尤其是抓取可变形袋子提手——以及长时序执行鲁棒性。抓住提手以及每放入一包薯片都获得分数点。成功率是三包薯片全部进入袋子的轨迹比例；“Open Bag”是成功抓住袋子提手的轨迹比例，这也是任务中的困难阶段。实验覆盖 10 个袋子位置，共评估 50 次。

**图 5：** EgoMimic 的三个真实世界长时序评估任务：(a) 连续物体入碗；(b) 衣物折叠；(c) 食品装袋。

**表 II：人体与机器人数据采集概览**

| 任务 | 人体示范数 | 人体采集时间（分钟） | 人体每分钟示范数 | 机器人示范数 | 机器人采集时间（分钟） | 机器人每分钟示范数 |
|---|---:|---:|---:|---:|---:|---:|
| 连续物体入碗 | 1400 | 60 | 23 | 270 | 120 | 2 |
| 食品装袋 | 160 | 80 | 2 | 300 | 300 | 1 |
| 衣物折叠 | 590 | 100 | 6 | 430 | 300 | 1 |

表 II 给出了每项任务的数据量。采集机器人数据时，作者有意随机扰动机器人位置，因为实验发现这样能提高鲁棒性。人体数据的采集效率与任务有关：连续物体入碗很容易扩展，而食品装袋因为每次都需要重置场景，采集较慢。

#### 对比方法

为验证人体数据能否提升域内成功率，EgoMimic 与先进模仿学习算法 ACT [1] 比较。实验还与 MimicPlay [5] 比较；后者从人类数据中学习规划器，并用其指导低层策略。该对比用于检验统一架构是否能更有效地共同利用人类与机器人数据。

为保证比较公平，作者使用与 EgoMimic 相同的 Transformer 主干实现 MimicPlay，并移除目标条件，因为 EgoMimic 使用的是单任务策略。由于 EgoMimic 相比 ACT 还包含同时预测关节动作与位姿动作的架构变化，实验增加 EgoMimic（0% Human）作为基线，以区分性能提升来自人类数据还是来自架构变化。

### B. 实验结果

**表 III：三个真实机器人任务的定量结果**

| 方法 | 入碗 Pts | 衣物 Pts | 衣物 SR | 食品 Pts | 食品 SR | 撑开袋口 |
|---|---:|---:|---:|---:|---:|---:|
| ACT [1] | 39 | 82 | 55% | 82 | 22% | 54% |
| MimicPlay [5] | 71 | 78 | 50% | 53 | 8% | 40% |
| EgoMimic（无人体数据） | 68 | 104 | 73% | 92 | 28% | 60% |
| EgoMimic | **128** | **114** | **88%** | **110** | **30%** | **70%** |

#### EgoMimic 改善域内任务表现

在所有任务中，EgoMimic 的任务分数相对提高 34%–228%，相对于 ACT 的绝对成功率提高 8–33%。最大的提升出现在连续物体入碗任务：相对于 ACT，任务分数提高 228%。作者观察到，基线经常在玩具或碗附近偏离几英寸；这表明手部数据可能帮助策略更精确地到达玩具。图 6 展示了定性结果。

为了验证提升来自人手数据而非单纯的架构变化，作者还与 EgoMimic（0% Human）比较。完整 EgoMimic 的分数提高 10%–88%，成功率提高 2–15%。

**图 6：** EgoMimic 的成功案例与失败模式。失败包括：(e) 未能与玩具正确对齐；(f) 未能抓住袋子提手；(g) 策略只抓住衬衫的一侧。EgoMimic 降低了这些失败的发生频率，相对基线把成功率提高 8%–33%。

#### EgoMimic 能够泛化到新物体乃至新场景

实验考察两种域偏移：使用训练中未见颜色的衬衫完成折叠，以及在完全不同的场景中执行连续物体入碗。图 7 显示，ACT 在未见颜色的衬衫上表现很差，成功率为 25%；EgoMimic 则基本保留原有表现，成功率达到 85%。

更值得注意的是，EgoMimic 仅通过学习新场景中的人体数据——其背景和照明均未在机器人数据中出现——就能在没有任何新机器人数据的情况下泛化到该环境，获得 63 分。相比之下，MimicPlay 虽然获得了相同的人类信息，但通过分层架构只在高层使用人手数据，最终仅得到 4 分。这一结果表明，EgoMimic 的架构促进了人手—机器人的联合表示，而分层架构可能形成泛化瓶颈。

**图 7：策略泛化评估。** (a) 使用训练中未见颜色的衣物评估折叠策略，并报告各方法成功率；(b) 在未见场景中评估连续物体入碗策略。

#### 人体数据与机器人数据的扩展性比较

为了研究两种数据源的扩展效果，作者为连续物体入碗任务额外采集数据。如图 8 所示，使用 2 小时机器人数据和 1 小时人体数据训练的 EgoMimic，明显优于使用 3 小时机器人数据训练的 ACT，得分分别为 128 和 74。

一小时人体数据包含 1,400 条示范，而一小时机器人数据只有 135 条示范。结果说明 EgoMimic 能利用人体具身数据更高的采集效率，产生比单独扩展机器人数据更明显的性能增长。作者同时指出：只使用 2 小时机器人数据时，EgoMimic 架构也优于使用相同机器人数据量的 ACT，因此观察到的部分提升仍应归因于架构，而不能全部归因于人体数据。

**图 8：机器人数据与人体数据的扩展。** 蓝线表示使用 2 小时机器人数据并逐渐加入人体数据的 EgoMimic；橙线表示只逐渐加入机器人数据的 ACT。2 小时机器人数据加 1 小时人手数据的 EgoMimic 明显优于使用 3 小时机器人数据的 ACT。

#### 消融实验

作者在连续物体入碗任务上进行消融，以验证各项设计的重要性（表 IV）。移除动作归一化后，任务分数下降 38%，说明动作分布对齐对联合训练十分重要。随后分别移除视觉对齐技术：去掉红色方向线后分数下降 13%；同时去掉方向线和人手/机械臂遮罩后分数下降 26%。最后，不使用任何人手数据训练时，分数下降 47%，表明在该系统上进行人手—机器人联合训练具有显著作用。

**表 IV：连续物体入碗任务的消融结果**

| 方法 | 联合训练得分（Pts） |
|---|---:|
| EgoMimic | **128** |
| 不使用红色方向线 | 112 |
| 不使用方向线和视觉遮罩 | 95 |
| 不使用动作归一化 | 79 |
| 不使用人手数据 | 68 |

## V. 结论

本文提出 EgoMimic：一个使用人类第一人称视频与机器人遥操作数据联合训练操作策略的框架。通过 Project Aria 眼镜、低成本双臂平台、跨域对齐技术和统一策略学习架构，EgoMimic 在三个具有挑战性的真实任务上优于先进基线，并表现出对新场景的泛化能力和良好的数据扩展特性。

未来工作将探索如何泛化到新的机器人具身形态，以及如何学习只在人类数据中出现的全新行为，例如从折叠衬衫泛化到折叠裤子。总体而言，EgoMimic 为通过被动数据采集扩展机器人数据开辟了新的研究方向。

## VI. 附录

### A. 数据处理与域对齐

人类和遥操作机器人完成任务的速度不同。为了联合训练，必须在时间上对齐两类数据。沿用 MimicPlay [5]，作者把人体数据“放慢”，并通过实验发现 4 倍的因子足以对齐两个域。具体而言，机器人数据使用未来 4 秒构造关节和位姿动作，而人体数据使用未来 1 秒。两类数据的动作块大小均为 100，即在各自预测时域内均匀采样 100 个未来动作。

这种时间对齐不依赖原始数据记录频率：人体数据以 30 Hz 记录，机器人数据以 50 Hz 记录。图 9 并排展示人体数据和机器人数据，以及叠加的真实动作轨迹（紫色）。尽管人手运动明显快于机器人，对齐后的动作轨迹长度相似。

**图 9：** 人体数据与机器人数据及其真实动作叠加结果。尽管人手运动速度远快于机器人，经时间对齐后，两种动作轨迹具有近似长度。

联合训练时，系统分别归一化两种具身形态的本体感知和动作（图 3）。给定本体感知 $p_t\in\mathbb{R}^d$，其中 $d$ 随具身形态而变化，使用数据集均值和标准差进行 Z-score 归一化：

$$
\operatorname{norm}(p_t)=\frac{p_t-\mu_p}{\sigma_p}.
$$

动作 $a_{t:t+h}\in\mathbb{R}^{d\times100}$ 使用同样方法归一化。

为了缩小人手与机器人手臂之间的外观差距，系统通过 SAM 2 [52] 对两种具身主体进行遮罩，并在遮罩上叠加红线以增强对齐（图 3）。对于机器人，先通过正运动学计算机器人坐标系中的腕部、夹爪和前臂等三个关键关节的三维坐标：

$$
p_t^R=FK(q_t)\in\mathbb{R}^{3\times3}.
$$

然后使用相机内参 $I_{cam}^{pixels}$ 和外参 $T_R^{cam}$，把这些三维坐标投影到图像平面：

$$
p_t^{pixel}=I_{cam}^{pixels}T_R^{cam}p_t^R\in\mathbb{R}^{3\times2}.
$$

投影后的二维关键点用于提示 SAM 2 [52] 生成机械臂遮罩。得到遮罩后，在 RGB 图像中从夹爪到肘部绘制一条红线。人体数据使用类似流程，通过人手三维坐标提示 SAM 2 生成遮罩，再从手部轮廓包围盒的右下角到左上角沿轮廓绘制红线。

训练期间，人手和机器人手臂都被遮罩，以对齐视觉表示。评估期间，在桌面计算机上实时运行 SAM 2，对机械臂施加相同遮罩和红线叠加。这种方法改善了人手与机器人之间的视觉对齐，促进模型跨人类任务和机器人任务泛化。

### B. Aria Machine Perception Services（MPS）

系统使用 MPS 处理 Aria 眼镜采集的人体数据。Aria 原始数据包含带时间戳的多种传感器信息，包括 RGB 相机、SLAM 相机、IMU、眼动相机和麦克风等。原始数据上传到 MPS 服务器后，云端服务通过 SLAM 估计设备位姿，同时估计环境的半稠密点云、相对于设备坐标系的手部跟踪结果，甚至包括视线方向。

MPS 返回的 SLAM 结果是世界坐标系下、带时间戳的设备位姿 CSV；手部跟踪结果则是时间对齐设备坐标系中的笛卡尔位置 CSV。由于头部运动，每一时刻的手部位置都位于不同参考系中，因此需要按照 III-B 的方法，把未来动作投影到当前设备坐标系。最终，系统把去畸变后的 Aria RGB 图像与手部跟踪、SLAM 信息配对，构建与 robomimic [10] 训练格式兼容的 HDF5 文件。

### C. 人类—机器人联合策略的训练细节

图 10 给出了完整算法结构。每一步同时采样一批手部数据和一批机器人数据，并送入统一架构。EgoMimic 分别对人手与机器人的本体感知和动作执行 Z-score 归一化。归一化本体感知经过线性层形成一个本体感知 token。

与此同时，人手和机器人顶部视角图像经过基于 SAM 的遮罩模块；这些图像以及机器人腕部视图一起送入共享 ResNet-18 视觉编码器，产生视觉 token。模型还加入来自 CVAE 编码器的风格 token $z$；图 10 未画出该部分，其实现与 ACT [1] 一致。所有 token 随后进入 Transformer 编码器—解码器。Transformer 解码器的隐输出根据所需输出类型进入相应线性解码器，生成位姿动作 $\hat a^p$ 或关节动作 $\hat a^j$。

对于机器人数据批次，损失为：

$$
L_{robot}=L_1({}^{R}\hat a^p,{}^{R}a^p)
+L_1({}^{R}\hat a^j,{}^{R}a^j)+KL.
$$

对于人手数据批次，损失为：

$$
L_{hand}=L_1({}^{H}\hat a^p,{}^{H}a^p)+KL,
$$

其中 $KL$ 是 ACT [1] 中使用的 CVAE 潜变量正则项。每一步优化总损失：

$$
L=L_{robot}+L_{hand}.
$$

模型利用 Transformer 可变输入序列，处理不同模态拥有不同视觉观测数量的问题：机器人数据包含腕部图像，人手数据则没有。当腕部图像存在时，系统像 ACT [1] 一样把额外视觉 token 拼接到 Transformer 输入序列中。实验表明，这一策略足以在两类数据上有效联合训练；作者计划进一步尝试 HPT [53] 等更复杂的跨具身学习技术。

人类数据不包含抓取开合动作，因为 Aria 只记录手部位姿。因此，抓取动作仅由机器人关节预测损失 $L_1({}^{R}\hat a^j,{}^{R}a^j)$ 监督，其中夹爪被表示为额外的一个关节。

**图 10：** EgoMimic 的详细架构。两种数据经过各自的归一化与输入头，视觉观测经遮罩后进入共享 ResNet-18，视觉、本体感知和 CVAE 风格 token 共同输入 Transformer。共享隐表示再由不同输出头转换为位姿动作或机器人关节动作。

### D. 训练设置

所有模型训练 120,000 次迭代，使用 4 张 A40 GPU、全局批大小 128，耗时约 24 小时。代码基于 robomimic [10] 实现。

**表 V：EgoMimic 训练设置**

| 项目 | 设置 |
|---|---|
| 策略 | ACT |
| 批大小 | 128 |
| 优化器 | AdamW |
| 初始学习率 | $5\times10^{-5}$ |
| 衰减因子 | 1 |
| 调度器 | Linear |
| 编码器层数 | 4 |
| 解码器层数 | 7 |
| 隐层维度 | 512 |
| 前馈层维度 | 3200 |
| 注意力头数 | 8 |
| 数据增强 | Color Jitter |

### E. MimicPlay 实现

本文对 MimicPlay [5] 的实现尽量遵循原始设置，分别训练高层规划器和低层控制策略。首先训练基于 ResNet-18 的高层编码器，使用高斯混合模型（GMM）生成三维轨迹。高层编码器同时使用人类数据和机器人数据训练，以预测三维轨迹。

高层编码器训练完成后，从 ResNet-18 编码器（即高层规划器）提取潜在表示，并将其作为风格变量 $z$ 输入图 10 所示 Transformer 编码器—解码器。随后，低层 ACT 策略只使用机器人数据训练，高层策略的额外输入作为指导。

**表 VI：MimicPlay 训练设置**

| 部分 | 项目 | 设置 |
|---|---|---|
| 高层 | 网络 | ResNet-18 |
| 高层 | 初始学习率 | 0.0001 |
| 高层 | 衰减因子 | 0.1 |
| 高层 | 批大小 | 50 |
| 高层 | GMM 模态数 | 5 |
| 低层 | 策略 | ACT |
| 低层 | 初始学习率 | $5\times10^{-5}$ |
| 低层 | 优化器 | AdamW |
| 低层 | 衰减因子 | 1 |
| 低层 | 调度器 | Linear |

### F. 策略执行

策略在配备 NVIDIA RTX 4090 GPU 的桌面计算机上运行：推理频率为 1 Hz，控制频率为 25 Hz。预测动作时域为 4 秒，每次只执行预测结果的第 1 秒，再以滚动时域方式重新预测。除以 30 FPS 输出的 Aria 相机外，机器人所有传感器均以 50 Hz 更新。

**表 VII：人类与机器人数据的记录和执行频率**

| 类型 | 人类（Hz） | 机器人（Hz） |
|---|---:|---:|
| 记录 | 30 | 50 |
| 执行（推理） | — | 1 |
| 执行（控制） | — | 25 |

系统将人体数据的时间尺度乘以 0.25，即把人体动作“放慢”，以补偿人和机器人执行任务速度的差异。

**图 11：** EgoMimic 在三个任务中的定性成功案例：(a) 连续物体入碗；(b) 衣物折叠；(c) 食品装袋。

## 参考文献

以下参考文献保留英文题名和原始编号，以便检索。

[1] T. Z. Zhao, V. Kumar, S. Levine, and C. Finn, “Learning fine-grained bimanual manipulation with low-cost hardware,” 2023. <https://arxiv.org/abs/2304.13705>.

[2] ALOHA Team et al., “ALOHA 2: An enhanced low-cost hardware for bimanual teleoperation,” 2024. <https://arxiv.org/abs/2405.02292>.

[3] P. Wu, Y. Shentu, Z. Yi, X. Lin, and P. Abbeel, “GELLO: A general, low-cost, and intuitive teleoperation framework for robot manipulators,” 2024. <https://arxiv.org/abs/2309.13037>.

[4] C. Chi et al., “Universal manipulation interface: In-the-wild robot teaching without in-the-wild robots,” 2024. <https://arxiv.org/abs/2402.10329>.

[5] C. Wang et al., “MimicPlay: Long-horizon imitation learning by watching human play,” 2023. <https://arxiv.org/abs/2302.12422>.

[6] H. Bharadhwaj, A. Gupta, V. Kumar, and S. Tulsiani, “Towards generalizable zero-shot manipulation via translating human interaction plans,” 2023. <https://arxiv.org/abs/2312.00775>.

[7] J. Engel et al., “Project Aria: A new tool for egocentric multi-modal AI research,” 2023. <https://arxiv.org/abs/2308.13561>.

[8] A. Paraschos, C. Daniel, J. R. Peters, and G. Neumann, “Probabilistic movement primitives,” *Advances in Neural Information Processing Systems*, vol. 26, 2013.

[9] C. Finn, T. Yu, T. Zhang, P. Abbeel, and S. Levine, “One-shot visual imitation learning via meta-learning,” 2017. <https://arxiv.org/abs/1709.04905>.

[10] A. Mandlekar et al., “What matters in learning from offline human demonstrations for robot manipulation,” 2021. <https://arxiv.org/abs/2108.03298>.

[11] C. Chi et al., “Diffusion Policy: Visuomotor policy learning via action diffusion,” 2024. <https://arxiv.org/abs/2303.04137>.

[12] S. Young et al., “Visual imitation made easy,” 2020. <https://arxiv.org/abs/2008.04899>.

[13] A. Brohan et al., “RT-1: Robotics Transformer for real-world control at scale,” 2023. <https://arxiv.org/abs/2212.06817>.

[14] A. Brohan et al., “RT-2: Vision-language-action models transfer web knowledge to robotic control,” 2023. <https://arxiv.org/abs/2307.15818>.

[15] S. Nair et al., “R3M: A universal visual representation for robot manipulation,” 2022. <https://arxiv.org/abs/2203.12601>.

[16] I. Radosavovic et al., “Real-world robot learning with masked visual pre-training,” *Conference on Robot Learning*, pp. 416–426, 2023.

[17] Y. J. Ma et al., “VIP: Towards universal visual reward and representation via value-implicit pre-training,” 2022. <https://arxiv.org/abs/2210.00030>.

[18] H. Xiong et al., “Learning by watching: Physical imitation of manipulation skills from human videos,” 2021. <https://arxiv.org/abs/2101.07241>.

[19] C. Wen et al., “Any-point trajectory modeling for policy learning,” 2024. <https://arxiv.org/abs/2401.00025>.

[20] H. Bharadhwaj et al., “Track2Act: Predicting point tracks from internet videos enables generalizable robot manipulation,” 2024. <https://arxiv.org/abs/2405.01527>.

[21] S. Bahl et al., “Affordances from human videos as a versatile representation for robotics,” 2023. <https://arxiv.org/abs/2304.08488>.

[22] A. Mandlekar et al., “Learning to generalize across long-horizon tasks from human demonstrations,” 2020. <https://arxiv.org/abs/2003.06085>.

[23] V. Dhat, N. Walker, and M. Cakmak, “Using 3D mice to control robot manipulators,” *ACM/IEEE International Conference on Human-Robot Interaction*, 2024.

[24] Y. Zhu et al., “VIOLA: Imitation learning for vision-based manipulation with object proposal priors,” 2023. <https://arxiv.org/abs/2210.11339>.

[25] S. P. Arunachalam et al., “Holo-Dex: Teaching dexterity with immersive mixed reality,” *ICRA*, pp. 5962–5969, 2023.

[26] A. George, A. Bartsch, and A. B. Farimani, “OpenVR: Teleoperation for manipulation,” 2023. <https://arxiv.org/abs/2305.09765>.

[27] I. A. Tsokalo et al., “Remote robot control with human-in-the-loop over long distances using digital twins,” *GLOBECOM*, pp. 1–6, 2019.

[28] X. Cheng et al., “Open-TeleVision: Teleoperation with immersive active visual feedback,” 2024. <https://arxiv.org/abs/2407.01512>.

[29] T. He et al., “OmniH2O: Universal and dexterous human-to-humanoid whole-body teleoperation and learning,” 2024. <https://arxiv.org/abs/2406.08858>.

[30] H. Fang et al., “AirExo: Low-cost exoskeletons for learning whole-arm manipulation in the wild,” 2023. <https://arxiv.org/abs/2309.14975>.

[31] S. Yang et al., “ACE: A cross-platform visual-exoskeletons system for low-cost dexterous teleoperation,” 2024. <https://arxiv.org/abs/2408.11805>.

[32] A. Sivakumar, K. Shaw, and D. Pathak, “Robotic telekinesis: Learning a robotic hand imitator by watching humans on YouTube,” 2022. <https://arxiv.org/abs/2202.10448>.

[33] V. Jain et al., “Vid2Robot: End-to-end video-conditioned policy learning with cross-attention transformers,” 2024. <https://arxiv.org/abs/2403.12943>.

[34] Z. Fu et al., “HumanPlus: Humanoid shadowing and imitation from humans,” *Conference on Robot Learning*, 2024.

[35] N. M. M. Shafiullah et al., “On bringing robots home,” 2023. <https://arxiv.org/abs/2311.16098>.

[36] C. Wang et al., “DexCap: Scalable and portable mocap data collection system for dexterous manipulation,” 2024. <https://arxiv.org/abs/2403.07788>.

[37] G. Papagiannis et al., “R+X: Retrieval and execution from everyday human videos,” 2024. <https://arxiv.org/abs/2407.12957>.

[38] K. Grauman et al., “Ego-Exo4D: Understanding skilled human activity from first- and third-person perspectives,” *CVPR*, pp. 19383–19400, 2024.

[39] Open X-Embodiment Collaboration et al., “Open X-Embodiment: Robotic learning datasets and RT-X models,” 2024. <https://arxiv.org/abs/2310.08864>.

[40] L. Y. Chen et al., “Mirage: Cross-embodiment zero-shot policy transfer with cross-painting,” 2024. <https://arxiv.org/abs/2402.19249>.

[41] W. Huang, I. Mordatch, and D. Pathak, “One policy to control them all: Shared modular policies for agent-agnostic control,” 2020. <https://arxiv.org/abs/2007.04976>.

[42] J. Yang et al., “Pushing the limits of cross-embodiment learning for manipulation and navigation,” 2024. <https://arxiv.org/abs/2402.19432>.

[43] J. Yang, D. Sadigh, and C. Finn, “Polybot: Training one policy across robots while embracing variability,” 2023. <https://arxiv.org/abs/2307.03719>.

[44] K. Grauman et al., “Ego4D: Around the world in 3,000 hours of egocentric video,” 2022. <https://arxiv.org/abs/2110.07058>.

[45] L. Ma et al., “Nymeria: A massive collection of multimodal egocentric daily motion in the wild,” 2024. <https://arxiv.org/abs/2406.09905>.

[46] S. Haddadin et al., “The Franka Emika Robot: A reference platform for robotics research and education,” *IEEE Robotics and Automation Magazine*, vol. 29, no. 2, pp. 46–64, 2022.

[47] Meta Research, “Basics — Project Aria docs,” 2024. <https://facebookresearch.github.io/projectaria_tools/docs/data_formats/mps/mps_summary>.

[48] J. Yang et al., “Pushing the limits of cross-embodiment learning for manipulation and navigation,” 2024. <https://arxiv.org/abs/2402.19432>.

[49] J. Hejna et al., “Re-Mix: Optimizing data mixtures for large scale imitation learning,” 2024. <https://arxiv.org/abs/2408.14037>.

[50] Y. Zhou, Y. Aytar, and K. Bousmalis, “Manipulator-independent representations for visual imitation,” 2021. <https://arxiv.org/abs/2103.09016>.

[51] S. Bahl, A. Gupta, and D. Pathak, “Human-to-robot imitation in the wild,” 2022. <https://arxiv.org/abs/2207.09450>.

[52] N. Ravi et al., “SAM 2: Segment Anything in images and videos,” 2024. <https://arxiv.org/abs/2408.00714>.

[53] L. Wang, X. Chen, J. Zhao, and K. He, “Scaling proprioceptive-visual learning with heterogeneous pre-trained transformers,” *NeurIPS*, 2024.
