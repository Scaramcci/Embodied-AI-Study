# UniVLA：利用以任务为中心的潜动作，学习在任意环境中行动

作者：Qingwen Bu、Yanting Yang、Jisong Cai、Shenyuan Gao、Guanghui Ren、Maoqing Yao、Ping Luo、Hongyang Li。

单位：香港大学、OpenDriveLab、AgiBot。代码：https://github.com/OpenDriveLab/UniVLA

原文版本：arXiv:2505.06111v3，2025 年 11 月 3 日。本文根据同目录的 `UniVLA.pdf` 翻译。术语说明：latent action 统一译为“潜动作”，embodiment 译为“具身形态”（指不同机器人或人体的身体结构与控制方式），generalist policy 译为“通用策略”。参考文献保留原文，以便检索。原文中个别数字或描述存在前后不一致之处，译文保留原值并在必要处注明。

> **图 1（原文第 1 页）：UniVLA 总览。** 机器人操作、人类视频、室内外导航的视频帧对，都被映射到统一的、以任务为中心的潜动作空间。该方法允许使用不同视角、不同具身形态且没有动作标签的数据。经过大规模视频预训练后，只需以较低成本学习动作解码器，即可将通用策略部署到不同机器人。图中与 OpenVLA 对比的结果为：LIBERO 76.5→95.2；SimplerEnv 1.0→47.9；真实机器人 38.3→81.7；CALVIN 连续完成五项任务的成功率 43.5→56.5；Room2Room 17.5→47.1。

## 摘要

通用机器人应当能够在各种环境中有效工作。然而，现有方法大多严重依赖扩大带动作标注的数据规模来提升能力。因此，它们往往局限于某一种物理配置，难以从不同具身形态和环境中学到可迁移的知识。

为解决这些限制，我们提出 UniVLA，一个用于学习跨具身视觉—语言—动作（VLA）策略的新框架。核心创新是利用潜动作模型，从视频中提取以任务为中心的动作表示，使我们能够利用覆盖广泛具身形态和视角的海量数据。为了减轻与任务无关的动态变化带来的影响，我们引入语言指令，并在 DINO 特征空间中建立潜动作模型。

通用策略从互联网规模的视频中学习，再通过高效的潜动作解码部署到不同机器人上。我们在多个操作和导航基准以及真实机器人部署中获得了最先进的结果。UniVLA 使用不到 OpenVLA 的 1/20 预训练计算量以及 1/10 下游数据，就能取得更好的表现。随着训练流水线纳入更多异构数据，甚至包括人类视频，模型表现持续提升。这些结果表明，UniVLA 有望推动可扩展且高效的机器人策略学习。

## I. 引言

随着大规模机器人数据集的出现 [78,63,38,1]，基于视觉—语言—动作模型的机器人策略取得了令人鼓舞的进展 [10,28,39]。但它们通常依赖真实动作标签进行监督，限制了它们利用来自多样环境的互联网规模数据的能力。此外，不同具身形态（如 Franka、WidowX，甚至人手）与不同任务（如操作和导航）之间，动作空间和观测空间存在显著差异，这给有效的知识迁移带来了很大挑战。

由此产生一个关键问题：我们能否学到一种统一动作表示，使通用策略能够有效规划，释放互联网规模视频的潜力，并促进知识在不同具身形态和环境之间迁移？

为应对这些挑战，我们提出 UniVLA，支持在不同具身形态和环境中进行可扩展、高效规划的通用策略学习框架。类似于大型语言模型学习跨语言共享知识 [22,18]，我们希望构建统一动作空间，促进各种机器人演示和第一人称人类视频之间的知识迁移。我们的方案包含三个关键阶段：

1. **以任务为中心的潜动作学习**：以无监督方式，从大规模跨具身视频中提取与任务有关的动作表示。具体通过 VQ-VAE [76]，将成对视频帧的逆动力学所得到的潜动作离散化。
2. **下一潜动作预测**：用离散潜动作 token 训练自回归视觉语言模型，赋予其不依赖具体具身形态的规划能力。
3. **潜动作解码**：把潜在计划解码为物理行为，高效地将预训练通用策略适配到未见任务。

近期研究 [87,16] 已探索从网络规模视频中学习潜动作的可行性，但存在重要局限：朴素的重建目标往往会捕捉与任务无关的动态，例如其他参与者的运动或不可预测的相机移动。这些带噪表示会向策略预训练引入无关干扰。对此，我们利用预训练 DINOv2 特征 [62]，从像素中提取 patch 级表示，提供空间先验和以物体为中心的先验，更好地捕捉与任务有关的信息。进一步利用现成的语言指令作为条件，将运动解耦为两类互补动作表示，其中一类明确表示以任务为中心的动作。

UniVLA 在多个操作基准和导航任务上取得了最先进的表现，显著超过 OpenVLA [39]，同时所需预训练成本仅约为其 1/20（按 GPU 小时计）。这种效率来自以任务为中心的潜动作空间：它将任务相关动态与无关视觉变化分离。动作表示不仅降低了计算开销，也支持高效扩展。随着数据集增大，UniVLA 的表现持续提升，能够有效利用跨具身、跨视角的机器人数据集乃至无动作标注的人类视频，扩展预训练语料并提取可迁移知识。尤其值得注意的是，即使只在 Bridge-V2 [78] 上预训练，UniVLA 也能超过在更大的 Open X-Embodiment [63] 上训练的 OpenVLA 和 LAPA，体现了从有限数据中提炼可迁移知识的能力。

此外，我们采用仅有 10.8M 参数的轻量解码器，把潜动作转换为可执行轨迹，显著降低大规模微调的需求。这利用了潜动作空间紧凑且信息丰富的特点，使 UniVLA 能用少量下游数据高效适配多种任务和具身形态。覆盖操作、导航和真实部署的全面评估表明，该框架高效、可扩展且泛化良好，是迈向下一代通用机器人策略的一条可行路径。

主要贡献如下：

- 提出 UniVLA：在统一且与具身形态无关的动作空间中规划，通过网络规模视频学习，实现可扩展、高效的决策。
- 提出从跨具身视频提取任务相关潜动作的新方法，将以任务为中心的动态与无关视觉变化分离。定性和定量实验均展示了相对于已有工作的优势。
- 在多个基准和真实机器人测试中取得最先进表现。原文此处报告：LIBERO 成功率比 OpenVLA 提高 18.5%，导航提高 29.6%，真实部署提高 36.7%。

译注：本文的成功率差值通常实际表示“百分点”。LIBERO 表中 95.2−76.5=18.7 个百分点，与引言贡献列表的 18.5 不一致；真实部署相对 OpenVLA 为 43.4 个百分点，相对 LAPA 为 36.7 个百分点。

## II. 相关工作

### A. 视觉—语言—动作模型

在预训练视觉基础模型、大型语言模型和视觉语言模型成功的基础上，VLA 被用于处理视觉观测、语言指令等多模态输入，并产生完成具身任务所需的机器人动作。RT-1 [11] 和 Octo [28] 使用基于 Transformer 的策略，将覆盖不同任务、物体、环境和具身形态的机器人轨迹整合起来。

另一些工作 [10,39,46] 利用预训练 VLM，从大规模视觉语言数据中获得世界知识，再生成机器人动作。例如，RT-2 [10] 和 OpenVLA [39] 将动作视为语言模型词表中的 token，而 RoboFlamingo [46] 增加额外的策略头来预测动作。在这些通用策略的基础上，RoboDual [13] 提出协同双系统，结合通用策略和专用策略的优势。其他工作引入目标图像 [9] 或视频 [24,82,14] 的预测任务，根据语言指令生成有效且可执行的计划，再由这些视觉线索指导策略生成动作。

但这些方法严重依赖带真实动作标签的交互数据，显著限制了 VLA 的扩展能力。相比之下，我们从视觉变化中学习统一潜动作表示，不依赖动作标签，释放互联网规模无动作标注视频的潜力。

### B. 跨具身学习

由于不同机器人系统在相机视角、本体感知输入、关节配置、动作空间和控制频率上存在差异，训练通用机器人策略非常困难。早期方法 [86] 人工对齐导航和操作的动作空间，但操作部分局限于腕部相机。近期基于 Transformer 的方法 [28,23] 通过支持可变观测与动作来应对这些差异。CrossFormer [23] 在四种不同动作空间上联合训练，既不约束观测空间，也不要求显式对齐动作空间。

描述图像或点云中查询点未来轨迹的流（flow）表示，已广泛用于跨具身学习 [81,88,26,83]。ATM [81] 从人类演示学习流生成；Im2Flow2Act [83] 无需域内数据，就能从人类视频预测物体流。与此同时，以物体为中心的表示 [32,8] 提供了另一条路径，SPOT [32] 预测 SE(3) 中的物体轨迹，使具身动作与感知输入解耦。

现有方法需要大量多样数据来覆盖可能的状态转移模式，还需要显式标注，导致数据利用效率低。我们的方法以无监督方式，用离散码本编码潜动作，有效过滤视觉噪声，并通过向量量化实现高效信息压缩，从而提高训练效率、减少对数据多样性的依赖。

### C. 潜动作学习

一些已有工作在原始动作轨迹上学习变分自编码器 [64,76]，建立新的动作空间，强调有助于行为生成和任务适配的紧凑潜表示，如 VQ-BeT [44]、Quest [59]。这些方法也被用于强化学习，以加速收敛 [3]。近期工作 [79,74] 探索将向量量化作为动作空间适配器，使动作更好地融入大型语言模型。但这些方法的关键限制仍是依赖真实动作标签，限制了可扩展性。

为了利用更广泛的视频数据，Genie [12] 通过以未来帧预测为条件的因果潜动作模型提取潜动作。LAPO [70] 和 DynaMo [20] 也直接从视觉数据学习潜动作，在域内操作任务上绕开显式动作标签。LAPA [87] 和 IGOR [16] 提出无监督预训练，用离散潜动作训练 VLA，尝试迁移人类视频中的知识。

但这些方法从原始像素编码所有视觉变化，会捕捉相机抖动、其他参与者运动、新物体出现等任务无关动态，最终降低策略表现。我们提出新的训练框架，将以任务为中心的动态与无关视觉变化分离，建立更有效的潜动作空间，以支持稳健策略规划。

## III. 方法

UniVLA 包括三个步骤：

1. 利用语言描述的目标，以无监督方式从大规模视频中提取逆动力学，得到可在不同具身形态和领域间泛化的离散任务中心潜动作。
2. 以此训练基于自回归 Transformer 的 VLA，根据视觉观测和任务指令，在统一潜空间预测潜动作 token。
3. 引入专门的策略头，将潜动作解码为可执行控制信号，从而高效适配不同机器人控制系统。

### A. 以任务为中心的潜动作学习

第一步为框架打基础，生成伪动作标签，即潜动作 token，供后续通用策略训练使用。

**潜动作量化。** 图 2 展示了潜动作模型的两阶段训练流程和整体结构。输入是一对视频帧 $\{o_t,o_{t+k}\}$，帧间隔为 $k$。为了让不同数据集的实际时间间隔统一为约 1 秒，我们根据各数据集的录制频率调整 $k$。

潜动作模型由逆动力学模型（IDM）编码器 $I(a_t\mid o_t,o_{t+k})$ 和前向动力学模型（FDM）解码器 $F(o_{t+k}\mid o_t,a_t)$ 构成。编码器根据成对观测推断潜动作；解码器根据指定潜动作预测未来观测。遵循 Villegas 等人 [77]，编码器采用带因果时间掩码的时空 Transformer [84]。一组可学习动作 token $a_q\in\mathbb{R}^{N\times d}$（维度 $d$ 预先设定）按序拼接到视频特征后，用于提取动态。

为了进一步压缩信息，并与自回归 Transformer 策略的学习目标 [66] 对齐，我们量化动作 token。量化后的动作 token $a_z\in\mathbb{R}^{N\times d}$ 采用 VQ-VAE [76] 目标优化，码本词表大小为 $|C|$。解码器采用空间 Transformer，利用量化动作 token 学习预测未来帧。我们不向解码器输入历史帧，以防模型过度依赖上下文或仅仅记住数据集。

近期工作 [12,27,87] 在原始像素上预测，但我们发现像素空间预测会迫使模型关注纹理、光照等带噪且与任务无关的细节 [30]。在网络规模或众包视频 [29] 中，不受控的拍摄条件会进一步放大这一问题。受联合嵌入预测架构 JEPA [5,6,96] 启发，我们使用 DINOv2 [62] 的空间 patch 特征作为语义丰富的表示。它们以物体为中心、具有空间感知能力，既适合作为潜动作模型的输入，也适合作为预测目标。

自监督目标最小化嵌入重建误差：

$$\|\hat O_{t+k}-O_{t+k}\|_2.$$

其中 $\{O_t,O_{t+k}\}$ 是视频帧 $\{o_t,o_{t+k}\}$ 的 DINOv2 特征。紧凑潜动作必须编码观测之间的变换，才能降低预测误差。

**潜动作解耦。** 网络规模视频中的机器人动作常与无关环境变化纠缠。为减轻任务无关动态的影响，我们在潜动作模型第一阶段训练中加入现成的语言指令。语言经预训练 T5 文本编码器 [67] 编码，作为编码器和解码器的上下文条件：

$$\begin{aligned}
\text{编码：}\quad &\hat a^{TI}=I([O_t;O_{t+k};a^{TI};\ell]),\quad \tilde a^{TI}=\mathrm{VQ}(\hat a^{TI}),\\
\text{解码：}\quad &\hat O_{t+k}=F([O_t;\tilde a^{TI};\ell]).
\end{aligned}$$

$[;]$ 表示沿序列维度拼接，VQ 为向量量化动作表示的码本，$\ell$ 是 T5 产生的指令嵌入。

向解码器提供任务指令，会给予其关于动作的高层语义指导。由于码本容量有限 [2]，量化潜动作只需编码环境变化与视觉细节 [89]，而不必重复编码已由语言给出的高层任务信息。因此，这一阶段学习的是任务无关潜动作，例如新物体出现、外部参与者运动、相机运动产生的视觉伪影。这些动态虽有助于模型理解视觉环境，却与任务的具体目标正交。

> **图 2（原文第 4 页）：任务中心潜动作学习。** 左侧是第一阶段：成对帧经过 DINOv2，语言经 T5 编码，二者共同输入编码器和解码器；语言提供任务语义，码本优先编码剩余的任务无关变化。右侧是第二阶段：复制第一阶段模型权重，冻结任务无关码本，去掉语言输入并引入新的任务中心动作 token 和码本，用它们补足之前由语言承担的任务相关信息。两阶段均以未来帧 DINOv2 特征作为监督。

随后，我们复用第一阶段训练得到的任务无关码本和模型参数，进入第二阶段，学习新的任务中心潜动作 $\hat a^{TC}$，供策略训练使用。该阶段为：

$$\begin{aligned}
\text{编码：}\quad &\{\hat a^{TI},\hat a^{TC}\}=I([O_t;O_{t+k};a^{TI};a^{TC}]),\\
&\tilde a^{TI}=\mathrm{VQ}(\hat a^{TI}),\quad \tilde a^{TC}=\mathrm{VQ}_{TC}(\hat a^{TC}),\\
\text{解码：}\quad &\hat O_{t+k}=F([O_t;\tilde a^{TI};\tilde a^{TC}]).
\end{aligned}$$

$\mathrm{VQ}_{TC}$ 是新初始化的任务中心动态码本。在已学到任务无关表示的基础上，我们冻结其对应码本，使模型专注于细化新的潜动作。这有助于准确建模物体操作、朝向目标的运动轨迹等任务相关动态。

显式解耦潜动作表示，可以提高通用策略对不同环境和任务的泛化能力。相对于 LAPA [87] 等朴素潜动作学习方法，只在任务中心表示上训练能够更快收敛，同时保持稳健表现，说明这种潜动作对后续策略学习更有信息价值。

### B. 通用策略预训练

训练完潜动作模型后，我们根据未来帧 $o_{t+k}$，给视频帧 $o_t$ 标注潜动作 $a_z$，再用这些标签训练通用策略。为了与 Kim 等人 [39] 对齐，我们以 Prismatic-7B [37] VLM 为基础。架构包括融合 SigLIP [90] 和 DINOv2 [62] 的视觉编码器、将视觉嵌入对齐到语言模态的投影层，以及 LLaMA-2 [75] 大型语言模型。

RT-2 [10] 和 OpenVLA [39] 将 LLaMA tokenizer 中不常用的词映射到 $[-1,1]$ 内均匀分布的动作区间，直接在低层动作空间规划。我们则扩展词表，加入 $|C|$ 个特殊 token：`ACT_1, ACT_2, ACT_3, ..., ACT_C`。潜动作根据码本索引映射到这些 token。这样既保留 VLM 的原始架构和训练目标，又能充分利用其预训练知识来迁移到机器人控制。

策略模型 $\pi_\phi$ 接收观测 $o_t$、任务指令 $l$ 与潜动作前缀 $a_{z,<i}$，最小化下一潜动作的负对数概率总和：

$$\mathcal L=\mathbb E_{o_t,l,a_{z,<i}}\left[-\sum_{i=1}^{N}\log\pi_\phi(\hat a_{z,i}=a_{z,i}\mid o_t,l,a_{z,<i})\right].$$

$N$ 是动作 token 序列的总长度。所有实验均取 $N=4$。经验结果表明，压缩动作空间（例如从 OpenVLA 的 $256^7$ 减少为 $|C|=16$ 时的 $16^4$）会显著加快收敛。我们只用 960 A100 GPU 小时就能取得有竞争力的结果，而 OpenVLA 预训练需要 21,500 A100 GPU 小时。

通过在统一潜动作空间训练，策略能够利用跨领域数据中的可迁移知识。Yang 等人 [86] 需要通过视觉上相似的第一人称运动人工对齐动作空间，例如将操作中的腕部相机运动与第一人称导航对齐；我们的方法无需这种人工对齐，因而能利用更多数据并提高整体表现。

> **图 3（原文第 5 页）：通用策略架构。** 第三人称 RGB 由 DINOv2 与 SigLIP 编码，视觉特征投影后与任务指令 token 一起输入 Prismatic-7B 的自回归 Transformer，预测潜动作 token。针对不同机器人，专用动作解码器将潜动作嵌入作为键和值，以视觉信息构造查询，再输出对应机器人动作空间中的动作序列 $a\in\mathbb R^{k\times d}$。

### C. 面向部署的后训练

**潜动作解码。** 下游适配时，预训练通用策略继续预测下一潜动作，保留不依赖具体具身形态的性质。为了把潜动作转为可执行行为，我们加入动作解码器（图 3）。先通过多头注意力池化 [43] 将视觉嵌入序列汇聚为单个 token，再用它作为查询，从潜动作嵌入提取信息：

$$\begin{aligned}
E'_v&=\mathcal A(Q=q_v,K=V=E_v),\\
E'_a&=\mathcal A(Q=q_a+E'_v,K=V=E_a).
\end{aligned}$$

$\mathcal A$ 为多头注意力，$\{E_v,E_a\}$ 为 VLM 最后一层的视觉与潜动作嵌入，$\{q_v,q_a\}$ 是随机初始化的视觉和动作查询。最终动作嵌入 $E'_a$ 经线性投影，映射到目标机器人的动作空间。

由于潜动作表示约 1 秒内的动作，它们可以自然地解码为动作块 [93]。块大小可针对具体具身形态调整，以实现更平滑、更精确的控制。

实践中我们使用 LoRA [33] 进行参数高效微调。加上仅含 12.6M 参数的动作头后，总可训练参数约为 123M。模型端到端训练，同时优化下一潜动作预测损失与真实低层动作和预测动作之间的 L1 损失。

译注：引言称解码器有 10.8M 参数，本节和真实实验架构表写 12.6M。原文未进一步解释两者关系。

**从历史输出学习。** 历史观测对机器人序列决策非常重要 [60,42,45]。但直接向大型 VLA 输入多个历史观测会引入明显推理延迟，还会产生冗余视觉 token [94,45]。受 LLM 思维链（CoT）[80] 启发，我们利用历史潜动作输出辅助机器人决策。类似于 LLM 逐步解决问题，机器人每个时间步都把过去动作纳入输入提示，建立反馈环，使策略能够从自身决策中学习并适应动态环境。

具体地，我们用潜动作模型为历史帧提取的动作打标签，映射到 LLaMA token 词表，并附加到任务指令中。后训练时加入历史动作输入，赋予模型上下文学习能力。推理时，除初始步外，每步加入一步历史潜动作，即 $N=4$ 个 token。实验表明，这个简单设计能提升表现，尤其有利于长时程任务。

## IV. 评估

我们在操作基准 LIBERO [48]、CALVIN [56]、SimplerEnv [47]，导航基准 R2R [4]，以及真实环境中评估 UniVLA。还分析潜动作是否确实以任务为中心，并消融关键设计。主要问题为：

1. **表现与适应能力**：能否把预训练知识迁移到新的具身形态与任务，并高效适配？
2. **泛化能力**：面对未见场景表现如何？
3. **可扩展性**：能否有效利用包括人类视频在内的不同数据源，并随着数据规模扩大持续获益？

### A. 主要结果

#### 1. LIBERO 操作基准

**实验设置。** 完整潜动作模型使用操作数据、导航数据和人类视频预训练，分别来自 Open X-Embodiment（OpenX）[63] 的子集、GNM [72] 和 Ego4D [29]。细节见附录 A.1。

LIBERO [48] 包含四个任务组，用于研究机器人操作的终身学习。我们的实验只关注目标任务组内的监督微调，比较基于成功演示、通过行为克隆训练的策略。每个任务组有 10 个任务，每任务 50 条人类遥操作演示：

- **LIBERO-Spatial**：根据空间关系准确放置碗，考查几何推理。
- **LIBERO-Object**：场景布局不变，改变物体种类，考查跨物体泛化。
- **LIBERO-Goal**：保持物体和布局一致，改变任务目标，考查目标导向行为与适应能力。
- **LIBERO-Long**：多个子目标组成的长时程操作，含异构物体、布局与任务序列，考查复杂多步规划。

> **图 4（原文第 6 页）：LIBERO 任务设置。** Spatial 示例：拿起最上方抽屉中的碗并放到盘子上；Object 示例：拿起沙拉酱并放入篮子；Goal 示例：打开柜子中间的抽屉；Long 示例：把黄白色杯子放进微波炉并关门。图中的各类变化分别对应空间布局、物体类型、目标和长时程组合。

我们遵循 OpenVLA [39] 的数据处理流程，剔除训练演示中的失败样本。LIBERO-Long 训练 40k 步，其余任务组训练 30k 步，全局 batch size 为 128。输入仅包括第三人称图像和语言指令。策略与潜动作模型的预训练数据均不包含 LIBERO，因此两者都必须泛化到该环境。

除完整数据预训练模型外，我们还报告仅用 Bridge-V2 或人类数据预训练的模型，分别记为 Bridge 和 Human。每任务组评估 500 次，即每任务 50 次，并报告三个随机种子下的平均成功率。

**基线。** LAPA [87] 从无标签人类视频学习潜动作；Octo [28] 用统一动作表示处理多样机器人数据；MDT [68] 根据多模态目标用扩散模型生成动作序列；OpenVLA [39] 利用包括 OpenX 在内的大规模预训练；MaIL [35] 用选择性状态空间模型改进模仿学习的效率与扩展性。表中还包括 Diffusion Policy [17]。

**表 I：LIBERO 成功率（%）。** † 表示还使用腕部相机输入；* 表示我们用 Prismatic-7B 重现 LAPA。

| 方法 | Spatial | Object | Goal | Long | 平均 |
|---|---:|---:|---:|---:|---:|
| LAPA* | 73.8 | 74.6 | 58.8 | 55.4 | 65.7 |
| Diffusion Policy | 78.3 | 92.5 | 68.3 | 50.5 | 72.4 |
| Octo | 78.9 | 85.7 | 84.6 | 51.1 | 75.1 |
| MDT† | 78.5 | 87.5 | 73.5 | 64.8 | 76.1 |
| OpenVLA | 84.7 | 88.4 | 79.2 | 53.7 | 76.5 |
| MaIL† | 74.3 | 90.1 | 81.8 | 78.6 | 83.5 |
| UniVLA（Human） | 91.2 | 94.2 | 90.2 | 79.4 | 88.7 |
| UniVLA（Bridge） | 95.2 | 95.4 | 91.9 | 87.5 | 92.5 |
| UniVLA（Full） | 96.5 | 96.8 | 95.6 | 92.0 | 95.2 |

**结果。** UniVLA 在四个任务组中均显著超过 OpenVLA、LAPA 和 Octo 等已有通用策略。完整数据预训练平均成功率为 95.2%，分别比 OpenVLA 和 LAPA 高 18.7 与 29.5 个百分点。只用 Bridge-V2 预训练也能达到 92.5%，超过还使用腕部相机的 MaIL（83.5%）和 MDT（76.1%）。只用人类视频预训练时，相对使用域内 OpenX 数据训练的 OpenVLA 仍提高 12.2 个百分点。结果表明其知识迁移能力突出，建立了新的 LIBERO 最先进结果。CALVIN 和 SimplerEnv 结果见附录 B。

#### 2. Room2Room 导航基准

**实验设置。** 我们在 VLN-CE [41] 上评估导航。该基准提供语言引导任务，机器人在重建的照片级真实室内场景中执行低层动作。我们关注其广泛使用的 Room2Room（R2R）[4] 任务。所有方法均使用 R2R 训练集的 10,819 个样本训练，并在 val-unseen 的 1,839 个样本上评估。

指标为 oracle success rate：若一次导航过程中智能体曾到达距目标 3 米以内，则判定成功。

**基线。** 为公平比较，我们选择仅输入 RGB、不使用深度或里程计、直接预测低层动作的方法。Seq2Seq [40] 使用循环序列到序列策略；CMA [40] 用跨模态注意力融合指令与 RGB；LLaVA-Nav 是用 NaVid [91] 所提数据联合微调的 LLaVA [49]，以观测到历史的机制编码历史；OpenVLA 增加特殊 token 来表示导航动作，再在 R2R 训练集微调；NaVid [91] 是视频 VLM，编码所有历史 RGB 观测，用预训练视觉编码器和 LLM 预测动作。

> **图 6（原文第 7 页）：R2R oracle 成功率。** Seq2Seq 8.1%，CMA 10.8%，LLaVA-Nav 14.0%，OpenVLA 17.5%，NaVid 49.1%，UniVLA 47.1%。UniVLA 当前视觉输入只有单帧 RGB，再结合紧凑历史潜动作，就能接近使用全部历史观测的 NaVid。

**结果。** UniVLA 显著超过 Seq2Seq 和 CMA，将成功率从 8.10% 提高到 47.1%。由于 LLaVA-Nav 历史提示计算量大，我们沿用 NaVid 的做法，在 R2R val-unseen 的 100 个 episode 子集上报告其结果。UniVLA 比 LLaVA-Nav 和 OpenVLA 分别高 33.1 与 29.6 个百分点。它接近编码所有历史观测的 NaVid，而自身只依赖当前观测和历史潜动作。

#### 3. 真实机器人部署

**实验设置。** 所有真实实验均使用 AgileX Robotics 的 Piper 机械臂，动作空间为 7 自由度，搭配第三人称 Orbbec DABAI RGB-D 相机；模型只使用 RGB 图像。我们设计四项任务，覆盖不同策略能力：

1. **空间感知**：拿起螺丝刀放进柜子并关门，即“收纳螺丝刀”。
2. **工具使用与非抓取操作**：拿起扫帚，把砧板上的东西扫进簸箕，即“清理砧板”。
3. **可变形物体操作**：把毛巾对折两次，即“毛巾折叠两次”。
4. **语义理解**：先把中号塔放在大号塔上，再把小号塔放在中号塔上，即“堆叠汉诺塔”。

按任务复杂度，每项收集 20–80 条轨迹用于微调。泛化实验涵盖光照变化、视觉干扰和新物体。成功率不足以全面区分策略能力，因此每项任务还使用最高 3 分的阶段评分，对各执行阶段完成情况计分。细节见附录 C。

**基线。** Diffusion Policy 单任务训练；OpenVLA、LAPA 等通用模型则在所有任务上联合训练，并接收指令。为公平比较，LAPA 用 Prismatic-7B VLM 与动作解码头重现，架构与我们对齐，以突出潜动作空间的贡献。

> **图 5（原文第 7 页）：真实机器人实验。** 展示收纳螺丝刀、清理砧板、毛巾折叠两次与堆叠汉诺塔的场景、成功率和综合分数。完整 UniVLA 四项成功率依次为 93.3%、100.0%、46.7%、86.7%，平均 81.7%；平均分 2.63。相对第二好的 LAPA，平均成功率提高 36.7 个百分点，平均分提高 0.68。完整数值见表 A-V。

**结果。** 单任务 Diffusion Policy 在毛巾折叠这种选对边后基本执行固定轨迹的任务上表现较好，成功率 53.3%，高于 UniVLA 的 46.7%。但 UniVLA 阶段得分更高（2.47 对 2.33），说明即使最终执行失败，它也更稳定地完成选边、部分折叠等中间阶段。在动态真实环境中，这种部分进展很有价值。

这一权衡来自 UniVLA 的通用设计：Diffusion Policy 的单任务训练提高特定流程的轨迹精度，却难以处理需要语义推理的任务。例如在堆叠汉诺塔上，其成功率仅 6.7%，而 UniVLA 达到 86.7%。在螺丝刀具有不同姿态和位置、需要精确物体操作与空间推理的收纳任务中，UniVLA 也达到 93.3%。

通过紧凑潜动作规划与高效动作块预测（实际块大小为 12），UniVLA 在 NVIDIA RTX 4090 上达到 10 Hz 实时闭环推理。OpenVLA 即使在大量机器人数据上训练，仍受推理延迟影响而动作卡顿：预测单步约需 0.18 秒，大小为 4 的动作块约需 0.68 秒，真实环境平均成功率仅 38.3%。UniVLA 比第二好的 LAPA 高 36.7 个百分点与 0.68 平均分，展示了任务中心潜动作空间在真实环境中的优势。

**泛化分析。** 我们考查三个方面：

> **图 7（原文第 8 页）：泛化评估设置。** 光照变化：调暗环境光，并从指定方向施加强光；视觉干扰：在桌面增加碗、笔记本和胶带；新物体：把要操作的螺丝刀替换为未见过的记号笔。图中同时展示原始场景以供对比。

**表 II：泛化成功率（%）与阶段分数。**

| 方法 | 光照变化成功率 | 分数 | 视觉干扰成功率 | 分数 | 新物体成功率 | 分数 | 平均成功率 | 平均分数 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Diffusion Policy | 20.0 | 0.60 | 26.7 | 0.80 | 26.7 | 0.67 | 24.4 | 0.69 |
| OpenVLA | 13.3 | 0.93 | 20.0 | 0.73 | 26.7 | 1.27 | 20.0 | 0.98 |
| LAPA | 26.7 | 1.60 | 6.7 | 0.60 | 53.3 | 1.87 | 28.9 | 1.36 |
| UniVLA | 66.7 | 2.33 | 53.3 | 2.40 | 86.7 | 2.73 | 68.9 | 2.49 |

UniVLA 在成功率和阶段得分上均明显超过基线。光照变化下达到 66.7%，体现对环境变化的鲁棒性。视觉干扰下，更依赖语义信息的 LAPA 与 UniVLA 均出现相对明显的性能下降。新物体实验把螺丝刀替换为记号笔，并相应调整通用策略的语言指令；该变化对 UniVLA 影响很小，成功率仅下降 6.6 个百分点。整体平均成功率为 68.9%、平均分为 2.49，显著超过 LAPA（28.9%、1.36）和 OpenVLA（20.0%、0.98）。补充材料提供了视频演示。

### B. 潜动作讨论

**定性分析。** 我们将不同数据源中拥有相同潜动作标签的帧对可视化，检查跨域可迁移性。每组动作在不同具身形态中对应语义一致的行为。虽然潜动作模型没有见过 LIBERO 数据，仍能够准确标注这个新领域中的动作。它还学会把操作任务中的腕部视角与导航中的第一人称运动对齐，体现连接不同模态与具身形态的能力。

> **图 8（原文第 9 页）：潜动作分析。** A 组为“拿起物体”，B 组为“放下物体”，均覆盖 Bridge、RT-1、LIBERO 和 Ego4D；C 组为“向前移动”，覆盖 GNM 室外、GNM 室内、DobbE 腕部视角与 Ego4D。同一潜动作在不同来源中具有一致行为语义。

**定量分析。** 我们使用不同潜动作标签训练策略，再比较 LIBERO 部署表现。为放大任务解耦的优势，预训练仅使用含大量不可预测运动的人类视频。相比捕捉全部视觉变化的 Genie [12] 方式，我们的方法平均成功率高 6.4 个百分点，其中 LIBERO-Goal、Long 分别提高 13.0、9.8 个百分点。

**表 III：不同潜动作标签下的 LIBERO 成功率（%）。** 所有策略均在 Ego4D 上预训练。

| 潜动作 | Spatial | Object | Goal | Long | 平均 |
|---|---:|---:|---:|---:|---:|
| Genie | 89.8 | 92.8 | 77.2 | 69.6 | 82.3 |
| 任务无关潜动作 | 68.0 | 90.4 | 67.2 | 0.2 | 56.5 |
| 任务中心潜动作 | 91.2 | 94.2 | 90.2 | 79.4 | 88.7 |

任务无关潜动作与真实动作对齐较差，策略难以根据观测和语言推断它们。这既体现为训练时较低的动作 token 预测准确率，也体现为推理表现差。在困难的 LIBERO-Long 上，用任务无关潜动作训练的策略成功率接近零。

### C. 更多消融实验

**数据可扩展性。** 图 9 展示随着数据增长及新领域加入，UniVLA 如何变化。仅用 Bridge-V2 就已在 LIBERO 取得最先进结果；继续加入 OpenX 跨具身数据和 Ego4D 人类视频，平均成功率进一步提升（原文文字写 2.0 个百分点）。虽然 LIBERO 表现趋于饱和，真实任务中仍持续改善。相对只用 Bridge，扩展到 OpenX 后真实任务平均分增加 0.3；再加入无动作标签、与机器人身体差异很大的人类视频后，增加 0.28。R2R 中也呈现类似趋势。

> **图 9（原文第 9 页）：数据可扩展性。** 三种数据规模依次为 Bridge-V2、OpenX（操作+导航）、操作+导航+人类视频。LIBERO 得分依次为 92.5、94.2、95.2；真实机器人分数依次为 2.05、2.35、2.64（表 A-V 最后一项为 2.63）；R2R 图上以约 30、38、44、49 的径向刻度表示持续改善趋势。不同领域数据加入后，下游表现继续提高。

译注：图中 LIBERO 从 92.5 到 95.2 实际相差 2.7 个百分点，正文此处写 2.0，均按原文保留。

**数据效率。** 接下来考查用少量数据适配未见环境的能力。在 LIBERO-Goal 和 Long 上仅使用部分训练数据。相对 OpenVLA 等通用策略和 ATM [81] 等显式点预测方法，UniVLA 数据效率更高。仅用 10% 演示，Goal 成功率就为 86.3%，超过完整数据训练的 OpenVLA（79.2%）。在 Goal 和 Long 上，仅用 10% 和 50% episode 就分别取得新的最先进结果。统一潜动作空间使模型充分利用预训练知识，高效适配新环境。

> **图 10（原文第 10 页）：数据效率。** 横向比较训练数据占比 10%、20%、50%、100%。UniVLA 在 LIBERO-Goal 上依次为 86.3%、90.4%、93.1%、95.6%；LIBERO-Long 上依次为 62.4%、71.4%、87.0%、92.0%。图中同时给出先前方法的参考性能，突出少量下游演示即可取得较好结果。

**潜动作解码器。** 我们将提出的动作解码方案与 OpenVLA、LAPA 式自回归逐个生成离散动作的方式比较。所有任务组表现均更高，在 LIBERO-Long 上尤其提高 42.1 个百分点。使用视觉嵌入作为查询，可以减少多模态分布的歧义，进一步提高平均成功率（原文写 2.2 个百分点）。

**表 IV：解码器设计消融，成功率（%）。** “不使用视觉”指不以视觉嵌入作为潜动作解码查询。

| 动作解码器 | Spatial | Object | Goal | Long | 平均 |
|---|---:|---:|---:|---:|---:|
| 自回归 | 85.2 | 81.2 | 79.0 | 49.0 | 73.6 |
| 本文方法，不使用视觉 | 95.0 | 95.4 | 93.7 | 86.0 | 92.5 |
| 本文方法 | 96.5 | 96.8 | 95.6 | 92.0 | 95.2 |

译注：表中平均值之差为 95.2−92.5=2.7 个百分点，与正文写的 2.2 不一致。

由于潜动作概括约 1 秒的动态，解码为动作块很自然；动作块大小可根据目标机器人控制频率选择。实现上，只需扩展最后线性投影层的输出维度，相对自回归方式几乎不增加推理成本。

**历史潜动作。** 我们把历史潜动作附加到指令输入，改动很小，但对长时程任务尤其有效。仅加入四个 token（一组历史潜动作），R2R 与 LIBERO-Long 成功率分别提高 16.5、3.9 个百分点。继续延长历史范围的收益递减。相比需要多帧冗余视觉 token 的方法 [91,45]，该设计提供紧凑历史指导，同时让模型通过自身输出反复改进决策，在不引入不必要计算的情况下提升上下文感知。

**表 V：历史动作使用的消融，成功率（%）。**

| 提示输入 | LIBERO-Goal | LIBERO-Long | R2R |
|---|---:|---:|---:|
| 仅指令 | 95.0 | 88.1 | 30.6 |
| 加入历史动作 | 95.6 | 92.0 | 47.1 |

## V. 结论

我们提出 UniVLA，在统一且以任务为中心的潜动作空间中规划，高效适配新的机器人配置。全面评估表明，UniVLA 在多个操作与导航基准上取得了最先进表现。它能利用异构预训练数据持续提升下游能力，在数据有限时也具有很强适应性。我们希望这项工作为下一代通用策略铺路，使其无论面对何种具身形态差异、是否存在动作标签，都能利用网络规模视频训练。

## VI. 局限与未来工作

**潜动作设计。** 尽管 UniVLA 推动了通用机器人策略，仍有局限。固定潜动作粒度与预设码本大小，并不一定对所有任务或具身形态都最优。根据环境条件动态调整二者，可能进一步改善表现。另外，UniVLA 主要在单臂操作上评估；当前 token 的动作粒度相对固定。推广到双臂人形机器人或灵巧手，可能需要更复杂、更细粒度的动作空间建模，留待后续探索。

**语言标注要求。** 任务相关潜动作设计为编码完成任务所需的主体运动，同时排除非主体动态，例如“烧水”时水壶冒出的蒸汽。数据集中多数指令较细，描述短时程动作而非高层目标。表达更充分的语言可能减少潜动作学习中的歧义，但我们强调，该方法支持不同粒度指令下的可扩展学习。无需特殊处理指令，就能超过朴素潜动作学习方法。

**与世界模型集成。** 潜动作模型的解码器实质是世界模型：给定潜动作，预测未来观测。它可以实时以策略采样的潜动作为条件，生成多个对应视觉计划。这为通过强化学习进行偏好对齐 [92]、通过规划树 [25] 实现测试时扩展创造了条件，可用 VLM [54] 或启发式函数作为奖励模型。

**上下文学习。** 上下文学习对提升 VLA 性能上限至关重要。潜动作模型能够提取连接人类与机器人操作的可迁移运动表示，因此可以把人类演示视频编码为紧凑潜动作嵌入序列，作为上下文样例。从概念上看，潜动作模型发挥视频 tokenizer 的作用，可能无需额外微调即可实现零样本技能获取。我们将在未来探索这一方向。

## 致谢

感谢 Li Chen、Modi Shi 和 Chengen Xie 提供宝贵反馈与有益讨论。

## 附录

### A. 实现细节

#### A.1 预训练细节

机器人操作数据选自 Open X-Embodiment [63] 中使用单臂末端执行器控制的子集。导航数据使用 GNM [72] 的部分数据，包括第一人称鱼眼相机拍摄的室内和越野场景。虽然机器人数据提供动作和本体感知状态，预训练时我们全部排除，只使用 episode 图像帧与文本指令。

此外，我们加入 Ego4D [29] 的开放世界第一人称人类日常活动视频。除 SimplerEnv [47]（它旨在复现 Bridge-V2 环境设置）外，其他下游评估环境在预训练时均未被策略或潜动作模型见过，因此二者都需要较强泛化能力。详细数据构成与混合权重如下。

**表 A-I：UniVLA 训练数据混合比例。**

| 数据集 | 比例 |
|---|---:|
| Fractal [11] | 13.9% |
| Kuka [36] | 6.3% |
| Bridge [78] | 6.8% |
| Taco Play [57] | 3.5% |
| Jaco Play [21] | 0.6% |
| Berkeley Cable Routing [51] | 0.3% |
| Roboturk [55] | 2.8% |
| Viola [99] | 1.1% |
| Berkeley Autolab UR5 [15] | 1.4% |
| Toto [95] | 2.4% |
| Language Table [53] | 5.2% |
| Stanford Hydra Dataset [7] | 5.3% |
| Austin Buds Dataset [98] | 0.3% |
| NYU Franka Play Dataset [19] | 1.0% |
| Furniture Bench Dataset [31] | 2.9% |
| UCSD Kitchen Dataset [85] | <0.1% |
| Austin Sailor Dataset [61] | 2.6% |
| Austin Sirius Dataset [50] | 2.0% |
| DLR EDAN Shared Control [65] | 0.1% |
| IAMLab CMU Pickup Insert [69] | 1.1% |
| UTAustin Mutex [73] | 2.6% |
| Berkeley Fanuc Manipulation [97] | 0.9% |
| CMU Stretch [58] | 0.2% |
| BC-Z [34] | 8.8% |
| FMB Dataset [52] | 8.4% |
| DobbE [71] | 1.7% |
| RECON [38] | 8.9% |
| CoryHall [38] | 2.3% |
| SACSoN [38] | 3.5% |
| Ego4D [38]（原表引用编号） | 3.0% |

表题说明数据来自 OXE [63]、GNM [72] 和 Ego4D [29]。译注：原表 Ego4D 行标为 [38]，正文及表题使用 [29]。

训练时联合优化通用策略所有组件，包括视觉编码器、LLM 主干和 token 预测头。batch size 为 1,024，每设备为 32，恒定学习率 $2\times10^{-5}$。20,000 个优化步骤即可达到稳健下游表现，在 32 张 NVIDIA A100 上约需 30 小时。Human 和 Bridge 单独预训练使用 8 张 GPU，全局 batch size 为 258，约 200 A100 GPU 小时。

### B. 更多结果

#### B.1 CALVIN

**实验设置。** CALVIN [56] 包含 34 项任务，具有自由形式任务指令，覆盖简单抓取放置到铰接物体操作。基准有四个不同环境，每个环境均使用 Franka Panda 机械臂进行桌面操作。我们采用困难的 ABC→D 设置：在 A、B、C 环境演示上训练，在 D 环境零样本评估。测试包含 1,000 条不同指令链，每条包含连续五项任务，以严格评估泛化能力。

OpenVLA 使用官方检查点，通过 LoRA 微调 200k 步，动作块大小为 8，以尽可能提高表现。UniVLA 训练 100k 步，batch size 为 128；前 80k 步学习率 $1.5\times10^{-4}$，其余为 $1.5\times10^{-5}$。与 LIBERO 相同，仅输入第三人称 RGB 与语言指令。

**表 A-II：CALVIN ABC→D 语言条件视觉运动控制。** 各列为连续完成 1 至 5 项任务的成功率（%），平均长度为每条评估链完成的任务数。* 表示重现时加入动作块预测。

| 方法 | 1 项 | 2 项 | 3 项 | 4 项 | 5 项 | 平均长度 |
|---|---:|---:|---:|---:|---:|---:|
| RT-1 | 53.3 | 22.2 | 9.4 | 3.8 | 1.3 | 0.90 |
| RoboFlamingo | 82.4 | 61.9 | 46.6 | 33.1 | 23.5 | 2.48 |
| SuSIE | 87.0 | 69.0 | 49.0 | 38.0 | 26.0 | 2.69 |
| GR-1 | 85.4 | 71.2 | 59.6 | 49.7 | 40.1 | 3.06 |
| OpenVLA* | 91.3 | 77.8 | 62.0 | 52.1 | 43.5 | 3.27 |
| CLOVER | 96.0 | 83.5 | 70.8 | 57.5 | 45.4 | 3.53 |
| RoboDual | 94.4 | 82.7 | 72.1 | 62.4 | 54.4 | 3.66 |
| UniVLA | 95.5 | 85.8 | 75.4 | 66.9 | 56.5 | 3.80 |

**结果。** UniVLA 连续完成全部五项任务的成功率为 56.5%，比 CLOVER（45.4%）高 11.1 个百分点，比 OpenVLA 高 13 个百分点。平均连续任务数从 OpenVLA 的 3.27 提高到 3.80。任务链越长，优势越明显，说明它能应对复杂长时程操作。原文称 CLOVER 为“此前最好方法”，但同表 RoboDual 为 54.4%，译文按原叙述保留；表题还指出 UniVLA 是这些方法中唯一仅依赖第三人称 RGB 输入的方法。

#### B.2 SimplerEnv

**实验设置。** SimplerEnv [47] 通过模拟真实物理动态和视觉外观，尽可能反映真实策略表现。我们关注 WidowX + Bridge 配置的四项任务：把勺子放在桌布上；把胡萝卜放在盘子上；把绿色方块叠到黄色方块上；把茄子放进篮子。待抓取物体的姿态和位置按随机种子初始化。

由于 Bridge-V2 包含在预训练中，我们考查冻结其余组件、仅训练动作解码头的适配，记为 Decoder-only。同时，还在完整 Bridge-V2 上对模型使用 LoRA 微调并评估。沿用 Li 等人 [45] 的流程，每任务进行 24 次独立试验。

**表 A-III：SimplerEnv 抓取率和任务成功率（%）。**

| 方法 | 抓勺子 | 勺子任务成功 | 抓胡萝卜 | 胡萝卜任务成功 | 抓绿块 | 堆块任务成功 | 抓茄子 | 茄子任务成功 | 总体任务平均 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| RT-1-X | 16.7 | 0 | 20.8 | 4.2 | 8.3 | 0 | 0.0 | 0 | 1.1 |
| Octo-Base | 34.7 | 12.5 | 52.8 | 8.3 | 31.9 | 0 | 66.7 | 43.1 | 16.0 |
| Octo-Small | 77.8 | 47.2 | 27.8 | 9.7 | 40.3 | 4.2 | 87.5 | 56.9 | 30.0 |
| OpenVLA | 4.1 | 0 | 33.3 | 0 | 12.5 | 0 | 8.3 | 4.1 | 1.0 |
| RoboVLM | 54.2 | 29.2 | 25.0 | 25.0 | 45.8 | 12.5 | 58.3 | 58.3 | 31.3 |
| UniVLA（仅解码器） | 70.8 | 37.5 | 62.5 | 33.3 | 37.5 | 4.2 | 87.5 | 66.7 | 35.4 |
| UniVLA | 76.4 | 52.8 | 79.2 | 55.6 | 66.7 | 2.8 | 93.0 | 80.6 | 47.9 |

**结果。** 即使只适配解码器，UniVLA 在抓取与任务成功率上也显示优势。仅解码器成功率为 35.4%，说明保留预训练知识同时可以降低适配成本。原文随后称“完整微调相比仅解码器训练降低了抓取率，可能是对训练场景布局过拟合”，并报告总体任务成功率 42.7%，比 OpenVLA 和 Octo-Base 分别高 41.7、26.7 个百分点。

译注：上述原文分析与表 A-III 不一致：表中完整微调的四项抓取率均更高；总体平均为 47.9%，不是 42.7%。原文首页也使用 47.9%。这里保留两套原值，阅读时可优先参考完整数据表。

#### B.3 更多可视化

**更多潜动作分析。** 我们继续展示不同数据源中具有相同潜动作的帧对，以探索跨域可迁移性。

> **图 A-1（原文第 17 页）：补充潜动作示例。** D 组“把物体向上移动”、E 组“把物体向下移动”、F 组“向下移动”，分别展示 Bridge、RT-1 和 LIBERO 的同标签帧对。每组在不同具身形态中保持一致行为语义。

**任务中心潜动作分析。** 我们可视化任务中心潜动作与图像 patch 的注意力图。热力图集中于任务关键区域：机械臂末端执行器（例如夹爪）与交互物体（例如鸡蛋），忽略无关背景。这表明潜动作内在编码了以任务为中心的空间先验，关注下游学习必需的实体。

> **图 A-2（原文第 17 页）：注意力热力图。** 潜动作与图像 patch 的高注意力区域落在机器人末端和目标物体上，支持它学到任务相关动态而非无关背景的判断。

### C. 真实机器人

#### C.1 任务设置与评估

“收纳螺丝刀”训练中，随机将螺丝刀放在三种位置，测试用四种位置，以评估位置泛化。清理砧板任务中，物品随机摆放，有时一次扫动即可进入簸箕，有时数据采集需要两次扫动。原文在这一句误写为“收纳螺丝刀”，此处按所述行为译为清理砧板。

“毛巾折叠两次”使用 20 cm × 20 cm 毛巾，平铺在桌面。训练和测试都随机旋转毛巾角度，以评估泛化。“堆叠汉诺塔”随机打乱三个杯子，训练和测试均覆盖六种排列。

评估结合成功率与任务特定评分。相同成功率可能对应不同阶段得分，反映完成质量差异。Diffusion Policy 等单任务方法擅长平滑、连续、结构性强的序列，如毛巾折叠。虽然其该项成功率较高，但对不同旋转角度的泛化有限，分数低于 UniVLA。UniVLA 在不同位置配置下更稳健，即使只完成部分任务，也能获得较高分数。

**表 A-IV：任务评分。** 每完成一个子目标得 1 分，每任务满分为 3。

| 任务 | 子目标 1 | 子目标 2 | 子目标 3 |
|---|---|---|---|
| 收纳螺丝刀 | 拿起螺丝刀 | 放进柜子 | 关上柜门 |
| 清理砧板 | 拿起扫帚 | 把部分物品扫进簸箕 | 把所有物品扫进簸箕 |
| 毛巾折叠两次 | 抓住正确毛巾边 | 完成第一次折叠 | 完成第二次折叠 |
| 堆叠汉诺塔 | 选对杯子 | 中号叠到大号上 | 小号叠到中号上 |

**表 A-V：完整真实实验结果。** 成功率单位为 %，分数最高为 3。

| 方法 | 收纳螺丝刀成功率 | 分数 | 清理砧板成功率 | 分数 | 折毛巾成功率 | 分数 | 汉诺塔成功率 | 分数 | 平均成功率 | 平均分 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Diffusion Policy | 40.0 | 1.20 | 33.3 | 0.67 | 53.3 | 2.33 | 6.7 | 1.60 | 33.3 | 1.45 |
| OpenVLA | 40.0 | 1.47 | 53.3 | 1.27 | 33.3 | 1.87 | 26.7 | 1.93 | 38.3 | 1.63 |
| LAPA（OXE） | 60.0 | 2.00 | 40.0 | 1.47 | 33.3 | 2.20 | 46.7 | 2.13 | 45.0 | 1.95 |
| UniVLA（Bridge） | 66.7 | 2.13 | 73.3 | 1.87 | 33.3 | 2.07 | 46.7 | 2.13 | 55.0 | 2.05 |
| UniVLA（OXE） | 80.0 | 2.73 | 73.3 | 1.93 | 33.3 | 2.13 | 60.0 | 2.60 | 63.3 | 2.35 |
| UniVLA（Full） | 93.3 | 2.87 | 100.0 | 2.33 | 46.7 | 2.47 | 86.7 | 2.87 | 81.7 | 2.63 |

#### C.2 动作解码器架构

LAPA 与我们的方法均使用两个多头注意力模块处理潜动作和视觉嵌入，并用 MLP 处理本体感知状态。随后拼接嵌入，经投影层映射到目标动作维度。本体感知投影模块仅用于真实机器人实验。

**表 A-VI：真实机器人动作解码器详细参数。**

| 模块 | 参数项 | 值 |
|---|---|---:|
| 潜动作注意力池化 | 注意力头数 | 8 |
| 潜动作注意力池化 | 每头维度 | 64 |
| 潜动作注意力池化 | 隐藏维度 | 512 |
| 潜动作注意力池化 | MLP 比例 | 4 |
| 视觉嵌入注意力池化 | 注意力头数 | 8 |
| 视觉嵌入注意力池化 | 每头维度 | 64 |
| 视觉嵌入注意力池化 | 隐藏维度 | 512 |
| 视觉嵌入注意力池化 | MLP 比例 | 4 |
| 动作投影 | 层数 | 1 |
| 动作投影 | 隐藏维度 | 512 |
| 本体感知投影 | 层数 | 2 |
| 本体感知投影 | 隐藏维度 | 512 |
| 总参数量 | — | 12.6M |

## 参考文献（原文）

以下保留原论文的作者、标题、会议及编号，便于与正文引用对应。双栏 PDF 提取的列表顺序按原页呈现。

```text
to enhance its downstream performance, and remains highly            [1] AgiBot-World-Contributors, Qingwen Bu, Jisong Cai,
adaptable even in data-limited scenarios. We aim for our work            Li Chen, Xiuqi Cui, Yan Ding, Siyuan Feng, Shenyuan
to pave the way for the next generation of generalist policies,          Gao, Xindong He, Xuan Hu, Xu Huang, Shu Jiang,
capable of leveraging web-scale video data for training, regard-         Yuxin Jiang, Cheng Jing, Hongyang Li, Jialu Li, Chiming
less of embodiment gaps or the availability of action labels.            Liu, Yi Liu, Yuxiang Lu, Jianlan Luo, Ping Luo, Yao
                                                                         Mu, Yuehan Niu, Yixuan Pan, Jiangmiao Pang, Yu Qiao,
           VI. L IMITATIONS AND F UTURE W ORK                            Guanghui Ren, Cheng Ruan, Jiaqi Shan, Yongjian Shen,
                                                                         Chengshi Shi, Mingkang Shi, Modi Shi, Chonghao Sima,
Latent action design. While UniVLA advances generalist                   Jianheng Song, Huijie Wang, Wenhao Wang, Dafeng
robotic policies, several limitations remain. The fixed gran-            Wei, Chengen Xie, Guo Xu, Junchi Yan, Cunbiao Yang,
ularity of the latent action and the predefined codebook size            Lei Yang, Shukai Yang, Maoqing Yao, Jia Zeng, Chi
may not be optimal for all tasks or embodiments. Exploring               Zhang, Qinglin Zhang, Bin Zhao, Chengyue Zhao, Jiaqi
adaptive mechanisms to dynamically adjust these based on                 Zhao, and Jianchao Zhu. Agibot world colosseo: A large-
environmental conditions could potentially improve perfor-               scale manipulation platform for scalable and intelligent
mance. In addition, UniVLA is primarily evaluated on single-             embodied systems. arXiv preprint arXiv:2503.06669,
arm manipulation tasks. The action granularity represented by            2025. 1
latent action tokens are relatively fixed within our framework.      [2] Alexander A Alemi, Ian Fischer, Joshua V Dillon, and
Extending the framework to dual-arm humanoid systems or                  Kevin Murphy. Deep variational information bottleneck.
dexterous hands could require more complex and finer-grained             In ICLR, 2017. 4
action space modeling. We leave this for future exploration.         [3] Arthur Allshire, Roberto Martı́n-Martı́n, Charles Lin,
Requirements on language annotation. Regarding language                  Shawn Manuel, Silvio Savarese, and Animesh Garg.
granularity, task-relevant latent actions are designed to encode         Laser: Learning a latent action space for efficient rein-
ego-agent movements critical for task completion, while ex-              forcement learning. In ICRA, 2021. 3
cluding non-ego dynamics (e.g., steam rising from a kettle           [4] Peter Anderson, Qi Wu, Damien Teney, Jake Bruce, Mark
during “boiling water”). The majority of our dataset comprises           Johnson, Niko Sünderhauf, Ian Reid, Stephen Gould, and
fine-grained instructions that describe short-horizon actions            Anton Van Den Hengel. Vision-and-language navigation:
rather than high-level goals. While more expressive language             Interpreting visually-grounded navigation instructions in
instructions could potentially reduce ambiguity in latent action         real environments. In CVPR, 2018. 2, 5, 7

 [5] Mahmoud Assran, Quentin Duval, Ishan Misra, Piotr Bo-             Cousineau, Benjamin Burchfiel, and Shuran Song. Dif-
     janowski, Pascal Vincent, Michael Rabbat, Yann LeCun,             fusion Policy: Visuomotor policy learning via action
     and Nicolas Ballas. Self-supervised learning from images          diffusion. In RSS, 2023. 6, 8, 18
     with a joint-embedding predictive architecture. In CVPR,     [18] A Conneau. Unsupervised cross-lingual representation
     2023. 3                                                           learning at scale. arXiv preprint arXiv:1911.02116, 2019.
 [6] Adrien Bardes, Quentin Garrido, Jean Ponce, Xinlei                1
     Chen, Michael Rabbat, Yann LeCun, Mahmoud Assran,            [19] Zichen Jeff Cui, Yibin Wang, Nur Muhammad Mahi
     and Nicolas Ballas. Revisiting feature prediction for             Shafiullah, and Lerrel Pinto. From play to policy:
     learning visual representations from video. arXiv preprint        Conditional behavior generation from uncurated robot
     arXiv:2404.08471, 2024. 3                                         data. arXiv preprint arXiv:2210.10047, 2022. 16
 [7] Suneel Belkhale, Yuchen Cui, and Dorsa Sadigh. HY-           [20] Zichen Jeff Cui, Hengkai Pan, Aadhithya Iyer, Siddhant
     DRA: Hybrid robot actions for imitation learning. arXiv           Haldar, and Lerrel Pinto. DynaMo: In-domain dynamics
     preprint arXiv:2306.17237, 2023. 16                               pretraining for visuo-motor control. In NeurIPS, 2024. 3
 [8] Homanga Bharadhwaj, Abhinav Gupta, Vikash Kumar,             [21] Shivin Dass, Jullian Yapeter, Jesse Zhang, Jiahui Zhang,
     and Shubham Tulsiani. Towards generalizable zero-shot             Karl Pertsch, Stefanos Nikolaidis, and Joseph J. Lim.
     manipulation via translating human interaction plans. In          CLVR jaco play dataset, 2023. URL https://github.com/
     ICRA, 2024. 2                                                     clvrai/clvr jaco play dataset. 16
 [9] Kevin Black, Mitsuhiko Nakamoto, Pranav Atreya,              [22] Jacob Devlin. Bert: Pre-training of deep bidirectional
     Homer Rich Walke, Chelsea Finn, Aviral Kumar, and                 transformers for language understanding. arXiv preprint
     Sergey Levine. Zero-shot robotic manipulation with pre-           arXiv:1810.04805, 2018. 1
     trained image-editing diffusion models. In ICLR, 2024.       [23] Ria Doshi, Homer Walke, Oier Mees, Sudeep Dasari,
     2, 16                                                             and Sergey Levine. Scaling Cross-Embodied Learning:
[10] Anthony Brohan, Noah Brown, Justice Carbajal, Yevgen              One policy for manipulation, navigation, locomotion and
     Chebotar, Xi Chen, Krzysztof Choromanski, Tianli Ding,            aviation. In CoRL, 2024. 2
     Danny Driess, Avinava Dubey, Chelsea Finn, et al. RT-2:      [24] Yilun Du, Sherry Yang, Bo Dai, Hanjun Dai, Ofir
     Vision-language-action models transfer web knowledge              Nachum, Josh Tenenbaum, Dale Schuurmans, and Pieter
     to robotic control. In CoRL, 2023. 1, 2, 4                        Abbeel. Learning universal policies via text-guided video
[11] Anthony Brohan, Noah Brown, Justice Carbajal, Yev-                generation. In NeurIPS, 2024. 2
     gen Chebotar, Joseph Dabis, Chelsea Finn, Keerthana          [25] Yilun Du, Sherry Yang, Pete Florence, Fei Xia, Ayzaan
     Gopalakrishnan, Karol Hausman, Alex Herzog, Jasmine               Wahid, brian ichter, Pierre Sermanet, Tianhe Yu, Pieter
     Hsu, et al. RT-1: Robotics transformer for real-world             Abbeel, Joshua B. Tenenbaum, Leslie Pack Kaelbling,
     control at scale. In RSS, 2023. 2, 16, 17                         Andy Zeng, and Jonathan Tompson. Video language
[12] Jake Bruce, Michael D Dennis, Ashley Edwards, Jack                planning. In ICLR, 2024. 11
     Parker-Holder, Yuge Shi, Edward Hughes, Matthew Lai,         [26] Chongkai Gao, Haozhuo Zhang, Zhixuan Xu, Zhehao
     Aditi Mavalankar, Richie Steigerwald, Chris Apps, et al.          Cai, and Lin Shao. FLIP: Flow-centric generative plan-
     Genie: Generative interactive environments. In ICML,              ning for general-purpose manipulation tasks. In ICLR,
     2024. 3, 9, 10                                                    2025. 2
[13] Qingwen Bu, Hongyang Li, Li Chen, Jisong Cai, Jia            [27] Shenyuan Gao, Siyuan Zhou, Yilun Du, Jun Zhang, and
     Zeng, Heming Cui, Maoqing Yao, and Yu Qiao. Towards               Chuang Gan. AdaWorld: Learning adaptable world mod-
     synergistic, generalized, and efficient dual-system for           els with latent actions. arXiv preprint arXiv:2503.18938,
     robotic manipulation. arXiv preprint arXiv:2410.08001,            2025. 3
     2024. 2, 16                                                  [28] Dibya Ghosh, Homer Walke, Karl Pertsch, Kevin Black,
[14] Qingwen Bu, Jia Zeng, Li Chen, Yanchao Yang, Guyue                Oier Mees, Sudeep Dasari, Joey Hejna, Tobias Kreiman,
     Zhou, Junchi Yan, Ping Luo, Heming Cui, Yi Ma, and                Charles Xu, Jianlan Luo, et al. Octo: An open-source
     Hongyang Li. Closed-loop visuomotor control with gen-             generalist robot policy. In RSS, 2024. 1, 2, 6, 17
     erative expectation for robotic manipulation. In NeurIPS,    [29] Kristen Grauman, Andrew Westbury, Eugene Byrne,
     2024. 2, 16                                                       Zachary Chavis, Antonino Furnari, Rohit Girdhar, Jack-
[15] Lawrence Yunliang Chen, Simeon Adebola, and Ken                   son Hamburger, Hao Jiang, Miao Liu, Xingyu Liu, et al.
     Goldberg. Berkeley UR5 demonstration dataset. https:              Ego4D: Around the world in 3,000 hours of egocentric
     //sites.google.com/view/berkeley-ur5/home. 16                     video. In CVPR, 2022. 3, 6, 10, 16
[16] Xiaoyu Chen, Junliang Guo, Tianyu He, Chuheng Zhang,         [30] Danijar Hafner, Timothy Lillicrap, Ian Fischer, Ruben
     Pushi Zhang, Derek Cathera Yang, Li Zhao, and Jiang               Villegas, David Ha, Honglak Lee, and James Davidson.
     Bian. IGOR: Image-goal representations are the atomic             Learning latent dynamics for planning from pixels. In
     control units for foundation models in embodied ai. arXiv         ICML, 2019. 3
     preprint arXiv:2411.00785, 2024. 2, 3                        [31] Minho Heo, Youngwoon Lee, Doohyun Lee, and
[17] Cheng Chi, Siyuan Feng, Yilun Du, Zhenjia Xu, Eric                Joseph J. Lim. FurnitureBench: Reproducible real-world

     benchmark for long-horizon complex manipulation. In             Kim, Nur Muhammad Mahi Shafiullah, and Lerrel Pinto.
     RSS, 2023. 16                                                   Behavior generation with latent actions. In ICML, 2024.
[32] Cheng-Chun Hsu, Bowen Wen, Jie Xu, Yashraj Narang,              3
     Xiaolong Wang, Yuke Zhu, Joydeep Biswas, and Stan          [45] Xinghang Li, Peiyan Li, Minghuan Liu, Dong Wang,
     Birchfield.     SPOT: Se (3) pose trajectory diffu-             Jirong Liu, Bingyi Kang, Xiao Ma, Tao Kong, Hanbo
     sion for object-centric manipulation. arXiv preprint            Zhang, and Huaping Liu. Towards generalist robot
     arXiv:2411.00965, 2024. 2                                       policies: What matters in building vision-language-action
[33] Edward J Hu, Yelong Shen, Phillip Wallis, Zeyuan Allen-         models. arXiv preprint arXiv:2412.14058, 2024. 5, 11,
     Zhu, Yuanzhi Li, Shean Wang, Lu Wang, and Weizhu                17
     Chen. LoRA: Low-rank adaptation of large language          [46] Xinghang Li, Minghuan Liu, Hanbo Zhang, Cunjun Yu,
     models. In ICLR, 2022. 5, 16, 17                                Jie Xu, Hongtao Wu, Chilam Cheang, Ya Jing, Weinan
[34] Eric Jang, Alex Irpan, Mohi Khansari, Daniel Kappler,           Zhang, Huaping Liu, Hang Li, and Tao Kong. Vision-
     Frederik Ebert, Corey Lynch, Sergey Levine, and Chelsea         language foundation models as effective robot imitators.
     Finn. BC-Z: Zero-shot task generalization with robotic          In ICLR, 2024. 2, 16
     imitation learning. In CoRL, 2022. 16                      [47] Xuanlin Li, Kyle Hsu, Jiayuan Gu, Karl Pertsch, Oier
[35] Xiaogang Jia, Qian Wang, Atalay Donat, Bowen Xing,              Mees, Homer Rich Walke, Chuyuan Fu, Ishikaa Lunawat,
     Ge Li, Hongyi Zhou, Onur Celik, Denis Blessing, Rudolf          Isabel Sieh, Sean Kirmani, et al. Evaluating real-world
     Lioutikov, and Gerhard Neumann. MaIL: Improving                 robot manipulation policies in simulation. In CoRL,
     imitation learning with selective state space models. In        2024. 5, 16, 17
     CoRL, 2024. 6                                              [48] Bo Liu, Yifeng Zhu, Chongkai Gao, Yihao Feng, Qiang
[36] Dmitry Kalashnikov, Alex Irpan, Peter Pastor, Julian            Liu, Yuke Zhu, and Peter Stone. LIBERO: Benchmark-
     Ibarz, Alexander Herzog, Eric Jang, Deirdre Quillen,            ing knowledge transfer for lifelong robot learning. In
     Ethan Holly, Mrinal Kalakrishnan, Vincent Vanhoucke,            NeurIPS, 2024. 2, 5, 6, 9
     et al. Scalable deep reinforcement learning for vision-    [49] Haotian Liu, Chunyuan Li, Yuheng Li, and Yong Jae
     based robotic manipulation. In CoRL, 2018. 16                   Lee. Improved baselines with visual instruction tuning.
[37] Siddharth Karamcheti, Suraj Nair, Ashwin Balakrishna,           In CVPR, 2023. 7
     Percy Liang, Thomas Kollar, and Dorsa Sadigh. Pris-        [50] Huihan Liu, Soroush Nasiriany, Lance Zhang, Zhiyao
     matic VLMs: Investigating the design space of visually-         Bao, and Yuke Zhu. Robot learning on the job: Human-
     conditioned language models. In ICML, 2024. 4, 5, 8             in-the-loop autonomy and learning during deployment.
[38] Alexander Khazatsky, Karl Pertsch, Suraj Nair, Ash-             In RSS, 2023. 16
     win Balakrishna, Sudeep Dasari, Siddharth Karam-           [51] Jianlan Luo, Charles Xu, Xinyang Geng, Gilbert Feng,
     cheti, Soroush Nasiriany, Mohan Kumar Srirama,                  Kuan Fang, Liam Tan, Stefan Schaal, and Sergey Levine.
     Lawrence Yunliang Chen, Kirsty Ellis, et al. DROID:             Multi-stage cable routing through hierarchical imitation
     A large-scale in-the-wild robot manipulation dataset. In        learning. TRO, 2023. 16
     RSS, 2024. 1, 16                                           [52] Jianlan Luo, Charles Xu, Fangchen Liu, Liam Tan,
[39] Moo Jin Kim, Karl Pertsch, Siddharth Karamcheti, Ted            Zipeng Lin, Jeffrey Wu, Pieter Abbeel, and Sergey
     Xiao, Ashwin Balakrishna, Suraj Nair, Rafael Rafailov,          Levine. FMB: a functional manipulation benchmark for
     Ethan Foster, Grace Lam, Pannag Sanketi, et al. Open-           generalizable robotic learning. IJRR, 2023. 16
     VLA: An open-source vision-language-action model. In       [53] Corey Lynch, Ayzaan Wahid, Jonathan Tompson, Tianli
     CoRL, 2024. 1, 2, 4, 6, 7, 8, 10, 16, 17, 18                    Ding, James Betker, Robert Baruch, Travis Armstrong,
[40] Jacob Krantz, Erik Wijmans, Arjun Majumdar, Dhruv               and Pete Florence. Interactive language: Talking to robots
     Batra, and Stefan Lee. Beyond the nav-graph: Vision-            in real time. RA-L, 2023. 16
     and-language navigation in continuous environments. In     [54] Yecheng Jason Ma, Joey Hejna, Ayzaan Wahid, Chuyuan
     ECCV, 2020. 7                                                   Fu, Dhruv Shah, Jacky Liang, Zhuo Xu, Sean Kirmani,
[41] Jacob Krantz, Erik Wijmans, Arjun Majundar, Dhruv               Peng Xu, Danny Driess, et al. Vision language models
     Batra, and Stefan Lee. Beyond the nav-graph: Vision             are in-context value learners. In ICLR, 2025. 11
     and language navigation in continuous environments. In     [55] Ajay Mandlekar, Yuke Zhu, Animesh Garg, Jonathan
     ECCV, 2020. 7                                                   Booher, Max Spero, Albert Tung, Julian Gao, John
[42] Hanna Kurniawati. Partially observable markov deci-             Emmons, Anchit Gupta, Emre Orbay, Silvio Savarese,
     sion processes (pomdps) and robotics. arXiv preprint            and Li Fei-Fei. RoboTurk: A crowdsourcing platform
     arXiv:2107.07599, 2021. 5                                       for robotic skill learning through imitation. In CoRL,
[43] Juho Lee, Yoonho Lee, Jungtaek Kim, Adam Kosiorek,              2018. 16
     Seungjin Choi, and Yee Whye Teh. Set transformer:          [56] Oier Mees, Lukas Hermann, Erick Rosete-Beas, and
     A framework for attention-based permutation-invariant           Wolfram Burgard. CALVIN: A benchmark for language-
     neural networks. In ICML, 2019. 5                               conditioned policy learning for long-horizon robot ma-
[44] Seungjae Lee, Yibin Wang, Haritheja Etukuru, H Jin              nipulation tasks. RA-L, 2022. 5, 16

[57] Oier Mees, Jessica Borja-Diaz, and Wolfram Burgard.              rose, and Sergey Levine. GNM: A general navigation
     Grounding language with visual affordances over un-              model to drive any robot. In ICRA, 2023. 6, 16
     structured data. In ICRA, 2023. 16                          [73] Rutav Shah, Roberto Martı́n-Martı́n, and Yuke Zhu.
[58] Russell Mendonca, Shikhar Bahl, and Deepak Pathak.               MUTEX: Learning unified policies from multimodal task
     Structured world models from human videos. In CoRL,              specifications. In CoRL, 2023. 16
     2023. 16                                                    [74] Andrew Szot, Bogdan Mazoure, Harsh Agrawal, Devon
[59] Atharva Mete, Haotian Xue, Albert Wilcox, Yongxin                Hjelm, Zsolt Kira, and Alexander Toshev. Ground-
     Chen, and Animesh Garg. Quest: Self-supervised skill             ing multimodal large language models in actions. In
     abstractions for learning continuous control. In NeurIPS,        NeurIPS, 2024. 3
     2024. 3                                                     [75] Hugo Touvron, Louis Martin, Kevin Stone, Peter Albert,
[60] Nicolas Meuleau, Leonid Peshkin, Kee-Eung Kim, and               Amjad Almahairi, Yasmine Babaei, Nikolay Bashlykov,
     Leslie Pack Kaelbling. Learning finite-state controllers         Soumya Batra, Prajjwal Bhargava, Shruti Bhosale, et al.
     for partially observable environments. arXiv preprint            Llama 2: Open foundation and fine-tuned chat models.
     arXiv:1301.6721, 2013. 5                                         arXiv preprint arXiv:2307.09288, 2023. 4
[61] Soroush Nasiriany, Tian Gao, Ajay Mandlekar, and Yuke       [76] Aaron Van Den Oord, Oriol Vinyals, and Koray
     Zhu. Learning and retrieval from prior data for skill-           Kavukcuoglu. Neural discrete representation learning.
     based imitation learning. In CoRL, 2022. 16                      In NeurIPS, 2017. 1, 3
[62] Maxime Oquab, Timothée Darcet, Théo Moutakanni,           [77] Ruben Villegas, Mohammad Babaeizadeh, Pieter-Jan
     Huy Vo, Marc Szafraniec, Vasil Khalidov, Pierre Fer-             Kindermans, Hernan Moraldo, Han Zhang, Moham-
     nandez, Daniel Haziza, Francisco Massa, Alaaeldin El-            mad Taghi Saffar, Santiago Castro, Julius Kunze, and
     Nouby, et al. DINOv2: Learning robust visual features            Dumitru Erhan. Phenaki: Variable length video gener-
     without supervision. TMLR, 2024. 2, 3, 4                         ation from open domain textual descriptions. In ICLR,
[63] Abhishek Padalkar, Acorn Pooley, Ajinkya Jain, Alex              2023. 3
     Bewley, Alex Herzog, Alex Irpan, Alexander Khazatsky,       [78] Homer Rich Walke, Kevin Black, Tony Z Zhao, Quan
     Anant Rai, Anikait Singh, Anthony Brohan, et al. Open            Vuong, Chongyi Zheng, Philippe Hansen-Estruch, An-
     X-Embodiment: Robotic learning datasets and RT-X                 dre Wang He, Vivek Myers, Moo Jin Kim, Max Du, et al.
     models. In ICRA, 2024. 1, 2, 6, 10, 16                           BridgeData v2: A dataset for robot learning at scale. In
[64] Yunchen Pu, Zhe Gan, Ricardo Henao, Xin Yuan, Chun-              CoRL, 2023. 1, 2, 6, 10, 16, 17
     yuan Li, Andrew Stevens, and Lawrence Carin. Vari-          [79] Zihao Wang, Shaofei Cai, Zhancun Mu, Haowei Lin,
     ational autoencoder for deep learning of images, labels          Ceyao Zhang, Xuejie Liu, Qing Li, Anji Liu, Xiaojian
     and captions. In NeurIPS, 2016. 3                                Ma, and Yitao Liang. OmniJARVIS: Unified vision-
[65] Gabriel Quere, Annette Hagengruber, Maged Iskandar,              language-action tokenization enables open-world instruc-
     Samuel Bustamante, Daniel Leidner, Freek Stulp, and              tion following agents. In NeurIPS, 2024. 3
     Joern Vogel. Shared Control Templates for Assistive         [80] Jason Wei, Xuezhi Wang, Dale Schuurmans, Maarten
     Robotics. In ICRA, Paris, France, 2020. 16                       Bosma, Fei Xia, Ed Chi, Quoc V Le, Denny Zhou,
[66] Alec Radford. Improving language understanding by                et al. Chain-of-thought prompting elicits reasoning in
     generative pre-training. 2018. 3                                 large language models. In NeurIPS, 2022. 5
[67] Colin Raffel, Noam Shazeer, Adam Roberts, Katherine         [81] Chuan Wen, Xingyu Lin, John So, Kai Chen, Qi Dou,
     Lee, Sharan Narang, Michael Matena, Yanqi Zhou, Wei              Yang Gao, and Pieter Abbeel. Any-point trajectory
     Li, and Peter J Liu. Exploring the limits of transfer            modeling for policy learning. In RSS, 2023. 2, 10
     learning with a unified text-to-text transformer. JMLR,     [82] Hongtao Wu, Ya Jing, Chilam Cheang, Guangzeng Chen,
     2020. 3, 4                                                       Jiafeng Xu, Xinghang Li, Minghuan Liu, Hang Li, and
[68] Moritz Reuss, Ömer Erdinç Yağmurlu, Fabian Wenzel,            Tao Kong. Unleashing large-scale video generative pre-
     and Rudolf Lioutikov. Multimodal Diffusion Trans-                training for visual robot manipulation. In ICLR, 2024.
     former: Learning versatile behavior from multimodal              2, 16
     goals. In ICRA Workshops, 2024. 6                           [83] Mengda Xu, Zhenjia Xu, Yinghao Xu, Cheng Chi, Gor-
[69] Saumya Saxena, Mohit Sharma, and Oliver Kroe-                    don Wetzstein, Manuela Veloso, and Shuran Song. Flow
     mer. Multi-resolution sensing for real-time control with         as the cross-domain manipulation interface. In CoRL,
     Vision-Language Models. In CoRL, 2023. 16                        2024. 2
[70] Dominik Schmidt and Minqi Jiang. Learning to act            [84] Mingxing Xu, Wenrui Dai, Chunmiao Liu, Xing Gao,
     without actions. In ICLR, 2024. 3                                Weiyao Lin, Guo-Jun Qi, and Hongkai Xiong. Spatial-
[71] Nur Muhammad Mahi Shafiullah, Anant Rai, Haritheja               temporal transformer networks for traffic flow forecast-
     Etukuru, Yiqian Liu, Ishan Misra, Soumith Chintala, and          ing. arXiv preprint arXiv:2001.02908, 2020. 3
     Lerrel Pinto. On bringing robots home. arXiv preprint       [85] Ge Yan, Kris Wu, and Xiaolong Wang. ucsd kitchens
     arXiv:2311.16098, 2023. 16                                       Dataset. August 2023. 16
[72] Dhruv Shah, Ajay Sridhar, Arjun Bhorkar, Noriaki Hi-        [86] Jonathan Yang, Catherine Glossop, Arjun Bhorkar,

     Dhruv Shah, Quan Vuong, Chelsea Finn, Dorsa Sadigh,
     and Sergey Levine.         Pushing the limits of cross-
     embodiment learning for manipulation and navigation.
     In RSS, 2024. 2, 5
[87] Seonghyeon Ye, Joel Jang, Byeongguk Jeon, Sejune Joo,
     Jianwei Yang, Baolin Peng, Ajay Mandlekar, Reuben
     Tan, Yu-Wei Chao, Bill Yuchen Lin, et al. Latent action
     pretraining from videos. In ICLR, 2025. 2, 3, 4, 6, 8, 18
[88] Chengbo Yuan, Chuan Wen, Tong Zhang, and Yang Gao.
     General flow as foundation affordance for scalable robot
     learning. In CoRL, 2024. 2
[89] Kaiwen Zha, Lijun Yu, Alireza Fathi, David A Ross,
     Cordelia Schmid, Dina Katabi, and Xiuye Gu. Language-
     guided image tokenization for generation. arXiv preprint
     arXiv:2412.05796, 2024. 4
[90] Xiaohua Zhai, Basil Mustafa, Alexander Kolesnikov, and
     Lucas Beyer. Sigmoid loss for language image pre-
     training. In ICCV, 2023. 4
[91] Jiazhao Zhang, Kunyu Wang, Rongtao Xu, Gengze Zhou,
     Yicong Hong, Xiaomeng Fang, Qi Wu, Zhizheng Zhang,
     and He Wang. NaVid: Video-based vlm plans the next
     step for vision-and-language navigation. In RSS, 2024.
     7, 11
[92] Zijian Zhang, Kaiyuan Zheng, Zhaorun Chen, Joel Jang,
     Yi Li, Chaoqi Wang, Mingyu Ding, Dieter Fox, and
     Huaxiu Yao. GRAPE: Generalizing robot policy via
     preference alignment. arXiv preprint arXiv:2411.19309,
     2024. 11
[93] Tony Z Zhao, Vikash Kumar, Sergey Levine, and Chelsea
     Finn. Learning fine-grained bimanual manipulation with
     low-cost hardware. In RSS, 2023. 5, 10
[94] Ruijie Zheng, Yongyuan Liang, Shuaiyi Huang, Jianfeng
     Gao, Hal Daumé III, Andrey Kolobov, Furong Huang,
     and Jianwei Yang. TraceVLA: Visual trace prompting en-
     hances spatial-temporal awareness for generalist robotic
     policies. In ICLR, 2025. 5
[95] Gaoyue Zhou, Victoria Dean, Mohan Kumar Srirama,
     Aravind Rajeswaran, Jyothish Pari, Kyle Hatch, Aryan
     Jain, Tianhe Yu, Pieter Abbeel, Lerrel Pinto, et al. Train
     offline, test online: A real robot learning benchmark. In
     ICRA, 2023. 16
[96] Gaoyue Zhou, Hengkai Pan, Yann LeCun, and Lerrel
     Pinto. DINO-WM: World models on pre-trained vi-
     sual features enable zero-shot planning. arXiv preprint
     arXiv:2411.04983, 2024. 3
[97] Xinghao Zhu, Ran Tian, Chenfeng Xu, Mingxiao Huo,
     Wei Zhan, Masayoshi Tomizuka, and Mingyu Ding.
     Fanuc Manipulation: A dataset for learning-based ma-
     nipulation with FANUC Mate 200iD Robot. 2023. 16
[98] Yifeng Zhu, Peter Stone, and Yuke Zhu. Bottom-up skill
     discovery from unsegmented demonstrations for long-
     horizon robot manipulation. RA-L, 2022. 16
[99] Yifeng Zhu, Abhishek Joshi, Peter Stone, and Yuke
     Zhu. VIOLA: Imitation learning for vision-based ma-
     nipulation with object proposal priors. arXiv preprint
     arXiv:2210.11339, 2023. 16
```
