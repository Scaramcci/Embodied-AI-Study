
\documentclass[Afour,sageh,times]{sagej}

\usepackage{moreverb,url}
\usepackage{enumitem}
\usepackage{booktabs}
\usepackage{rotating}
\usepackage{pifont}
\newcommand{\cmark}{\ding{51}}
\newcommand{\xmark}{\ding{55}}
\usepackage{makecell}

\usepackage{xcolor}
\usepackage{tikz}
\usetikzlibrary{arrows.meta}

\newcommand{\timelinecite}[1]{%
  \shortstack[c]{\citeauthor{#1}\\\citeyearpar{#1}}%
}

\usepackage{booktabs}
\usepackage{tabularx}
\usepackage{array}
\usepackage{multirow}



\usepackage[colorlinks,bookmarksopen,bookmarksnumbered,citecolor=red,urlcolor=red]{hyperref}

\usepackage[table]{xcolor}

\newcommand\BibTeX{{\rmfamily B\kern-.05em \textsc{i\kern-.025em b}\kern-.08em
T\kern-.1667em\lower.7ex\hbox{E}\kern-.125emX}}

\def\volumeyear{2026}

\setcounter{secnumdepth}{3}

\begin{document}

\runninghead{Ma et al.}

<!-- 全文中文翻译；保留 LaTeX 公式、图表、模型名称与引用命令。 -->
\title{从人类视频中学习机器人：综述}

\author{Junyi Ma\affilnum{1,*}, Erhang Zhang\affilnum{1,*}, Haoran Yang\affilnum{1}, Ditao Li\affilnum{1}, Chenyang Xu\affilnum{1}, Guangming Wang\affilnum{2}, Hesheng Wang\affilnum{1}}

\affiliation{\affilnum{1}Shanghai Jiao Tong University, China\\
\affilnum{2}University of Cambridge, UK\\ \affilnum{*}Authors are with equal contributions}


\corrauth{Hesheng Wang, is with the Department of Automation, Shanghai Jiao Tong University, Shanghai 200240, China and the Key Laboratory of System Control and Information Processing, Ministry of Education of China.}

\email{wanghesheng@sjtu.edu.cn}


\begin{abstract}
具身智能与机器人技术进一步发展的关键瓶颈之一，是机器人数据规模化的挑战。近年来，受益于丰富的人类活动视频和计算机视觉进步，从人类视频数据中学习机器人操作技能受到广泛关注。这一方向有望让机器人被动地从海量且易获取的人类示范中学习技能，为通用机器人系统的规模化学习提供支持。本文综述人类视频驱动的机器人学习技术，重点讨论人机技能迁移与数据基础。我们首先回顾机器人策略学习基础，随后介绍引入人类视频的基本接口；接着提出将人类视频迁移为机器人技能的层次化分类，涵盖任务、观测和动作导向路径，并分析不同数据配置与学习范式之间的耦合关系。此外，我们调研常用人类视频数据集与视频生成方案，给出数据集发展和使用的大规模统计趋势。最后总结该领域的挑战与局限，并展望未来研究方向。论文列表见 \url{https://github.com/IRMVLab/awesome-robot-learning-from-human-videos}。
\end{abstract}

\keywords{Human-Robot Skill Transfer, Video-Based Learning, Robot Manipulation, Imitation Learning, Reinforcement Learning}

\maketitle


\section{介绍}

随着现代工业和社会对自动化需求的迅速增长，具身智能与机器人技术在过去几年中取得了快速进展。模仿学习、强化学习等机器人学习技术的显著发展，是推动这一进步的关键动力，为机器人操作和全身控制提供了重要而广泛的解决方案。

\begin{figure}[t]
  \centering
  \captionsetup{belowskip=1pt}
  \includegraphics[width=1\linewidth]{figs/teaser.pdf}
  \caption{本文综述的人类视频与机器人执行衔接示意图。相关工作被分为任务导向、观测导向和动作导向三类迁移路径；家族内分析和家族间比较用于突出其设计原则与权衡，并进一步给出选择合适 LfHV 路径的实践指南。}
  \label{fig:teaser}
  \vspace{-0.49cm}
\end{figure}

\begin{figure*}[t]
  \centering
  \captionsetup{aboveskip=2pt, belowskip=0pt}
  \includegraphics[width=1\linewidth]{figs/taxonomy.pdf}
  \caption{从人类视频中学习机器人的分类体系。}
  \label{fig:taxonomy}
  \vspace{-0.3cm}
\end{figure*}

然而，制造、物流和日常服务中的任务场景日益复杂，对机器人系统的通用性和泛化能力提出了更大挑战。传统模仿学习范式~\citep{brohan2022rt,zhao2023learning,fu2024mobile,ze20243d,chi2025diffusion} 依赖耗时且重复的示教采集过程，包括动作捕捉或遥操作示范，这显著降低了机器人策略在真实世界中的部署效率。示范数据的多样性有限且数量不足，也进一步限制了策略在新操作环境中的泛化。引入强化学习算法~\citep{schulman2017proximal,fujimoto2018addressing,haarnoja2018soft,hafner2019dream,janner2019trust} 可以通过与环境交互提升策略适应性，但通常依赖精心设计的奖励函数以及大量试错经验，不仅使真实机器人系统的训练成本高昂，还带来样本效率、训练稳定性和探索安全性方面的担忧。因此，模仿学习和强化学习在将机器人技能扩展到多样化开放世界场景时仍面临根本挑战。近年来，大语言模型和视觉语言模型的发展很大程度上得益于训练数据规模的急剧增长~\citep{chen2024expanding,grattafiori2024llama,yang2025qwen3}。受此启发，要提高机器人策略的泛化能力，就需要寻找比传统机器人数据更易采集、也更易扩展的数据来源。


在这一背景下，人类活动视频成为机器人学习的有前景的监督来源。随着计算机视觉持续进步，人类视频能够被更准确、高效地分析。这类数据天然包含密集的任务语义以及与多种物体交互的丰富模式，与机器人策略学习的需求高度契合。与遥操作示范相比，人类视频更易采集，互联网上还已经存在海量现成视频，使通用机器人开发所需的大规模数据获取成为可能。尽管已有综述~\citep{mccarthy2025towards,eze2025learning,feng2026human,zheng2026video} 为基于视频的机器人学习提供了有价值的视角，但 LfHV 仍需要更聚焦的梳理。尤其是，当前领域缺少以“信息如何从人类视频流向机器人执行”为中心的分类体系；围绕视角选择、对真实机器人数据的依赖以及学习范式，对不同迁移路径进行系统交叉比较的工作也十分有限。人类视频来源的整理同样较为零散，特别是在数据集使用频率、使用模式和视频生成方案的新兴作用方面。鉴于相关文献发展迅速，近期出现的一些方法和数据集也有必要在后续讨论。







\begin{table*}[t]
\centering
\scriptsize
\setlength{\tabcolsep}{4.2pt}
\caption{定量证据表明，人类视频比传统机器人遥操作具有更高的数据效率。}
\label{tab:human_video_efficiency}
\begin{tabularx}{\linewidth}{p{2.3cm}p{1.8cm}p{3.4cm} X}
\toprule
参考文献 & 设置 & 对比设置 & 定量效率结论 \\
\midrule
\cite{jang2022bc} & 单臂 & 人类视频 vs. 机器人遥操作示范 & 人类视频的采集速度比机器人遥操作示范快 \textbf{5--7 倍}。 \\
\cite{kareer2025egomimic} & 双臂 & 一小时人类数据 vs. 一小时机器人数据 & 一小时人类数据约产生 \textbf{1400 条示范}，而一小时机器人数据仅产生 \textbf{135 条示范}（数据产出约高 \textbf{$\sim$10.4 倍}）。 \\
\cite{dan2025x} & 单臂 & 人类视频 vs. 机器人遥操作示范 & 人类视频每个片段约需 \textbf{20 秒}，而机器人示范约需 \textbf{60 秒}。 \\
\cite{zhou2025you} & 双臂 & 人类视频驱动的自动 rollout 示范 vs. 遥操作 & 自动 rollout 的速度\textbf{远快于遥操作}，8 小时约可采集 \textbf{300 条示范}，并支持将每项任务扩展 \textbf{100 倍}至 \textbf{5K--24K} 条轨迹。 \\
\cite{freeman2026warped} & 单臂 & 第一视角人类示范 vs. 遥操作 & 基于人类视频的流程所需数据采集时间减少 \textbf{5--8 倍}，即速度约为遥操作的 \textbf{5--8 倍}。 \\
\bottomrule
\end{tabularx}
\end{table*}



为此，本文对人类视频驱动机器人学习的方法体系、数据基础和新兴研究趋势进行全面总结与细致分类，旨在为具身智能和机器人领域的后续研究提供更清晰的基础。如图~\ref{fig:teaser} 所示，我们将问题概念化为通过多个层次的迁移来衔接人类视频与机器人操作；综述的总体结构见图~\ref{fig:taxonomy}。主要贡献如下：
\begin{itemize}[leftmargin=1em]
    \setlength{\parskip}{0pt}
    \item \textbf{技能迁移的层次化桥接机制：} 我们提出连接人类视频与机器人执行路径的层次化分类，说明人机技能迁移如何在任务、观测和动作层面建立，并为每个层面识别作为迁移桥梁的关键视频中间表示，给出选择合适 LfHV 路径的实践指南。
    \item \textbf{跨数据配置与学习范式的家族间分析：} 除了构建分类体系，我们比较不同迁移家族与视角选择、真实机器人数据依赖和学习范式之间的关系，揭示现有 LfHV 方法中特有的设计耦合与方法权衡。
    \item \textbf{人-物交互分析的系统总结：} 在分类技能迁移路径之外，我们系统总结视频中解析人-物交互的常用方法，重点回顾二维、三维和四维空间中的手与物体检测、跟踪、重建和姿态估计工具，帮助研究者了解 LfHV 文献中当前实用且常见的现成交互分析技术。
    \item \textbf{人类视频数据的演变和偏好：} 我们在 LfHV 背景下提出了迄今为止（迄今为止）最大的人类视频源统计分析，系统地总结了人类视频数据集的发展趋势和相关生成技术。基于综合情况，我们进一步分析了不同类别的 LfHV 方法所表现出的数据偏好。
    \item \textbf{跨模型、数据和基准的未来方向：} 根据在桥接机制和数据基础中观察到的趋势，我们确定了未来研究的几个有希望的方向。我们特别强调新的建模范式、更丰富的数据模式、更标准化的基准和更具协作性的生态系统的机会。
\end{itemize}

为了保持更清晰、更有针对性的范围，本次调查关注的是利用人类视频数据来促进机器人操纵策略的 LfHV 作品，而不是那些无需复杂操纵的全身控制和运动的作品~\citep{mao2024learning,allshire2025visual,li2025robomirror,yang2026zerowbc}。本文的其余部分组织如下：Sec.~\ref{sec:background}（背景）回顾了基础机器人学习范例及其用于合并人类视频的接口，并介绍了 LfHV 问题的统一表述。 Sec.~\ref{sec:hr_skill_transfer}（人类-机器人技能转移）对人类视频和机器人执行之间的桥接机制进行了分类，并以分层方式研究了相关工作。 Sec.~\ref{sec:data_foundations}（数据基础）介绍了现有人类视频的开源数据集，以及想象的对应物的生成技术。 Sec.~\ref{sec:discussion}（讨论）深入研究了这一新兴领域的关键挑战，并概述了有希望的未来方向。最后，Sec.~\ref{sec:conclusion}（结论）提供了本次调查的总结。


\begin{figure*}[t]
  \centering
  \captionsetup{aboveskip=2pt, belowskip=0pt}
  \includegraphics[width=1\linewidth]{figs/bridging_overview_new.pdf}
  \caption{在任务、观测和动作层面衔接人类视频与机器人执行的示意图。}
  \label{fig:bridging_overview}
\end{figure*}



\section{背景} \label{sec:background}

机器人从人类视频中学习通常建立在机器人技术的两个基本范例之上：\textit{模仿学习} (IL) 和 \textit{强化学习} (RL)。它们提供了学习视觉运动策略的核心框架，现有的 LfHV 方法可以被视为扩展或重新解释它们。因此，在回顾基于人类视频的机器人学习之前，我们简要回顾一下 IL 和 RL 的数学基础，并讨论将人类视频纳入这些框架的接口。本节进一步提供了将 LfHV 表征为最小化跨实施例差异的统一公式。



\subsection{模仿学习}

模仿学习旨在通过模仿专家演示来学习策略。在机器人技术中，轨迹通常表示为 $\tau = \{(o_t, s_t, a_t)\}_{t=1}^T$，其中 $o_t$ 表示视觉观察，$s_t$ 表示本体感受状态，$a_t$ 对应于动作。在现代的具体人工智能系统中，通常会合并任务指令 $l$ 来指定任务目标。模仿学习的标准公式是对专家演示数据集 $\mathcal{D}_{\text{expert}}$ 的最大似然估计：
\begin{equation}
\max_{\theta} \sum_{\tau \in \mathcal{D}_{\text{expert}}} \sum_{t} 
\log \pi_{\theta}(a_t \mid o_{\leq t}, s_{\leq t}, l),
\label{eq:il_eq}
\end{equation}
其中 $\pi_{\theta}$ 表示由 $\theta$ 参数化的 IL 策略。


将人类视频融入机器人模仿学习中，旨在降低通过远程操作收集$\mathcal{D}_{\text{expert}}$的大量成本（见表~\ref{tab:human_video_efficiency}）。因此，它尝试使用从人类视频中提取的信息来重建等式~(\ref{eq:il_eq})中的$l$、$o_t$和$a_t$。根据$o_t$和$a_t$的形式可以确定$s_t$。对于任务指令 $l$，人类视频本质上提供了人类如何完成目标操纵任务的程序结构。因此，可以轻松地从文本或图像形式的人类视频中解析任务指令，以进行机器人任务规划。对于视觉观察$o_t$，最直观的策略是将人类视频观察转化为与实施例无关或以机器人为中心的观察。或者，从人类视频中学习视觉编码器以将 $o_t$ 压缩为机器人策略可直接使用的视觉表示也是实用的。对于动作 $a_t$，从人类视频中提取的手部物体姿势和潜在动作表示等显式可供性可以用作机器人动作生成的指导。







\subsection{强化学习}

强化学习侧重于通过与环境的交互来学习策略，旨在最大化累积奖励。形式上，RL 目标是：
\begin{equation}
\max_{\theta} \; \mathbb{E}_{\tau \sim \pi_{\theta}} \left[
\sum_{t=1}^{T} \gamma^{t-1} R_{\phi}(s_t, a_t)
\right], \,\, \text{with } \theta \leftarrow \theta_{0},
\end{equation}
其中$R_{\phi}(s_t, a_t)$表示由$\phi$参数化的奖励函数，$\gamma$是折扣因子，$\theta$表示可学习的策略参数，$\theta_{0}$表示策略的初始化。与模仿学习相比，强化学习不一定需要专家的动作标签，而是通过奖励引导的试错探索来改进策略。然而，设计合理的奖励函数并实现有效的探索是现实世界机器人应用面临的主要挑战。

因此，人类视频可以通过两个重要的接口（$\theta_{0}$ 的策略初始化和 $R_{\phi}$ 的奖励学习）相应地纳入 RL 框架中。对于策略初始化，人类视频可以提供明确的可供性（例如手部轨迹）作为 $\theta_{0}$ 之前的初始策略。这种初始化可以减轻下游机器人学习中的探索负担并提高样本效率。对于奖励塑造，可以从人类视频中推断出视觉嵌入和可供性等信息信号来构建奖励函数，而不是手动设计 $R_{\phi}$。通过这种方式，人类视频可以为策略优化提供更好的起点，或者提供信息更丰富且一致的学习目标来指导强化学习。

可以看出，人类视频在机器人学习中的作用可以通过模仿学习和强化学习的镜头来解释。从模仿学习的角度来看，人类视频通过提供任务说明、视觉观察和动作提示，可以作为专家演示的可扩展替代品。从强化学习的角度来看，它们为策略初始化和奖励构建提供了信息丰富的先验，从而降低了探索难度和手动奖励工程。这个观点还表明，大多数现有的 LfHV 方法可以被视为在 IL 和 RL 的特定接口上运行。可以从 IL 和 RL 范式的这些接口中进一步抽象出不同的桥接机制，从而促进以下方法分类。

\subsection{从人类视频学习的统一形式化} \label{sec:unified_formulation}

尽管策略学习范式存在差异，但机器人通常会接收任务指令，感知其环境，然后生成动作来完成操纵任务。因此，从人类视频中学习的问题可以进一步抽象为最小化跨实施例差异的多个来源。具体来说，我们可以将学习目标描述为：
\begin{equation}
\Phi^* = \arg\min_{\Phi} 
\mathcal{L}_{\text{obs}}(\Phi) + 
\mathcal{L}_{\text{act}}(\Phi) + 
\mathcal{L}_{\text{obj}}(\Phi),
\end{equation}
其中 $\Phi$ 表示将人类视频映射到共享表示空间的桥接函数。在这里，$\mathcal{L}_{\text{obs}}$ 测量人类和机器人感知之间的观察差距，$\mathcal{L}_{\text{act}}$ 捕获人类行为和机器人控制空间之间的动作差距，$\mathcal{L}_{\text{obj}}$ 表示由于人类视频中缺乏任务注释或明确奖励而导致的客观差距。值得注意的是，这种概念表述自然涵盖了更广泛的转移范式，包括那些不属于传统 IL 或 RL 的范式，例如从人类演示中直接重定向。


根据这个提法，我们自然可以将文献分为不同的类别。在下一节中，我们回顾每个类别下的代表性方法，并分析它们的设计选择，以缩小人类视频和机器人控制之间的差距。


\section{人机技能迁移} \label{sec:hr_skill_transfer}

根据Sec.~\ref{sec:unified_formulation}中的表述，从人类视频到机器人执行的桥接机制可以分为三类：\textit{面向任务的传输、面向观察的传输和面向动作的传输}。如图~\ref{fig:bridging_overview}所示，这些类别对应于六种形式的信息流，包括\textit{任务结构、任务意图、转换视频、视觉嵌入、可供性和潜在动作}。接下来，我们将回顾每个类别下的代表性方法，并讨论它们如何实现从人类视频到机器人系统的技能转移。我们为与主导人机机器人技能转移的主要信息桥相对应的系列分配一种方法，即使使用了其他系列的辅助组件。


\subsection{任务导向迁移}

面向任务的传输旨在在任务指令层面连接人类视频和机器人执行。尽管野外人类视频不能直接为机器人策略学习提供动作标签，但任务的程序组织和目标可以作为指令跨实施例转移。因此，该类别强调从人类视频中提取高级任务知识以指导下游机器人决策。这种桥接机制中的现有方法可以分为两组：（1）\textit{任务结构作为桥梁}，它将人类视频中演示的任务显式分解为时间指令；（2）\textit{任务意图作为桥梁}，它在不构建完整指令序列的情况下推断全局任务目标或任务阶段转换信号。也就是说，任务结构是任务过程的显式的、按时间组织的表示，而任务意图表示任务目标的紧凑的、隐式的表示。


\begin{figure}[t]
  \centering
  \includegraphics[width=1\linewidth]{figs/task_structure_transfer.pdf}
  \caption{作为桥梁} 的 \textit{任务结构的高级图。}
  \label{fig:task_structure_transfer}
\end{figure}



\begin{figure*}[t]
  \centering
  \resizebox{\linewidth}{!}{%
  \begin{tikzpicture}[x=1cm,y=1cm,>=Stealth]
    \definecolor{timelinegreen}{RGB}{122,145,139}
    \definecolor{timelineorange}{RGB}{176,126,116}
    \definecolor{timelinegray}{RGB}{218,220,221}
    \definecolor{timelineyear}{RGB}{118,116,112}
    \definecolor{timelinebubble}{RGB}{166,206,227}

    \draw[timelinegray,line width=4.2pt,-{Stealth[length=3.6mm]}] (-0.10,0) -- (20.90,0);

    \foreach \x/\year in {0.53/2015,1.48/2017,2.43/2018,3.38/2019,4.33/2022,7.18/2023,9.08/2024,12.88/2025} {
      \fill[timelinebubble,draw=white,line width=0.7pt] (\x,0) circle (0.17);
      \node[font=\bfseries\scriptsize,text=timelineyear] at (\x,-0.36) {\year};
    }


    \draw[timelinegreen,line width=2.5pt,-{Stealth[length=2.2mm]}] (1.00,0.05) -- (1.00,0.90);
    \node[align=center,font=\fontsize{8}{6.2}\selectfont,text=timelinegreen] at (1.00,1.17) {\timelinecite{yang2015robot}};

    \draw[timelinegreen,line width=2.5pt,-{Stealth[length=2.2mm]}] (1.95,-0.05) -- (1.95,-0.90);
    \node[align=center,font=\fontsize{8}{6.2}\selectfont,text=timelinegreen] at (1.95,-1.19) {\timelinecite{aksoy2017unsupervised}};

    \draw[timelinegreen,line width=2.5pt,-{Stealth[length=2.2mm]}] (2.90,0.05) -- (2.90,0.90);
    \node[align=center,font=\fontsize{8}{6.2}\selectfont,text=timelinegreen] at (2.90,1.17) {\timelinecite{nguyen2018translating}};

    \draw[timelinegreen,line width=2.5pt,-{Stealth[length=2.2mm]}] (3.85,-0.05) -- (3.85,-1.35);
    \node[align=center,font=\fontsize{8}{6.2}\selectfont,text=timelinegreen] at (3.85,-1.65) {\timelinecite{yang2019learning}};

    \draw[timelinegreen,line width=2.5pt,-{Stealth[length=2.2mm]}] (4.80,0.05) -- (4.80,0.90);
    \node[align=center,font=\fontsize{8}{6.2}\selectfont,text=timelinegreen] at (4.80,1.17) {\timelinecite{yang2022learning}};

    \draw[timelinegreen,line width=2.5pt,-{Stealth[length=2.2mm]}] (5.75,-0.05) -- (5.75,-0.90);
    \node[align=center,font=\fontsize{8}{6.2}\selectfont,text=timelinegreen] at (5.75,-1.19) {\timelinecite{pertsch2022cross}};

    \draw[timelinegreen,line width=2.5pt,-{Stealth[length=2.2mm]}] (6.70,0.05) -- (6.70,1.35);
    \node[align=center,font=\fontsize{8}{6.2}\selectfont,text=timelinegreen] at (6.70,1.65) {\timelinecite{yang2022explicit}};

    \draw[timelinegreen,line width=2.5pt,-{Stealth[length=2.2mm]}] (7.65,-0.05) -- (7.65,-0.90);
    \node[align=center,font=\fontsize{8}{6.2}\selectfont,text=timelinegreen] at (7.65,-1.19) {\timelinecite{guo2023learning}};

    \draw[timelinegreen,line width=2.5pt,-{Stealth[length=2.2mm]}] (8.60,0.05) -- (8.60,1.35);
    \node[align=center,font=\fontsize{8}{6.2}\selectfont,text=timelinegreen] at (8.60,1.65) {\timelinecite{yang2023watch}};

    \draw[timelineorange,line width=2.5pt,-{Stealth[length=2.2mm]}] (9.55,0.05) -- (9.55,1.00);
    \node[align=center,font=\fontsize{8}{6.2}\selectfont,text=timelineorange] at (9.65,1.29) {\timelinecite{wake2024gpt}};

    \draw[timelineorange,line width=2.5pt,-{Stealth[length=2.2mm]}] (10.50,0.05) -- (10.50,1.65);
    \node[align=center,font=\fontsize{8}{6.2}\selectfont,text=timelineorange] at (10.50,1.95) {\timelinecite{ding2024knowledge}};

    \draw[timelineorange,line width=2.5pt,-{Stealth[length=2.2mm]}] (11.45,-0.05) -- (11.45,-1.00);
    \node[align=center,font=\fontsize{8}{6.2}\selectfont,text=timelineorange] at (11.45,-1.29) {\timelinecite{wang2024vlm}};

    \draw[timelineorange,line width=2.5pt,-{Stealth[length=2.2mm]}] (12.40,-0.05) -- (12.40,-1.65);
    \node[align=center,font=\fontsize{8}{6.2}\selectfont,text=timelineorange] at (12.40,-1.95) {\timelinecite{chen2024vlmimic}};

    \draw[timelineorange,line width=2.5pt,-{Stealth[length=2.2mm]}] (13.35,0.05) -- (13.35,0.90);
    \node[align=center,font=\fontsize{8}{6.2}\selectfont,text=timelineorange] at (13.35,1.17) {\timelinecite{clark2025action}};

    \draw[timelineorange,line width=2.5pt,-{Stealth[length=2.2mm]}] (14.30,-0.05) -- (14.30,-0.90);
    \node[align=center,font=\fontsize{8}{6.2}\selectfont,text=timelineorange] at (14.30,-1.19) {\timelinecite{hori2025interactive}};

    \draw[timelineorange,line width=2.5pt,-{Stealth[length=2.2mm]}] (15.25,0.05) -- (15.25,1.35);
    \node[align=center,font=\fontsize{8}{6.2}\selectfont,text=timelineorange] at (15.25,1.65) {\timelinecite{wang2025chain}};

    \draw[timelineorange,line width=2.5pt,-{Stealth[length=2.2mm]}] (16.20,-0.05) -- (16.20,-1.35);
    \node[align=center,font=\fontsize{8}{6.2}\selectfont,text=timelineorange] at (16.20,-1.65) {\timelinecite{ma2025egoloc}};

    \draw[timelineorange,line width=2.5pt,-{Stealth[length=2.2mm]}] (17.15,0.05) -- (17.15,0.90);
    \node[align=center,font=\fontsize{8}{6.2}\selectfont,text=timelineorange] at (17.15,1.17) {\timelinecite{ye2025watch}};

    \draw[timelineorange,line width=2.5pt,-{Stealth[length=2.2mm]}] (18.10,-0.05) -- (18.10,-0.90);
    \node[align=center,font=\fontsize{8}{6.2}\selectfont,text=timelineorange] at (18.10,-1.19) {\timelinecite{chen2025fmimic}};

    \draw[timelineorange,line width=2.5pt,-{Stealth[length=2.2mm]}] (19.05,0.05) -- (19.05,1.65);
    \node[align=center,font=\fontsize{8}{6.2}\selectfont,text=timelineorange] at (19.05,1.95) {\timelinecite{hori2025robot}};

    \draw[timelineorange,line width=2.5pt,-{Stealth[length=2.2mm]}] (20.00,-0.05) -- (20.00,-1.65);
    \node[align=center,font=\fontsize{8}{6.2}\selectfont,text=timelineorange] at (20.00,-1.95) {\timelinecite{lin2025physbrain}};

    \draw[timelinegreen,line width=2.6pt,rounded corners=1pt] (0.10,-2.18) -- (0.78,-2.18);
    \node[anchor=west,font=\bfseries\footnotesize,text=timelinegreen] at (0.92,-2.18) {传统判别方法};
    
    \draw[timelineorange,line width=2.6pt,rounded corners=1pt] (0.10,-2.53) -- (0.78,-2.53);
    \node[anchor=west,font=\bfseries\footnotesize,text=timelineorange] at (0.92,-2.53) {现代 VLM 增强方法};

  \end{tikzpicture}%
  }
  \caption{\textit{任务结构下的方法按时间顺序概述，作为 Sec.~\ref{sec:task_structures} 中的桥梁}。}
  \label{fig:task_structure_timeline}
\end{figure*}




\subsubsection{任务结构} \label{sec:task_structures}
如图~\ref{fig:task_structure_transfer}所示，\textit{任务结构作为桥梁，}旨在在机器人执行之前将人类视频转换为明确的、按时间组织的中间阶段（例如，细粒度形式：手柄上方的位置$\rightarrow$向下移动$\rightarrow$关闭夹具$\rightarrow$向上移动，或粗粒度形式）形式：从柜台上拿起刀（$\rightarrow$），用刀（$\rightarrow$）切白菜（将刀放在柜台上）。它引导机器人在不同阶段遵循有针对性的任务计划。为了清楚起见，我们将相关方法分为\textit{传统判别方法}和\textit{现代VLM增强方法}，并在图~\ref{fig:task_structure_timeline}所示的时间线中总结它们的发展。

\textit{(a) 传统判别方法：}早期代表性工作采用规模有限的判别模型或基于规则的机制，将人类视频中的任务分解为步骤。例如，\cite{yang2015robot}先从视频帧识别抓取类型和被操作物体，再将这些感知线索整合为“视觉句子”；随后依据概率操纵动作语法，将视觉句子解析为层次化语法树，最终转换为可执行的原子任务指令序列。受~\cite{aksoy2017unsupervised}启发，\cite{nguyen2018translating}以端到端方式结合 CNN 和 RNN，直接将人类视频翻译为动词-名词指令序列。沿着视频到指令的路线，\cite{yang2019learning}、\cite{yang2022explicit} 和 \cite{yang2023watch}联合利用全局场景特征与抓取感知的局部物体特征，进一步改进了用于机器人操纵的 LSTM 指令生成。\cite{pertsch2022cross}引入更具扩展性的动作识别模型，直接预测人类示范视频中的技能分布，得到任务结构的离散高级语义标签。为理解周期性任务的结构，\cite{yang2022learning}引入 RepNet，从单个人类视频估计动作循环次数，使复杂长时任务能够自动分解为标准化周期组件。为获得交互层面的细粒度分解，\cite{guo2023learning}识别人-物和物-物关系，将人类视频分割为三种可泛化的接触事件原语。然而，受模型容量和预定义规则限制，这些方法在多样且复杂的任务分解中泛化能力有限。

\textit{(b) 现代 VLM 增强方法：}得益于近年来生成式基础模型的快速发展，越来越多工作采用 VLM 进行时间任务分解，并在互联网规模的人类视频上取得更强的泛化能力。例如，\cite{wake2024gpt}率先使用 GPT-4V~\citep{achiam2023gpt}识别视频中的人类动作，并将其转写为顺序文本指令。
通过引入思想链技术，\cite{clark2025action} 提高了 VLM 推理能力，自动注释人类视频并提供详细的任务计划描述。 SeeDo~\citep{wang2024vlm} 和 Super-Mimic~\citep{ye2025watch} 进一步利用手部速度信息进行关键帧提取和视频分割，然后使用 VLM 为结果子任务生成语言描述。
为了进一步丰富任务规划的层次结构，PhysBrain~\citep{lin2025physbrain}采用了三种基于场景的视频分割策略，包括固定间隔分割、事件驱动分割和运动学感知分割。然后，它通过七维模板化 VQA 方案生成任务描述。可以注意到，现有的基于 VLM 的方法，如 SeeDo~\citep{wang2024vlm}、Super-Mimic~\citep{ye2025watch} 和 PhysBrain~\citep{lin2025physbrain} 基本上只能理解人类行为，并仅从单个分段剪辑或关键帧生成相应的任务描述。然而，长视野任务中的微步骤自然取决于整个视频的上下文。因此，剪辑级和关键帧级指令生成失去了远程依赖性，并导致任务理解不理想。为了解决这个问题，\cite{hori2025robot} 提出了一种长上下文 Q-Former，它进一步合并了当前视频片段之外的相邻剪辑的时间上下文。该架构提高了机器人确认生成和细粒度任务规划的准确性。为了减轻 VLM 推理的开环性质，\cite{hori2025interactive} 引入了额外的人为纠错机制，当初始计划不正确时，可以交互式重新规划显式子任务序列。 \cite{ma2025egoloc} 相反开发了一种端到端时间交互定位算法，无需人工干预即可实现闭环反馈。它集成了有效的 VLM 检查器，可自动验证手部对象交互事件的任务分解结果。



尽管上述基于 VLM 的方法在互联网规模的人类视频中实现了鲁棒的时间任务分解，但所得的任务结构仍然与机器人动作规划松散耦合。它们通常需要一个额外的阶段，使用分解的指令来指导单独的机器人策略。为了缩小这一差距，\cite{ding2024knowledge} 提出了一种基于知识的演示编程框架。它将人类视频分解为结构化的行动计划，并通过产品感知参数化将其语义映射到可执行的机器人任务。 VLMimic~\citep{chen2024vlmimic} 和 FMimic~\citep{chen2025fmimic} 进一步使用 VLM 来总结人类视频中控制动作的高级语义约束和低级几何代码参数。这使得机器人能够更直接地重放所演示的行为。此外，CoM~\citep{wang2025chain} 集成了多模态线索，将人类视频表示为结构化操作程序。该方案将演示的任务分解为具有相关控制相关参数的有序子任务，然后将它们转换为可执行的机器人代码。它进一步加强了任务结构和机器人动作生成之间的联系。

\textit{(c) 任务结构小结：}\textit{任务结构作为桥梁}在动作生成前为机器人提供显式且按时间组织的程序知识。该方向已从基于规则和判别式的分解，发展到具有更强扩展性和更丰富语义的 VLM 任务解析。近期工作还通过提高任务结构的可执行性，进一步缩小任务分解与下游执行之间的差距。不过，这些方法主要仍处于规划层面，通常需要额外的落地模块将任务结构转换为特定实施例的机器人动作。

\begin{figure}[t]
  \centering
  \includegraphics[width=1\linewidth]{figs/task_intent_transfer.pdf}
  \caption{\textit{任务意图的高级图作为桥梁}。}
  \label{fig:task_intent_transfer}
\end{figure}

\begin{figure}[t]
  \centering
  \resizebox{\linewidth}{!}{%
  \begin{tikzpicture}[x=1cm,y=1cm,>=Stealth]
    \definecolor{timelineblue}{RGB}{120,138,150}
    \definecolor{timelinebrick}{RGB}{171,128,120}
    \definecolor{timelinegray}{RGB}{218,220,221}
    \definecolor{timelineyear}{RGB}{118,116,112}
    \definecolor{timelinebubble}{RGB}{166,206,227}

    \draw[timelinegray,line width=4.2pt,-{Stealth[length=3.6mm]}] (-0.07,0) -- (10.18,0);


    \foreach \x/\year in {0.31/2016,1.57/2018,4.08/2019,5.34/2022,6.60/2023,7.85/2024,9.11/2026} {
      \fill[timelinebubble,draw=white,line width=0.7pt] (\x,0) circle (0.17);
      \node[font=\bfseries\scriptsize,text=timelineyear] at (\x,-0.36) {\year};
    }

    \draw[timelineblue,line width=2.5pt,-{Stealth[length=2.2mm]}] (2.20,0.05) -- (2.20,0.95);
    \node[align=center,font=\fontsize{8}{8.6}\selectfont,text=timelineblue] at (2.20,1.25) {\timelinecite{yu2018one}};

    \draw[timelineblue,line width=2.5pt,-{Stealth[length=2.2mm]}] (5.97,0.05) -- (5.97,0.95);
    \node[align=center,font=\fontsize{8}{8.6}\selectfont,text=timelineblue] at (5.97,1.25) {\timelinecite{jang2022bc}};

    \draw[timelineblue,line width=2.5pt,-{Stealth[length=2.2mm]}] (8.48,0.05) -- (8.48,0.95);
    \node[align=center,font=\fontsize{8}{8.6}\selectfont,text=timelineblue] at (8.48,1.25) {\timelinecite{jain2024vid2robot}};

    \draw[timelinebrick,line width=2.5pt,-{Stealth[length=2.2mm]}] (0.94,-0.05) -- (0.94,-0.95);
    \node[align=center,font=\fontsize{8}{8.6}\selectfont,text=timelinebrick] at (0.94,-1.25) {\timelinecite{sermanet2016unsupervised}};

    \draw[timelinebrick,line width=2.5pt,-{Stealth[length=2.2mm]}] (3.45,-0.05) -- (3.45,-0.95);
    \node[align=center,font=\fontsize{8}{8.6}\selectfont,text=timelinebrick] at (3.45,-1.25) {\timelinecite{yu2018one_hil}};

    \draw[timelinebrick,line width=2.5pt,-{Stealth[length=2.2mm]}] (4.71,0.05) -- (4.71,1.35);
    \node[align=center,font=\fontsize{8}{8.6}\selectfont,text=timelinebrick] at (4.71,1.67) {\timelinecite{sharma2019third}};

    \draw[timelinebrick,line width=2.5pt,-{Stealth[length=2.2mm]}] (7.23,-0.05) -- (7.23,-1.35);
    \node[align=center,font=\fontsize{8}{8.6}\selectfont,text=timelinebrick] at (7.23,-1.67) {\timelinecite{xu2023xskill}};

    \draw[timelinebrick,line width=2.5pt,-{Stealth[length=2.2mm]}] (9.74,-0.05) -- (9.74,-1.35);
    \node[align=center,font=\fontsize{8}{8.6}\selectfont,text=timelinebrick] at (9.74,-1.67) {\timelinecite{li2026act}};

    \draw[timelineblue,line width=2.6pt,rounded corners=1pt] (0.13,-2.03) -- (0.63,-2.03);
    \node[anchor=west,font=\bfseries\footnotesize,text=timelineblue] at (0.73,-2.03) {全局意图提取};

    \draw[timelinebrick,line width=2.6pt,rounded corners=1pt] (0.13,-2.38) -- (0.63,-2.38);
    \node[anchor=west,font=\bfseries\footnotesize,text=timelinebrick] at (0.73,-2.38) {阶段信号生成};
  \end{tikzpicture}%
  }
  \caption{按时间顺序概述 \textit{任务意图下的方法，作为 Sec.~\ref{sec:task_intents} 中的桥梁}。}
  \label{fig:task_intent_timeline}
\end{figure}



\subsubsection{任务意图} \label{sec:task_intents}

与作为桥梁} 的显式 \textit{任务结构相比，作为桥梁} 的 \textit{任务意图不需要将人类视频转换为完整的符号指令序列。相反，如图〜\ref{fig:task_intent_transfer}所示，他们从人类视频中提取更高级别的指导信号，例如全局任务目标和任务阶段转换信号。随后，他们可以将机器人控制调节为任务意图。因此，该桥接机制涉及\textit{接下来应该实现什么}以及\textit{跨实施例任务进展应该如何在接下来的}中发展。我们将相关工作分类为\textit{全局意图提取}和\textit{相位信号生成}，如图~\ref{fig:task_intent_timeline}所示。

\textit{(a) 全局意图提取：}该类早期工作将完整人类视频表示为用于策略适配的全局任务意图。\cite{yu2018one}利用域自适应元学习，从单个人类示范视频提取与任务相关的意图，并将其迁移到新任务的机器人策略适配中。此时，人类视频是待完成任务目标的紧凑表示。BC-Z~\citep{jang2022bc}将这一思想扩展到更广泛的多任务场景，以语言或人类视频产生的任务嵌入为条件训练共享机器人策略，从而无需为每个新任务收集机器人示范即可实现零样本泛化。类似地，Vid2Robot~\citep{jain2024vid2robot}将人类提示视频的视觉标记作为全局意图输入机器人策略；与 BC-Z 的 FiLM 层相比，它采用更强的交叉注意力 Transformer~\citep{vaswani2017attention}融合全局意图。


\textit{(b) 阶段信号生成：}当机器人操纵任务变得复杂且时间跨度较长时，仅有全局任务意图往往不够，还需要反映任务进度的更丰富信号。\cite{sermanet2016unsupervised}从人类视频发现隐式中间阶段，并将其转化为稠密感知奖励，证明无需构建显式指令序列也能获得任务阶段信号。\cite{yu2018one_hil}进一步使用阶段预测器从未剪辑视频推断任务进展，使机器人自主决定下一步调用哪个人类动作原语。XSkill~\citep{xu2023xskill}从无标注视频提取跨实施例技能原型，并规定这些潜在技能在未知机器人任务中的组合方式。\cite{sharma2019third}从第三人称人类视频逐步生成机器人第一人称视觉子目标，使低层控制器能在机器人自身环境中完成这些子目标。近期，\cite{li2026act}将任务意图扩展到非马尔可夫主动感知，通过认知辅助头推断机器人何时应在信息寻求与任务执行阶段之间切换行为。


\textit{(c) 任务意图小结：}\textit{任务意图作为桥梁}无需显式解析完整指令序列，而是利用人类视频为机器人控制生成紧凑的高级指导。现有方法主要通过提取任务总体目标、建模任务进度随时间的演化来实现这一点。与任务结构相比，任务意图避免固定的符号分解，通常更灵活，也更易跨实施例迁移；但仍需完善的机器人学习策略将推断出的意图落地为具体动作规划。

\subsubsection{任务导向迁移小结}

面向任务的传输为桥接人类视频和机器人执行提供了最与具体实施无关的途径。它不需要观察和行动之间的直接对应，而是在指令级别提取与任务相关的指导，在指令级别跨实施例迁移更自然可行。从这个角度来看，\textit{任务结构作为桥梁} 和 \textit{任务意图作为桥梁} 可以被视为组织人类视频中的高级知识的两种互补方式。前者强调显式的程序分解，使转移的知识更易于下游规划的解释。后者放松了对完整符号解析的需求，而是提供了紧凑的指导信号，这些信号通常对于跨域和长期政策适应更加灵活。它们的差异本质上反映了 \textit{显性} 和 \textit{灵活性} 之间更广泛的权衡。

剩下的一个关键瓶颈在于如何将人类视频的任务指导转化为具有足够精度和鲁棒性的可执行机器人行为。未来的进展可能取决于面向任务的迁移与面向观察和面向行动的迁移更紧密地结合。因此，来自人类视频的高级任务语义可以与实施例感知感知和低级控制联系起来。这种集成可能最终决定面向任务的迁移是否仍然只是一种规划辅助，还是成为可扩展机器人从人类视频中学习的更核心的界面。



\begin{figure*}[t]
  \centering
  \resizebox{\linewidth}{!}{%
  \begin{tikzpicture}[x=1cm,y=1cm,>=Stealth]
    \definecolor{timelineblue}{RGB}{120,138,150}
    \definecolor{timelinebrick}{RGB}{171,128,120}
    \definecolor{timelinegray}{RGB}{218,220,221}
    \definecolor{timelineyear}{RGB}{118,116,112}
    \definecolor{timelinebubble}{RGB}{166,206,227}

    \draw[timelinegray,line width=4.2pt,-{Stealth[length=3.6mm]}] (-0.10,0) -- (21.20,0);


    \foreach \x/\year in {0.40/2020,1.60/2021,4.00/2022,6.40/2023,8.80/2024,10.00/2025,19.60/2026} {
      \fill[timelinebubble,draw=white,line width=0.7pt] (\x,0) circle (0.17);
      \node[font=\bfseries\scriptsize,text=timelineyear] at (\x,-0.36) {\year};
    }

    \draw[timelineblue,line width=2.5pt,-{Stealth[length=2.2mm]}] (2.20,-0.05) -- (2.20,-0.90);
    \node[align=center,font=\fontsize{8}{8.6}\selectfont,text=timelineblue] at (2.20,-1.19) {\timelinecite{zhou2021manipulator}};

    \draw[timelineblue,line width=2.5pt,-{Stealth[length=2.2mm]}] (4.60,-0.05) -- (4.60,-0.90);
    \node[align=center,font=\fontsize{8}{8.6}\selectfont,text=timelineblue] at (4.60,-1.19) {\timelinecite{bahl2022human}};

    \draw[timelineblue,line width=2.5pt,-{Stealth[length=2.2mm]}] (7.00,-0.05) -- (7.00,-0.90);
    \node[align=center,font=\fontsize{8}{8.6}\selectfont,text=timelineblue] at (7.00,-1.19) {\timelinecite{chang2023look}};

    \draw[timelineblue,line width=2.5pt,-{Stealth[length=2.2mm]}] (9.40,-0.05) -- (9.40,-1.00);
    \node[align=center,font=\fontsize{8}{8.6}\selectfont,text=timelineblue] at (9.40,-1.29) {\timelinecite{li2024ag2manip}};

    \draw[timelineblue,line width=2.5pt,-{Stealth[length=2.2mm]}] (10.60,0.05) -- (10.60,0.90);
    \node[align=center,font=\fontsize{8}{8.6}\selectfont,text=timelineblue] at (10.60,1.17) {\timelinecite{xiong2025ag2x2}};

    \draw[timelinebrick,line width=2.5pt,-{Stealth[length=2.2mm]}] (1.00,0.05) -- (1.00,1.00);
    \node[align=center,font=\fontsize{8}{8.6}\selectfont,text=timelinebrick] at (1.00,1.29) {\timelinecite{smith2020avid}};

    \draw[timelinebrick,line width=2.5pt,-{Stealth[length=2.2mm]}] (3.40,0.05) -- (3.40,1.35);
    \node[align=center,font=\fontsize{8}{8.6}\selectfont,text=timelinebrick] at (3.40,1.65) {\timelinecite{xiong2021learning}};

    \draw[timelinebrick,line width=2.5pt,-{Stealth[length=2.2mm]}] (5.80,0.05) -- (5.80,1.00);
    \node[align=center,font=\fontsize{8}{8.6}\selectfont,text=timelinebrick] at (5.80,1.29) {\timelinecite{sun2022learning}};

    \draw[timelinebrick,line width=2.5pt,-{Stealth[length=2.2mm]}] (8.20,0.05) -- (8.20,1.00);
    \node[align=center,font=\fontsize{8}{8.6}\selectfont,text=timelinebrick] at (8.20,1.29) {\timelinecite{duan2023ar2}};

    \draw[timelinebrick,line width=2.5pt,-{Stealth[length=2.2mm]}] (11.80,-0.05) -- (11.80,-1.35);
    \node[align=center,font=\fontsize{8}{8.6}\selectfont,text=timelinebrick] at (11.80,-1.65) {\timelinecite{lepert2025phantom}};

    \draw[timelinebrick,line width=2.5pt,-{Stealth[length=2.2mm]}] (13.00,0.05) -- (13.00,0.90);
    \node[align=center,font=\fontsize{8}{8.6}\selectfont,text=timelinebrick] at (13.00,1.17) {\timelinecite{li2025h2r}};

    \draw[timelinebrick,line width=2.5pt,-{Stealth[length=2.2mm]}] (14.20,-0.05) -- (14.20,-1.65);
    \node[align=center,font=\fontsize{8}{8.6}\selectfont,text=timelinebrick] at (14.20,-1.95) {\timelinecite{lepert2025masquerade}};

    \draw[timelinebrick,line width=2.5pt,-{Stealth[length=2.2mm]}] (15.40,0.05) -- (15.40,1.35);
    \node[align=center,font=\fontsize{8}{8.6}\selectfont,text=timelinebrick] at (15.40,1.65) {\timelinecite{li2025mimicdreamer}};

    \draw[timelinebrick,line width=2.5pt,-{Stealth[length=2.2mm]}] (16.60,-0.05) -- (16.60,-1.35);
    \node[align=center,font=\fontsize{8}{8.6}\selectfont,text=timelinebrick] at (16.60,-1.65) {\timelinecite{ci2025h2r}};

    \draw[timelinebrick,line width=2.5pt,-{Stealth[length=2.2mm]}] (17.80,0.05) -- (17.80,1.65);
    \node[align=center,font=\fontsize{8}{8.6}\selectfont,text=timelinebrick] at (17.80,1.95) {\timelinecite{tang2025trajectory}};

    \draw[timelinebrick,line width=2.5pt,-{Stealth[length=2.2mm]}] (19.00,-0.05) -- (19.00,-1.65);
    \node[align=center,font=\fontsize{8}{8.6}\selectfont,text=timelinebrick] at (19.00,-1.95) {\timelinecite{song2025mitty}};

    \draw[timelinebrick,line width=2.5pt,-{Stealth[length=2.2mm]}] (20.20,0.05) -- (20.20,1.35);
    \node[align=center,font=\fontsize{8}{8.6}\selectfont,text=timelinebrick] at (20.20,1.65) {\timelinecite{freeman2026warped}};

    \draw[timelineblue,line width=2.6pt,rounded corners=1pt] (0.10,-2.03) -- (0.78,-2.03);
    \node[anchor=west,font=\bfseries\footnotesize,text=timelineblue] at (0.92,-2.03) {实施例抑制};

    \draw[timelinebrick,line width=2.6pt,rounded corners=1pt] (0.10,-2.38) -- (0.78,-2.38);
    \node[anchor=west,font=\bfseries\footnotesize,text=timelinebrick] at (0.92,-2.38) {实施例变换};

  \end{tikzpicture}%
  }
  \caption{按时间顺序概述了 \textit{将视频转换为桥梁} 的方法。~\ref{sec:transformed_videos}。}
  \label{fig:transformed_videos_timeline}
\end{figure*}

\subsection{观测导向迁移}

与面向任务的迁移相比，面向观察的迁移侧重于在视觉感知层面连接人类视频和机器人执行。它不是提取符号指令或高级意图，而是旨在将原始人类视频转换为与机器人的感知和控制管道直接兼容的观察表示。人类视频和机器人观察通常在视角、实体外观和环境条件方面存在显着差异。因此，这一类别强调生成可转移的视觉表示，以跨实施例对齐感知空间。具体来说，我们根据两个标准对现有的面向观察的转移工作进行分类：（1）\textit{将视频转换为桥梁}，它将人类视频直接转换为与实施例无关或类似机器人的视觉格式，以及（2）\textit{视觉嵌入作为桥梁}，其目标是学习实施例不变的潜在视觉表示，从而在共享特征中对齐人类和机器人观察。空间。



\begin{figure}[t]
  \centering
  \includegraphics[width=1\linewidth]{figs/transformed_videos_transfer.pdf}
  \caption{\textit{将视频转换为桥梁} 的插图。一些元素改编自\cite{li2024ag2manip,lepert2025phantom}。}
  \label{fig:transformed_videos_transfer}
\end{figure}

\subsubsection{变换后的视频} \label{sec:transformed_videos}
连接人类视频和机器人感知的最直接方法是将人类视频转换为视觉观察，从而抑制人类体现线索（即观察到的身体外观）。可选地，可以用特定的机器人实施例进一步呈现变换后的观察结果。因此，我们将相关方法分为\textit{实施例抑制}和\textit{实施例变换}，并使用图~\ref{fig:transformed_videos_timeline}所示的时间线来呈现它们。

\textit{(a) 实施例抑制：}由于机器人观测不包含人类外观，一些工作从视频中抑制与实施例相关的视觉线索，以缩小人类示范与机器人观测之间的形态差距（见图~\ref{fig:transformed_videos_transfer}(a)）。MIR~\citep{zhou2021manipulator}通过构建不可见手臂环境，聚焦物体状态变化并学习与机械臂无关的表示。\cite{bahl2022human}利用现成视频修复方法~\citep{lee2019copy}从人类和机器人视频中移除执行体，同时保持物体状态与场景动态，再以修复视频设计与实施例无关的对齐目标，通过真实交互改进策略。\cite{chang2023look}则基于单帧修复模型~\citep{rombach2022high}，将第一视角人类视频显式分解为执行体与环境成分；相比直接丢弃手部信号，这种分解更结构化，并保留指示交互位置的末端执行器运动。

有趣的是，从Ag2Manip~\citep{li2024ag2manip}到Ag2x2~\citep{xiong2025ag2x2}也可以观察到类似的进化模式。 Ag2Manip~\citep{li2024ag2manip} 从视频中分割出人手，然后将 E$^2$FGVI~\citep{li2022towards} 修复与时间对比学习相结合，以获得与代理无关的视觉表示。相比之下，Ag2x2~\citep{xiong2025ag2x2} 认识到从视频中完全消除人为因素可能会丢失重要的物体进展和双手协调信息。因此，它保留了人类视频中手部物体交互点的坐标，并将它们与视觉观察结合起来用于策略学习。


\textit{(b) 实施例变换：}在移除人类外观后进一步渲染机器人手臂，将人类视频转换为与机器人观测一致的视觉结果。AVID~\citep{smith2020avid} 使用 CycleGAN 完成视频翻译并为各阶段选择目标图像；后续方法结合关键点检测和扩散模型提升几何一致性与策略学习效果，但在野外场景中仍可能受到视点差异和生成伪影影响。

随着生成建模的发展，底层视频翻译范式已经从前面提到的基于 GAN 的风格化发展到基于扩散的具有修复技术的实施例转换。例如，Phantom~\citep{lepert2025phantom} 像 Ag2Manip~\citep{li2024ag2manip} 一样通过 E$^2$FGVI~\citep{li2022towards} 移除人类手臂，并进一步在其位置覆盖渲染的机器人以产生与机器人一致的观察结果。尽管获得了高质量的渲染结果，但它需要固定的第三人称相机设置来合成策划的外心机器人视点。在处理互联网上存在的大量具有不同观点的以自我为中心的人类活动视频时，这种假设限制了鲁棒性。
为了解决这个问题，Masquerade~\citep{lepert2025masquerade}将虚拟双手机器人放置在具有已知内参和外参的机器人相机坐标系中，并驱动机器人末端执行器跟踪恢复的人手运动。然后，它从原始视点渲染机器人观察结果，减少野外以自我为中心的人类视频与机器人执行之间的视点差异。
此外，考虑到野外人类视频通常没有相应的度量深度，\cite{lepert2025masquerade} 进一步使用 2D 关键点位置作为视觉模型中辅助损失的监督标签。这规避了像 Phantom~\citep{lepert2025phantom} 这样使用深度观测来完善 HaMeR 的要求。他们还证明，与仅使用视点对齐视频进行视觉编码器预训练的并发工作 H2R~\citep{li2025h2r} 相比，他们的协同训练管道可以在复杂的长视野双手任务上实现稳健的机器人策略。 MimicDreamer~\citep{li2025mimicdreamer}提出了一种更系统的人机视频对齐框架，共同解决视点对齐、动作对齐和视觉对齐问题。转换后的视频和对齐的动作轨迹直接用于训练 $\pi_0$ VLA 模型~\citep{black2024pi_0}。最近，WARPED~\citep{freeman2026warped} 进一步推动了基于渲染的实施例向手腕对齐观察的转变。它将手部物体跟踪和轨迹重定向与高斯泼溅相结合，以合成逼真的机器人手腕视图观察和对齐动作。与这些基于渲染的方法不同，H2R-Grounder~\citep{ci2025h2r} 将实施例转换制定为无配对数据的视频生成问题。它学习将人类和机器人视频分解为由操纵器姿势提示和干净的背景视频组成的共享表示。然后，在给定最小姿态指示器和背景的情况下对视频扩散模型进行微调，以从人类演示中合成时间对齐的机器人视频。该方案避免了直接机器人渲染中常见的浮动和未对准伪影~\citep{lepert2025masquerade,li2025h2r}。
为了方便下游应用程序，\cite{duan2023ar2} 开发了一款 iOS 应用程序，让用户可以在增强现实中记录机器人一致的操作演示。录制的演示可以直接用于下面的行为克隆~\citep{shridhar2023perceiver}，显着提高部署效率。


与上述直接使用转换后的视频进行机器人策略学习的方法相比，Mitty~\citep{song2025mitty} 还利用它们来训练端到端的人机视频转换模型。这种范式可以更好地概括未知的任务和环境。与 Mitty~\citep{song2025mitty} 类似，\cite{tang2025trajectory} 也专注于端到端转换建模。此外，他们引入稀疏光流轨迹作为附加生成条件，从而获得合理的视觉质量和轨迹可控性。

\textit{(c) 变换视频小结：}\textit{变换视频作为桥梁}以最直接的方式减少人类视频与机器人观测的视觉差异。现有方法沿两条路线发展：实施例抑制在保留交互场景信息的同时移除人类特有外观；实施例变换则进一步从人类视频合成与机器人一致的视觉观测。视频生成模型的进步推动了该方向，但方法仍高度依赖修复和渲染质量，几何不一致与视点不匹配等生成伪影可能传递到下游策略学习，尤其是在不受约束的野外场景中。




\begin{figure*}[t]
  \centering
  \resizebox{\linewidth}{!}{%
  \begin{tikzpicture}[x=1cm,y=1cm,>=Stealth]
    \definecolor{timelineblue}{RGB}{120,138,150}
    \definecolor{timelinebrick}{RGB}{171,128,120}
    \definecolor{timelinegray}{RGB}{218,220,221}
    \definecolor{timelineyear}{RGB}{118,116,112}
    \definecolor{timelinebubble}{RGB}{166,206,227}

    \draw[timelinegray,line width=4.2pt,-{Stealth[length=3.6mm]}] (-0.10,0) -- (25.50,0);

    \fill[timelinebubble,draw=white,line width=0.7pt] (0.64,0) circle (0.17);
    \node[font=\bfseries\scriptsize,text=timelineyear] at (0.64,-0.36) {2017};
    
    \fill[timelinebubble,draw=white,line width=0.7pt] (1.36,0) circle (0.17);
    \node[font=\bfseries\scriptsize,text=timelineyear] at (1.36,-0.36) {2018};
    
    \fill[timelinebubble,draw=white,line width=0.7pt] (2.55,0) circle (0.17);
    \node[font=\bfseries\scriptsize,text=timelineyear] at (2.55,-0.36) {2020};
    
    \fill[timelinebubble,draw=white,line width=0.7pt] (3.70,0) circle (0.17);
    \node[font=\bfseries\scriptsize,text=timelineyear] at (3.70,0.36) {2021};
    
    \fill[timelinebubble,draw=white,line width=0.7pt] (4.30,0) circle (0.17);
    \node[font=\bfseries\scriptsize,text=timelineyear] at (4.33,-0.36) {2022};
    
    \fill[timelinebubble,draw=white,line width=0.7pt] (7.30,0) circle (0.17);
    \node[font=\bfseries\scriptsize,text=timelineyear] at (7.33,-0.36) {2023};
    
    \fill[timelinebubble,draw=white,line width=0.7pt] (13.90,0) circle (0.17);
    \node[font=\bfseries\scriptsize,text=timelineyear] at (13.80,0.36) {2024};
    
    \fill[timelinebubble,draw=white,line width=0.7pt] (17.50,0) circle (0.17);
    \node[font=\bfseries\scriptsize,text=timelineyear] at (17.50,-0.36) {2025};
    
    \fill[timelinebubble,draw=white,line width=0.7pt] (24.70,0) circle (0.17);
    \node[font=\bfseries\scriptsize,text=timelineyear] at (24.70,-0.36) {2026};

    \draw[timelineblue,line width=2.5pt,-{Stealth[length=2.2mm]}] (1.00,0.05) -- (1.00,0.85);
    \node[align=center,font=\fontsize{6.0}{7.2}\selectfont,text=timelineblue] at (0.9,1.15) {\timelinecite{sermanet2017time}};

    \draw[timelineblue,line width=2.5pt,-{Stealth[length=2.2mm]}] (1.60,0.05) -- (1.60,1.30);
    \node[align=center,font=\fontsize{6.0}{7.2}\selectfont,text=timelineblue] at (1.60,1.62) {\timelinecite{rothfuss2018deep}};

    \draw[timelinebrick,line width=2.5pt,-{Stealth[length=2.2mm]}] (2.20,-0.05) -- (2.20,-0.85);
    \node[align=center,font=\fontsize{6.0}{7.2}\selectfont,text=timelinebrick] at (2.20,-1.15) {\timelinecite{liu2018imitation}};

    \draw[timelineblue,line width=2.5pt,-{Stealth[length=2.2mm]}] (2.80,0.05) -- (2.80,1.75);
    \node[align=center,font=\fontsize{6.0}{7.2}\selectfont,text=timelineblue] at (2.80,2.09) {\timelinecite{schmeckpeper2020reinforcement}};

    \draw[timelinebrick,line width=2.5pt,-{Stealth[length=2.2mm]}] (3.40,-0.05) -- (3.40,-1.30);
    \node[align=center,font=\fontsize{6.0}{7.2}\selectfont,text=timelinebrick] at (3.40,-1.62) {\timelinecite{smith2020avid}};

    \draw[timelinebrick,line width=2.5pt,-{Stealth[length=2.2mm]}] (4.00,-0.05) -- (4.00,-0.85);
    \node[align=center,font=\fontsize{6.0}{7.2}\selectfont,text=timelinebrick] at (4.00,-1.15) {\timelinecite{chen2021learning}};

    \draw[timelineblue,line width=2.5pt,-{Stealth[length=2.2mm]}] (4.60,0.05) -- (4.60,0.85);
    \node[align=center,font=\fontsize{6.0}{7.2}\selectfont,text=timelineblue] at (4.60,1.15) {\timelinecite{nair2022r3m}};

    \draw[timelineblue,line width=2.5pt,-{Stealth[length=2.2mm]}] (5.20,0.05) -- (5.20,1.30);
    \node[align=center,font=\fontsize{6.0}{7.2}\selectfont,text=timelineblue] at (5.20,1.62) {\timelinecite{xiao2022masked}};

    \draw[timelineblue,line width=2.5pt,-{Stealth[length=2.2mm]}] (5.80,0.05) -- (5.80,1.75);
    \node[align=center,font=\fontsize{6.0}{7.2}\selectfont,text=timelineblue] at (5.80,2.09) {\timelinecite{ma2022vip}};

    \draw[timelinebrick,line width=2.5pt,-{Stealth[length=2.2mm]}] (6.40,-0.05) -- (6.40,-1.30);
    \node[align=center,font=\fontsize{6.0}{7.2}\selectfont,text=timelinebrick] at (6.40,-1.62) {\timelinecite{zakka2022xirl}};

    \draw[timelinebrick,line width=2.5pt,-{Stealth[length=2.2mm]}] (7.00,-0.05) -- (7.00,-1.75);
    \node[align=center,font=\fontsize{6.0}{7.2}\selectfont,text=timelinebrick] at (7.00,-2.09) {\timelinecite{xiong2022robotube}};

    \draw[timelineblue,line width=2.5pt,-{Stealth[length=2.2mm]}] (7.60,0.05) -- (7.60,0.85);
    \node[align=center,font=\fontsize{6.0}{7.2}\selectfont,text=timelineblue] at (7.60,1.15) {\timelinecite{ma2023liv}};

    \draw[timelineblue,line width=2.5pt,-{Stealth[length=2.2mm]}] (8.20,0.05) -- (8.20,1.30);
    \node[align=center,font=\fontsize{6.0}{7.2}\selectfont,text=timelineblue] at (8.20,1.62) {\timelinecite{bhateja2023robotic}};

    \draw[timelineblue,line width=2.5pt,-{Stealth[length=2.2mm]}] (8.80,0.05) -- (8.80,1.75);
    \node[align=center,font=\fontsize{6.0}{7.2}\selectfont,text=timelineblue] at (8.5,2.09) {\timelinecite{radosavovic2023real}};

    \draw[timelineblue,line width=2.5pt,-{Stealth[length=2.2mm]}] (9.40,0.05) -- (9.40,2.20);
    \node[align=center,font=\fontsize{6.0}{7.2}\selectfont,text=timelineblue] at (9.40,2.56) {\timelinecite{karamcheti2023language}};

    \draw[timelineblue,line width=2.5pt,-{Stealth[length=2.2mm]}] (10.00,0.05) -- (10.00,0.85);
    \node[align=center,font=\fontsize{6.0}{7.2}\selectfont,text=timelineblue] at (10.00,1.15) {\timelinecite{dasari2023unbiased}};

    \draw[timelineblue,line width=2.5pt,-{Stealth[length=2.2mm]}] (10.60,0.05) -- (10.60,1.30);
    \node[align=center,font=\fontsize{6.0}{7.2}\selectfont,text=timelineblue] at (10.30,1.62) {\timelinecite{majumdar2023we}};

    \draw[timelineblue,line width=2.5pt,-{Stealth[length=2.2mm]}] (11.20,0.05) -- (11.20,1.75);
    \node[align=center,font=\fontsize{6.0}{7.2}\selectfont,text=timelineblue] at (11.20,2.09) {\timelinecite{burns2023makes}};

    \draw[timelineblue,line width=2.5pt,-{Stealth[length=2.2mm]}] (11.80,0.05) -- (11.80,2.20);
    \node[align=center,font=\fontsize{6.0}{7.2}\selectfont,text=timelineblue] at (11.80,2.56) {\timelinecite{wu2023unleashing}};

    \draw[timelinebrick,line width=2.5pt,-{Stealth[length=2.2mm]}] (12.0,-0.05) -- (12.0,-1.30);
    \node[align=center,font=\fontsize{6.0}{7.2}\selectfont,text=timelinebrick] at (12.0,-1.62) {\timelinecite{mendonca2023structured}};

    \draw[timelinebrick,line width=2.5pt,-{Stealth[length=2.2mm]}] (12.8,-0.05) -- (12.8,-0.85);
    \node[align=center,font=\fontsize{6.0}{7.2}\selectfont,text=timelinebrick] at (12.8,-1.15) {\timelinecite{chane2023learning}};

    \draw[timelinebrick,line width=2.5pt,-{Stealth[length=2.2mm]}] (13.60,-0.05) -- (13.60,-1.75);
    \node[align=center,font=\fontsize{6.0}{7.2}\selectfont,text=timelinebrick] at (13.60,-2.09) {\timelinecite{huo2023efficient}};

    \draw[timelineblue,line width=2.5pt,-{Stealth[length=2.2mm]}] (14.20,0.05) -- (14.20,0.85);
    \node[align=center,font=\fontsize{6.0}{7.2}\selectfont,text=timelineblue] at (14.20,1.15) {\timelinecite{jain2024vid2robot}};

    \draw[timelinebrick,line width=2.5pt,-{Stealth[length=2.2mm]}] (14.80,-0.05) -- (14.80,-1.30);
    \node[align=center,font=\fontsize{6.0}{7.2}\selectfont,text=timelinebrick] at (14.80,-1.62) {\timelinecite{qian2024contrast}};

    \draw[timelineblue,line width=2.5pt,-{Stealth[length=2.2mm]}] (15.40,0.05) -- (15.40,1.30);
    \node[align=center,font=\fontsize{6.0}{7.2}\selectfont,text=timelineblue] at (15.40,1.62) {\timelinecite{li2024ag2manip}};

    \draw[timelineblue,line width=2.5pt,-{Stealth[length=2.2mm]}] (16.00,0.05) -- (16.00,1.75);
    \node[align=center,font=\fontsize{6.0}{7.2}\selectfont,text=timelineblue] at (16.00,2.09) {\timelinecite{liu2024masked}};

    \draw[timelineblue,line width=2.5pt,-{Stealth[length=2.2mm]}] (16.60,0.05) -- (16.60,0.85);
    \node[align=center,font=\fontsize{6.0}{7.2}\selectfont,text=timelineblue] at (16.60,1.15) {\timelinecite{zeng2024learning}};

    \draw[timelineblue,line width=2.5pt,-{Stealth[length=2.2mm]}] (17.20,0.05) -- (17.20,2.20);
    \node[align=center,font=\fontsize{6.0}{7.2}\selectfont,text=timelineblue] at (17.20,2.56) {\timelinecite{cheang2024gr}};

    \draw[timelineblue,line width=2.5pt,-{Stealth[length=2.2mm]}] (17.80,0.05) -- (17.80,1.30);
    \node[align=center,font=\fontsize{6.0}{7.2}\selectfont,text=timelineblue] at (17.80,1.62) {\timelinecite{sun2025vtao}};

    \draw[timelineblue,line width=2.5pt,-{Stealth[length=2.2mm]}] (18.40,0.05) -- (18.40,1.75);
    \node[align=center,font=\fontsize{6.0}{7.2}\selectfont,text=timelineblue] at (18.40,2.09) {\timelinecite{shah2025mimicdroid}};

    \draw[timelineblue,line width=2.5pt,-{Stealth[length=2.2mm]}] (19.00,0.05) -- (19.00,2.20);
    \node[align=center,font=\fontsize{6.0}{7.2}\selectfont,text=timelineblue] at (19.00,2.56) {\timelinecite{zhang2025generative}};

    \draw[timelineblue,line width=2.5pt,-{Stealth[length=2.2mm]}] (19.60,0.05) -- (19.60,1.30);
    \node[align=center,font=\fontsize{6.0}{7.2}\selectfont,text=timelineblue] at (19.60,1.62) {\timelinecite{jiang2025rynnvla}};

    \draw[timelineblue,line width=2.5pt,-{Stealth[length=2.2mm]}] (20.20,0.05) -- (20.20,1.75);
    \node[align=center,font=\fontsize{6.0}{7.2}\selectfont,text=timelineblue] at (20.20,2.09) {\timelinecite{pai2025mimic}};

    \draw[timelineblue,line width=2.5pt,-{Stealth[length=2.2mm]}] (20.80,0.05) -- (20.80,0.85);
    \node[align=center,font=\fontsize{6.0}{7.2}\selectfont,text=timelineblue] at (20.80,1.15) {\timelinecite{xiong2025ag2x2}};

    \draw[timelineblue,line width=2.5pt,-{Stealth[length=2.2mm]}] (21.40,0.05) -- (21.40,1.30);
    \node[align=center,font=\fontsize{6.0}{7.2}\selectfont,text=timelineblue] at (21.40,1.62) {\timelinecite{zhou2025mitigating}};

    \draw[timelineblue,line width=2.5pt,-{Stealth[length=2.2mm]}] (22.00,0.05) -- (22.00,1.75);
    \node[align=center,font=\fontsize{6.0}{7.2}\selectfont,text=timelineblue] at (22.00,2.09) {\timelinecite{kedia2025one}};

    \draw[timelineblue,line width=2.5pt,-{Stealth[length=2.2mm]}] (22.60,0.05) -- (22.60,2.20);
    \node[align=center,font=\fontsize{6.0}{7.2}\selectfont,text=timelineblue] at (22.60,2.56) {\timelinecite{punamiya2025egobridge}};

    \draw[timelineblue,line width=2.5pt,-{Stealth[length=2.2mm]}] (23.20,0.05) -- (23.20,1.30);
    \node[align=center,font=\fontsize{6.0}{7.2}\selectfont,text=timelineblue] at (23.20,1.62) {\timelinecite{liu2025immimic}};

    \draw[timelineblue,line width=2.5pt,-{Stealth[length=2.2mm]}] (23.80,0.05) -- (23.80,1.75);
    \node[align=center,font=\fontsize{6.0}{7.2}\selectfont,text=timelineblue] at (23.80,2.09) {\timelinecite{zhu2025learning}};

    \draw[timelinebrick,line width=2.5pt,-{Stealth[length=2.2mm]}] (24.40,-0.05) -- (24.40,-1.30);
    \node[align=center,font=\fontsize{6.0}{7.2}\selectfont,text=timelinebrick] at (24.40,-1.62) {\timelinecite{goswami2025world}};

    \draw[timelineblue,line width=2.5pt,-{Stealth[length=2.2mm]}] (25.00,0.05) -- (25.00,2.20);
    \node[align=center,font=\fontsize{6.0}{7.2}\selectfont,text=timelineblue] at (25.00,2.56) {\timelinecite{ye2026visual}};

    \draw[timelineblue,line width=2.6pt,rounded corners=1pt] (0.10,-2.03) -- (0.78,-2.03);
    \node[anchor=west,font=\bfseries\footnotesize,text=timelineblue] at (0.92,-2.03) {Visual pretraining};

    \draw[timelinebrick,line width=2.6pt,rounded corners=1pt] (0.10,-2.38) -- (0.78,-2.38);
    \node[anchor=west,font=\bfseries\footnotesize,text=timelinebrick] at (0.92,-2.38) {Visual guidance};

  \end{tikzpicture}%
  }
  \caption{按时间顺序概述了 \textit{视觉嵌入作为桥梁} 下的方法。~\ref{sec:visual_embeddings}。}
  \label{fig:visual_embeddings_timeline}
\end{figure*}





\begin{figure*}[t]
  \centering
  \includegraphics[width=0.95\linewidth]{figs/visual_embeddings_transfer.pdf}
  \caption{\textit{视觉嵌入作为桥梁} 的高级图。插图的某些元素改编自 \cite{nair2022r3m,xiao2022masked,zhu2025learning,punamiya2025egobridge,chen2021learning}。}
  \label{fig:visual_embeddings_transfer}
\end{figure*}

\subsubsection{视觉嵌入} \label{sec:visual_embeddings}
为了避免转换视频引入的显式生成伪影，越来越多的研究重点关注将人类视频压缩为视觉嵌入。这些嵌入可用于预训练下游机器人策略的感知模型或构建指导机器人探索的视觉信号。因此，我们将 \textit{视觉嵌入作为桥梁} 分为两个渐进类别：\textit{视觉预训练} 和 \textit{视觉指导}。相关工作的时间线如图~\ref{fig:visual_embeddings_timeline}所示。

\textit{(1) 视觉预训练:} Temporal contrastive learning (TCL) is one of the most commonly used strategies for pretraining perception models in the temporal dimension. In the early stage, \cite{sermanet2017time} propose the pioneering framework that employs the TCL pipeline on human videos. They treat visual embeddings of temporally distinct frames from the same sequence as negative samples, leading to viewpoint-invariant visual representations for downstream robot learning. However, this negative-sample construction may fragment the semantic continuity of human-object interactions, making it less suitable for learning single-view robot policies. Instead, the following works~\citep{nair2022r3m,ma2022vip,ma2023liv} pull visual embeddings from adjacent frames closer while pushing apart embeddings from frames that are farther apart along the time axis, as illustrated in Fig.~\ref{fig:visual_embeddings_transfer}(a). Thus, the perception models can learn from human videos how visual states transit through the fine-grained progress of temporal interactions. For example, R3M~\citep{nair2022r3m} achieves this TCL pipeline on the large-scale Ego4D dataset~\citep{grauman2022ego4d} together with video-language alignment and feature sparsity regularization. It produces a reusable frozen visual encoder to generate visual embeddings for robotic manipulation. Owing to its strong generalization across tasks and environments, R3M has inspired multiple foundational perception models in the subsequent robot learning policies~\citep{shaw2023videodex,mendonca2023structured,li2024ag2manip,xiong2025ag2x2}. Compared to R3M which additionally requires video textual descriptions to align its representation, VIP~\citep{ma2022vip} is developed as a fully self-supervised learning paradigm. It further models temporal reachability between visual embeddings through a value-implicit objective. LIV~\citep{ma2023liv} extends the VIP paradigm~\citep{ma2022vip} to multimodal value function learning, simultaneously supporting both language goals and image goals. 
\cite{bhateja2023robotic} further evolve the TCL paradigm of VIP~\citep{ma2022vip} into a temporal-difference learning (TDL) framework, yielding an intent-conditioned value function (ICVF). By modeling the reachability from the current state to a variety of future goal states, the learned value function captures scene dynamics as a transferable visual representation. To capture embodiment-agnostic visual embeddings during pretraining, \cite{li2024ag2manip} and \cite{xiong2025ag2x2} both utilize inpainted human videos to achieve temporal contrastive learning, encouraging the encoder to focus on interaction-relevant scene dynamics rather than embodiment-specific appearance cues.

可以注意到，时间对比学习致力于限制时间维度中的视觉嵌入。相比之下，掩模预训练（MP）范式侧重于空间维度上的图像重建任务（见图~\ref{fig:visual_embeddings_transfer}（b））来预训练视觉编码器。该范式的相关工作实质上受到了屏蔽自动编码器优化原理的启发~\citep{he2022masked}。例如，\cite{xiao2022masked} 提出 MVP，通过在大规模人类视频上使用掩模图像重建来预训练视觉编码器，从而构建 MP 范式的基础。他们冻结这些编码器用于下游电机控制，证明仅空间屏蔽预训练就可以为机器人学习产生可转移的视觉表示。 \cite{radosavovic2023real}通过缩放预训练人类视频数据和模型大小进一步扩展了MVP~\citep{xiao2022masked}，并将其下游应用扩展到现实世界机器人操作的大规模模仿学习。通过仔细重现 MVP~\citep{xiao2022masked} 和 R3M~\citep{nair2022r3m}，\cite{karamcheti2023language} 证明，将 R3M 等语言监督引入 MVP 的屏蔽预训练范式可以弥补语义限制，同时保留用于视觉嵌入生成的强大空间建模能力。与 \cite{karamcheti2023language} 使用语言模态辅助视觉模态相比，\cite{liu2024masked} 的 M$2$VTP 在重建机制中结合了触觉信号，以实现互补的交互线索。它旨在解决视力被遮挡或难以视觉感知精细局部几何形状的情况。 VTAO-BiManip~\citep{sun2025vtao}在M$2$VTP~\citep{liu2024masked}的基础上进一步引入了手部动作和以对象为中心的理解。它将 M$2$VTP 的屏蔽预训练从视觉-触觉框架扩展到视觉-触觉-动作框架。最近，\cite{ye2026visual} 将重点从对象理解转移到捕获更深层次的类人操作模式。他们受到人脑顶下小叶 (IPL) 神经元的启发，提出了一种 IPL 令牌，用于在掩蔽预训练过程中通过 Transformer 编码器 ~\citep{vaswani2017attention} 进行多感觉整合。考虑到集成的表示，他们通过强化学习为不同任务的专家策略训练多任务动作策略，并通过在线模仿学习将这些专家提炼成统一的策略。
与上述通过图像重建来优化感知模型的MP范式相比，MimicDroid~\citep{shah2025mimicdroid}直接使用掩模图像作为手部预测预训练的输入。它隐式地减少了对人类特定视觉线索的过度拟合，并鼓励模型专注于环境和对象交互。

在 TCL 和 MP 范式的基础上，一些研究人员进一步深入研究了哪些类型的现有模型架构和预训练数据可以为下游机器人操作产生更有效的视觉嵌入。例如，\cite{majumdar2023we} 将注意力转向发现哪种视觉预训练范例最有效。他们系统地对 TCL 和 MP 方法进行了基准测试，以表明没有单一模型能够在所有机器人任务中普遍占主导地位。他们进一步使用 MAE 训练多个不同尺度的 ViT 模型 ~\citep{dosovitskiy2020image}，并最终获得 VC-1，这是一种平均优于现有预训练方法的统一视觉编码器。 \cite{dasari2023unbiased} 进一步将问题从使用哪种视觉预训练转向使用哪种数据。他们展示了数据集的图像分布比下游视觉运动学习的规模更重要。他们还观察到，即使是 ImageNet~\citep{deng2009imagenet}、Kinetics~\citep{smaira2020short} 和 100DOH~\citep{shan2020understanding} 等传统视觉数据集对于机器人视觉预训练也具有惊人的竞争力。
与\cite{dasari2023unbiased}和\cite{majumdar2023we}相比，\cite{burns2023makes}专门关注视觉泛化能力并推进预测泛化的指标。他们确定了强泛化的秘诀：具有高紧急分割精度的 ViT 模型往往会在视觉分布变化下生成更泛化的视觉嵌入。此外，与许多其他鲁棒性指标相比，新兴分割精度是更强的泛化预测指标，且无需额外的训练过程。


值得注意的是，TCL 范式通过在时间维度上强制执行相似关系来捕获视觉表示，但它不一定要求编码器对人与物体交互背后的更深层次的物理机制进行建模。 MP 范式强调通过重建来理解空间，但大多数重建目标可以从单帧内的静态纹理和外观线索中恢复，而无需推理潜在的交互动态。这些限制激发了另一项工作，即通过人类视频预测（HVP）学习视觉嵌入，如图〜\ref{fig:visual_embeddings_transfer}（c）所示。通过从过去的交互中预测未来的观察结果，此类方法鼓励视觉编码器不仅捕获时空规律，而且捕获与下游机器人操作更直接相关的物理动力学的因果关系。
HVP 范式与最近文献中的 \textit{世界模型} 的概念密切相关，因为世界模型从根本上关注预测未来的观察如何从过去的相互作用和与动作相关的动态演化~\citep{liao2025genie,ye2026world}。值得注意的是，在这里我们只回顾那些明确使用人类视频进行视觉预训练的作品。
\cite{rothfuss2018deep} 的早期工作通过预测未来的人类视频帧来预训练视觉编码器，并使用由此产生的视觉嵌入从情景记忆中检索最相似的人类演示片段。然后使用检索到的演示来提取低级机器人动作的对象运动。然而，预测的帧通常在视觉上是模糊的，这可能会限制学习的视觉表示的质量，从而损害视觉预训练的有效性。相比之下，\cite{zeng2024learning} 通过仅预测过渡帧和最终帧来避免长视野视频生成。通过强调关键的交互状态，他们的 MPI 框架鼓励视觉编码器学习操纵的核心因果结构和状态演化。他们凭经验验证 MPI 在视觉预训练方面优于几种流行的 TCL 和 MP 范例 ~\citep{nair2022r3m,xiao2022masked,karamcheti2023language}。受益于生成技术的发展和模型容量的扩展，最近的工作重新审视了连续视频剪辑的直接预测，作为视觉预训练的更丰富的监督信号。例如，GVF-TAPE~\citep{zhang2025generative} 使用人类视频作为补充数据来预训练基于整流流~\citep{liu2022flow} 的端到端视频预测模型。
与仅执行特定于实施例的视频预测的GVF-TAPE~\citep{zhang2025generative}相比，\cite{zhu2025learning}进一步引入了用于跨实施例预测的交叉预测视频生成。也就是说，它们致力于根据人类图像预测机器人视频以及根据机器人图像预测人类视频。因此，学习到的视觉嵌入成为用于跨实施例捕获任务语义和环境上下文的更统一的表示。最近，研究人员还发现，将人类视频预测范式集成到 VLA 模型中可以通过预测未来事件来促进生成更相关和更合适的动作。以\cite{wu2023unleashing}为例，GR-1将大规模视频生成预训练集成到GPT式VLA中，以端到端的方式预测未来图像和机器人动作，从而提高动作生成性能。与GR-1~\citep{wu2023unleashing}（从80万到3800万）相比，GR-2~\citep{cheang2024gr}将人类视频生成预训练数据量进一步扩展了近50倍，从而在各种未见过的场景中具有更强的泛化能力。为了弥合纯人类视频预测和动作生成之间的差距，RynnVLA-001~\citep{jiang2025rynnvla} 提出了一个中间阶段，其中结合了手腕轨迹预测，以学习视觉变化与其潜在人体运动之间的关联。 imit-video~\citep{pai2025mimic} 不是从头开始训练视频预测模型，而是直接使用 Cosmos-Predict2~\citep{agarwal2025cosmos,ali2025world} 作为视频生成骨干，并在其视觉表示上调节流匹配动作解码器。


尽管 HVP 范式通过使用人类视频预测目标预训练视觉编码器来关注物理维度，但最终的视觉嵌入仍然编码人类交互行为而不是机器人交互状态。这不可避免地会导致潜在的形态差距，因为在视觉预训练过程中只有人类数据可用~\citep{mower2026robot}。为了进一步缓解实施维度中的这个问题，一些工作将机器人数据集成到人类视频的视觉预训练过程中。如图~\ref{fig:visual_embeddings_transfer}(d)所示，该范例实现了联合域适应（JDA），使语义相似的人类和机器人观察的视觉嵌入在共享表示空间中更紧密地结合在一起。因此，预训练的视觉编码器更适合在下游机器人任务中生成视觉嵌入。 \cite{schmeckpeper2020reinforcement} 提出对抗性域混淆来学习域不变编码器，将人类视频帧和机器人观察映射到共享特征空间。他们进一步表明，少量配对的人类机器人数据有助于锚定跨实施例的视觉嵌入对齐。随后的 JDA 工作通常侧重于直接减少人类视频的视觉嵌入和机器人观察之间的距离。例如，Vid2Robot~\citep{jain2024vid2robot} 引入了基于时间周期一致性的视频对齐损失，鼓励视觉编码器生成对实施例和环境因素不变的视觉嵌入。 \cite{kedia2025one} 还根据配对的人类和机器人片段之间的最佳传输距离，通过将匹配的视觉嵌入拉得更近来学习共享视觉编码器。为了进一步减轻不同实施例的时间不一致和运动学变化的问题，\cite{punamiya2025egobridge}引入动态时间扭曲(DTW)~\citep{sakoe1978dynamic}以实现视觉表示对齐的最佳传输。与\cite{punamiya2025egobridge}类似，\cite{liu2025immimic}也使用DTW来配对每个人类时间步
根据视觉嵌入的最佳匹配机器人时间步长。他们还应用 MixUp~\citep{zhang2017mixup} 为后续协同训练过程生成插值人体数据。 \cite{zhou2025mitigating} 进一步让任务描述功能与人类和机器人视频的视觉嵌入交互，并实现跨实施例的任务感知对比学习。

\textit{(b) 视觉引导:} As shown in Fig.~\ref{fig:visual_embeddings_transfer}(e), another line of research shifts the focus from vision encoder pretraining to how visual embeddings derived from human videos can directly construct reward or cost functions that guide robot interaction with the environment. Encoders obtained through \textit{visual pretraining} can often be directly reused within the \textit{visual guidance} paradigm. \cite{liu2018imitation} formulate the reinforcement learning objective by penalizing the squared Euclidean distance between the robot's current visual embedding and the demonstration embedding translated from human videos. Similarly, XIRL~\citep{zakka2022xirl} defines the reinforcement learning reward as the negative distance to the goal state in the learned visual embedding space. A related one-shot setting is explored by~\cite{huo2023efficient}, who extract a state alignment-based reward from a single observation-only demonstration video and combine it with sampling-based MPC for efficient policy optimization in contact-rich fabric manipulation. RoboTube~\citep{xiong2022robotube} complements the visual guidance paradigm by providing a curated human video dataset together with RT-sim, a suite of simulated twin environments that closely match the appearance and dynamics of the real scenes. It enables visual guidance learned from human videos to be benchmarked reproducibly in simulation and more reliably transferred to real robots. \cite{qian2024contrast} further parse visual embeddings into interaction-aware temporal relations through IAAFormer. The alignment distance reflects the cross-embodiment task process at the sequence level. It provides more structured visual guidance for downstream robot adaptation. \cite{mendonca2023structured} further learn an affordance-grounded latent space from human videos, where distances between latent states can also serve as planning-oriented visual guidance. Rather than relying only on instantaneous visual embedding similarity for reward design, it models how these affordance-centric visual states evolve under actions through a world model, enabling more effective downstream control. \cite{goswami2025world} also follow the world model scheme and propose DexWM, a dexterous world model trained on large-scale human videos. At test time, DexWM performs goal-conditioned MPC using a planning cost defined by the visual state distance and hand-keypoint pixel differences.

与这些使用特征距离作为视觉引导的方法相比，\cite{smith2020avid} 进一步将视觉嵌入转换为二元分类器，用于确定输入图像是否与指定目标图像匹配，以利用输出对数概率构建奖励函数。与 \cite{smith2020avid} 类似，\cite{chen2021learning} 开发了 DVD，它在视觉嵌入之上学习二元分类器，以量化任务方面的功能相似性作为奖励。与仅考虑域内数据的 \cite{smith2020avid} 相比，他们明确专注于利用野外人类视频和适度的机器人演示来提高奖励函数的通用性。 \cite{chane2023learning} 遵循 DVD 模型~\citep{chen2021learning} 构建奖励函数，但在没有任何带注释的机器人视频的情况下学习功能相似性。

\textit{(c) 视觉嵌入小结:} \textit{Visual embeddings as a bridge} avoid the explicit inpainting and rendering errors of transformed videos by mapping human observations into latent representations that are more readily transferable to robot learning. Existing methods have mainly developed along two complementary directions. Visual pretraining learns reusable perception models from human videos through temporal contrastive learning, masked pretraining, human video prediction, and joint domain adaptation. Visual guidance further uses visual embeddings to define reward and cost for downstream robot interaction. Compared with transformed videos, this bridging mechanism is generally more compact and robust to appearance gaps across embodiments. However, whether the learned representations preserve task-relevant interaction dynamics and cross-embodiment consistency sufficiently to support reliable downstream action planning remains largely implicit.

\subsubsection{观测导向迁移小结}

面向观察的迁移解决了 LfHV 中最基本的挑战之一，即如何减少人类视频和机器人观察之间的感知差距。与通过高级任务语义桥接实施例的面向任务的迁移相比，该类别的操作更接近视觉运动界面。因此，它在确定机器人是否能够以与下游控制兼容的方式解释人类演示方面发挥着更直接的作用。从这个角度来看，\textit{将视频转换为桥梁} 和 \textit{视觉嵌入作为桥梁} 代表了同一问题的两种互补解决方案。前者明确地将人类观察结果修改为与实施例无关或与机器人一致的视觉格式，使传输的信息更加直观和直接可用。相反，后者将人类观察压缩到共享的潜在空间中，牺牲视觉的明确性来换取更大的紧凑性、鲁棒性和灵活性。它们的差异本质上反映了 \textit{显式感知对齐} 和 \textit{隐式表示对齐} 之间的权衡。转换后的视频提供了更具可解释性的桥梁，而视觉嵌入则提供了更具可扩展性和通用性的界面。

这一类别的一个明显趋势是从外观级别对齐转向更深入的交互动态和跨实体一致性建模。早期的工作主要集中在抑制特定于实施例的外观线索或从人类视频中学习通用视觉特征。最近的方法越来越多地结合时间预测、人机联合对齐和世界模型目标。这种演变表明，有效的观察转移需要匹配视觉外观，同时还捕获交互如何随着时间的推移在实施例中展开。有鉴于此，面向观察的迁移的核心挑战在于保留与动作相关的动态，同时消除特定于实施例的干扰因素。因此，未来的进展可能取决于转换后的视频和视觉嵌入之间更紧密的集成。它还可能需要与面向动作的传输更强的耦合，以便感知对齐可以更好地支持可执行且具有物理意义的机器人行为。





\subsection{动作导向迁移}

与面向任务的传输和面向观察的传输相比，面向动作的传输在动作规划层面更直接地连接人类视频和机器人执行。它致力于从人类视频中提取与动作相关的信息，例如交互可供性和潜在动作，然后将它们转移到机器人策略中作为可执行指导。因此，我们将这一类别组织成两种形式的信息流：\textit{作为桥梁} 的可供性，它从人类演示视频中暴露显式的几何动作线索，而 \textit{潜在动作作为桥梁}，它将观察到的人类行为压缩为可转移的动作抽象，以供下游机器人策略学习。

\begin{figure*}[t]
  \centering
  \includegraphics[width=1\linewidth]{figs/hoi_affordances.pdf}
  \caption{HOI 分析技术和从人类视频中提取可供性的插图。部分图像取自\cite{zhang2020mediapipe,labbe2022megapose,sivakumar2022robotic,qin2022dexmv,cheng2023towards,wen2023bundlesdf,wang2023mimicplay,kumar2023graph,bahl2023affordances,wen2023any,karaev2024cotracker,bahety2024screwmimic,kerr2024robot,zhang2025hawor,xiao2025spatialtrackerv2,chen2025visa,hsieh2025dexman,hsu2025spot,chen2025web2grasp,zhou2025you,cong2025dytact,wang2026paws}。}
  \label{fig:hoi_affordances}
\end{figure*}

\subsubsection{可供性} \label{sec:affordances}
\textit{可供性作为桥梁} are more directly grounded in action compared with task instructions and visual embeddings. As introduced by \cite{bahl2023affordances}, affordances from human videos explicitly specify \textit{where} and \textit{how} the hand-object interaction (HOI) should occur. That is, when manipulating an object, affordances explicitly indicate where on the object to make contact, and how to make this contact~\citep{kannan2023deft}. Therefore, in this survey, we broadly instantiate \textit{affordances} as all possible interaction-related geometric and functional signals that can be extracted from human videos, including 2D/3D hand\&object positions (e.g., trajectories, motion flow, contact/separation regions), 6D hand\&object poses (e.g., grasping poses, sequential rigid transformations), hand\&object geometric representations (e.g., meshes, point clouds, hand parametric representations), and physical object functionality (e.g., 4D object parts, articulations, functional keypoints). We will detail how these affordances facilitate action-oriented transfer in the following sections.



\textit{(a) 人-物交互分析:} Hand-object interactions in human videos fundamentally facilitate affordance extraction. Therefore, before delving into specific affordance-based bridging mechanisms, we first review how existing works analyze hand-object interactions to recover action-relevant cues from human videos.

首先，我们介绍在2D空间中广泛使用的HOI检测方法，如图~\ref{fig:hoi_affordances}(a)-(b)所示。 \cite{shan2020understanding} 通过从互联网人体视频中联合推断 2D 手部位置、手部侧面、接触状态以及接触物体的边界框，建立检测范式。他们预先训练的 HOI 检测器随后成为在后续各种 LfHV 作品 ~\citep{bahl2022human,bahl2023affordances,wang2023mimicplay,kumar2023graph,mendonca2023structured,srirama2024hrp,ju2024robo,jonnavittula2025view,lu2025visual} 中提取手部接触线索的实用基础。在这种 2D 手部接触分析的基础上，\cite{goyal2022human} 进一步将人手视为交互式对象理解的探针。通过利用以自我为中心的人类视频中的手部外观和动作，他们以交互区域和提供的抓握的形式学习对象可供性。这将重点从接触检测转移到下游机器人策略学习的更丰富的 2D 可供性发现。其颜色抖动和裁剪等增强策略也启发了后续的 LfHV 作品，例如 2HandedAfforder~\citep{heidinger20252handedafforder}。 \cite{cheng2023towards}进一步将HOI分析扩展到更丰富的接触词汇，区分触摸、握持和使用。它也被用作多个 LfHV 作品中的现成分段器~\citep{heppert2024ditto,shan2025slot,wang2026paws}。 GLIP~\citep{li2022grounded}、GroundingDINO~\citep{liu2024grounding}、YOLO系列~\citep{Ultralytics2023,khanam2024yolov5,sohan2024review,cheng2024yolo}和SAM系列~\cite{kirillov2023segment,zhang2023faster,ren2024grounded,ravi2024sam,carion2025sam}等视觉基础模型也被LfHV作品广泛使用，以可推广的方式从人类视频中提取手部物体边界框和分割掩模~\citep{xu2024flow,wang2024vlm,ma2025madiff,yoshida2025developing,ma2025uni,ma2025egoloc,li2025h2r,chen2025visa,hsu2025spot,xiong2025ag2x2}。

除了上述2D HOI区域提取之外，2D点跟踪方法也成为基于可供性的桥接机制中的重要技术组成部分。它们主要用于生成物体运动流并进一步恢复刚性变换。例如，CoTracker 系列~\citep{karaev2024cotracker,karaev2025cotracker3} 联合跟踪视频帧中的大量查询点，即使在遮挡情况下，也能在长视频范围内产生时间一致的密集轨迹。这使得它们对 LfHV 研究特别有吸引力~\citep{bharadhwaj2024track2act,li2024okami,yuan2024general,werby2025articulated,chen2025visa,hsu2025spot,guzey2025bridging,chen2025graphmimic,haldar2025point,liu2025egozero,ci2025h2r,tang2025functo,guzey2025dexterity,shi2026care}，因为以自我为中心的人类视频本质上涉及手和被操纵物体之间频繁的相互遮挡。 TAPIR~\citep{doersch2023tapir} 及其增强版本~\citep{doersch2024bootstap} 通过通过时间细化的每帧匹配来跟踪任意查询点，提供类似的通用替代方案。它们保持时间相干轨迹的能力也使它们非常适合在一些 LfHV 作品 ~\citep{xu2024flow,papagiannis2025r,chen2025graphmimic,spiridonov2025generalist} 中估计人类演示中的手部物体运动流。 LocoTrack~\citep{cho2024local}也是一种有前途的2D点跟踪方法，它结合了双向对应、匹配平滑性和紧凑的时间聚合。因此，它对机器人从人类视频中学习的重复纹理和同质区域具有坚实的鲁棒性~\citep{hu2025learning}。


由于人与物体的交互基本上发生在 3D 现实世界环境中，因此仅 2D HOI 分析通常不足以充分表征潜在的交互。因此，我们回顾了用于 3D 手部对象重建和姿势估计的流行 HOI 分析工作。我们从 LfHV 文献中广泛使用且有前途的 3D 人手检测和重建算法开始，如图〜\ref{fig:hoi_affordances}（c）-（d）所示。
作为野外 3D 手部检测的开创性工作，MediaPipe~\citep{zhang2020mediapipe} 强调通过手掌检测和地标回归从单目 RGB 进行轻量级实时 3D 手部地标（关键点）估计。它的效率使其在 LfHV 中很受欢迎，用于从不受约束的人类视频中提取可扩展的以手为中心的可供性~\citep{arunachalam2022dexterous,qin2022one,gao2023k,gu2023rt,zhou2025human,lu2025visual,haldar2025point}。除了 MediaPipe 的手部标志提取之外，FrankMocap~\citep{rong2020frankmocap} 还根据单眼 RGB 估计 3D 手部和身体运动，并将它们集成到统一的参数表示中以生成手部网格结构。它提供了一种实用工具，用于从人类视频中恢复 3D 手部运动线索，作为 LfHV 文献 ~\citep{patel2022learning,mandikal2022dexvip,sivakumar2022robotic,kannan2023deft,srirama2024hrp,bahety2024screwmimic,chen2024vlmimic,chen2025fmimic} 中的可供性。 HaMeR~\citep{pavlakos2024reconstructing} 通过完全基于 Transformer 的架构进一步致力于更高保真度的单目 3D 手部网格恢复。它通过扩大模型架构和数据消耗，显着提高了野外手部重建和姿势估计的鲁棒性和准确性。这使得它更适合需要更丰富的几何信息或高质量的手部姿势作为可见性的 LfHV 设置，而不是单独的稀疏地标 ~\citep{li2024okami,shi2025zeromimic,papagiannis2025r,lum2025crossing,liu2025egozero,hsieh2025dexman,luo2025being,guzey2025dexterity,chen2026dexterous}。为了解决 HaMeR 端到端回归固有的未对准和不正确姿势问题，WiLoR~\citep{potamias2025wilor} 引入了一个额外的细化层，该层使用网格对齐的多尺度特征来变形手部姿势。它支持高效的多手重建和平滑的单目视频跟踪，这对于从人类视频中进行大规模可供性提取很有用~\citep{zhou2025you,yuan2025hermes,zhu2025learning,shah2025mimicdroid}。 HaMeR 和 WiLoR 主要恢复相机帧中的手部几何形状，而 HaWoR~\citep{zhang2025hawor} 进一步针对从自我中心视频中重建世界空间手部运动。它将相机空间手恢复与世界空间相机轨迹估计分离，并进一步引入了视野外帧的运动填充。因此，它产生了时间连贯的全局手部轨迹，更直接地适用于现代 LfHV~\citep{li2025scalable,luo2026being,luo2026joint,feng2025spatial,yang2026aoe} 中的动作导向迁移。最近，EgoHandICL~\citep{xie2026egohandicl} 通过引入 VLM 引导的样本检索的上下文学习，成为一种有前途的手部重建方法，这提高了在具有挑战性的以自我为中心的 HOI 条件下的语义对齐和鲁棒性。此外，SAM 3D Body (3DB)~\citep{yang2026sam} 将这条路线从以手为中心的重建延伸到快速的全身网格恢复，联合估计身体、脚和手，具有很强的野外泛化能力。因此，它为未来的 LfHV 作品提供了更丰富的全身可供性线索。 \cite{ma2025uni} 的扩展工作尝试将 3DB 集成到面向操作的传输范式中，该范式已在其存储库中开源。

接下来，我们介绍LfHV文献中代表性的物体重建和姿态估计方法，如图~\ref{fig:hoi_affordances}(e)-(f)所示。一般来说，获得可靠的物体重建是准确的物体姿态估计的先决条件。 BundleSDF~\citep{wen2023bundlesdf} 是针对人类视频中出现的被操纵对象的最基本的对象重建方法之一。它将神经对象场与姿态图优化结合起来。当部署在使用质量高度可变的人类视频的 LfHV 作品 ~\citep{chen2024vlmimic,patel2025robotic,hsu2025spot} 上时，这增强了其在姿势变化、遮挡、无纹理表面和镜面高光方面的稳定性。之后，更多的重建方法，如InstantMesh~\citep{xu2024instantmesh}、MesyAI~\citep{meshyai}和TRELLIS~\citep{xiang2025structured}，只需要单个图像即可直接为目标人体视频帧~\citep{chen2025web2grasp,ye2025video2policy,hsieh2025dexman,soraki2026objectforesight,chen2026dexterous}内的遮罩对象区域生成对象网格。它们消除了连续扫描的需要，显着提高了特定任务对象重建的效率。

可以基于重建的对象进一步执行对象姿态估计。给定 CAD 模型和感兴趣区域，MegaPose~\citep{labbe2022megapose} 可以直接应用于 LfHV 作品~\citep{liang2024dreamitate,patel2025robotic}，以从粗到细的方式估计新物体的姿态，而无需重新训练。在过去的两年里，FoundationPose~\citep{wen2024foundationpose} 已成为一种更流行的物体姿态估计方法，因为它将基于模型和无模型的新颖物体姿态估计和跟踪统一在一个框架内。与 MegaPose 相比，它进一步利用神经隐式表示进行新颖视图合成以及大规模合成训练，在具有挑战性的 LfHV 设置中实现更强的泛化和更鲁棒的姿势跟踪〜\citep{chen2024vlmimic,yuan2025hermes,hsieh2025dexman,mao2025robot,lum2025crossing,hsu2025spot,patel2025robotic,soraki2026objectforesight,fan2026robopaint,zou2026activeglasses}。最近，Any6D~\citep{lee2025any6d} 还放松了对重建 CAD 模型的依赖，并引入了全面到部分匹配策略。它通过改编自 FoundationPose~\citep{wen2024foundationpose} 的渲染和比较程序联合对齐 2D 外观、3D 几何和公制比例。这为物体尺度和姿态估计提供了一种有前途的替代方案~\citep{hsieh2025dexman}，特别是当难以获得高质量物体重建时。



为了实现更通用的无模型 6D 物体姿态估计，一些研究人员〜\citep{bharadhwaj2024track2act,zhu2024vision,haldar2025point,liu2025egozero,tang2025functo} 手动将上述 2D 点跟踪提升到具有深度信息或立体三角测量的 3D 空间，然后根据所得的 3D 物体流计算刚性变换。尽管如此，还是有现成的 3D 点跟踪方法可用于直接生成用于姿态估计的 3D 对象流。如图~\ref{fig:hoi_affordances}(g)所示，SpatialTracker~\citep{xiao2024spatialtracker}和SpatialTrackerV2~\citep{xiao2025spatialtrackerv2}将视频深度估计集成到统一的基于Transformer的跟踪框架中，从而能够从人类视频~\citep{hsieh2025dexman,yoshida2025generating,yoshida2025developing}直接预测时间一致的3D点轨迹。

如图~\ref{fig:hoi_affordances}(h)-(i)所示，HOI分析的注意力最近开始从静态3D检测和重建转向4D可供性提取，其中时间演化与空间结构一起建模。例如，4D 对象重建从人类交互视频中恢复对象或部件随时间的运动，例如以部件为中心的轨迹和关节状态~\citep{kerr2024robot,wang2026paws}。此外，4D接触演化重建估计了手部物体接触区域在操作过程中如何随时间变化~\citep{cong2025dytact}。通过整合时间信息，这些 4D 表示提供了比静态姿势或接触区域更丰富的可供性线索，使它们成为从人类视频中提取物理基础和执行可行的可供性的有前途的方向。


值得注意的是，现成的 HOI 分析技术的广泛生态系统已经出现，支持从人类视频中有效提取可供性。特别是，包括 HOI 检测和点跟踪在内的 2D 方法提供了可扩展且强大的工具，用于在遮挡等挑战性条件下识别交互区域并估计对象运动流。作为补充，3D 重建和姿势估计方法进一步将这些交互线索提升为基于空间的表示，从而能够恢复手部运动学、物体几何形状和刚性变换。新兴的 4D 重建进一步共同丰富了可供性中的时间信息和物理约束。这些即插即用的 2D、3D 和 4D HOI 分析方法共同构成了实用的技术基础，可有效提取从人类视频到机器人策略的面向行动的传输中的可供性。与本次调查的范围一致，我们不会审查基于动作捕捉设备的 HOI 分析方案，因为我们的重点是从人类视频传输而不是仪器化捕捉设置。

考虑到 HOI 分析的可供性，如图~\ref{fig:affordances_transfer} 所示，我们根据它们与机器人动作的耦合程度来组织基于可供性的桥接机制，范围从主干优化、奖励塑造、策略调节到直接策略构建。收集作品的时间线见图~\ref{fig:affordances_timeline}。


\begin{figure}[t]
  \centering
  \includegraphics[width=1\linewidth]{figs/affordances_transfer_vertical.pdf}
  \caption{\textit{作为桥梁} 的高级图表。}
  \label{fig:affordances_transfer}
\end{figure}


\begin{figure*}[t]
  \centering
  \resizebox{\linewidth}{!}{%
  \begin{tikzpicture}[x=1cm,y=1cm,>=Stealth]
    \definecolor{timelineblue}{RGB}{120,138,150}
    \definecolor{timelinebrick}{RGB}{171,128,120}
    \definecolor{timelinegold}{RGB}{181,156,104}
    \definecolor{timelineplum}{RGB}{145,129,149}
    \definecolor{timelinegray}{RGB}{218,220,221}
    \definecolor{timelineyear}{RGB}{118,116,112}
    \definecolor{timelinebubble}{RGB}{166,206,227}

    \newcommand{\TopEvent}[4]{%
      \pgfmathsetmacro{\starty}{(#3 > 0) ? 0.06 : -0.06}
      \pgfmathsetmacro{\labely}{#3 + ((#3 > 0) ? 0.62 : -0.62)}
      \draw[#2,line width=2.15pt,-{Stealth[length=2.0mm]}] (#1,\starty) -- (#1,#3);
      \node[align=center,font=\fontsize{10.8}{12.0}\selectfont,text=#2,fill=white,fill opacity=0.96,text opacity=1,inner sep=1.0pt,rounded corners=1pt]
在 (#1,\labely) {\timelinecite{#4}};
    }
    \newcommand{\MidEvent}[4]{%
      \pgfmathsetmacro{\starty}{(#3 > -8.40) ? -8.34 : -8.46}
      \pgfmathsetmacro{\labely}{#3 + ((#3 > -8.40) ? 0.62 : -0.62)}
      \draw[#2,line width=2.15pt,-{Stealth[length=2.0mm]}] (#1,\starty) -- (#1,#3);
      \node[align=center,font=\fontsize{10.8}{12.0}\selectfont,text=#2,fill=white,fill opacity=0.96,text opacity=1,inner sep=1.0pt,rounded corners=1pt]
在 (#1,\labely) {\timelinecite{#4}};
    }
    \newcommand{\BotEvent}[4]{%
      \pgfmathsetmacro{\starty}{(#3 > -16.80) ? -16.74 : -16.86}
      \pgfmathsetmacro{\labely}{#3 + ((#3 > -16.80) ? 0.62 : -0.62)}
      \draw[#2,line width=2.15pt,-{Stealth[length=2.0mm]}] (#1,\starty) -- (#1,#3);
      \node[align=center,font=\fontsize{10.8}{12.0}\selectfont,text=#2,fill=white,fill opacity=0.96,text opacity=1,inner sep=1.0pt,rounded corners=1pt]
在 (#1,\labely) {\timelinecite{#4}};
    }


    \draw[timelinegray,line width=4.2pt,-{Stealth[length=3.6mm]}] (-0.10,0) -- (29.60,0);
    \draw[timelinegray,line width=4.2pt] (29.60,0) -- (29.60,-8.40);
    \draw[timelinegray,line width=4.2pt,{Stealth[length=3.6mm]}-] (-0.10,-8.40) -- (29.60,-8.40);
    \draw[timelinegray,line width=4.2pt] (-0.10,-8.40) -- (-0.10,-16.80);
    \draw[timelinegray,line width=4.2pt,-{Stealth[length=3.6mm]}] (-0.10,-16.80) -- (29.60,-16.80);

    \fill[timelinebubble,draw=white,line width=0.8pt] (0.48,0) circle (0.20);
    \node[font=\bfseries\fontsize{9.8}{10.8}\selectfont,text=timelineyear] at (0.48,-0.60) {2017};

    \fill[timelinebubble,draw=white,line width=0.8pt] (1.35,0) circle (0.20);
    \node[font=\bfseries\fontsize{9.8}{10.8}\selectfont,text=timelineyear] at (1.3,-0.60) {2020};

    \fill[timelinebubble,draw=white,line width=0.8pt] (2.25,0) circle (0.20);
    \node[font=\bfseries\fontsize{9.8}{10.8}\selectfont,text=timelineyear] at (2.25,-0.60) {2021};

    \fill[timelinebubble,draw=white,line width=0.8pt] (3.15,0) circle (0.20);
    \node[font=\bfseries\fontsize{9.8}{10.8}\selectfont,text=timelineyear] at (3.1,-0.60) {2022};

    \fill[timelinebubble,draw=white,line width=0.8pt] (11.25,0) circle (0.20);
    \node[font=\bfseries\fontsize{9.8}{10.8}\selectfont,text=timelineyear] at (11.25,-0.60) {2023};

    \fill[timelinebubble,draw=white,line width=0.8pt] (22.95,0) circle (0.20);
    \node[font=\bfseries\fontsize{9.8}{10.8}\selectfont,text=timelineyear] at (22.95,-0.60) {2024};

    \fill[timelinebubble,draw=white,line width=0.8pt] (23.85,-8.40) circle (0.20);
    \node[font=\bfseries\fontsize{9.8}{10.8}\selectfont,text=timelineyear] at (24.22,-7.82) {2025};

    \fill[timelinebubble,draw=white,line width=0.8pt] (22.95,-16.80) circle (0.20);
    \node[font=\bfseries\fontsize{9.8}{10.8}\selectfont,text=timelineyear] at (22.80,-17.40) {2026};

    \TopEvent{0.90}{timelinegold}{1.25}{lee2017learning}
    \TopEvent{1.80}{timelinebrick}{-1.15}{sieb2020graph}
    \TopEvent{2.70}{timelinebrick}{2.55}{das2021model}
    \TopEvent{3.60}{timelinebrick}{-2.45}{patel2022learning}
    \TopEvent{4.50}{timelinebrick}{3.85}{mandikal2022dexvip}
    \TopEvent{5.40}{timelineplum}{-3.75}{sivakumar2022robotic}
    \TopEvent{6.30}{timelineplum}{1.25}{arunachalam2022dexterous}
    \TopEvent{7.20}{timelineplum}{-1.15}{qin2022one}
    \TopEvent{8.10}{timelineplum}{2.55}{bahl2022human}
    \TopEvent{9.00}{timelineplum}{-2.45}{wen2022you}
    \TopEvent{9.90}{timelineplum}{3.85}{jiang2022ditto}
    \TopEvent{10.80}{timelineplum}{-3.75}{qin2022dexmv}
    \TopEvent{11.70}{timelineblue}{1.25}{shaw2023videodex}
    \TopEvent{12.60}{timelinebrick}{-1.15}{kumar2023graph}
    \TopEvent{13.50}{timelinegold}{2.55}{wang2023mimicplay}
    \TopEvent{14.40}{timelinegold}{-2.45}{bharadhwaj2023towards}
    \TopEvent{15.30}{timelinegold}{3.85}{wen2023any}
    \TopEvent{16.20}{timelinegold}{-3.75}{wang2023robot}
    \TopEvent{17.10}{timelinegold}{1.25}{gu2023rt}
    \TopEvent{18.00}{timelineplum}{-1.15}{bharadhwaj2023zero}
    \TopEvent{18.90}{timelineplum}{2.55}{bahl2023affordances}
    \TopEvent{19.80}{timelineplum}{-2.45}{kannan2023deft}
    \TopEvent{20.70}{timelineplum}{3.85}{ko2023learning}
    \TopEvent{21.60}{timelineplum}{-3.75}{gao2023k}
    \TopEvent{22.50}{timelineplum}{1.25}{ye2023learning}
    \TopEvent{23.40}{timelineblue}{-1.15}{srirama2024hrp}
    \TopEvent{24.30}{timelinegold}{2.55}{bharadhwaj2024track2act}
    \TopEvent{25.20}{timelinegold}{-2.45}{xu2024flow}
    \TopEvent{26.10}{timelineplum}{3.85}{kuang2024ram}
    \TopEvent{27.00}{timelineplum}{-3.75}{yuan2024general}
    \TopEvent{27.90}{timelineplum}{1.25}{heppert2024ditto}

    \MidEvent{27.90}{timelineplum}{-9.65}{ju2024robo}
    \MidEvent{27.00}{timelineplum}{-5.85}{kerr2024robot}
    \MidEvent{26.10}{timelineplum}{-10.95}{bahety2024screwmimic}
    \MidEvent{25.20}{timelineplum}{-4.55}{zhu2024vision}
    \MidEvent{24.30}{timelineplum}{-10.5}{li2024okami}
    \MidEvent{23.40}{timelineblue}{-7.15}{chen2025visa}
    \MidEvent{22.50}{timelineblue}{-9.65}{spiridonov2025generalist}
    \MidEvent{21.60}{timelineblue}{-5.85}{yang2025ar}
    \MidEvent{20.70}{timelineblue}{-10.95}{jiang2025rynnvla}
    \MidEvent{19.80}{timelineblue}{-4.55}{yoshida2025developing}
    \MidEvent{18.90}{timelineblue}{-12.25}{yang2025egovla}
    \MidEvent{18.00}{timelineblue}{-7.15}{luo2025being}
    \MidEvent{17.10}{timelineblue}{-9.65}{li2025scalable}
    \MidEvent{16.20}{timelineblue}{-5.85}{cai2025n}
    \MidEvent{15.30}{timelineblue}{-10.95}{feng2025spatial}
    \MidEvent{14.40}{timelineblue}{-4.55}{kareer2025egomimic}
    \MidEvent{13.50}{timelineblue}{-12.25}{qiu2025humanoid}
    \MidEvent{12.60}{timelineblue}{-7.15}{yuan2025motiontrans}
    \MidEvent{11.70}{timelineblue}{-9.65}{cheang2025gr}
    \MidEvent{10.80}{timelineblue}{-5.85}{wen2025gr}
    \MidEvent{9.90}{timelineblue}{-10.95}{kareer2025emergence}
    \MidEvent{9.00}{timelinebrick}{-4.55}{singh2025deep}
    \MidEvent{8.10}{timelinebrick}{-12.25}{dan2025x}
    \MidEvent{7.20}{timelinebrick}{-7.15}{lum2025crossing}
    \MidEvent{6.30}{timelinebrick}{-9.65}{jonnavittula2025view}
    \MidEvent{5.40}{timelinebrick}{-5.85}{chen2025vividex}
    \MidEvent{4.50}{timelinebrick}{-10.95}{guzey2025bridging}
    \MidEvent{3.60}{timelinebrick}{-4.55}{zhao2025dexh2r}
    \MidEvent{2.70}{timelinebrick}{-12.25}{yuan2025hermes}
    \MidEvent{1.80}{timelinebrick}{-7.15}{hsieh2025dexman}
    \MidEvent{0.90}{timelinebrick}{-9.65}{li2025maniptrans}

    \BotEvent{0.90}{timelinebrick}{-15.55}{zhao2025towards}
    \BotEvent{1.80}{timelinebrick}{-18.05}{ye2025video2policy}
    \BotEvent{2.70}{timelinegold}{-14.25}{yang2025tra}
    \BotEvent{3.60}{timelinegold}{-19.35}{chen2025graphmimic}
    \BotEvent{4.50}{timelinegold}{-12.95}{zhou2025human}
    \BotEvent{5.40}{timelinegold}{-20.65}{papagiannis2025r}
    \BotEvent{6.30}{timelinegold}{-15.55}{park2025demodiffusion}
    \BotEvent{7.20}{timelineplum}{-18.05}{shi2025zeromimic}
    \BotEvent{8.10}{timelineplum}{-14.25}{chen2025vidbot}
    \BotEvent{9.00}{timelineplum}{-19.35}{ma2025uni}
    \BotEvent{9.90}{timelineplum}{-12.95}{ren2025motion}
    \BotEvent{10.80}{timelineplum}{-20.65}{li2025novaflow}
    \BotEvent{11.70}{timelineplum}{-15.55}{yin2025object}
    \BotEvent{12.60}{timelineplum}{-18.05}{shan2025slot}
    \BotEvent{13.50}{timelineplum}{-14.25}{hsu2025spot}
    \BotEvent{14.40}{timelineplum}{-19.35}{tang2025functo}
    \BotEvent{15.30}{timelineplum}{-12.95}{tang2025mimicfunc}
    \BotEvent{16.20}{timelineplum}{-20.65}{werby2025articulated}
    \BotEvent{17.10}{timelineplum}{-15.55}{zhang2025actron3d}
    \BotEvent{18.00}{timelineplum}{-18.05}{haldar2025point}
    \BotEvent{18.90}{timelineplum}{-14.25}{liu2025egozero}
    \BotEvent{19.80}{timelineplum}{-19.35}{hu2025learning}
    \BotEvent{20.70}{timelineplum}{-12.95}{chen2025web2grasp}
    \BotEvent{21.60}{timelineplum}{-20.65}{zhou2025you}
    \BotEvent{22.50}{timelineplum}{-15.55}{heidinger20252handedafforder}
    \BotEvent{23.30}{timelineblue}{-18.05}{bi2026h}
    \BotEvent{24.05}{timelineblue}{-12.95}{zheng2026egoscale}
    \BotEvent{24.85}{timelineblue}{-15.55}{zhu2026emma}
    \BotEvent{25.65}{timelineblue}{-20.65}{luo2026being}
    \BotEvent{26.45}{timelineplum}{-14.25}{soraki2026objectforesight}
    \BotEvent{27.25}{timelineplum}{-19.35}{chen2026dexterous}
    \BotEvent{28.05}{timelineplum}{-12.95}{wang2026paws}
    \BotEvent{29.00}{timelineblue}{-18.05}{zhang2026unidex}


    \draw[timelineblue,line width=2.8pt,rounded corners=1pt] (0.20,-22.55) -- (1.10,-22.55);
    \node[anchor=west,font=\bfseries\fontsize{12.2}{11.4}\selectfont,text=timelineblue] at (1.30,-22.55) {Affordances for robot policy backbone training};

    \draw[timelinebrick,line width=2.8pt,rounded corners=1pt] (17.30,-22.55) -- (18.20,-22.55);
    \node[anchor=west,font=\bfseries\fontsize{12.2}{11.4}\selectfont,text=timelinebrick] at (18.40,-22.55) {Affordances for reward construction in robot policy};

    \draw[timelinegold,line width=2.8pt,rounded corners=1pt] (0.20,-23.25) -- (1.10,-23.25);
    \node[anchor=west,font=\bfseries\fontsize{12.2}{11.4}\selectfont,text=timelinegold] at (1.30,-23.25) {Affordances as robot policy condition};

    \draw[timelineplum,line width=2.8pt,rounded corners=1pt] (17.30,-23.25) -- (18.20,-23.25);
    \node[anchor=west,font=\bfseries\fontsize{12.2}{11.4}\selectfont,text=timelineplum] at (18.40,-23.25) {Affordances as robot policy};

  \end{tikzpicture}%
  }
  \caption{按时间顺序概述 \textit{下的方法作为桥梁} 在 Sec.~\ref{sec:affordances} 中。}
  \label{fig:affordances_timeline}
\end{figure*}


\begin{table*}[t]
\centering
\scriptsize
\setlength{\tabcolsep}{3.2pt}
\caption{为机器人策略骨干培训制定可供性的代表性方法的比较。}
\label{tab:affordance_backbone}
\begin{tabularx}{\linewidth}{p{3.3cm}p{3.3cm} X X p{3.3cm}}
\toprule
参考&手可供性&物体可供性&联合可供性&末端执行器\\
\midrule
\rowcolor{gray!15}
\multicolumn{5}{l}{\textit{Affordance-based pretraining}} \\
\cite{shaw2023videodex} & 6D wrist pose, MANO & -- & -- & Dexterous hand \\
\cite{srirama2024hrp} & 2D hand position & 2D object bbox & Contact region & Parallel gripper \\
\cite{chen2025visa} & 2D hand mask, 2D action flow & 2D object mask, 2D action flow & -- & Parallel gripper \\
\cite{spiridonov2025generalist} & 3D hand keypoint flow & -- & -- & Parallel gripper \\
\cite{yang2025ar} & 3D hand keypoint & -- & -- & Parallel gripper \\
\cite{jiang2025rynnvla} & 2D hand keypoint & -- & -- & Parallel gripper \\
\cite{yoshida2025developing} & -- & 6D object pose & -- & Parallel gripper \\
\cite{yang2025egovla} & 6D wrist pose, MANO & -- & -- & Dexterous hand \\
\cite{luo2025being} & 6D wrist pose, MANO & -- & -- & Dexterous hand \\
\cite{li2025scalable} & 3D hand trajectory & -- & -- & Dexterous hand \\
\cite{cai2025n} & 6D wrist pose, 3D finger position & -- & -- & Dexterous hand \\
\cite{feng2025spatial} & 3D hand trajectory, MANO & 2D object bbox & -- & Dexterous hand, parallel gripper \\
\cite{bi2026h} & 6D wrist pose, 3D finger position & -- & -- & Parallel gripper \\
\cite{zheng2026egoscale} & 6D wrist pose, hand joint angle & -- & -- & Dexterous hand \\
\cite{zhang2026unidex} & 3D fingertip trajectory & -- & -- & Dexterous hand \\
\midrule
\rowcolor{gray!15}
\multicolumn{5}{l}{\textit{Affordance-based co-training}} \\
\cite{kareer2025egomimic} & 6D hand pose & -- & -- & Parallel gripper \\
\cite{qiu2025humanoid} & 6D wrist pose, 3D finger position & -- & -- & Dexterous hand \\
\cite{yuan2025motiontrans} & 6D wrist pose, 3D hand keypoint & -- & -- & Dexterous hand \\
\cite{cheang2025gr} & 3D hand trajectory & -- & -- & Parallel gripper \\
\cite{wen2025gr} & 6D wrist pose, hand joint angle, 3D fingertip position & -- & -- & Dexterous hand \\
\cite{kareer2025emergence} & 3D hand keypoint, 6D hand pose & -- & -- & Parallel gripper \\
\cite{luo2026being} & 6D wrist pose, MANO & -- & Interaction timing & Dexterous hand, parallel gripper \\
\cite{zhu2026emma} & 6D hand pose & -- & -- & Parallel gripper \\
\bottomrule
\end{tabularx}
\end{table*}


 

\textit{(b) 用于机器人策略骨干训练的可供性:} Affordances encompass rich and explicit hand-object interaction patterns. Therefore, they provide more action-grounded transfer signals between human videos and robot policies, which can be used to pretrain the backbone of robot policies after attaching an affordance-specific decoder. The high-level diagram of this bridging mechanism is illustrated in Fig.~\ref{fig:affordances_transfer}(a). For example, VideoDex~\citep{shaw2023videodex} explicitly extracts human wrist poses and hand pose parameters from Internet videos, and retargets them into robot wrist and finger trajectories. These reconstructed motions are used as an action prior for pretraining a Neural Dynamic Policy (NDP), which is then adapted with a small number of in-domain teleoperated demonstrations. To further enrich the supervision signals from affordances, HRP~\citep{srirama2024hrp} is required to predict future contact points, human hand poses, and the target object bounding boxes given a video frame as input. Thus, it is encouraged to focus on actionable scene regions, target objects, and interaction-relevant hand motion, leading to stronger downstream robotic performance across diverse tasks, robot morphologies, and camera views. Nevertheless, the NDP model of VideoDex~\citep{shaw2023videodex} and the ViT-B backbone of HRP~\citep{srirama2024hrp} are both relatively lightweight, with parameter scales below roughly one hundred million. This may limit the effectiveness of large-scale affordance-based pretraining for the backbone of robot policies. Therefore, more researchers scale affordance supervisions to optimize the VLA backbone with hundreds of millions to billions of parameters (e.g., PaliGemma~\citep{beyer2024paligemma}, InternVL3~\citep{chen2024expanding}, NVILA~\citep{liu2025nvila}). For instance, ViSA-Flow~\citep{chen2025visa} explicitly learns to predict future 2D hand-object interaction masks with a vision decoder. Its large-scale Transformer backbone then has the ability to capture semantic action flow to enhance robot skill learning with only a small dataset of robot demonstrations. In contrast, \cite{spiridonov2025generalist} directly pretrains the VLM of MotoVLA by predicting the 3D flow of human hand keypoints. Similarly, AR-VRM~\citep{yang2025ar} also adopts hand keypoint prediction to pretrain the VLA backbone. It further distinguishes itself by retrieving analogous human video exemplars as additional context for the mapping between hand motions and robot components. RynnVLA-001~\citep{jiang2025rynnvla} instead uses hand keypoint trajectories as auxiliary motion signals for future video prediction. It allows the backbone to anticipate incoming visual evolution along with physical dynamics for subsequent robot action planning. Considering the wide availability of off-the-shelf 6D hand\&object pose annotation tools, some pretraining schemes have switched to optimize the backbone with the task of hand\&object pose prediction. For example, \cite{yoshida2025developing} leverages the EgoScaler object-trajectory generation framework~\citep{yoshida2025generating} to construct annotated 6D object pose trajectories from egocentric videos. These pose labels are then used to pretrain the VLM backbone of a $\pi_0$ VLA model~\citep{black2024pi_0}. However, a larger body of existing works focuses on predicting hand poses and joint parameters for affordance-based pretraining. Compared with object-centric alternatives, capturing hand motion~\citep{pavlakos2024reconstructing,potamias2025wilor,zhang2025hawor} is generally more feasible on diverse Internet-scale human videos, because it does not depend on prior object reconstruction or point tracking. For example, \cite{yang2025egovla} pretrain EgoVLA by directly regressing future human wrist translations, wrist rotations, and hand joint parameters from egocentric videos in a unified action space. This hand-centric objective encourages the backbone to internalize temporal motion dynamics priors for action planning of the dexterous hands of humanoid robots. Instead of sharing the action head, Being-H0~\citep{luo2025being} introduces a dedicated part-level motion tokenizer that separately discretizes wrist and finger motions into hand motion tokens. This work also proposes UniHand-1.0, a large-scale mixed human video dataset with unified hand pose annotations. UniHand-1.0 comprises 130 million frames, substantially exceeding the approximately 500,000 frames used by EgoVLA~\citep{yang2025egovla}. As a concurrent work of Being-H0~\citep{luo2025being}, \cite{li2025scalable} argue that the training recipe with the original human annotations leads to temporal or granularity misalignment between text and actions. This weakens instruction following of the predicted actions. Thus, they convert human videos into robot-style VLA episodes with atomic hand-action segments, frame-aligned 3D hand trajectories, and newly generated imperative action descriptions. They also demonstrate that their proposed VITRA outperforms Being-H0~\citep{luo2025being}, even trained with a smaller human video dataset containing 26 million frames. To better organize the backbone pretraining data, \cite{cai2025n} distinguish human videos into in-the-wild data, which exceed 1,000 hours and are diverse and easy to collect, and on-task data, which exceed 20 hours and are aligned with the target robot tasks. VIPA-VLA~\citep{feng2025spatial} performs explicit visual-physical alignment on human videos by jointly leveraging 3D visual annotations and hand trajectory annotations, enabling the VLA backbone to acquire 2D-3D spatial grounding before robot post-training. A representative extension of hand-centric affordance pretraining to bimanual manipulation is H-RDT~\citep{bi2026h}. It pretrains a diffusion Transformer backbone with 3D bimanual hand pose annotations in a unified 48-dimensional action space. It then transfers these human manipulation priors to different robot embodiments through modular action encoders and decoders during cross-embodiment fine-tuning. JoyAI-RA~\citep{zhang2026joyai} further scales pretraining by integrating web data, large-scale egocentric human videos, simulation-generated trajectories, and real-robot demonstrations in a multi-source multi-level fashion. It recovers hand trajectories from human videos and retargets them to multiple robot embodiments through action-space unification. EgoScale~\citep{zheng2026egoscale} interestingly shows that affordance-based backbone pretraining on egocentric human videos follows a clear log-linear scaling law, where increasing human data scale consistently reduces the validation loss of wrist motion and retargeted
灵巧的手部动作预测。更重要的是，这种验证损失与下游机器人性能密切相关，这表明基于可供性的骨干预训练的扩展为改进灵巧操作提供了可预测的途径。最近，UniDex~\citep{zhang2026unidex} 从运动和感知方面解决了骨干预训练的实施例差异。具体来说，它依靠交互式重定向过程将人类指尖运动映射到机器人手，同时保持物理上合理的手部物体接触。它将人手从重建的 3D 点云中移除，以进一步缓解运动学和视觉不匹配。所得数据用于大规模骨干预训练，建立支持跨手转移的灵巧手基础模型。总体而言，基于可供性的预训练主要用于赋予骨干网可转移的操作先验，而不是直接可执行的机器人策略。在实践中，这些先验仍然需要特定于机器人的后训练或微调，以弥合剩余实施例和动作空间差距。




与使用可供性来预训练机器人策略的骨干相反，一些研究人员转向了统一的协同训练方案。如图~\ref{fig:affordances_transfer}(b)所示，该方案减轻了后续机器人微调过程中人类操作先验的损失，以及上述两阶段训练流程中潜在的复合故障。此外，与基于可供性的预训练不同，协同训练通常会产生可直接用于下游机器人操作的策略，因为其训练过程已经包含了特定于机器人的演示。例如，EgoMimic~\citep{kareer2025egomimic} 在以自我为中心的人类视频上与 3D 手部跟踪和远程操作机器人数据共同训练模仿策略，将两者视为同等重要的具体演示。它见证了协同训练方案在使用人类数据进行扩展时性能的显着提升。这项工作从 ALOHA~\citep{zhao2023learning} 中汲取灵感，设计了一种新颖的机器人机械手来模仿人类手臂的运动，并为机器人配备了 Aria 眼镜，以更好地匹配人类演示的自我中心观察。这些对齐技术有助于缩小协同训练数据中固有的实施例差距。 EMMA~\citep{zhu2026emma} 通过以自我为中心的人体全身运动数据与静态机器人操纵数据进行协同训练，进一步将 EgoMimic~\citep{kareer2025egomimic} 扩展到移动操纵。它通过将人体头部姿势投影到地平面上并使用人体航路点优化速度命令来弥补导航运动学差距。然而，\cite{qiu2025humanoid} 发现严格的视觉传感器对齐和启发式设计（例如 EgoMimic~\citep{kareer2025egomimic} 中的视觉掩蔽）会导致复合失败。因此，他们转而在统一的人类-机器人状态-动作空间中训练人类动作变压器。凭借可微的重定向和简单的图像增强，该设计在部署在具有灵巧双手的人形机器人上时，避免了严格的传感器匹配、启发式掩蔽和专门的硬件重新设计。考虑到 \cite{qiu2025humanoid} 协同训练方案中人类和机器人数据之间潜在的不平衡，\cite{yuan2025motiontrans} 采用了受 \cite{wei2025empirical} 启发的加权策略。它采用数据集大小来确定域权重，以便在协同训练期间平衡人类和机器人数据的总贡献。这项工作还验证了 VLA 模型 ~\citep{black2024pi_0} 上的多任务人机协同训练对于零样本操作的有效性。 \cite{cheang2025gr} 还结合了人类轨迹数据，并利用视觉语言数据和机器人轨迹共同训练 VLA 模型。与 GR-1~\citep{wu2023unleashing} 和 GR-2~\citep{cheang2024gr} 相比，GR-3 通过在微调过程中引入人手轨迹监督，显着提高了对不可见物体的少样本泛化能力。 GR-Dexter~\citep{wen2025gr} 沿袭了 GR-3 的主干，但进一步丰富了动作空间，从二元离散抓手动作到手臂关节动作、手臂末端执行器姿势、手部关节动作和指尖位置的组合。与使用复合动作向量的 GR-Dexter 相比，Being-H0.5~\citep{luo2026being} 提出了语义对齐的统一动作空间，以在共享物理词汇下共同训练人类和异构机器人实施例。这项工作还构建了 UniHand-2.0 数据集，该数据集由人类、机器人和视觉语言数据组成，比之前的工作 ~\citep{luo2025being} 中提出的 UniHand-1.0 数据集大大约 200 倍。有趣的是，\cite{kareer2025emergence} 最近发现人机迁移是多种 VLA 预训练的一个新兴特性。只有在跨场景、任务和实施例进行足够多样化的机器人预训练之后，简单的人机协同训练方法才开始发挥作用。他们的分析进一步表明，这种出现是由越来越多的与具体化无关的潜在表示驱动的，这使得人类和机器人的观察可以在特征空间中对齐，而无需任何明确的传输机制。这些关键发现将进一步支持统一的人机协同训练作为在 VLA 模型中利用人类视频的可扩展途径，特别是当机器人预训练数据中已经包含足够的多样性时。

值得注意的是，基于可供性的预训练和统一的人机协同训练都表现出明显的扩展趋势，从轻量级的特定任务模型发展到在日益多样化的人类视频混合上训练的大型 VLA 主干。这一进展在很大程度上得益于 HOI 分析技术的进步、具有更丰富注释的人类视频数据集的快速增长，以及大型基础模型的出现，这些模型使大规模跨实体学习变得越来越实用。

\begin{table*}[t]
\centering
\scriptsize
\setlength{\tabcolsep}{3.2pt}
\caption{为机器人策略学习中的奖励构建制定可供性的代表性方法的比较。}
\label{tab:affordance_reward}
\begin{tabularx}{\linewidth}{p{3.3cm}p{3.3cm}p{5.5cm} X X}
\toprule
参考&手可供性&物体可供性&联合可供性&末端执行器\\
\midrule
\rowcolor{gray!15}
\multicolumn{5}{l}{\textit{Single-modality reward construction}} \\
\cite{das2021model} & -- & 2D object keypoint & -- & Parallel gripper \\
\cite{singh2025deep} & 3D fingertip position & -- & -- & Dexterous hand \\
\cite{dan2025x} & -- & 6D object pose & -- & Parallel gripper \\
\cite{ye2025video2policy} & -- & 6D object pose, 2D object mask & -- & Parallel gripper \\
\midrule
\rowcolor{gray!15}
\multicolumn{5}{l}{\textit{Multimodal reward construction}} \\
\cite{sieb2020graph} & 3D finger position & 6D object pose, 3D object keypoint, 3D object bbox & Grasp state & Parallel gripper \\
\cite{patel2022learning} & 6D palm pose, hand joint angle & 6D object pose & -- & Parallel gripper \\
\cite{mandikal2022dexvip} & 6D hand pose & 3D object keypoint & Contact point & Dexterous hand \\
\cite{kumar2023graph} & 2D hand bbox & 2D object bbox, inter-object graph & -- & Parallel gripper \\
\cite{lum2025crossing} & MANO & 6D object pose & -- & Dexterous hand \\
\cite{jonnavittula2025view} & 3D wrist position & 3D object position & Contact state & Parallel gripper \\
\cite{chen2025vividex} & 3D hand joint position & 6D object pose & -- & Dexterous hand \\
\cite{guzey2025bridging} & 2D fingertip position & 2D object keypoint & -- & Dexterous hand \\
\cite{zhao2025dexh2r} & 6D hand pose, MANO & 6D object pose & -- & Dexterous hand \\
\cite{yuan2025hermes} & 3D hand keypoint, 6D palm pose & 6D object pose & Contact prior & Dexterous hand \\
\cite{hsieh2025dexman} & 6D wrist pose, 3D fingertip position, MANO & 6D object pose & Contact prior & Dexterous hand \\
\cite{li2025maniptrans} & 6D wrist pose, MANO & 6D object pose & Contact prior & Dexterous hand \\
\cite{zhao2025towards} & MANO & 3D object keypoint &  Contact region & Dexterous hand \\
\bottomrule
\end{tabularx}
\end{table*}






\textit{(c) 用于机器人策略奖励构建的可供性：}相关工作根据人类视频中的手部、物体姿态、接触点和运动轨迹设计奖励函数，使机器人动作尽量重现观察到的交互模式，并通过强化学习优化策略。
为了更紧密地将可供性纳入机器人策略学习中，一些工作使用可供性来构建直接指导机器人策略优化的奖励函数。通过评估机器人动作再现人类视频中观察到的可供性模式的程度，这些奖励信号有助于将机器人动作与人类交互动态结合起来。与前面提到的基于可供性的骨干训练相比，这种范式更直接地影响机器人策略优化。它使机器人能够通过反复试验来完善自己的行为，同时保持人类交互的基础。 Fig.~\ref{fig:affordances_transfer}(c) 展示了使用单一交互方式构建奖励。例如，\cite{das2021model} 通过预先训练的自监督关键点检测器从人类视频中学习成本函数，然后使用它通过视觉模型预测控制来优化机器人行为。 \cite{singh2025deep} 不是关键点预测，而是根据人类交互视频训练未来人类指尖运动的预测模型，并使用其对机器人轨迹的零样本预测来定义跟踪奖励。然后将这种学习到的运动跟踪奖励与稀疏任务奖励相结合，通过强化学习来优化机器人感觉运动策略。 \cite{dan2025x} 没有使用手部动作作为参考，而是使用从人类视频中提取的对象运动来在重建的真实感模拟器中定义以对象为中心的奖励。具体来说，奖励是根据模拟的机器人引起的物体轨迹与从视频中提取的目标物体轨迹之间的差异构建的。因此，驱动策略优化以与实施例无关的方式匹配对象状态变化。最近，Video2Policy~\citep{ye2025video2policy} 通过使用 LLM 自动生成的上下文中以对象为中心的奖励函数来训练 RL 策略，从而扩展了这个方向。它不是从单个演示视频中生成奖励，而是使用大量日常人类视频来合成各种可奖励的模拟任务，支持可扩展的 Real2Sim2Real 策略学习。



如图~\ref{fig:affordances_transfer}(d)所示，更多相关工作结合了人类视频中手部和目标物体的运动先验来构建奖励函数，而不是仅仅使用单一的运动模态。 \cite{patel2022learning} 是向更丰富的手部物体奖励设计的早期过渡。这项工作联合优化了来自互联网视频的双手和物体的 4D 轨迹，同时仍然主要通过模拟中的物体姿势模仿来训练机器人策略。它可以被视为从纯粹的单模态奖励到后来结合手部先验和基于对象的奖励信号的方法的桥梁。如 \cite{mandikal2022dexvip} 所示，他们构建了一个物体可供性接触奖励，鼓励机器人手接近物体上与人类接触的抓取区域。同时，他们还引入了姿势奖励，鼓励机器人关节匹配重新定位的 6D 人类抓取姿势。为了减少先前 RL 范式中探索推出的次数，\cite{lum2025crossing} 利用预操作 MANO 手部姿势作为探索先验。然后，他们通过将机器人引起的物体运动与人类视频中演示的物体轨迹进行比较，构建与实施例无关的奖励。相比之下，VIEW~\citep{jonnavittula2025view}和ViViDex~\citep{chen2025vividex}从人类视频中提取更细粒度的手（指尖）路径点作为先验，进一步提高探索效率。此后，以手部轨迹作为先验，同时以物体轨迹作为残差学习奖励信号的人类引导强化学习范式成为该方向流行的设计模式~\citep{guzey2025bridging,zhao2025dexh2r,yuan2025hermes,hsieh2025dexman}。 \cite{zhao2025dexh2r} 进一步引入了所需的人手和物体轨迹的测试时指导，使机器人能够将学习到的策略适应新的操作场景，并具有更强的泛化能力。 HERMES~\citep{yuan2025hermes} 将这种 RL 范例从桌面灵巧操作扩展到更远距离的移动操作。它结合了以对象为中心的距离链和对象跟踪奖励以及功率惩罚，以捕获手部对象接触期间的动态空间关系并增强执行平滑度。导航基础模型进一步与闭环 PnP 定位集成，以实现移动操控功能。 \cite{hsieh2025dexman} 还认识到像 HERMES~\citep{yuan2025hermes} 这样的手部物体接触指导的重要性，并提出了接触优先吸引奖励来细化重定向动作。 ManipTrans~\citep{li2025maniptrans} 在手部动作模仿和物体跟踪奖励的基础上进一步引入了接触力奖励。具体来说，当演示的手足够接近物体时，它会在模拟中奖励非零指尖接触力，从而鼓励更稳定的抓握并改善灵巧双手操作的剩余学习。为了实现更加基于语义的接触监督，Z​​XQ0012QXZ 引入了额外的负面可供性指导，以在剩余策略细化期间惩罚功能上不适当的接触区域。

~\cite{sieb2020graph} 提出了一种更加结构化的奖励变体。它们通过匹配机器人场景和人类演示之间的手/抓手物体 3D 位置的相对空间配置来生成奖励。为了解决先前工作〜\citep{sieb2020graph}中相同域视觉轨迹的限制，\cite{kumar2023graph}通过从不同视频中学习通用对齐函数，进一步瞄准跨域和跨实施例的模仿。它不依赖于手动设计的对应规则，而是将演示表示为图形，并直接在图形空间中学习手部对象交互，从而产生能够更稳健地跨领域和实施例转移的奖励函数。


与基于可供性的骨干训练不同，基于可供性的奖励构建通过塑造优化目标本身将可供性纳入机器人学习中。相关工作已经从单一模态运动奖励发展到更丰富的手部物体奖励设计，这些设计联合编码抓握先验、物体运动、接触几何形状和接触力。这种设计在 LfHV 设置中提供了更强的灵活性，因为机器人可以通过在人类目标下的试错来完善其行为。


\begin{table*}[t]
\centering
\scriptsize
\setlength{\tabcolsep}{3.2pt}
\caption{将可供性制定为机器人策略条件的代表性方法的比较。}
\label{tab:affordance_condition}
\begin{tabularx}{\linewidth}{p{2.7cm}X X X p{1.7cm}}
\toprule
参考&手可供性&物体可供性&联合可供性&末端执行器\\
\midrule
\rowcolor{gray!15}
\multicolumn{5}{l}{\textit{Predicted affordances as policy conditions}} \\
\cite{lee2017learning} & 2D hand position & 2D object position & -- & Parallel gripper \\
\cite{wang2023mimicplay} & 3D hand position & -- & -- & Parallel gripper \\
\cite{bharadhwaj2023towards} & 2D hand mask & 2D object mask & -- & Parallel gripper \\
\cite{wen2023any} & -- & -- & Point track & Parallel gripper \\
\cite{bharadhwaj2024track2act} & -- & -- & Point track & Parallel gripper \\
\cite{yang2025tra} & -- & -- & Point track & Parallel gripper \\
\cite{xu2024flow} & -- & 2D object bbox, 2D object keypoint, motion flow & -- & Parallel gripper \\
\cite{chen2025graphmimic} & 2D fingertip position & 2D object mask, 2D object keypoint & Interaction graph & Parallel gripper \\
\cite{zhou2025human} & 3D hand keypoint & -- & -- & Parallel gripper \\
\midrule
\rowcolor{gray!15}
\multicolumn{5}{l}{\textit{Prompt-extracted affordances as policy conditions}} \\
\cite{wang2023robot} & 3D hand trajectory & Object features, insertion geometry & -- & Parallel gripper \\
\cite{gu2023rt} & 2D hand trajectory sketch & -- &  2D interaction marker & Parallel gripper \\
\cite{papagiannis2025r} & 3D hand keypoints, MANO & -- & 3D scene keypoints & Parallel gripper \\
\cite{park2025demodiffusion} & 6D hand pose & -- & -- & Parallel gripper \\
\bottomrule
\end{tabularx}
\end{table*}




 \textit{(d) Affordances as robot policy condition:} 
除了作为骨干训练的监督和策略优化的奖励信号之外，可供性还可以作为显式条件更直接地注入到机器人策略中。这个方向的大多数现有工作都集中于预测 \textit{未来可供性} 作为条件，因为它们可以用作动作指导信号（目标），以在人类视频理解和机器人执行之间建立更紧密的联系。如图~\ref{fig:affordances_transfer}(e)所示，这种桥接机制还需要预训练可供性预测模型，例如基于可供性的机器人策略骨干预训练。然而，它进一步将预测的可供性明确地集成到下游机器人策略中，而不是使用主干网。 \cite{lee2017learning} 提出了一个早期示例，通过从以自我为中心的人类视频中预测未来的手部位置，使用可供性作为明确的策略条件。然后将这些预测的未来手部物体交互状态作为中间动作引导信号输入到操纵网络中。该方案使机器人能够根据预期的未来交互而不仅仅是当前的观察结果生成运动命令。 MimicPlay~\citep{wang2023mimicplay} 不是明确预测手部位置，而是根据人类视频预测的未来潜在子目标来控制机器人控制。未来的 3D 人手轨迹在附加 GMM 解码器后监督潜在预测模型。为了进一步放宽 MimicPlay~\citep{wang2023mimicplay} 中域内视频的假设，\cite{bharadhwaj2023towards} 使用大量野外人类视频片段训练扩散模型，以幻觉未来的手部和物体掩模，以调节单​​独的机器人操纵策略。之后，更多与预测可供性相关的工作，因为条件涉及预测更密集的点轨迹（运动流）以实现更精细的机器人控制引导。例如，ATM~\citep{wen2023any} 预训练一个语言条件轨迹 Transformer，以预测图像中任意点的未来轨迹。然后，它使用生成的密集点轨迹作为策略学习的显式条件。这些基于点的运动提示提供详细的控制指导并保持对象的持久性。然而，ATM 框架并不容易适用于网络视频，因为它的策略依赖于每步图像观察来预测点轨迹。此外，ATM 需要昂贵的现实世界机器人数据与域内人类演示数据一起进行训练。为了解决这些限制，作为 ATM 的并行工作，Track2Act~\citep{bharadhwaj2024track2act} 学习仅根据初始图像和互联网人类视频来预测点轨迹。它通过将预测轨迹转换为刚性对象变换，为开环执行留下了一个接口。预测的轨迹还可以用作学习轻量级实施例特定剩余策略的条件，以补偿执行错误和实施例失配。 Tra-MoE~\citep{yang2025tra} 还旨在通过在学习轨迹条件策略时针对更广泛的多域数据引入稀疏 MoE 轨迹预测器来改进 ATM。它还集成了自适应策略调节技术，该技术利用图像对齐的可学习嵌入构建掩模模态输入。带有动作标记的机器人演示用于后续行为克隆。可以看出，Track2Act~\citep{bharadhwaj2024track2act} 和 Tra-MoE~\citep{yang2025tra} 都需要收集现实世界的机器人数据来学习闭环机器人策略。相比之下，\cite{xu2024flow} 将管道分解为在真实人类视频上训练的流生成网络和完全在模拟机器人游戏数据上训练的流条件闭环策略。通过根据以对象为中心的流而不是特定于实施例的轨迹来调节机器人动作，该方案绕过了收集现实世界机器人训练数据的需要。它仍然可以直接部署在现实世界中，并且模拟与真实的差距最小。尽管如此，\cite{chen2025graphmimic} 认为上述基于流的方法直接对像素空间的表示进行建模，忽略了对象的内部结构、空间对象-对象和对象-效应器关系。因此，他们提出了 GraphMimic，它将每个人类视频帧抽象为具有对象顶点和视觉动作顶点的结构化图。然后，他们预训练图到图生成模型来预测未来图作为政策条件。通过对图空间中的对象结构和空间关系进行建模，它提供了比像素空间流更结构化的动作指导。通过使用轨迹专家直接预测拇指和食指关键点中点的 3D 轨迹，Traj2Action~\citep{zhou2025human} 生成高级运动计划来调节机器人动作专家。

与使用预测可供性作为条件的现有作品相比，一些作品接收视频作为附加提示，可以直接提取可供性作为条件，而无需额外的预测阶段，如图〜\ref{fig:affordances_transfer}（f）所示。例如，\cite{wang2023robot} 从单个人类演示视频中提取手部轨迹，以生成模仿的机器人接近运动，同时定位对象特征以进行后续的视觉伺服。 RT-Trajectory~\citep{gu2023rt} 相反，使用人类视频来构建粗略的事后轨迹草图，该草图将末端执行器运动和交互标记可视化编码为机器人策略的明确任务规范。将人类演示表示为粗略的运动草图而不是精确的几何轨迹，它提供了动作指导条件，同时保持足够的灵活性以概括新任务。 R+X~\citep{papagiannis2025r} 不会通过明确的可供性提示来优化机器人策略。相反，它从长的、未标记的第一人称人类视频中检索相关片段，提取其视觉关键点和手部关节，最后使用它们来调节上下文模仿学习方法~\citep{di2024keypoint}。最近，DemoDiffusion~\citep{park2025demodiffusion} 利用 6D 手部姿势作为重新定位的开环机器人运动的有效初始化，然后使用预先训练的通用扩散策略细化该轨迹，使其既任务一致又机器人可行。因此，它减轻了实施例差距和闭环反馈的缺乏。

与基于可供性的骨干训练和奖励塑造相比，使用可供性作为策略条件，通过直接将交互感知的几何线索注入下游控制，在人类视频和机器人执行之间建立了更紧密的联系。现有的方法已经从预测稀疏的未来手位置和潜在子目标发展到生成更密集的运动条件，例如掩模、点轨迹、流和结构化图。一小部分工作直接从人类视频中提取可供性，作为政策学习或执行的提示。尽管这种范式提供了比主干训练和奖励构建更明确的行动指导，但它通常仍然依赖于单独的可供性预测或提取阶段。在许多情况下，需要额外的机器人演示或策略调整来将条件转化为特定于实施例的动作。


\begin{table*}[t]
\centering
\scriptsize
\setlength{\tabcolsep}{3.2pt}
\caption{将可供性制定为机器人策略的代表性方法的比较。}
\label{tab:affordance_policy}
\begin{tabularx}{\linewidth}{p{2.9cm}X X p{4.5cm} p{1.7cm}}
\toprule
参考&手可供性&物体可供性&联合可供性&末端执行器\\
\midrule
\rowcolor{gray!15}
\multicolumn{5}{l}{\textit{Hand-centric policy grounding}} \\
\cite{sivakumar2022robotic} & 6D hand pose, MANO & -- & -- & Dexterous hand \\
\cite{arunachalam2022dexterous} & 2.5D hand keypoint & -- & -- & Dexterous hand \\
\cite{qin2022one} & 2D hand bbox, 6D wrist pose, SMPL-X & -- & -- & Dexterous hand \\
\cite{bahl2022human} & 2D hand bbox, 3D wrist rotation & -- & Interaction timing & Parallel gripper \\
\cite{bharadhwaj2023zero} & 6D palm pose & -- & -- & Parallel gripper \\
\cite{bahl2023affordances} & 2D hand trajectory & -- & 2D contact point & Parallel gripper \\
\cite{kannan2023deft} & 6D wrist pose, hand joint angles, MANO & -- & 3D contact point & Dexterous hand \\
\cite{kuang2024ram} & 3D hand trajectory, post-contact direction vector & -- & 3D contact point & Parallel gripper \\
\cite{shi2025zeromimic} & 6D wrist trajectory & -- & 2D contact point & Parallel gripper \\
\cite{ma2025uni} & 3D hand keypoints & -- & Interaction timing & Parallel gripper \\
\midrule
\rowcolor{gray!15}
\multicolumn{5}{l}{\textit{Object-centric policy grounding}} \\
\cite{wen2022you} & -- & 6D object pose & -- & Parallel gripper \\
\cite{ko2023learning} & -- & 2D object mask, 3D object keypoint & Optical flow & Parallel gripper \\
\cite{yuan2024general} & -- & 3D general flow & -- & Parallel gripper \\
\cite{heppert2024ditto} & -- & 6D object pose & -- & Parallel gripper \\
\cite{ju2024robo} & -- & 3D function point & -- & Parallel gripper \\
\cite{kerr2024robot} & -- & 4D differentiable part model & -- & Parallel gripper \\
\cite{li2025novaflow} & -- & 2D object mask, 3D object keypoint & -- & Parallel gripper \\
\cite{yin2025object} & -- & 2D object mask, 3D motion field & -- & Parallel gripper \\
\cite{shan2025slot} & -- & 2D object mask & -- & Parallel gripper \\
\cite{hsu2025spot} & -- & 6D object pose & -- & Parallel gripper \\
\cite{tang2025functo} & -- & 2D objece mask, 3D function point & 3D grasp point & Parallel gripper \\
\cite{zhang2025actron3d} & -- & 3D point flow & 2D contact mask & Parallel gripper \\
\midrule
\rowcolor{gray!15}
\multicolumn{5}{l}{\textit{Interaction-centric policy grounding}} \\
\cite{qin2022dexmv} & 6D hand pose, MANO & 6D object pose & -- & Dexterous hand \\
\cite{gao2023k} & 3D hand keypoint & 3D object keypoint & Geometric keypoint constraint & Dexterous hand \\
\cite{ye2023learning} & 3D hand joint position & Object point cloud & -- & Dexterous hand \\
\cite{bahety2024screwmimic} & 6D wrist pose & Object point cloud & 3D grasp/placement point & Parallel gripper \\
\cite{li2024okami} & SMPL-H trajectory & 2D object keypoint, 2D object keypoint, object point cloud & -- & Dexterous hand \\
\cite{haldar2025point} & 3D hand keypoint & 3D object keypoint & Grasp timing & Parallel gripper \\
\cite{liu2025egozero} & 6D hand pose, 3D hand keypoint & 3D object keypoint & Grasp timing & Parallel gripper \\
\cite{chen2025web2grasp} & MANO & Object point cloud & Point-to-point distance & Dexterous hand \\
\cite{zhou2025you} & 6D hand pose & Object point cloud & Bimanual coordination order & Parallel gripper \\
\cite{heidinger20252handedafforder} & 2D hand mask & 2D object mask & Interaction region & Parallel gripper \\
\cite{chen2026dexterous} & 6D hand pose & 6D object pose, object mesh & Contact map & Dexterous hand \\
\cite{wang2026paws} & 3D hand trajectory, MANO & Articulated object structure & Motion type, motion axis, and motion origin & Parallel gripper \\
\bottomrule
\end{tabularx}
\end{table*}





\textit{(e) 作为机器人策略的可供性：}人类视频中的可供性可直接作为可执行动作表示，经重定向、优化或实施例专用控制器转换为机器人控制命令，从而构成更直接的动作迁移路径。
例如，机器人心灵传动~\citep{sivakumar2022robotic} 学习将单眼人类手臂运动重新定位为平滑且安全的机器人手臂轨迹，从而允许演示的手部运动本身直接定义执行的机器人行为。 \cite{arunachalam2022dexterous} 进一步将这种以手为中心的转移范式扩展为高效的学习框架。 MediaPipe~\citep{zhang2020mediapipe} 从单个 RGB 摄像头估计的指尖运动被转换为机器人演示，用于通过 IL 和 RL 训练灵巧的操作策略。作为\cite{sivakumar2022robotic}和\cite{arunachalam2022dexterous}的并行工作，\cite{qin2022one}开发了一款更匹配操作者运动结构的定制机器人手。定制的手部充当桥梁，将收集到的手部轨迹稳定地传输到多个实际指定的机器人手上。本研究提供了后续工作~\citep{singh2025hand}的代码库，进一步引入了互联网人类数据作为先验。 \cite{bahl2022human} 首先提取人类视频中交互开始和结束的时间步的手部位置以及中点。它们用于初始化机器人策略，然后通过与任务无关的在线探索策略迭代改进。然而，这些先前的工作受到视频提示模仿或现实世界中每个任务在线微调的要求的限制。为了解决这些限制，\cite{bharadhwaj2023zero} 学习场景条件手部轨迹预测模型，并通过以零镜头方式将预测轨迹映射到机器人动作，直接将其部署用于机器人操作。受到直接模仿演示的类似限制的启发，\cite{bahl2023affordances} 训练了一个可供性模型，该模型可以从与人类无关的视频帧中预测接触热图以及接触后手腕路径点。这种以手为中心的 VRB 公式以与代理无关的形式明确捕获目标交互位置和相应的操作模式。因此，学习到的可供性对于多个下游机器人学习范例来说更加通用。该作品中的可供性表现启发了许多后续作品~\citep{kannan2023deft,kuang2024ram,shi2025zeromimic,chen2025vidbot,ma2025uni}。例如，DEFT~\citep{kannan2023deft} 通过手腕旋转和手关节角度如何抓取进一步扩展了 VRB 表示。与预测手部 MANO 参数~\citep{romero2022embodied} 的 DEFT 相比，ZeroMimic~\citep{shi2025zeromimic} 而是使用 AnyGrasp~\citep{fang2023anygrasp} 来确定 VRB 选择的点云上的抓取动作。在这些工作之后，更多的工作如 RAM~\citep{kuang2024ram} 和 VidBot~\citep{chen2025vidbot} 一致地将 VRB 表示从 2D 空间扩展到 3D 空间。 RAM~\citep{kuang2024ram} 从大型多源可供性存储器中分层检索类似的演示。然后，它使用基于采样的策略将检索到的 2D 可供性提升为域内 3D 接触点和 3D 接触后方向，该策略还使用 AnyGrasp~\citep{fang2023anygrasp} 生成抓取建议。这种检索和传输设计可以实现更通用的零样本操作。继 RAM~\citep{kuang2024ram} 之后，VidBot~\citep{chen2025vidbot} 还使用普通簇作为线索将像素级轨迹从 VRB 提升到 3D。它进一步采用从粗到细的可供性模型，首先预测粗略的动作类型，然后使用扩散模型生成细粒度的 3D 交互轨迹。该设计改进了新颖场景和实施例下的零样本操作。Motion Tracks~\citep{ren2025motion} 没有遵循 VRB 风格的可供性表示，而是将可供性定义为短视野 2D 运动轨迹，捕捉图像空间中人手或机器人末端执行器的运动预测方向。通过多视图合成将预测的轨迹提升为可执行的 6D 机器人轨迹。这项工作引入了一种可学习的重定向网络，将机器人关键点映射到图像空间中的人手结构，从而缩小了体现差距。抓取时间戳是根据指尖关键点和分割对象掩模之间的接近度确定的。最近，\cite{ma2025uni} 通过明确地将相机自我运动与手部运动解耦并预测未来的手部轨迹，进一步增强了以手为中心的可供性构建。他们用时间接触和分离事件取代了先前作品中的空间接触可供性，这些事件可以由 EgoLoc~\citep{zhang2025zero,ma2025egoloc} 自动定位。

上述工作主要采用以手为中心的可供性，其中人类的手部动作作为政策构建的主要锚点。相比之下，一些工作已经转向以对象为中心的可供性，将对象转换和功能对象状态视为机器人策略的主要可执行表示。我们在 \textit{中引入了 Track2Act~\citep{bharadhwaj2024track2act} 作为机器人策略条件}。相比之下，它的开环变体属于 \textit{作为机器人策略} 的可供性。这是因为预测的以对象为中心的点轨迹被直接转换为刚性对象变换，然后重新定位为可执行的机器人轨迹。为了解决 Track2Act 固有的 2D 流和域内微调的局限性，\cite{yuan2024general} 直接训练闭环 3D 流预测模型。他们通过手掩模增强和查询点采样技术提高了所得闭环策略的零样本泛化能力。与 \cite{bharadhwaj2024track2act} 和 \cite{yuan2024general} 显式预测运动流相反，\cite{ko2023learning} 实现视频预测并通过估计帧之间的光流推断闭合形式动作。 NovaFlow~\citep{li2025novaflow} 类似地从初始图像和语言指令生成任务视频。然后，它通过深度估计和 3D 跟踪提取可操作的 3D 对象流，将其直接映射到机器人动作。它对 \cite{ko2023learning} 的主要扩展是支持铰接和可变形对象操作。考虑到上述点云 3D 流存在噪声且无法准确表示运动，\cite{yin2025object} 在仿真中学习扩散模型来预测密集的 3D 物体运动场。该运动场比基于点的流保留了更精细的物体运动细节，并且可以直接转换为可执行的零射击机器人动作。他们的实验证明了深度鲁棒性和干扰泛化相对于先前作品的优越性~\citep{bharadhwaj2024track2act,yuan2024general}。与上述基于对象流的方法相比，DITTO~\citep{heppert2024ditto} 遵循来自单个 RGB-D 人体演示的以对象为中心的轨迹转换管道。它离线提取相对物体姿态变化，重新检测当前场景中的物体，然后扭曲演示轨迹以直接机器人执行。密切相关的工作~\citep{wen2022you} 也重新投影了演示的对象轨迹以供直接执行。与 DITTO~\citep{heppert2024ditto} 相比，它在模拟中学习类别级规范对象表示，使演示的轨迹能够适应不同的对象实例。对于精确的放置任务，\cite{shan2025slot} 进一步从人类视频中转移以对象为中心的放置关系。这项工作识别被操纵的对象和目标放置槽，然后估计机器人场景中的槽级 6D 放置变换以直接执行。受益于 FoundationPose~\citep{wen2024foundationpose}、SPOT~\citep{hsu2025spot} 和 ObjectForesight~\citep{soraki2026objectforesight} 的出现，可以直接训练具有精确姿态注释的扩散模型，以预测 6D 物体姿态轨迹作为机器人策略。最近，ActiveGlasses~\citep{zou2026activeglasses} 进一步将以对象为中心的可供性扩展到主动感知。它通过智能眼镜收集以自我为中心的演示，并提取物体轨迹和人类头部运动。训练以对象为中心的 3D 点云策略来共同预测操纵轨迹和主动相机运动。与使用对象流和姿势相比，Robo-ABC~\citep{ju2024robo} 将以对象为中心的可供性表示为功能接触点。通过检索相似的物体并通过语义对应将其接触点转移到未见过的物体，无需额​​外训练即可实现零样本跨类别抓取，这启发了后续工作~\citep{kuang2024ram}。 Functo~\citep{tang2025functo} 和 MimicFunc~\citep{tang2025mimicfunc} 通过受 ReKep~\citep{huang2024rekep} 启发的 VLM 函数推理进一步扩展了以对象为中心的策略构建。他们将复杂的工具抽象为以功能为中心的空间骨架，由三个关键点定义，即抓握点、功能点和中心点。然后，他们使用语义对应将这些功能锚点跨新颖的异构工具转移以进行零样本操作。对于铰接对象，对象可供性必须进一步捕获运动结构和部分状态演化，而不仅仅是静态接触锚。 Ditto~\citep{jiang2022ditto} 通过重建零件级几何结构以及交互前后观察的关节模型，为这个方向提供了早期基础。 \citep{kerr2024robot} 相反，从单个单眼人体演示和静态物体扫描中恢复 4D 零件运动，然后规划机器人运动以重现演示的零件轨迹。 \cite{werby2025articulated} 将铰接可供性提取推向控制较少的设置，在相机运动和部分可观察性下直接从以自我为中心的人类视频中估计铰接部分轨迹和关节轴。它们使这种以对象为中心的表示在野外更容易访问。最近，Actron3D~\citep{zhang2025actron3d} 将一些未校准的单目视频中的几何形状、外观和可供性线索提炼成紧凑的神经可供性函数，其中可以检索和优化可转移的 6D 操作策略。

其他一些工作涉及以交互为中心的可供性，其中手和物体线索共同主导机器人策略的生成。一个早期的例子是 DexMV~\citep{qin2022dexmv}，它从人类视频中提取 6D 手部和物体姿势，并将其关节轨迹重新定位到机器人演示中以进行模仿学习。相比之下，K-VIL~\citep{gao2023k} 将以交互为中心的可供性表示为从人类视频中提取的一组稀疏的手部对象关键点约束。在这项工作中，可供性反映了手与物体交互引起的结构化几何关系，然后通过基于关键点的导纳控制器在机器人上再现。随后，更多的工作集中在提取手部物体关键点运动作为以交互为中心的可供性~\citep{haldar2025point,liu2025egozero,hu2025learning}。例如，Point Policy~\citep{haldar2025point} 联合编码翻译的人类手部关键点和语义上有意义的对象关键点。基于 Transformer 的策略可预测未来 3D 点轨迹，并通过刚体几何约束进一步恢复机器人动作。受这项工作的启发，EgoZero~\citep{liu2025egozero} 还通过将状态和动作表示为紧凑的点集来克服人类视频和机器人执行之间的形态差距。此外，它通过直接从智能眼镜记录中提取相同的基于点的状态动作表示，消除了 Point Policy~\citep{haldar2025point} 对多摄像机校准设置的依赖。与使用手部物体关键点作为交互可供性相比，一些相关工作将人类手部姿势和物体点云作为联合输入，用人类视频训练可直接执行的机器人策略。 \cite{ye2023learning} 提出了一种连续抓取功能，以成对的人类手部姿势和物体点云作为输入，生成平滑、连续灵巧的抓取轨迹。他们首先将大规模的人类手部物体交互轨迹重新定位为机器人演示，然后随着时间的推移学习隐式生成策略。与 \cite{ye2023learning} 类似，\cite{chen2025web2grasp} 也从联合手部物体几何中学习直接可执行的灵巧抓取策略。然而，该策略输出目标抓取姿势中机器人手和物体点云之间所需的成对距离。 YOTO~\citep{zhou2025you} 还将双手姿势与操纵对象点云一起视为机器人策略构建的以交互为中心的可供性。它采用数据扩散策略，可以有效地增强跨不同对象和位置的单个演示。 \cite{chen2026dexterous} 使用 DemoGen~\citep{xue2025demogen} 从单个重建的交互中合成不同的训练轨迹，同时保留手部物体接触结构。为了解决从人类视频中学习螺钉运动的挑战，ScrewMimic~\citep{bahety2024screwmimic}从人类视频中提取双手手腕姿势以及抓握接触点，并将两只手之间的相对运动解释为螺钉动作。然后，它通过 3D 点云对被操纵物体进行手部运动，从而使 PointNet 模型能够预测机器人双手操纵的可执行螺钉动作。 PAWS~\citep{wang2026paws} 进一步将以交互为中心的可供性提取扩展到铰接式对象操作。它提取手部轨迹和物体关节结构作为可扩展的关节监督。为了通过观察实现开放世界模仿，\cite{zhu2024vision} 从单个人类视频中提取开放世界对象图，将手和被操纵对象及其属性和关系融入到以对象为中心的操纵计划中。然后，机器人策略以该图结构计划为条件，从而能够推广到新颖的开放世界设置。考虑到这项工作只能部署在单臂机械臂上，OKAMI~\citep{li2024okami} 使用视觉基础模型来识别与任务相关的对象，并从人类视频中重新定位上半身运动。对象感知扭曲的推出轨迹用于通过行为克隆训练闭环视觉运动策略。这项工作促进了从观察到开放世界的模仿~\citep{zhu2024vision}对于人形操纵来说更加实用。相比之下，\cite{heidinger20252handedafforder} 认为特定对象区域在人与对象交互的背景下更为重要。因此，他们提出了一种从人与物体交互视频中精确提取可操作可供性区域的范例。基于 VLM 的模型经过进一步优化，可以预测图像中逐像素可供性片段。




\textit{(f) 可供性小结：}可供性提供了人类视频与机器人执行之间最明确的动作级接口，研究已从手部或物体线索扩展到联合手-物动态，并逐步用于骨干预训练、奖励构建、策略条件和直接策略生成。

\begin{itemize}[leftmargin=1em]
\setlength{\parskip}{0pt}
\item 骨干训练的功能可供性主要用作可扩展的监督信号。因此，它们通常以手工为中心且格式相对简单。相比之下，作为机器人策略的可供性是最以执行为导向的，涵盖了从以手为中心到以对象为中心和以交互为中心的公式的最丰富的范围。这一趋势表明，随着功能可供性越来越接近直接塑造机器人行为，相关的 HOI 结构变得越来越重要。

\item 具有可供性的奖励构建更多地依赖于多模式手部对象耦合。与骨干训练相比，奖励导向的方法更频繁地结合手部姿势、物体姿势和明确的交互线索（例如抓取状态和接触区域）。这种模式表明，奖励必须评估交互是否成功，而不仅仅是评估表示是否提供信息。

\item 在末端执行器类型中，用作政策条件的可供性惊人地同质。具体来说，该类别的所有代表性作品都针对平行夹具。这与经常出现灵巧手的其他三个类别形成了有趣的对比。这表明当前的条件可供性接口大多是紧凑和低维的，与灵巧的手所需的细粒度控制相比，它们更自然地与更简单的夹具控制管道兼容。


\item 相反，末端执行器类型与可供性粒度密切相关。使用灵巧手的相关工作更有可能使用高维手部表示，例如 MANO 参数、关节角度和指尖位置，而平行夹具方法更经常依赖于稀疏手部轨迹、运动流、接触点和手部对象掩模。这反映了实施例复杂性和可供性紧凑性之间的权衡。
\end{itemize}

尽管基于可供性的迁移发展迅速，但其有效性仍然在很大程度上取决于可靠的 HOI 分析、准确的空间基础和强大的重定向。这在复杂的操作任务中尤其面临挑战，特别是在具有严重遮挡、大视点变化以及不同对象和效应器类别的开放世界环境中。






\begin{figure*}[t]
  \centering
  \resizebox{\linewidth}{!}{%
  \begin{tikzpicture}[x=1cm,y=1cm,>=Stealth]
    \definecolor{timelineblue}{RGB}{120,138,150}
    \definecolor{timelinebrick}{RGB}{171,128,120}
    \definecolor{timelinegray}{RGB}{218,220,221}
    \definecolor{timelineyear}{RGB}{118,116,112}
    \definecolor{timelinebubble}{RGB}{166,206,227}

    \draw[timelinegray,line width=4.2pt,-{Stealth[length=3.6mm]}] (-0.10,0) -- (21.70,0);


    \foreach \x/\year in {0.45/2024,2.65/2025,11.45/2026} {
      \fill[timelinebubble,draw=white,line width=0.7pt] (\x,0) circle (0.17);
      \node[font=\bfseries\scriptsize,text=timelineyear] at (\x,-0.36) {\year};
    }

    \draw[timelineblue,line width=2.5pt,-{Stealth[length=2.2mm]}] (1.00,0.05) -- (1.00,0.95);
    \node[align=center,font=\fontsize{7.0}{7.8}\selectfont,text=timelineblue] at (1.00,1.24) {\timelinecite{ye2024latent}};

    \draw[timelineblue,line width=2.5pt,-{Stealth[length=2.2mm]}] (2.10,-0.05) -- (2.10,-0.95);
    \node[align=center,font=\fontsize{7.0}{7.8}\selectfont,text=timelineblue] at (2.10,-1.24) {\timelinecite{chen2024igor}};

    \draw[timelineblue,line width=2.5pt,-{Stealth[length=2.2mm]}] (3.20,0.05) -- (3.20,1.30);
    \node[align=center,font=\fontsize{7.0}{7.8}\selectfont,text=timelineblue] at (3.20,1.60) {\timelinecite{chen2025moto}};

    \draw[timelineblue,line width=2.5pt,-{Stealth[length=2.2mm]}] (4.30,-0.05) -- (4.30,-1.30);
    \node[align=center,font=\fontsize{7.0}{7.8}\selectfont,text=timelineblue] at (4.30,-1.60) {\timelinecite{bu2025agibot}};

    \draw[timelineblue,line width=2.5pt,-{Stealth[length=2.2mm]}] (5.40,0.05) -- (5.40,0.95);
    \node[align=center,font=\fontsize{7.0}{7.8}\selectfont,text=timelineblue] at (5.40,1.24) {\timelinecite{bu2025univla}};

    \draw[timelineblue,line width=2.5pt,-{Stealth[length=2.2mm]}] (6.50,-0.05) -- (6.50,-0.95);
    \node[align=center,font=\fontsize{7.0}{7.8}\selectfont,text=timelineblue] at (6.50,-1.24) {\timelinecite{kim2025uniskill}};

    \draw[timelineblue,line width=2.5pt,-{Stealth[length=2.2mm]}] (12.00,0.05) -- (12.00,0.95);
    \node[align=center,font=\fontsize{7.0}{7.8}\selectfont,text=timelineblue] at (12.00,1.24) {\timelinecite{garrido2026learning}};

    \draw[timelineblue,line width=2.5pt,-{Stealth[length=2.2mm]}] (13.10,-0.05) -- (13.10,-1.30);
    \node[align=center,font=\fontsize{7.0}{7.8}\selectfont,text=timelineblue] at (13.10,-1.60) {\timelinecite{lee2026mvp}};

    \draw[timelineblue,line width=2.5pt,-{Stealth[length=2.2mm]}] (14.20,0.05) -- (14.20,1.30);
    \node[align=center,font=\fontsize{7.0}{7.8}\selectfont,text=timelineblue] at (14.20,1.60) {\timelinecite{gao2026dreamdojo}};

    \draw[timelineblue,line width=2.5pt,-{Stealth[length=2.2mm]}] (15.30,-0.05) -- (15.30,-1.30);
    \node[align=center,font=\fontsize{7.0}{7.8}\selectfont,text=timelineblue] at (15.30,-1.60) {\timelinecite{govind2026unilact}};

    \draw[timelineblue,line width=2.5pt,-{Stealth[length=2.2mm]}] (16.40,0.05) -- (16.40,0.95);
    \node[align=center,font=\fontsize{7.0}{7.8}\selectfont,text=timelineblue] at (16.40,1.24) {\timelinecite{sun2026vla}};

    \draw[timelinebrick,line width=2.5pt,-{Stealth[length=2.2mm]}] (7.60,0.05) -- (7.60,1.30);
    \node[align=center,font=\fontsize{7.0}{7.8}\selectfont,text=timelinebrick] at (7.60,1.60) {\timelinecite{chen2025villa}};

    \draw[timelinebrick,line width=2.5pt,-{Stealth[length=2.2mm]}] (8.70,-0.05) -- (8.70,-1.30);
    \node[align=center,font=\fontsize{7.0}{7.8}\selectfont,text=timelinebrick] at (8.70,-1.60) {\timelinecite{routray2025vipra}};

    \draw[timelinebrick,line width=2.5pt,-{Stealth[length=2.2mm]}] (9.80,0.05) -- (9.80,0.95);
    \node[align=center,font=\fontsize{7.0}{7.8}\selectfont,text=timelinebrick] at (9.80,1.24) {\timelinecite{bi2025motus}};

    \draw[timelinebrick,line width=2.5pt,-{Stealth[length=2.2mm]}] (10.90,-0.05) -- (10.90,-0.95);
    \node[align=center,font=\fontsize{7.0}{7.8}\selectfont,text=timelinebrick] at (10.90,-1.24) {\timelinecite{li2025latbot}};

    \draw[timelinebrick,line width=2.5pt,-{Stealth[length=2.2mm]}] (17.50,-0.05) -- (17.50,-0.95);
    \node[align=center,font=\fontsize{7.0}{7.8}\selectfont,text=timelinebrick] at (17.50,-1.24) {\timelinecite{shi2026care}};

    \draw[timelinebrick,line width=2.5pt,-{Stealth[length=2.2mm]}] (18.60,0.05) -- (18.60,1.30);
    \node[align=center,font=\fontsize{7.0}{7.8}\selectfont,text=timelinebrick] at (18.60,1.60) {\timelinecite{luo2026joint}};

    \draw[timelinebrick,line width=2.5pt,-{Stealth[length=2.2mm]}] (19.70,-0.05) -- (19.70,-1.30);
    \node[align=center,font=\fontsize{7.0}{7.8}\selectfont,text=timelinebrick] at (19.70,-1.60) {\timelinecite{zhang2026clap}};

    \draw[timelinebrick,line width=2.5pt,-{Stealth[length=2.2mm]}] (20.80,0.05) -- (20.80,0.95);
    \node[align=center,font=\fontsize{7.0}{7.8}\selectfont,text=timelinebrick] at (20.80,1.24) {\timelinecite{dai2026conla}};

    \draw[timelineblue,line width=2.6pt,rounded corners=1pt] (0.10,-2.05) -- (0.78,-2.05);
    \node[anchor=west,font=\bfseries\footnotesize,text=timelineblue] at (0.92,-2.05) {(a) 视觉重建得到的潜在动作};

    \draw[timelinebrick,line width=2.6pt,rounded corners=1pt] (0.10,-2.42) -- (0.78,-2.42);
    \node[anchor=west,font=\bfseries\footnotesize,text=timelinebrick] at (0.92,-2.42) {(b) 视觉-动作协同重建得到的潜在动作};

  \end{tikzpicture}%
  }
  \caption{按时间顺序概述了 \textit{潜在动作下的方法，作为 Sec.~\ref{sec:latent_action_transfer} 中的桥梁}。}
  \label{fig:latent_actions_timeline}
\end{figure*}





\begin{figure}[t]
  \centering
  \includegraphics[width=1\linewidth]{figs/latent_action_transfer.pdf}
  \caption{\textit{作为桥梁} 潜在动作的高级图。插图的某些元素改编自 \cite{ye2024latent}。}
  \label{fig:latent_action_transfer}
\end{figure}



\subsubsection{潜在动作} \label{sec:latent_action_transfer}

与显式编码几何交互线索的可供性相比，\textit{潜在动作作为桥梁} 旨在直接从未标记的人类视频中学习紧凑且可转移的动作先验。典型的范式是使用潜在动作模型（LAM），其中逆动力学模型（IDM）从相邻观测中推断潜在动作，而正向动力学模型（FDM）则根据当前观测和推断的潜在动作重建或预测未来观测。不同的 FDM 重建目标进一步将学习到的潜在动作偏向于运动的不同方面，例如粗略的视觉变化或更与任务相关的动作语义。因此，我们将这种流行的基于潜在动作的桥接分为两类：来自视觉重建}的\textit{潜在动作，它仅通过重建未来的视觉观察来学习潜在动作，以及来自视觉动作共同重建}的\textit{潜在动作，它进一步约束潜在动作以共同恢复视觉转换和动作相关的输出。相关工作的时间线如图~\ref{fig:latent_actions_timeline}所示。



\textit{(a) 视觉重建得到的潜在动作：}LAPA~\citep{ye2024latent} 等方法通过 VQ-VAE 视觉重建从大规模无标注人类视频提取离散潜在动作，将其作为伪动作标签预训练潜在 VLA 模型，再结合机器人示范进行微调。IGOR~\citep{chen2024igor} 压缩初始图像与目标状态之间的视觉变化，学习统一潜在动作空间并保持跨实施例语义一致性。
Moto~\citep{chen2025moto} 相反引入了端到端模型来自回归预测未来视频剪辑的潜在运动标记的轨迹。它使用带有查询标记的 M-Former 从视频中提取潜在运动标记。在机器人策略学习期间，附加动作查询标记来预测机器人动作，协同微调运动标记预测和机器人动作规划。 GO-1~\citep{bu2025agibot} 类似地引入了顺序潜在动作标记作为中间规划接口。然而，它将它们更明确地视为大规模机器人学习的视觉-语言-潜在-动作（ViLLA）框架中的分层规划接口。这项工作还纳入了训练数据收集过程中的故障恢复数据，并进一步采用人机交互的方法来评估和完善数据质量。

考虑到先前的工作隐含地结合了与任务无关的动态，例如相机抖动、视觉噪声和其他代理的干扰，\cite{bu2025univla} 专注于以任务为中心的潜在动作，以将任务相关的动态与不相关的视觉变化解耦。具体来说，他们首先从未标记的视频中学习通用的潜在动作，然后使用 DINO 特征空间中的语言指令对其进行细化，最终实现更快的收敛和更稳健的性能。同样受到潜在动作容易受到干扰这一事实的启发，\cite{garrido2026learning} 遵循潜在动作建模的标准 IDM-FDM 范式，但通过连续约束动作和显式信息正则化重新设计了潜在动作世界模型。为了进一步抑制潜在动作学习中的视点干扰，MVP-LAM~\citep{lee2026mvp} 通过跨视点重建目标从时间同步的多视图视频中学习离散的以动作为中心的潜在动作。通过要求从一个视图推断出的潜在动作来解释从另一个视图中未来的观察结果，它减少了对特定于观点的线索的依赖，并产生了关于潜在动作的更多信息的伪动作标签。 UniSkill~\citep{kim2025uniskill} 相反，将潜在动作视为显式技能表示，并直接根据学习到的表示训练技能条件策略。该框架需要额外的人类视频提示来提取一系列与具体实施无关的技能，然后由技能条件的机器人策略执行。 DreamDojo~\citep{gao2026dreamdojo} 通过引入连续潜在动作作为大规模人类视频的统一代理动作，进一步将这一方向扩展到动作条件世界建模。与之前的工作主要使用潜在动作进行策略预训练或中间目标抽象不同，这项工作使用它们来调节通用机器人世界模型中的未来视频预测。最近，为了进一步解决基于 RGB 的潜在动作中缺乏显式 3D 几何的问题，\cite{govind2026unilact} 引入了 UniLACT，它通过深度感知的潜在预训练结合了几何结构。该模型通过显式跨模式交互学习共享 RGB 深度潜在动作，从而生成的伪动作标签为下游机器人操作编码更强的空间先验。为了进一步缓解潜在动作学习中的信息泄漏和像素级偏差问题，\cite{sun2026vla} 提出了 VLA-JEPA，这是一种 JEPA 风格的 ~\citep{assran2025v} 潜在世界建模框架，可通过潜在空间预测来学习与动作相关的状态转换。未来的观察结果仅用作监督目标，而不是重建未来的框架或直接对其进行调节，以防止潜在的行动陷入捷径。通过预测以当前潜在动作和过去潜在状态为条件的未来潜在状态，该方法鼓励更强大且以动作为中心的表示，同时与之前的多阶段方法相比简化了训练流程。




\begin{table*}[t]
\centering
\scriptsize
\setlength{\tabcolsep}{3.2pt}
\caption{将潜在行动作为桥梁的代表性方法的比较。}
\label{tab:latent_action}
\begin{tabularx}{\linewidth}{p{2.8cm}p{3.3cm}p{1.8cm}X X}
\toprule
参考和监控信号、解缠结、IDM 模型和 FDM 模型 \\
\midrule
\rowcolor{gray!15}
\multicolumn{5}{l}{\textit{视觉重建得到的潜在动作}} \\
\cite{ye2024latent} & Pixel & No & C-C-ViViT tokenizer & LWM-Chat-1M \\
\cite{chen2024igor} & Pixel & No & ViT (encoder + decoder) + ST-Transformer (encoder) & Open-Sora \\
\cite{bjorck2025gr00t} & Pixel & No & C-ViViT tokenizer + DiT & Eagle-2 VLM \\
\cite{chen2025moto} & Pixel & No & M-Former + ViT (encoder + decoder) & Moto-GPT \\
\cite{bu2025agibot} & Pixel & No & C-ViViT tokenizer & InternVL2.5-2B \\
\cite{bu2025univla} & Future DINOv2 feature & Yes & DINOv2 + C-ViViT tokenizer & Prismatic-7B \\
\cite{kim2025uniskill} & Pixel + Depth & No & Depth encoder + ST Transformer encoder + diffusion decoder & Diffusion policy \\
\cite{garrido2026learning} & Pixel + latent bottleneck regularization & No & V-JEPA2 encoder + MLP/Transformer & ViT + RoPE + AdaLN-zero world model \\
\cite{lyu2026lda} & Future DINOv3 feature & No & Qwen3-VL + DINOv3 + MM-DiT & Multi-modal diffusion Transformer \\
\cite{lee2026mvp} & Self-view and cross-view future DINO feature & No & DINOv2 + ST-Transformer encoder + spatial Transformer decoder + VQ-tokenizer & Prismatic-7B \\
\cite{gao2026dreamdojo} & Pixel & No & Spatiotemporal Transformer VAE & Cosmos-Predict2.5 \\
\cite{govind2026unilact} & Pixel + depth & No & Diffusion policy & GPT-2 \\
\cite{sun2026vla} & Future V-JEPA2 feature & No & Qwen3-VL & Autoregressive Transformer-based world model \\
\midrule
\rowcolor{gray!15}
\multicolumn{5}{l}{\textit{视觉-动作协同重建得到的潜在动作}} \\
\cite{chen2025villa} & Pixel + proprioception & No & ST-Transformer (encoder) + ViT (visual decoder) + MLP & PaliGemma-3B \\
\cite{routray2025vipra} & Pixel + perception + optical flow  & No & DINOv2 + ST-Transformer (encoder + decoder) & LWM-Chat-1M \\
\cite{bi2025motus} & Optical flow & No & DC-AE (encoder + decoder) & Qwen2.5-VL-2B + Wan 2.1 5B + Transformer \\
\cite{li2025latbot} & Pixel + action & Yes & InternVL3.5-2B encoder + SANA-1.6B decoder & PaliGemma-3B \\
\cite{shi2026care} & Future visual feature + keypoint trajectory & No & Prismatic-7B & Prismatic-7B \\
\cite{luo2026joint} & Motion token + hidden state & No & Query cross-sttention encoder + self-attention + MLP + VQ-tokenizer & InternVL3-2B \\
\cite{zhang2026clap} & Future DINOv3 feature + action (contrastive) & Yes & DINOv3 + ST-Transformer encoder + spatial Transformer decoder + VQ-tokenizer & Qwen3VL-4B \\
\cite{dai2026conla} & Pixel + action (contrastive) + vision (contrastive) & Yes & ST Transformer encoder + VQ-tokenizer + spatial Transformer decoder & Large World Model-7B \\
\bottomrule
\end{tabularx}
\end{table*}

\textit{(b) 视觉-动作协同重建得到的潜在动作：}相关工作在重建帧差之外进一步重建本体感知、光流、关键点轨迹或机器人动作，以在潜在动作中编码更明确的运动动力学。villa-X、ViPRA、MoTUS、CARE 和 JALA 等方法通过协同重建或多任务目标提升潜在动作的时序一致性、物理基础和跨数据集扩展性。

此外，一些研究人员明确地解开了潜在表征中与动作相关和与动作无关的成分（见图~\ref{fig:latent_action_transfer}（e）），从而使学习到的潜在动作更具可转移性和物理基础。例如，LatBot~\citep{li2025latbot} 将潜在动作分解为可学习的运动标记和场景标记，以将机器人引起的运动与被动环境变化分开。这些标记共同用于指导未来的帧重建和帧间动作重建。相反，CLAP~\citep{zhang2026clap} 通过将从视频转换推断出的动作相关潜在因素与从机器人轨迹导出的物理动作空间进行对比对齐来解决视觉纠缠问题。这种跨模式对齐迫使潜在空间保留与操作相关的动态，同时过滤掉背景变化和其他不相关的视觉因素。最近，ConLA~\citep{dai2026conla} 通过引入对比解开模块进一步解决了潜在动作提取中的捷径学习问题。它利用人类视频中的动作类别和时间先验。它不是仅仅依赖于重建损失，而是鼓励语义相似的动作在不同的环境中紧凑地聚集，同时将动作动态与不相关的视觉内容分开。因此，这项工作为下游机器人策略学习产生了更多以运动为中心的潜在动作。





\textit{(c) 潜在动作小结：}潜在动作通过无标注人类视频学习可迁移运动先验，是显式可供性提取的紧凑替代方案。该方向已从单步视觉重建扩展到任务过滤、多视角一致性、深度线索、世界模型、自回归规划以及动作相关信号联合重建。

尽管如此，这一类别中的一个主要挑战仍然存在，即将与动作相关的动态与令人讨厌的视觉因素（例如相机自我运动和与实施例无关的背景变化）分开。此外，尽管潜在动作可以大规模捕获可转移的运动结构，但将它们纳入特定于实施例的控制仍然需要额外的机器人数据监督。这些问题在接触丰富的交互中变得更加明显，因为仅从原始视频中很难学习物理上有意义的潜在动作抽象。








\subsubsection{动作导向迁移小结}

与面向任务和面向观察的迁移相比，面向动作的迁移提供了从人类视频到机器人执行的最直接的桥梁。它的中心目标不再是理解 \textit{应该完成哪个任务} 或 \textit{应该如何感知场景}，而是提取可以更严格地约束 \textit{机器人应该如何行动} 的表示。在此类别中，\textit{作为桥梁的可供性} 和 \textit{作为桥梁的潜在动作} 代表了动作转移的两种互补哲学。基于可供性的方法强调明确的行动基础。它们揭示了几何交互线索，例如手部轨迹、物体运动流和手部与物体的关系。因此，它们为重新定位、奖励塑造、政策调节和直接政策构建提供了可解释的界面。相比之下，基于潜在动作的方法将行为压缩为从大规模视频中学习的隐式动作抽象。他们牺牲几何明确性来换取更好的可扩展性和更广泛的野外人类数据覆盖范围。它们的差异本质上反映了 \textit{物理可解释性} 和 \textit{数据可扩展性} 之间的权衡：可供性提供更强的基础和可控性，而潜在操作为吸收大规模行为先验提供了更经济的途径。

这一类别的一个明显趋势是，面向行动的迁移正在朝着日益结构化和可执行的表示方向发展。基于可供性的方法已经从简单的以手为中心的线索发展到更丰富的以对象为中心和以交互为中心的公式。潜在动作方法已经从外观驱动的重建发展到时间上更加连贯、以任务为中心和物理信息丰富的运动抽象。这些进展表明，成功的动作转移需要捕获可见的运动模式，同时保留使这些运动可以跨实施例执行的交互结构。尽管如此，这两个方向仍然存在共同的瓶颈。从人类视频中学习到的动作表示最终必须基于与机器人兼容的动作空间，保持物理有效性和跨领域通用性。因此，未来的进展可能取决于两种范式的优势的结合。例如，显式可供性可以对潜在动作施加更强的物理约束，而潜在动作学习可以提高基于可供性的迁移的可扩展性和鲁棒性。这种集成对于使面向动作的传输成为可扩展的机器人从人类视频中学习的更可靠的接口至关重要。

\subsection{跨数据配置与学习范式的桥接机制}

上述分类是由 \textit{组织的，} 中间信息从人类视频传输到机器人。一个同样重要的跨系列问题是 \textit{的数据配置} 和 \textit{每个桥接器最自然地支持哪些学习范式}。对于数据配置，我们关注不同的观点偏好以及对机器人数据的依赖程度。对于学习范式，讨论了模仿学习、强化学习和其他相关的政策学习方案。在这里，我们使用评论作品中的主要设计选择来分析这两个维度。我们希望这能够启发未来 LfHV 文献中数据源选择和学习范式的工作。


\begin{table*}[t]
\centering
\scriptsize
\setlength{\tabcolsep}{4pt}
\renewcommand{\arraystretch}{1.15}
\begin{tabularx}{\textwidth}{
>{\raggedright\arraybackslash}p{2.6cm}
>{\raggedright\arraybackslash}p{1.6cm}
X
>{\centering\arraybackslash}p{1.6cm}
}
\toprule
定向传输&视图类型&参考&百分比\\
\midrule

\multirow{5}{*}{Task-oriented}
＆ 自我
& \cite{pertsch2022cross,lin2025physbrain,li2026act}
& 13\% \\

＆Exo
& \cite{yang2015robot,sermanet2016unsupervised,nguyen2018translating,yu2018one,yu2018one_hil,sharma2019third,yang2022learning,xu2023xskill,ding2024knowledge,jain2024vid2robot,chen2024vlmimic,clark2025action,chen2025fmimic,hori2025interactive,hori2025robot}
& 65\% \\

& 自我+Exo
& \cite{jang2022bc,wake2024gpt,wang2024vlm,ma2025egoloc,ye2025watch}
& 22\% \\

\midrule

\multirow{10}{*}{Observation-oriented}
＆ 自我
& \cite{ma2022vip,nair2022r3m,bhateja2023robotic,chang2023look,duan2023ar2,ma2023liv,majumdar2023we,mendonca2023structured,wu2023unleashing,li2024ag2manip,liu2024masked,zeng2024learning,goswami2025world,jiang2025rynnvla,lepert2025masquerade,li2025h2r,li2025mimicdreamer,punamiya2025egobridge,song2025mitty,sun2025vtao,xiong2025ag2x2,freeman2026warped,ye2026visual}
& 49\% \\

＆Exo
& \cite{sermanet2017time,liu2018imitation,schmeckpeper2020reinforcement,smith2020avid,xiong2021learning,bahl2022human,sun2022learning,zakka2022xirl,jain2024vid2robot,qian2024contrast,zhu2024vision,ci2025h2r,kedia2025one,lepert2025phantom,liu2025immimic,shah2025mimicdroid,tang2025trajectory,zhang2025generative,zhu2025learning}
& 40\% \\

& 自我+Exo
& \cite{xiao2022masked,xiong2022robotube,dasari2023unbiased,radosavovic2023real,cheang2024gr}
& 11\% \\

\midrule

\multirow{18}{*}{Action-oriented}
＆ 自我
& \cite{lee2017learning,bahl2023affordances,bharadhwaj2023towards,bharadhwaj2023zero,kannan2023deft,shaw2023videodex,ju2024robo,kuang2024ram,srirama2024hrp,yuan2024general,ye2024latent,cai2025n,cheang2025gr,chen2025vidbot,feng2025spatial,heidinger20252handedafforder,hsu2025spot,jiang2025rynnvla,kareer2025egomimic,kareer2025emergence,li2025scalable,liu2025egozero,luo2025being,ma2025egoloc,ma2025uni,papagiannis2025r,qiu2025humanoid,shi2025zeromimic,wen2025gr,werby2025articulated,yang2025ar,yang2025egovla,yoshida2025developing,yuan2025motiontrans,zhang2025actron3d,zhang2025zero,bi2025motus,bu2025univla,bi2026h,chen2026dexterous,gao2026dreamdojo,li2025latbot,luo2026being,luo2026joint,lyu2026lda,soraki2026objectforesight,wang2026paws,zhang2026clap,zhang2026unidex,zheng2026egoscale,zhu2026emma}
& 52\% \\

＆Exo
& \cite{sieb2020graph,das2021model,arunachalam2022dexterous,bahl2022human,qin2022dexmv,qin2022one,wen2022you,gao2023k,gu2023rt,ko2023learning,kumar2023graph,wang2023mimicplay,wang2023robot,wen2023any,ye2023learning,bahety2024screwmimic,heppert2024ditto,li2024okami,xu2024flow,chen2025graphmimic,chen2025vividex,dan2025x,garrido2026learning,haldar2025point,hsieh2025dexman,jonnavittula2025view,li2025novaflow,lum2025crossing,park2025demodiffusion,ren2025motion,shan2025slot,singh2025deep,singh2025hand,spiridonov2025generalist,tang2025functo,tang2025mimicfunc,yang2025tra,yin2025object,zhao2025dexh2r,zhou2025human,zhou2025you}
& 41\% \\

& 自我+Exo
& \cite{mandikal2022dexvip,sivakumar2022robotic,bharadhwaj2024track2act,bjorck2025gr00t,chen2024igor,chen2025villa,kim2025uniskill,lee2026mvp}
& 7\% \\

\bottomrule
\end{tabularx}
\caption{LfHV 研究以自我为中心、外向中心以及以自我为中心+外向中心的视频配置。}
\label{tab:oriented_ego_exo_breakdown}
\end{table*}


\begin{figure*}[t]
  \centering
  \includegraphics[width=1\linewidth]{figs/yearly_grouped_bar_all.pdf}
  \caption{自我中心、外向中心、自我中心+外向中心视频配置的流行趋势。}
  \label{fig:yearly_grouped_bar_all}
  \vspace{-0.3cm}
\end{figure*}




\subsubsection{跨数据配置}

就数据配置而言，第一个主要区别是外中心（第三人称）和自我中心（第一人称）人类视频之间的区别。外心视频通常提供更清晰的全局场景布局和多阶段任务上下文。因此，当桥梁以粗略的任务和场景粒度运行时，它们很有吸引力。相比之下，以自我为中心的视频更直接地暴露手部物体接触、操作顺序和第一人称操作线索。当桥梁必须保留细粒度的交互几何形状或精确的动作计时时，它们特别有价值。此外，另一个区别在于对机器人数据的依赖程度。一些 LfHV 方法被设计为仅从人类视频中学习，而其他方法仍然需要真实世界的机器人演示或与环境的交互，以将转移的知识转化为可执行的控制。在本节中，我们总结了数据配置的详细分类，包括观点（即纯外心视频、纯自我中心视频和混合外心-自我中心设置），以及对现实世界机器人数据的依赖（即人类视频+现实世界机器人演示、人类视频+现实世界交互、仅人类视频）。我们只列出具有这些类别的有力证据的作品。




\textit{(a) 不同迁移家族及时间演化中的视点偏好:} The three transfer families, i.e., task-, observation-, and action-oriented transfer, exhibit clearly different viewpoint affinities. As shown in Tab.~\ref{tab:oriented_ego_exo_breakdown}, task-oriented transfer is dominated by exocentric videos (65\%), with only a small fraction relying purely on egocentric data (13\%). This bias is structurally reasonable. Task-oriented methods aim to recover global procedural structure, subtask boundaries, and potential intents. These signals are easier to infer from a stable external viewpoint that preserves the full scene-level arrangement and reduces camera egomotion. In contrast, first-person views often emphasize local interaction details at the expense of holistic scene context. This makes long-horizon task decomposition less direct. The mixed-view portion (22\%) further suggests that recent studies increasingly attend to task-level generalizability across both egocentric and exocentric videos.


与任务导向的迁移相比，观察导向和行动导向的迁移是自我中心主导的。与外心对应物相比，面向观察的方法明显偏爱以自我为中心的来源（49\% vs. 40\%）。这一趋势表明，一旦桥梁从符号任务理解转向缩小视觉差距，第一人称数据就会变得更有价值。这是因为机器人通常在自己的相机视野内操纵物体，因此以自我为中心的视频为捕捉细粒度的手部运动模式和局部物体外观提供了更好的视点匹配。尽管如此，外心视频在这一类别中仍然具有很强的竞争力，因为它们稳定的视角简化了跨场景转换和进度估计。在以行动为导向的迁移中，自我中心倾向变得更加明显，其中自我中心和外中心来源分别占所评论作品的 52% 和 41%。这种更强烈的偏好在结构上是预料之中的。一旦桥接机制接近可执行动作，除了对齐视觉语义之外，保留交互几何形状和时间精确的操作线索就变得更加重要。在这一类别中，以自我为中心的视频自然优于以外为中心的视频，因为它们提供了对手部物体交互和操作时间的更近距离的观察。这些因素对于学习可供性、潜在行动和可转移行动先验至关重要。这在灵巧操作、双手协调和接触丰富的任务中尤其明显，其中抓握姿势、手腕运动或物体姿势的微妙变化可以直接决定任务的成功。此外，混合视图动作转移的一小部分表明，在面向动作的转移中，联合解决视点差距和实施例差距变得更加困难。因此，大多数方法仍然关注一种主导观点。总体而言，在面向行动的迁移中更强的自我中心主导地位表明，随着桥梁机制越来越接近机器人控制，视点对齐变得越来越与物理交互保真度联系在一起，而不仅仅是语义意识。



图~\ref{fig:yearly_grouped_bar_all}中的流行趋势进一步阐明了视点偏好是如何沿着时间轴演变的。 2022 年之前，所审查的文献绝大多数都是外向的。这种早期趋势反映了数据的可用性和方法的便利性。第三人称视频更容易在互联网上收集，并且在动作识别基准测试中已经很常见。它们还可以更好地匹配依赖静态摄像机的系统。然而，从2022年开始，以自我为中心的来源迅速扩大，很快成为增长的主要动力。特别是，以自我为中心的使用量在 2024 年之后急剧上升。这种趋势可能受益于大规模以自我为中心的数据集 ~\citep{grauman2022ego4d,liu2022hoi4d,wang2023holoassist,banerjee2024hot3d,hoque2025egodex} 和可穿戴设备（例如 Vision Pro、Aria）的出现，以及以自我为中心的 HOI 分析技术的快速改进 ~\citep{labbe2022megapose,wen2023bundlesdf,wen2024foundationpose,pavlakos2024reconstructing,karaev2024cotracker,karaev2025cotracker3}。此外，灵巧操作~\citep{shaw2023videodex,wen2025gr,zhang2026unidex}和VLA预训练~\citep{yuan2025motiontrans,kareer2025emergence,cheang2025gr}都受益于第一人称交互证据，进一步促进了大规模以自我为中心的人类视频的更广泛采用。相比之下，以自我为中心+以外为中心的混合设置主要作为一种过渡设计选择。它们有限的长期流行表明，尽管多视图融合在概念上很有吸引力，但其低效收集管道以及同步和表示对齐的实际成本仍然限制了可扩展性。值得注意的是，以自我为中心的使用在最近的 2026 年 LfHV 研究中占据了显着的主导地位。这凸显了以自我为中心的数据生态系统的快速发展以及适应以自我为中心的数据的算法的不断创新。


\begin{table*}[t]
\centering
\scriptsize
\setlength{\tabcolsep}{4pt}
\renewcommand{\arraystretch}{1.15}
\begin{tabularx}{\textwidth}{
>{\raggedright\arraybackslash}p{2.8cm}
>{\raggedright\arraybackslash}p{2.6cm}
X
>{\centering\arraybackslash}p{1.6cm}
}
\toprule
定向传输&机器人数据要求&参考&百分比\\
\midrule

\multirow{3}{*}{Task-oriented}
& 人类视频 + 真实世界的机器人演示
& \cite{yu2018one,yu2018one_hil,sharma2019third,jang2022bc,xu2023xskill,jain2024vid2robot,clark2025action,lin2025physbrain,li2026act}
& 43\% \\

& 真人视频 + 真实世界互动
& \cite{sermanet2016unsupervised,yang2022learning}
& 10\% \\

仅限人类视频
& \cite{yang2015robot,nguyen2018translating,pertsch2022cross,chen2024vlmimic,ding2024knowledge,wake2024gpt,wang2024vlm,chen2025fmimic,ma2025egoloc,ye2025watch}
& 48\% \\

\midrule

\multirow{3}{*}{Observation-oriented}
& 人类视频 + 真实世界的机器人演示
& \cite{ma2022vip,nair2022r3m,bhateja2023robotic,dasari2023unbiased,duan2023ar2,ma2023liv,majumdar2023we,radosavovic2023real,wu2023unleashing,cheang2024gr,jain2024vid2robot,li2024ag2manip,zeng2024learning,ci2025h2r,jiang2025rynnvla,kedia2025one,lepert2025masquerade,li2025h2r,li2025mimicdreamer,liu2025immimic,punamiya2025egobridge,song2025mitty,zhang2025generative,zhu2025learning}
& 51\% \\

& 真人视频 + 真实世界互动
& \cite{sermanet2017time,liu2018imitation,schmeckpeper2020reinforcement,smith2020avid,bahl2022human,chang2023look,mendonca2023structured,qian2024contrast,ye2026visual}
& 19\% \\

仅限人类视频
& \cite{xiong2021learning,sun2022learning,xiao2022masked,xiong2022robotube,zakka2022xirl,liu2024masked,zhu2024vision,goswami2025world,lepert2025phantom,shah2025mimicdroid,sun2025vtao,tang2025trajectory,xiong2025ag2x2,freeman2026warped}
& 30\% \\

\midrule

\multirow{3}{*}{Action-oriented}
& 人类视频 + 真实世界的机器人演示
& \cite{lee2017learning,das2021model,arunachalam2022dexterous,qin2022one,sivakumar2022robotic,bharadhwaj2023towards,gu2023rt,shaw2023videodex,wang2023mimicplay,wen2023any,chen2024igor,srirama2024hrp,ye2024latent,bi2025motus,bjorck2025gr00t,bu2025univla,cai2025n,chen2025graphmimic,chen2025villa,feng2025spatial,jiang2025rynnvla,kareer2025egomimic,kareer2025emergence,kim2025uniskill,li2025latbot,li2025scalable,luo2025being,qiu2025humanoid,ren2025motion,singh2025hand,spiridonov2025generalist,wen2025gr,yang2025ar,yang2025egovla,yang2025tra,yoshida2025developing,yuan2025motiontrans,zhou2025human,bi2026h,gao2026dreamdojo,garrido2026learning,lee2026mvp,luo2026being,luo2026joint,lyu2026lda,zhang2026clap,zhang2026unidex,zheng2026egoscale,zhu2026emma}
& 49\% \\

& 真人视频 + 真实世界互动
& \cite{sieb2020graph,bahl2022human,kannan2023deft,bahety2024screwmimic,chen2025vividex,jonnavittula2025view}
& 6\% \\

仅限人类视频
& \cite{mandikal2022dexvip,qin2022dexmv,wen2022you,bahl2023affordances,bharadhwaj2023zero,gao2023k,ko2023learning,kumar2023graph,wang2023robot,ye2023learning,bharadhwaj2024track2act,heppert2024ditto,ju2024robo,kuang2024ram,li2024okami,xu2024flow,yuan2024general,chen2025vidbot,dan2025x,haldar2025point,heidinger20252handedafforder,hsieh2025dexman,hsu2025spot,li2025novaflow,liu2025egozero,lum2025crossing,ma2025egoloc,ma2025uni,papagiannis2025r,park2025demodiffusion,shan2025slot,shi2025zeromimic,singh2025deep,tang2025functo,tang2025mimicfunc,werby2025articulated,yin2025object,zhang2025actron3d,zhang2025zero,zhao2025dexh2r,zhou2025you,chen2026dexterous,soraki2026objectforesight,wang2026paws}
& 44\% \\

\bottomrule
\end{tabularx}
\caption{LfHV 研究中对现实世界机器人数据的依赖统计。}
\label{tab:oriented_robot_data_requirement}
\vspace{-0.2cm}
\end{table*}




\textit{(b) 对机器人数据的依赖:} 
考虑到人类视频源从根本上用于减轻现实世界机器人数据的数据收集成本，我们进一步介绍了每种传输机制在机器人开始学习或执行之前如何完全解决体现差距。在这里，我们将统计数据限制在原始论文中已部署在现实世界机器人实验中的作品。具体来说，表 ~\ref{tab:oriented_robot_data_requirement} 展示了不同传输系列对现实世界机器人数据的依赖程度。可以看出，面向任务的迁移对现实世界机器人数据的依赖性最弱，其中仅人类视频占 48%。由于任务级抽象距离低级执行相对较远，因此许多面向任务的方法在没有额外的真实机器人演示的情况下仍然有效，特别是当传输的输出被符号规划、基于 VLM 的推理或程序生成模块而不是学习的视觉运动控制器消耗时~\citep{ding2024knowledge,chen2024vlmimic,chen2025fmimic,wake2024gpt,wang2024vlm,ye2025watch}。这一趋势还表明，面向任务的转移方法通常停留在 \emph{做什么} 的水平，而不是 \emph{特定机器人应该如何物理执行} 的水平。因此，当主要瓶颈在于语义任务规范而不是特定于实施例的控制基础时，面向任务的传输可以最有效地减少对机器人数据的需求。当涉及到复杂环境中的细粒度操作时，仍然需要现实世界的机器人数据来学习合理的视觉运动策略。

相比之下，面向观察和面向行动的迁移都表现出对现实世界机器人数据（机器人演示和交互）的更强依赖。对于面向观察的方法，人类视频主要通过提供翻译的观察结果或可转移的视觉表示来帮助缩小视觉域差距。然而，他们通常不会自行确定如何将这些观察结果映射到机器人动作中。因此，许多方法仍然需要域内机器人演示，将学习到的观察空间转化为可执行控制~\citep{li2024ag2manip,li2025h2r,li2025mimicdreamer,lepert2025masquerade,jiang2025rynnvla}。面向动作的迁移更接近于执行，但当基于可供性的预训练/协同训练〜\citep{srirama2024hrp,luo2025being,kareer2025egomimic,zhu2026emma}和潜在动作〜\citep{ye2024latent,chen2024igor,chen2025villa,li2025latbot}捕获的人类动作模式时，大多数相关工作仍然依赖于机器人数据，仍然必须通过机器人动作监督或与现实世界环境的交互来扎根于机器人运动学。尽管如此，面向动作的传输包含最多数量的 LfHV 作品，这些作品仅使用人类视频数据即可实现现实世界的机器人部署。这是因为面向动作的方法更有可能产生相对可执行的中间接口，例如轨迹和接触区域，这些接口可以直接重定向或与通用的现成策略（例如 AnyGrasp~\citep{fang2023anygrasp}、KAT~\citep{di2024keypoint}）集成以进行机器人控制，而无需额外的现实世界机器人演示~\citep{bahl2023affordances,bharadhwaj2024track2act,kuang2024ram,papagiannis2025r,hsu2025spot,zhang2025actron3d}。


从最近的研究中可以看出，LfHV 社区尚未完全消除对现实世界机器人数据的需求。尽管有意义的作品子集支持仅使用人类视频进行现实世界的部署，但它们在复杂目标场景中的鲁棒性，特别是在分布外的条件下，仍然需要进一步改进。在大多数现有工作中，仍然需要真实的机器人演示或交互来生成具有可行的运动学和闭环校正的机器人特定策略。因此，目前的证据表明，人类视频基本上可以作为体现数据金字塔的一层（见图~\ref{fig:data_pyramid}），但还不能完全取代一般智能体的真实机器人数据。

\begin{figure}[t]
  \centering
  \includegraphics[width=1\linewidth]{figs/data_pyramid.pdf}
  \caption{数据金字塔分别由~\cite{bjorck2025gr00t,bi2025motus,wen2025gr}定义。}
  \label{fig:data_pyramid}
  \vspace{-0.3cm}
\end{figure}






\subsubsection{跨学习范式}

除了数据配置之外，我们还进一步探讨了这些迁移家族的学习范式的差异。学习范式之间的关键区别在于，人类视频提供的是可以直接被策略使用的信号，还是通过奖励或探索先验间接塑造机器人学习的信号。前者自然地与模仿学习（IL）和 VLA 式监督后训练保持一致，而后者则更与强化学习（RL）或探索策略保持一致。除了这两个主要范式之外，很大一部分作品将人类视频转换为程序、可供性或其他结构化中间体，这些中间体通过重定向、优化或分析控制器来部署，而不是通过学习的端到端策略（如 IL 和 RL）来部署。

我们观察到，面向任务的迁移主要由 IL 式的表述所主导。这是因为任务结构和任务意图通常充当下游策略遵循的高级提示、计划或子目标规范，而不是可以直接优化的密集目标。代表性例子包括BC-Z~\citep{jang2022bc}和Vid2Robot~\citep{jain2024vid2robot}。在这些作品中，人类视频通过任务嵌入或提示视频来调节机器人策略，而最终行为仍然是通过行为克隆来学习的。相对较小的子集不属于标准 IL 或 RL，因为传输的输出是可执行的语义程序或任务计划，而不是策略监督信号本身 ~\citep{ding2024knowledge,wake2024gpt,wang2024vlm,ye2025watch}。 RL 仅偶尔出现在这一类别中，通常是在任务进度明确转换为奖励信号时~\citep{sermanet2016unsupervised}。


与面向任务的迁移相比，面向观察的迁移更加范式灵活。其核心作用是缩小人机视觉观察差距。因此，同一桥自然可以支持不同的下游范例，具体取决于如何利用视觉表示。当转换后的视频或学习的视觉特征被视为机器人对齐的策略输入时，生成的管道通常是以 IL 为中心的~\citep{li2024ag2manip,lepert2025masquerade,li2025h2r,li2025mimicdreamer}。相反，当观察桥用于定义目标相似性、进度度量或成功分数时，它变得更自然地与 RL 范式兼容~\citep{smith2020avid,zakka2022xirl}。此外，面向观察的迁移还表现出以探索策略为中心的显着方向，其中人类视频主要为探索性决策提供先验~\citep{chang2023look,mendonca2023structured,goswami2025world}。

\begin{table*}[t]
\centering
\scriptsize
\setlength{\tabcolsep}{3pt}
\renewcommand{\arraystretch}{1.15}
\begin{tabularx}{\textwidth}{
>{\raggedright\arraybackslash}p{2.3cm}
X
X
X
}
\toprule
定向传输 & 为什么它有效 & 当它倾向于失败 & 当 \\ 时更喜欢这条路线
\midrule
任务导向转移&
它在最与实施例无关的级别上传输信息。任务结构、意图和程序可以绕过低级人机动作差距并指导现有的机器人技能或规划者~\citep{ding2024knowledge,wake2024gpt,wang2024vlm,ye2025watch}。 &
当高级计划未指定用于接触丰富的执行时，当VLM生成的步骤产生幻觉或错过物理约束时，或者当机器人缺乏执行计划所需的原始技能时，它就会失败。 &
该任务是长期的或语义复杂的，目标机器人已经具有可用的技能库或控制器，主要问题是决定 \textit{下一步做什么} 而不是学习低级控制。 \\
\midrule
观察导向的转移&
它通过编辑实体外观、预测类似机器人的视图或学习共享视觉表示来减少人类视频和机器人观察之间的感知差距~\citep{nair2022r3m,li2024ag2manip,lepert2025masquerade,li2025h2r}。 &
当视觉对齐仅是外观级别时，它会失败：生成的视频可能包含伪影，共享嵌入可能会忽略与接触相关的动态，并且视觉上相似的状态可能仍然需要不同的机器人动作。 &
下游策略或控制器已经可用，或者可以使用有限的机器人数据进行训练，主要问题是改进视觉泛化、数据增强或目标/奖励匹配。 \\
\midrule
基于可供性的行动转移&
它暴露了明确的几何线索，例如接触区域、手部轨迹和物体姿势。这些线索是可检查的，可用于奖励塑造、政策调节、重新定位或直接执行〜\citep{bahl2023affordances,bharadhwaj2024track2act,kuang2024ram,chen2025vidbot,zhang2025actron3d}。 &
当 HOI 解析由于遮挡、相机运动、对象重建错误或严重的形态不匹配而不可靠时，它会失败。当力、顺从性或接触稳定性无法仅从视觉推断出来时，它也会陷入困境。 &
该任务需要空间精确操纵、单次或多次传输、以对象为中心的运动、接触定位或具有分析重定向或通用控制器的纯人类视频部署管道。 \\
\midrule
潜在作用转移&
它从大规模视频中学习紧凑的与动作相关的抽象，而不需要显式的几何注释。这使得它可以针对 VLA 预训练和异构野外数据进行扩展~\citep{ye2024latent,chen2024igor,chen2025villa,luo2025being,yang2025egovla}。 &
当潜在代码捕获相机运动、背景变化或其他令人讨厌的动态而不是可控动作时，它会失败。即使是经过充分学习的潜在动作在变得可执行之前仍然需要机器人基础。 &
目标是大规模策略预训练、跨数据集吸收人类行为，或构建通用 VLA 骨干网，其中机器人演示可用于下游基础。 \\
\bottomrule
\end{tabularx}
\caption{选择 LfHV 换乘路线的实用指南。}
\label{tab:route_selection_guidelines}
\end{table*}


以行动为导向的转移涵盖了最广泛的范式。这个家庭的很大一部分人仍然遵循模仿学习范式。这是因为，一旦人类视频提供了足够的与动作相关的线索，它们就可以更直接地用作策略学习的动作监督，而不是基于交互的优化的奖励。这种趋势在基于可供性的主干预训练和协同训练管道中尤为明显~\citep{wang2023mimicplay,kareer2025egomimic,yang2025egovla,luo2025being}。对于基于潜在动作的方法，人类视频被转换为紧凑的动作抽象，因此总是需要通过机器人演示进行额外的 IL 式后期训练~\citep{ye2024latent,chen2024igor,chen2025villa}。相比之下，基于强化学习和以探索为中心的面向行动的方法主要用于可供性直接指定优化目标的环境，或者大的实施例不匹配和复杂的交互动态使得直接模仿不可靠的环境~\citep{das2021model,sieb2020graph,kumar2023graph,lum2025crossing}。除了IL和RL范式之外，面向动作的迁移还包含最多数量的直接执行方法，例如零样本重定向、轨迹优化和可供性引导部署~\citep{bahl2023affordances,kuang2024ram,chen2025vidbot,zhang2025actron3d,shi2025zeromimic}。这是因为作为策略的可供性产生了物理基础的中间表示，这些中间表示可以直接转换为机器人动作，而无需经过完整的策略学习阶段。


可以看出，随着观察对齐、可供性提取和潜在动作建模的改进，最近的方法可以将人类视频转换为机器人对齐的观察、伪动作和可执行中间体。这使得监督政策学习和 VLA 式的后期培训在规模上更加实用。尽管如此，当具体差距很大、交互动态难以离线建模、并且需要在线细化以实现物理可行性时，强化学习仍然是不可或缺的。因此，我们认为 LfHV 未来的一个重要方向在于将大规模人类视频的 IL 式预训练与目标任务环境中基于 RL 的在线改进相结合。该方向将可扩展的先前采集与特定于任务的物理适应相结合。



\subsection{路径选择：有效性、失效模式与实践指南}
\label{sec:route_selection}

前面的部分实现了 LfHV 方法的科内分析和跨科比较。仍然存在一个实际问题：\textit{应该为新的机器人学习问题选择哪个桥？} 答案更多地取决于人类视频预期解决的瓶颈，而不是标称模型架构。如果主要瓶颈是任务规范，则高级语义桥通常就足够了。如果瓶颈是视觉域不匹配，则观察级对齐变得更合适。如果瓶颈是可执行的动作，那么桥梁必须通过可供性和潜在动作更接近动作。表~\ref{tab:route_selection_guidelines} 总结了这个决策逻辑。



因此，传输路线的有效性取决于其与机器人动作的距离。面向任务的迁移是有效的，因为语义任务知识在不同实施例之间具有高度的可迁移性，但它与机器人控制的距离使其严重依赖于下游基础。当策略失败是由视域转移引起时，观察导向的迁移是有效的，但它本身不能解决动作缺失的问题。当提取的几何线索足够接近可执行运动并且在目标视点和交互几何结构下保持可靠时，基于可供性的迁移变得有效。潜在动作转移在规模上是有效的，因为它用自监督运动抽象取代了昂贵的显式注释。然而，其隐含性质使得可控性和物理基础更难验证。

这一观点还阐明了文献中的主要失效模式。远离行动的方法通常会因 \textit{底层} 而失败：机器人理解任务但无法精确执行。接近动作的方法通常会因 \textit{错误接地} 而失败：提取的轨迹、接触线索或潜在动作在人类视频中看似合理，但违反了目标机器人的运动学、控制频率、碰撞约束或接触动力学。面向观察的方法占据中间位置，并且经常因 \textit{错误视觉等价} 而失败，其中对齐的图像或嵌入并不意味着对齐的操作。

\textbf{For practical method design, a conservative strategy is to select the highest-level bridge that still resolves the limiting bottleneck.} If a robot already has reliable low-level manipulation primitives, task-oriented transfer can provide a data-efficient route for new long-horizon tasks. If the target task is clear and the controller exists but the visual domain gap is large, observation-oriented transfer is preferable. If the target behavior depends on where and how interactions occur, explicit affordances should be prioritized because they expose checkable and explicit intermediate states. If the goal is to train a scalable generalist policy from diverse videos, latent actions or affordance-supervised VLA pretraining become more suitable. Notably, they should be paired with robot demonstrations or interaction-based refinement for embodiment grounding. In contact-rich or high-risk settings, the most robust pipeline can be conducted in a hybrid manner. That is, task-level plans provide temporal structure, observation-level modules improve perception, action-level affordances or latent actions propose motion priors, and RL or closed-loop control corrects residual physical mismatch.






\section{数据基础} \label{sec:data_foundations}

人体视频数据的获取是LfHV研究的先决条件。在本节中，我们首先介绍现有人类视频数据集的来源，然后回顾当前从头开始合成人类视频的生成技术。


  
\subsection{开源数据集}\label{sec:data_sources}



虽然通过网络爬取可以直接获取大量的人类视频，但研究人员更喜欢有针对性地组织在线视频或在受控的实验室和日常环境中录制脚本视频。这些努力产生了丰富的开源人类视频数据集生态系统，促进了 LfHV 技术的进步。
在这项工作中，我们系统地编译了这些数据集的多样化集合。与之前的调查和数据集论文~\citep{liu2022hoi4d,grauman2022ego4d,mccarthy2025towards,eze2025learning,hoque2025egodex,banerjee2024hot3d,feng2026human}相比，我们的数据集统计呈现以下主要特征：
\begin{itemize}[leftmargin=1em]
    \setlength{\parskip}{0pt}
    \item \textbf{广泛但合理的数据集覆盖范围：} 我们对 50 个人类视频数据集进行了广泛的审查，包括 2014 年至 2026 年 LfHV 研究中广泛采用或引用的数据集，以及未来应用具有巨大潜力的新兴数据集。据我们所知，这项调查比较了文献中最大数量的人类视频数据集。
    \item \textbf{数据集属性的综合报告：} 我们提出了数据集属性的综合分析，例如帧和参与者计数、地理覆盖范围、记录模式、集合类型和注释特征。这些统计数据可以帮助未来的 LfHV 研究选择最适合其特定技术要求的数据集。
    \item \textbf{数据集发展趋势的时间视图：} 我们提供过去几年数据集演变的时间顺序分析，并讨论发展趋势和未来方向。这可以帮助研究人员更好地了解数据集设计选择如何随着时间的推移而演变，并确定构建自己的数据集的有希望的方向。
    \item \textbf{数据集流行度的附加分析：} 最后，我们通过总结哪些 LfHV 研究使用了每个数据集来额外分析数据集的使用频率，从而揭示这些数据集在不同 LfHV 类别中的流行度。这可能有助于未来的数据集构建者确定哪些类型的数据集最适合其研究目标，并且最有可能在 LfHV 文献中广泛采用。
\end{itemize}

在表~\ref{tab:human_video_datasets}中，我们总结了50个人类视频数据集的以下属性：
\begin{itemize}[leftmargin=1em]
    \setlength{\parskip}{0pt}
    \renewcommand\labelitemi{\(\circ\)}
    \item \textbf{年份：} 数据集论文的发布年份。我们根据数据集首次公开发布的时间对数据集进行排序。
    \item \textbf{帧：} 数据集视频中包含的图像帧总数。
    \item \textbf{序列：} 未修剪视频的数量，这些视频通常是进一步处理之前的原始录制素材，平均长度超过 \textit{一分钟}。
    \item \textbf{剪辑：} 分段视频剪辑或动作/轨迹片段的数量，通常平均长度小于 \textit{一分钟}。
    \item \textbf{小时：} 数据集中所有视频的总持续时间。
    \item \textbf{参与者：} 参与收集数据集视频的受试者数量。
    \item \textbf{地理覆盖范围：} 数据集的地理范围或类别覆盖范围。由于这些数据集使用不同的术语来描述收集站点，例如 \textit{位置}、\textit{场景}、\textit{环境}、\textit{城市} 和 \textit{类别}，因此我们直接报告每个数据集论文中使用的原始术语。
    \item \textbf{视图：} 数据集中包含的视点类型。 \textit{Ego}：以自我为中心，第一人称。 \textit{Exo}：外心，第三人称。
    \item \textbf{相机：} 用于视频录制的相机设备，不包括用于动作捕捉的功能相机。
    \item \textbf{手型：} 视频录制是双手还是单手。
    \item \textbf{2D 手部检测：} 数据集是否提供 2D 手部边界框或分段掩模注释。
    \item \textbf{手势：} 数据集是否提供 6-DOF 手势注释。
    \item \textbf{手关节：} 数据集是否提供 3D 手关节位置标签。
    \item \textbf{姿势注释：} 用于手部姿势标记的注释协议。 \textit{Mocap}：由动作捕捉系统直接捕捉。 \textit{设备跟踪}：由耳机内置跟踪算法直接记录。 \textit{RGB}：仅根据 RGB 图像估计。 \textit{RGB(-D) + 选项。}：根据 RGB 或 RGB-D 图像进行估计并通过优化进行细化。
    \item \textbf{深度：} 是否提供原始深度观测。单眼深度估计不计算在内。
    \item \textbf{Gaze：} 是否收集注视信息。
    \item \textbf{Audio：} 是否采集音频信号。
    \item \textbf{语言描述：} 是否提供语言描述或旁白。 \textit{动词 + 名词} 形式中的短操作标签不计入在内。
    \item \textbf{来源：} 采集协议对应的数据源。 \textit{策划的}：视频是在有组织的采集设置下收集的，具有预定义的任务、设备或录制程序。 \textit{In-the-wild}：视频是从自然发生或不受约束的环境中收集的，例如网络视频或无脚本的日常录音，没有严格的收集控制。 \textit{混合}：视频是从多个开源数据集编译而来的，包括精选的和野生的来源。
\end{itemize}

表~\ref{tab:human_video_datasets} 中的一些条目是根据可用统计数据估计的。例如，可以通过将剪辑的数量乘以平均剪辑长度来计算以小时为单位的总持续时间。符号“-”表示相应信息不可用。我们强调人类手部运动的采集和注释，因为有效的手部物体交互是使人类视频数据有利于机器人学习的关键因素。通过检查人类视频数据集的属性与其发布时间之间的关系，我们观察到以下时间趋势：
\begin{itemize}[leftmargin=1em]
    \setlength{\parskip}{0pt}
    \item \textbf{视频持续时间始终较长。} 人类视频数据集的总记录时间通常非常大，往往达到数百甚至数千小时。这一趋势凸显了采集人类视频数据的便利性，并进一步证明了其与传统机器人演示数据相比的可扩展性。此外，HowTo100M~\citep{miech2019howto100m}、EPIC-KITCHENS-100~\citep{damen2020rescaling}、Panda-70M~\citep{chen2024panda}和Action100M~\citep{chen2026action100m}等野外数据集基本上比策划的数据集具有更大的规模，这得益于更方便的收集协议，例如网络爬虫或无脚本活动录音。
    \item \textbf{纯粹野外数据集的下降。} 虽然野外数据集更容易收集，但近年来它们出现的频率较低。这表明，尽管牺牲了不受约束的现实场景中的多样性，但社区越来越优先考虑数据质量、注释可靠性和可控性。例如，虽然 EgoDex~\citep{hoque2025egodex}、OakInk2~\citep{zhan2024oakink2}、TACO~\citep{liu2024taco} 和 HOT3D~\citep{banerjee2024hot3d} 都包含 $<5$ 收集场景，但许多研究人员仍然更喜欢利用它们来提取可以转移到机器人操作的高质量人体运动。
    \item \textbf{从独立数据集到混合组合。} 早期的数据集通常作为独立资源引入，具有相对固定的采集协议。然而，最近出现了明显的混合组合趋势，即将多个数据集组合起来形成更全面的训练资源，例如UniHand系列~\citep{luo2025being,luo2026joint,luo2026being}。这降低了人类视频采集的成本，同时显着提高了视点、模式和场景等不同维度的数据多样性。
    \item \textbf{越来越重视细粒度的手动注释。} 最近的数据集~\citep{luo2025being,hoque2025egodex,qiu2025humanoid,luo2026being} 更注重详细的手部姿势和关节注释。这一趋势反映出人们越来越认识到准确的手部运动建模对于将 HOI 知识转移到机器人操作中至关重要。此外，随着智能眼镜（例如Vision Pro和Aria）的发展，可以通过内置跟踪算法有效地捕获手部姿势，而不需要额外的注释管道~\citep{hoque2025egodex,chavan2025indego,qiu2025humanoid}。
    \item \textbf{更多与任务相关的语言描述。} 文本注释也随着时间的推移变得越来越完整。与早期数据集~\citep{kuehne2014language,caba2015activitynet,goyal2017something}仅以\textit{动词+名词}形式提供粗略动作标签相比，较新的数据集~\citep{chavan2025indego,zhao2025taste,chen2026action100m}更有可能包含更丰富的人类视频语言描述和旁白，更适合语言驱动的机器人学习。
\end{itemize}






\clearpage
\begin{sidewaystable}[t]
\vspace{9cm}
\centering
\tiny
\setlength{\tabcolsep}{2.2pt}
\renewcommand{\arraystretch}{1.2}
\caption{开源人类视频数据集的统计。}
\begin{tabular}{cccccccccccccccccccc}
\toprule
数据集、年份、帧、序列、剪辑、时间、参与者、地理覆盖范围、视图、相机、手型和 2D 手部检测。 &手姿势&手关节&姿势注释。 & 深度 & 凝视 & 音频 & 语言描述。 ＆ 来源 \\
\midrule
早餐~\citep{kuehne2014language} & 2014 & 4M & 1,712 & 11,267 & 77 & 52 & 18 厨房 & Exo & \makecell[c]{Prosilica GE680C,\\ Bumblebee} & 双 & \xmark & \xmark & \xmark & - & \xmark & \xmark & \xmark & \xmark & 野外\\
ActivityNet~\citep{caba2015activitynet} & 2015 & - & 27,801 & - & 849 & - & - & Exo & - & Dual & \xmark & \xmark & \xmark & - & \xmark & \xmark & \xmark & \xmark & In-the-wild \\
EgoHands~\citep{bambach2015lending} & 2015 & 130,000 & 48 & - & 1.2 & 4 & 3 个位置 & Ego & Google Glass & 双 & \cmark & \xmark & \xmark & - & \xmark & \xmark & \xmark & \xmark & 策划 \\
Charades~\citep{sigurdsson2016hollywood} & 2016 & 8.6M & - & 9,848 & 82.3 & 267 & 15 个类别 & Exo & - & 双 & \xmark & \xmark & \xmark & - & \xmark & \xmark & \xmark & \cmark & 策划 \\
FPHA~\citep{garcia2017first} & 2017 & 105,459 & - & 1,175 & - & 6 & 3 场景 & Ego & 英特尔实感 SR300 & Single & \xmark & \cmark & \cmark & Mocap & \cmark & \xmark & \xmark & \xmark & Curated \\
Something-Something~\citep{goyal2017something} & 2017 & - & - & 108,499 & 121.5 & 1,133 & - & Exo & - & 双 & \xmark & \xmark & \xmark & - & \xmark & \xmark & \xmark & \xmark & 策划 \\
YouCook2~\citep{zhou2017towards} & 2017 & - & 2,000 & 15.4K & 176 & - & - & Exo & - & Dual & \xmark & \xmark & \xmark & - & \xmark & \xmark & \xmark & \cmark & In-the-wild \\
VLOG~\citep{fouhey2017lifestyle}&2017&37.2M&-&114K&344&10.7K&6类&Exo&-&双&\cmark&\xmark&\xmark&-&\xmark&\xmark&\xmark&\xmark&野外\\
EPIC-KITCHENS~\citep{damen2018scaling} & 2018 & 11.5M & 432 & 39,596 & 55 & 32 & 32 envs & Ego & GoPro & Dual & \xmark & \xmark & \xmark & - & \xmark & \xmark & \cmark & \cmark & In-the-wild \\
EGTEA Gaze+~\citep{li2018eye} & 2018 & 2.5M & 86 & 10,325 & 28 & 32 & 1 场景 & Ego & SMI & Dual & \cmark & \xmark & \xmark & - & \xmark & \cmark & \cmark & \xmark & Curated \\
HowTo100M~\citep{miech2019howto100m} & 2019 & - & 1.22M & 136M & 134,472 & - & - & Ego + Exo & - & Dual & \xmark & \xmark & \xmark & - & \xmark & \xmark & \cmark & \cmark & In-the-wild \\
FreiHAND~\citep{zimmermann2019freihand} & 2019 & 37K & - & - & - & 32 & 1 场景 & Exo & \makecell[c]{Basler acA800-510uc,\\ Basler acA1300-200uc} & Single & \cmark & \cmark & \cmark & RGB + opt。 & \cmark & \xmark & \xmark & \xmark & 策划 \\
100DOH~\citep{shan2020understanding} & 2020 & 100K & 27.3K & - & - & - & - & Ego + Exo & - & Dual & \cmark & \xmark & \xmark & - & \xmark & \xmark & \xmark & \xmark & In-the-wild \\
EPIC-KITCHENS-100~\citep{damen2020rescaling} & 2020 & 20M & 700 & 89,977 & 100 & 37 & 45 envs & Ego & GoPro & Dual & \xmark & \xmark & \xmark & - & \xmark & \xmark & \cmark & \cmark & In-the-wild \\
Kinetics-700~\citep{smaira2020short} & 2020 & - & - & 650,317 & 1,806 & - & 6 大洲 & Exo & - & Dual & \xmark & \xmark & \xmark & - & \xmark & \xmark & \xmark & \xmark & In-the-wild \\
MOW~\citep{cao2020reconstructing} & 2020 & 500 & - & - & - & - & - & Exo & - & Single & \cmark & \cmark & \cmark & RGB + mocap + opt。 & \xmark & \xmark & \xmark & \xmark & 野外 \\
DexYCB~\citep{chao2021dexycb} & 2021 & 582K & - & 1,000 & - & 10 & 1 场景 & Exo & 英特尔实感 D415 & 单 & \xmark & \cmark & \cmark & RGB-D + 选择。 & \cmark & \xmark & \xmark & \xmark & 策划 \\
H2O~\citep{kwon2021h2o} & 2021 & 571,645 & - & - & - & 4 & 3 envs & Ego & Azure Kinect & Dual & \xmark & \cmark & \cmark & RGB-D + 选择。 & \cmark & \xmark & \xmark & \xmark & 策划 \\
Ego4D~\citep{grauman2022ego4d} & 2021 & 19.2M & 83,647 & - & 3,670 & 931 & \makecell[c]{74 个地点 /\\ 74 个城市} & Ego & \makecell[c]{GoPro、Vuzix Blade、\\ Pupil Labs、ZShades、\\ ORDRO EP6、iVue Rincon \\ 1080 和 Weeview} & Dual & \cmark & \xmark & \xmark & - & \xmark & \cmark & \cmark & \cmark & In-the-wild \\
Assembly101~\citep{sener2022assembly101} & 2022 & 111M & 4,321 & 82K & 513 & 53 & 1 场景 & Ego + Exo & - & 双 & \xmark & \cmark & \cmark & RGB + 选择。 & \xmark & \xmark & \xmark & \xmark & 策划 \\
EgoPAT3D~\citep{li2022egocentric} & 2022 & 1M & 150 & 15,000 & 10 & 2 & 15 envs & Ego & Azure Kinect DK & Single & \xmark & \xmark & \xmark & - & \cmark & \xmark & \cmark & \xmark & 策划 \\
AGD20K~\citep{luo2022grounded} & 2022 & 26,117 & - & - & - & - & - & Ego + Exo & - & 双 & \xmark & \xmark & \xmark & - & \xmark & \xmark & \xmark & \xmark & 混合 \\
HOI4D~\citep{liu2022hoi4d} & 2022 & 2.4M & - & 4,000 & 7.6 & 4 & 610 个房间 & Ego & \makecell[c]{Intel RealSense D455,\\ Kinect v2} & Single & \cmark & \cmark & \cmark & RGB-D + 选择。 & \cmark & \xmark & \xmark & \xmark & 策划 \\
OakInk~\citep{yang2022oakink} & 2022 & 230,064 & - & - & - & 12 & 1 场景 & Exo & 英特尔实感 D435 & 单 & \xmark & \cmark & \cmark & RGB-D + 选项。 & \cmark & \xmark & \xmark & \xmark & 策划 \\
EgoHOS~\citep{zhang2022fine} & 2022 & 11,243 & 1,000 & - & - & - & - & Ego & GoPro & 双 & \cmark & \xmark & \xmark & - & \xmark & \xmark & \xmark & \xmark & 混合 \\
ARCTIC~\citep{fan2023arctic} & 2023 & 2.1M & 339 & - & 2.3 & 10 & 1 场景 & Ego + Exo & - & 双 & \xmark & \cmark & \cmark & Mocap & \xmark & \xmark & \xmark & \xmark & 策划 \\
RH20T-Human~\citep{fang2023rh20t} & 2023 & 10M & 110K & - & 100 & - & - & Ego + Exo & - & 双 & \xmark & \xmark & \xmark & - & \cmark & \xmark & \cmark & \cmark & 策划 \\
HoloAssist~\citep{wang2023holoassist} & 2023 & 17.1M & 2,221 & - & 166 & 222 & - & Ego & HoloLens 2 & Dual & \xmark & \cmark & \cmark & 设备跟踪 & \cmark & \cmark & \cmark & \cmark & Curated \\
Ego-Exo4D~\citep{grauman2023ego} & 2023 & - & 5,035 & - & 1,286 & 740 & \makecell[c]{123 个场景 /\\ 13 个城市} & Ego + Exo & \makecell[c]{Aria,\\ GoPro} & Dual & \cmark & \cmark & \cmark & RGB + opt. & \cmark & \cmark & \cmark & \cmark & 策划 \\
CaptainCook4D~\citep{peddi2024captaincook4d} & 2023 & - & 384 & - & 94.5 & 8 & 10 厨房 & Ego & GoPro、Hololens 2 & Dual & \xmark & \xmark & \xmark & - & \cmark & \xmark & \cmark & \cmark & Curated \\
TACO~\citep{liu2024taco} & 2024 & 5.2M & 2.5K & - & 3.2 & 14 & 1 场景 & Ego + Exo & FLIR、Realsense L515 & Dual & \cmark & \cmark & \cmark & RGB + mocap + opt。 & \cmark & \xmark & \xmark & \xmark & 策划 \\
Panda-70M~\citep{chen2024panda} & 2024 & - & 3.8M & 70.8M & 166.8K & - & - & Ego + Exo & - & Dual & \xmark & \xmark & \xmark & - & \xmark & \xmark & \xmark & \cmark & In-the-wild \\
OakInk2~\citep{zhan2024oakink2} & 2024 & 4.01M & 627 & - & 6.5 & 9 & 4 场景 & Ego + Exo & - & Dual & \xmark & \cmark & \cmark & Mocap & \xmark & \xmark & \xmark & \xmark & Curated \\
HO-Cap~\citep{wang2024ho} & 2024 & 656K & - & 64 & - & 9 & 1 场景 & Ego + Exo & \makecell[c]{HoloLens、Intel RealSense \\D455、Azure Kinect} & Dual & \cmark & \cmark & \cmark & RGB-D + opt。 & \cmark & \xmark & \xmark & \xmark & 策划 \\
HOT3D~\citep{banerjee2024hot3d} & 2024 & 3.7M & 425 & 3,832 & 13.9 & 19 & 4 场景 & Ego & Aria, Quest3 & Dual & \xmark & \cmark & \cmark & Mocap & \xmark & \cmark & \xmark & \xmark & Curated \\
Nymeria~\citep{ma2024nymeria} & 2024 & 201.2M & 1,200 & - & 300 & 264 & \makecell[c]{20 个场景 /\\ 50 个位置} & Ego + Exo & Aria & Dual & \xmark & \cmark & \cmark & Mocap & \xmark & \cmark & \cmark & \cmark & In-the-wild \\
EgoVid-5M~\citep{wang2024egovid} & 2024 & 600M & - & 5M & - & - & 5 个类别 & Ego & - & Dual & \xmark & \xmark & \xmark & - & \xmark & \xmark & \xmark & \cmark & In-the-wild \\
Egocentric-10k~\citep{buildaiegocentric10k2025} & 2025 & 1.08B & 192,900 & - & 10,000 & 2,138 & 85 工厂 & Ego & Build AI Gen 1 & Dual & \xmark & \xmark & \xmark & - & \xmark & \xmark & \xmark & \xmark & Curated \\
Egocentric-100k~\citep{buildaiegocentric100k2025} & 2025 & 10.8B & 2,010,759 & - & 100,405 & 14,228 & 238 工厂 & Ego & Build AI Gen 1 & Dual & \xmark & \xmark & \xmark & - & \xmark & \xmark & \xmark & \xmark & Curated \\
HD-EPIC~\citep{perrett2025hd} & 2025 & 4.46M & 156 & 59,454 & 41.3 & 9 & 9 厨房 & Ego & Aria & Dual & \cmark & \xmark & \xmark & - & \xmark & \cmark & \cmark & \cmark & In-the-wild \\
PH$^2$D~\citep{qiu2025humanoid} & 2025 & 3.02M & - & 26,824 & - & - & - & Ego & \makecell[c]{Vision Pro, Quest 3,\\ ZED Mini Stereo} & Dual & \xmark & \cmark & \cmark & 设备跟踪 & \cmark & \xmark & \xmark & \cmark & Curated \\
TASTE-Rob~\citep{zhao2025taste} & 2025 & 9M & - & 100,856 & 130 & - & 6 个场景 & Ego & - & 双 & \xmark & \cmark & \cmark & RGB & \xmark & \xmark & \xmark & \cmark & 策划 \\
EgoDex~\citep{hoque2025egodex} & 2025 & 90M & - & 338K & 829 & - & 1 个场景 & Ego & Vision Pro & Dual & \xmark & \cmark & \cmark & 设备跟踪 & \xmark & \xmark & \xmark & \cmark & Curated \\
UniHand-1.0~\citep{luo2025being} & 2025 & 130M & - & 444.1K & 1,155 & - & - & Ego & - & Dual & \xmark & \cmark & \cmark & - & \xmark & \xmark & \xmark & \cmark & 混合 \\
IndEgo~\citep{chavan2025indego} & 2025 & 17.6M & 4,552 & - & 294 & 20 & 5 个类别 & Ego + Exo & \makecell[c]{Aria, Sony A6400 APSC,\\ Samsung Galaxy A51,\\ iPhone 16} & Dual & \xmark & \cmark & \xmark & 设备跟踪 & \xmark & \cmark & \cmark & \cmark & 策划 \\
LVP-1M~\citep{chen2025large} & 2025 & - & - & 1.4M & 1,167 & - & - & Ego + Exo & - & 双 & \xmark & \xmark & \xmark & - & \xmark & \xmark & \xmark & \cmark & 混合 \\
Action100M~\citep{chen2026action100m} & 2026 & - & 1.2M & 147M & 127,896 & - & - & Ego + Exo & - & Dual & \xmark & \xmark & \xmark & - & \xmark & \xmark & \xmark & \cmark & In-the-wild \\
UniHand-2.0~\citep{luo2026being} & 2026 & 400M & - & - & 35,000 & - & - & Ego & - & 双 & \xmark & \cmark & \cmark & - & \xmark & \xmark & \xmark & \cmark & 混合 \\
DreamDojo-HV~\citep{gao2026dreamdojo} & 2026 & - & 1,135K & - & 43,827 & - & 9,869 个场景 & Ego & - & 双 & \xmark & \cmark & \cmark & - & \xmark & \xmark & \xmark & \cmark & 策划 \\
UniHand-Mix~\citep{luo2026joint} & 2026 & - & - & 7.5M & 2,123 & - & - & Ego & - & 双 & \xmark & \cmark & \cmark & - & \xmark & \xmark & \xmark & \cmark & 混合 \\
\bottomrule
\end{tabular}
\label{tab:human_video_datasets}
\end{sidewaystable}
\clearpage

\clearpage
\begin{table*}[t]
\centering
\tiny
\setlength{\tabcolsep}{4pt}
\renewcommand{\arraystretch}{1.5}
\caption{LfHV 研究按其使用的开源人类视频数据集分组。}
\begin{tabular}{p{0.22\textwidth} p{0.72\textwidth}}
\toprule
数据集并由 \\ 使用
\midrule
早餐~\citep{kuehne2014language} & \citep{nguyen2018translating} \\
ActivityNet~\citep{caba2015activitynet} & \citep{rothfuss2018deep} \\
EgoHands~\citep{bambach2015lending} & \citep{lee2017learning} \\
字谜~\citep{sigurdsson2016hollywood} & \citep{qian2024contrast} \\
FPHA~\citep{garcia2017first} & \citep{ding2024knowledge,luo2025being,feng2025spatial} \\
某事~\citep{goyal2017something} & \citep{rothfuss2018deep,chen2021learning,xiao2022masked,chane2023learning,majumdar2023we,bharadhwaj2023visual,radosavovic2023real,karamcheti2023language,burns2023makes,bharadhwaj2023towards,ye2024latent,bharadhwaj2024track2act,cheang2024gr,chen2024igor,ye2025video2policy,kim2025uniskill,li2025h2r,chen2025large,chen2025visa,jiang2025rynnvla,chen2025moto,chen2025villa,li2025scalable,routray2025vipra,shi2026care,dai2026conla,lyu2026lda,sun2026vla,nie2026lary,zhang2026disentangled} \\
YouCook2~\citep{zhou2017towards} & \citep{hori2025interactive,hori2025robot} \\
VLOG~\citep{fouhey2017lifestyle} & \citep{qian2024contrast} \\
EPIC-厨房~\citep{damen2018scaling} & \citep{xiao2022masked,sivakumar2022robotic,majumdar2023we,kannan2023deft,bharadhwaj2023zero,mendonca2023structured,burns2023makes,bharadhwaj2024track2act,li2024ag2manip,cheang2024gr,chen2024igor,xiong2025ag2x2,lepert2025masquerade,song2025mitty,shi2025zeromimic,li2025scalable,chen2025villa,bjorck2025gr00t,jiang2025rynnvla,luo2026being,soraki2026objectforesight,nie2026lary} \\
EGTEA 凝视+~\citep{li2018eye} & \citep{chen2024igor,chen2025villa,li2026gazevla} \\
HowTo100M~\citep{miech2019howto100m} & \citep{mandikal2022dexvip,cheang2024gr,jiang2025rynnvla} \\
FreiHAND~\citep{zimmermann2019freihand} & \citep{sivakumar2022robotic} \\
100DOH~\citep{shan2020understanding} & \citep{xiao2022masked,patel2022learning,sivakumar2022robotic,bahl2023affordances,majumdar2023we,radosavovic2023real,dasari2023unbiased,burns2023makes,srirama2024hrp,singh2025hand,jonnavittula2025view} \\
EPIC-KITCHENS-100~\citep{damen2020rescaling} & \citep{xiao2022masked,pertsch2022cross,bahl2023affordances,ma2023liv,chang2023look,radosavovic2023real,bharadhwaj2023towards,ju2024robo,chen2025large,chen2025vidbot,heidinger20252handedafforder,jiang2025rynnvla,lyu2026lda} \\
Kinetics-700~\citep{smaira2020short} & \citep{dasari2023unbiased,cheang2024gr,zhou2025mitigating} \\
MOW~\citep{cao2020reconstructing} & \citep{patel2022learning} \\
DexYCB~\citep{chao2021dexycb} & \citep{sivakumar2022robotic,qin2022dexmv,ye2023learning,qian2024contrast,ci2025h2r,singh2025deep,luo2025being,feng2025spatial,singh2025hand,zhao2025dexh2r,chen2025vividex,luo2026joint} \\
H2O~\citep{kwon2021h2o} & \citep{kim2025uniskill,ma2025uni,luo2025being,feng2025spatial,luo2026joint,zhang2026unidex,li2026gazevla} \\
Ego4D~\citep{grauman2022ego4d} & \citep{nair2022r3m,ma2022vip,majumdar2023we,bhateja2023robotic,radosavovic2023real,chang2023look,wu2023unleashing,kannan2023deft,dasari2023unbiased,burns2023makes,bharadhwaj2023towards,zeng2024learning,cheang2024gr,srirama2024hrp,chen2024igor,chen2025large,zhou2025mitigating,bu2025univla,jiang2025rynnvla,bjorck2025gr00t,li2025h2r,heidinger20252handedafforder,yoshida2025developing,lin2025physbrain,chen2025villa,yang2025ar,li2025scalable,bu2025agibot,luo2026being,luo2026joint,zhang2026clap,lyu2026lda,nie2026lary,zhang2026disentangled,li2026gazevla} \\
组件101~\citep{sener2022assembly101} & \citep{bjorck2025gr00t} \\
EgoPAT3D~\citep{li2022egocentric} & \citep{zhang2025zero,ma2025egoloc,ma2025uni,chen2025villa} \\
AGD20K~\citep{luo2022grounded} & \citep{ju2024robo} \\
HOI4D~\citep{liu2022hoi4d} & \citep{kannan2023deft,kuang2024ram,yuan2024general,bjorck2025gr00t,wang2025gat,zhu2025learning,feng2025spatial,chen2025villa,zhang2025actron3d,luo2025being,yang2025egovla,luo2026joint,lyu2026lda,zhang2026unidex,li2026gazevla} \\
OakInk~\citep{yang2022oakink} & \citep{chen2025web2grasp} \\
EgoHOS~\citep{zhang2022fine} & \citep{kannan2023learning,soraki2026objectforesight} \\
北极~\citep{fan2023arctic} & \citep{li2025maniptrans,luo2025being,feng2025spatial,luo2026joint,lyu2026lda} \\
RH20T-人类~\citep{fang2023rh20t} & \citep{bjorck2025gr00t,zhou2025mitigating,zhu2025learning,spiridonov2025generalist,chen2025villa,lyu2026lda} \\
HoloAssist~\citep{wang2023holoassist} & \citep{bjorck2025gr00t,yang2025egovla,chen2025villa,lyu2026lda,nie2026lary,li2026gazevla} \\
自我-Exo4D~\citep{grauman2023ego} & \citep{bjorck2025gr00t,yoshida2025developing,li2025scalable,li2026act,lyu2026lda,lee2026mvp,li2026gazevla} \\
CaptainCook4D~\citep{peddi2024captaincook4d} & \citep{li2026act} \\
TACO~\citep{liu2024taco} & \citep{hsieh2025dexman,yang2025egovla,luo2025being,feng2025spatial,luo2026joint,lyu2026lda,zhang2026unidex,nie2026lary,li2026gazevla} \\
熊猫-70M~\citep{chen2024panda} & \citep{chen2025large} \\
OakInk2~\citep{zhan2024oakink2} & \citep{yuan2025hermes,li2025maniptrans,zhao2025towards,luo2025being,feng2025spatial,hsieh2025dexman,luo2026joint,lyu2026lda,li2026gazevla} \\
HO-Cap~\citep{wang2024ho} & \citep{chen2025villa} \\
HOT3D~\citep{banerjee2024hot3d} & \citep{luo2025being,ma2025uni,yang2025egovla,soraki2026objectforesight,lyu2026lda,zhang2026unidex,li2026gazevla} \\
娜梅莉亚~\citep{ma2024nymeria} & \citep{yoshida2025developing,gao2026dreamdojo,li2026gazevla} \\
EgoVid-5M~\citep{wang2024egovid} & \citep{jiang2025rynnvla} \\
HD-EPIC~\citep{perrett2025hd} & \citep{yoshida2025developing} \\
PH$^2$D~\citep{qiu2025humanoid} & \citep{cai2025n} \\
味道-Rob~\citep{zhao2025taste} & \citep{kim2025dexterous,luo2025being,feng2025spatial,lyu2026lda} \\
EgoDex~\citep{hoque2025egodex} & \citep{bi2025h,lin2025physbrain,goswami2025world,li2025mimicdreamer,li2025latbot,jiang2025rynnvla,luo2025being,feng2025spatial,cai2025n,bi2025motus,luo2026joint,gao2026dreamdojo,zheng2026egoscale,lyu2026lda,nie2026lary,li2026gazevla} \\
UniHand-1.0~\citep{luo2025being} & \citep{luo2026joint,luo2026being} \\
以自我为中心-10k~\citep{buildaiegocentric10k2025} & \citep{lin2025physbrain,luo2026being,lyu2026lda} \\
以自我为中心-100k~\citep{buildaiegocentric100k2025} & \\
IndEgo~\citep{chavan2025indego} & - \\
LVP-1M~\citep{chen2025large} & - \\
动作100M~\citep{chen2026action100m} & - \\
UniHand-2.0~\citep{luo2026being} & - \\
DreamDojo-HV~\citep{gao2026dreamdojo} & - \\
UniHand-Mix~\citep{luo2026joint} & - \\
\bottomrule
\end{tabular}
\label{tab:human_video_datasets_usedby}
\end{table*}
\clearpage

此外，Tab.~\ref{tab:human_video_datasets_usedby} 总结了哪些 LfHV 作品使用了这些数据集。我们发现Ego4D~\citep{grauman2022ego4d}和EPIC-KITCHENS系列（EPIC-KITCHENS~\citep{damen2018scaling} + EPIC-KITCHENS-100~\citep{damen2020rescaling}）是LfHV文献中最常用的人类视频源。值得注意的是，所有这些数据都是在野外收集的，这表明尽管它们的可控性较弱且视觉条件较嘈杂，但它们明显偏爱大规模自然人类交互数据。这种趋势在面向观察的视觉预训练方法（例如，R3M~\citep{nair2022r3m}、MVP~\citep{xiao2022masked}）和人类视频转换或生成方法（例如，H2R~\citep{ci2025h2r}、LVP~\citep{chen2025large}）中尤其明显，这些方法强烈偏向于大规模、弱注释和时间多样化的数据集。这些模式表明，对于可推广的表示学习和生成建模，数据规模和交互多样性通常比有限场景内的精确几何注释更有价值。与这一观察结果一致，Something-Something~\citep{goyal2017something} 也因其大规模的数据量和细粒度的动作分类而变得非常受欢迎，尽管它的参与者提供了他们表演模板的精选视频。


相比之下，像 Uni-Hand~\citep{ma2025uni} 和 Web2Grasp~\citep{chen2025web2grasp} 和 H-RDT~\citep{bi2025h} 这样的面向动作的迁移，更多地依赖于注释丰富的数据集，比如 DexYCB~\citep{chao2021dexycb}、H2O~\citep{kwon2021h2o}、 OakInk2~\citep{zhan2024oakink2}、EgoDex~\citep{hoque2025egodex} 和 HOT3D~\citep{banerjee2024hot3d}。与大型野外语料库相比，这些数据集对细粒度交互状态提供了更丰富的监督。这表明，当传输目标更接近可执行操作时，这些数据集中的显式手势等几何注释变得越来越重要。它们充当从人类视频到特定实施例的机器人动作规划的更直接的桥梁。



此外，最近的 VLA 方案（例如，EgoVLA~\citep{yang2025egovla}、Being-H0~\citep{luo2025being}）和基于潜在动作的管道（例如，GR00T N1~\citep{bjorck2025gr00t}、LDA-1B~\citep{lyu2026lda}）越来越倾向于混合数据集组合，而不是任何单一来源。 UniHand-1.0~\citep{luo2025being}、UniHand-2.0~\citep{luo2026being}和UniHand-Mix~\citep{luo2026joint}等资源的出现表明，单个数据集无法为可扩展的跨实施例传输提供足够的观点、实施例、手工注释和任务多样性的覆盖。通过将现有数据集与不同的偏差和强度相结合，这种混合可以提高数据多样性和跨域稳健性。

\subsection{人类视频生成}\label{sec:human_video_gen}

仅在开源人类视频数据集上开发 LfHV 技术仍然受到限制。这些来源通常受到已记录的有限任务、环境、观点和实施例的限制。手动收集具有所需属性的其他视频会增加人力。这种限制最近促使新兴的工作超越使用预先存在的人类视频，从头开始生成人类视频（见图~\ref{fig:nova_flow_teaser}）。通过在可控任务设置、视点和场景配置下综合人类演示，这些方法提供了一种补充途径来扩展 LfHV 以人为中心的数据的多样性、覆盖范围和适应性。接下来，我们详细介绍他们如何从头开始生成人类视频，以及如何进一步利用这些视频来导出机器人策略。

\begin{figure}[t]
  \centering
  \includegraphics[width=1\linewidth]{figs/nova_flow_teaser.pdf}
  \caption{用于机器人执行的人类视频生成的插图，最初显示在~\cite{li2025novaflow}中。}
  \label{fig:nova_flow_teaser}
\end{figure}

~\cite{bonardi2020learning} 的早期工作探索了这个方向，通过用领域随机模拟人臂视频替换训练期间的真实人类演示。它建立在任务嵌入式控制网络的基础上，从这些合成人类演示中学习任务嵌入，并使机器人能够在测试时从单个真实人类视频中进行一次性模仿。随着生成模型的快速发展，越来越多的工作致力于直接合成以语言描述为条件的与任务相关的人类或机器人交互视频。例如，UniPi~\citep{du2023learning} 将策略学习制定为文本条件视频生成问题。视频扩散模型~\citep{ho2022imagen} 首先根据任务描述和当前观察生成未来的视觉计划，然后逆动力学模型从合成视频中提取可执行动作。与 UniPi~\citep{du2023learning} 使用人类视频来优化生成规划模型不同，Gen2Act~\citep{bharadhwaj2024gen2act} 进一步将生成的人类视频纳入下游策略优化。具体来说，它使用现成的语言条件视频生成器 ~\citep{kondratyuk2023videopoet} 来合成新颖场景中的人类视频，然后根据这些生成的视频以及辅助点轨迹预测目标训练闭环机器人策略。

为了进一步减轻对大量机器人特定数据的依赖，一些工作显式地从生成的人类视频中提取对象姿势并将其重新定位到机器人末端执行器。例如，Dreamitate~\citep{liang2024dreamitate} 使用可跟踪工具对人类立体视频的视频扩散模型~\citep{van2024generative} 进行微调。在推理过程中，它会生成人类操作视频，并使用已知的 CAD 模型和立体跟踪恢复工具的 6D 姿态轨迹。轨迹直接转换为机器人末端执行器的动作。 \cite{patel2025robotic} 不使用工具，而是跟踪 Sora~\citep{brooks2024video} 和 Kling~\citep{KlingAI2024} 生成的人类视频中的 6D 对象姿势，从而实现更广泛的操作任务。这项工作还引入了 GPT-4o~\citep{achiam2023gpt} 来自动高精度地过滤掉不成功的视频生成。为了放松这项工作的刚体假设，NovaFlow~\citep{li2025novaflow} 用从 Wan~\citep{wan2025wan} 和 Veo~\cite{wiedemer2025video} 生成的视频中提取的可操作 3D 对象流取代了 6D 姿态重定向。该方法本质上是无模型的，因此适用于刚性、铰接和可变形的物体。 Dream2Flow~\citep{dharmarajan2025dream2flow}还使用以对象为中心的流作为下游控制的接口。然而，它进一步将人类视频生成 ~\citep{wan2025wan} 与 RL 相结合，其中奖励函数鼓励匹配提取的 3D 对象流。

\cite{chen2025large} 不是生成人类视频来获取物体运动信息，而是专注于提取手部运动。他们训练一个大型视频基础模型作为互联网规模的人类和机器人视频的生成规划器。该方法在灵巧操作方面表现出特别突出的性能。相反，\cite{kim2025dexterous} 通过在以自我为中心的手部网格渲染以及渲染的静态 3D 场景上调节模型，将明确的手部运动信息输入到人类视频生成中。它明确地将静态场景结构与动作引起的变化分开，使用渲染的静态场景作为空间一致的输入，并训练模型仅合成由人类操作引起的残留动态。因此，该管道鼓励关注人为引起的变化，而不是重新生成整个场景。

人类视频生成正在成为 LfHV 静态人类视频语料库的可扩展补充。现有的工作已经从早期基于模拟的合成发展到语言条件视频生成，并进一步发展到将生成的视频与姿势重定向和流提取相结合的更结构化的管道。这个方向特别有前途，因为它扩展了任务和场景覆盖范围，超出了物理记录的范围。尽管当前的零镜头视频生成模型通常会产生比机器人视频更高质量的人类视频~\citep{bharadhwaj2024gen2act}，但它们的有效性在很大程度上取决于合成交互动力学的保真度、提取物理基础运动信号的可靠性以及跨实施例传输这些信号的鲁棒性。

\section{讨论} \label{sec:discussion}

尽管前文综述的研究进展迅速，从人类视频中学习机器人技能仍远未成为成熟、标准化的范式。该领域在任务解析、视觉对齐、可供性提取、潜在动作建模和数据扩展等多个方向快速发展，但若干根本问题尚未解决：如何更好地建模人-物交互动态、利用多模态人类信号、挖掘带噪互联网数据、从单智能体模仿扩展到协作场景，以及在统一协议下评估方法。本节总结主要挑战，并讨论由此产生的研究方向。

\subsection{具有物理基础的世界模型}
大多数现有的 LfHV 方法使用人类视频为下游机器人策略提供监督、先验或中间指导。尽管在许多目标案例中有效，但这些表述过度强调局部信息，如任务计划、视觉表示、可供性或潜在动作，而没有明确建模世界在具体交互下如何在全球范围内演变。因此，它们经常难以捕获长期因果依赖性并在顺序交互阶段保持物理一致性，从而限制了它们在开放世界操纵中的鲁棒性。
尽管一些作品~\citep{wu2023unleashing,mendonca2023structured,cheang2024gr,zhu2025learning}在人类视频预测方面显示出了可喜的结果，但它们过分强调视觉相似性监督，而忽视了物理交互引起的结构变化。尽管认识到需要通过引入人体运动信息来捕获物理动力学，但最近的 DexWM~\citep{goswami2025world} 和 DWM~\citep{kim2025dexterous} 仍然忽视对建模动力学施加严格的物理约束。缺乏物理约束可能会导致不切实际的机器人动作规划，以及未来物理上无效的部署，特别是在接触丰富和长视野操作场景中。

因此，下一步是将 LfHV 扩展到 \textit{物理接地世界模型}，其中机器人不仅模仿观察到的行为，而且还学会预测未来的物理交互状态和大规模人类视频的长期后果。这样的方向可以在单一预测框架下统一当前独立的范式，例如视觉预测、可供性预测、潜在动作建模和奖励构建。更重要的是，世界模型可以为反事实推理、故障恢复和闭环执行提供天然的基础，这些对于开放世界环境中的通用操作都至关重要。然而，构建在各个实施例中保持物理基础的世界模型而不是仅仅产生视觉上合理的展示是具有挑战性的。以视觉为主的人类视频固有的局限性进一步加剧了这个问题。因此，结合额外的基于 VLM 的人类视频理解 ~\citep{cheng2024egothink,plizzari2025omnia,vinod2025egovlm,su2025annexe,lin2025physbrain} 可能提供一种实用的方法，将更强的物理推理和远程时间约束注入到这样的世界模型中。通过提高策略骨干从人类视频中解析物理规律的能力，我们可以在世界建模过程中间接施加更强的物理约束，而无需引入额外的输入模式。

\subsection{物理感知的功能可供性提取}

当前基于可供性的 LfHV 方法主要提取视觉可观察的线索，例如接触区域、手部轨迹、物体姿势和运动流。这些表示提供了有效的操作级接口，但它们通常仍然局限于 HOI 几何轨迹。对于更一般的操作，未来的可供性提取应该朝着联合编码对象或对象部分支持的物理功能、如何通过运动实现该功能以及在机器人执行过程中必须遵守哪些运动学或动态约束进行。最近的工具操纵工作为这个方向提供了早期证据。 FUNCTO~\citep{tang2025functo} 和 MimicFunc~\citep{tang2025mimicfunc} 表明，通过识别以功能为中心的结构（例如功能关键点）可以更好地迁移工具使用，而不是仅仅依赖于视觉或几何相似性。这表明可供性不仅应该描述交互发生的地点和方式，还应该描述为什么特定的接触在功能上有意义并且在物理上对于实现操纵效果是可行的。类似地，铰接式对象操作进一步强调了将物理约束纳入可供性表示的需要。 DITTO~\citep{jiang2022ditto} 通过交互重建铰接物体的几何形状和运动结构，而 \cite{kerr2024robot} 从单眼人类演示中恢复 4D 以零件为中心的运动，并规划机器人运动以重现演示的物体零件轨迹。最近的作品~\citep{werby2025articulated,wang2026paws} 进一步利用野外以自我为中心的手部物体交互来推断关节轴、零件轨迹和场景级运动结构。这些研究表明，对象可供性不应被单独视为静态区域或自由形式轨迹。相反，它们应该受到物理属性和操作语义的约束。

因此，一个有前途的未来方向是开发 \textit{物理感知功能可供性提取} 方法，将视觉交互证据、语义功能和物理结构集成到统一的表示中。这种可供性不仅可以指定接触区域或运动轨迹，还可以指定预期的对象功能、操作部分、可行的交互模式以及控制执行的物理约束。这将使基于可供性的迁移对于工具、铰接物体和接触丰富的操作更加稳健，其中成功的机器人执行取决于尊重物体功能和物理可行性，而不仅仅是以视频形式再现观察到的人类运动。


\subsection{利用人类视频数据进行持续学习}

最近的机器人基础模型和 VLA 系统越来越依赖于大规模异构数据，以及特定于任务或实施例的后训练~\citep{black2024pi_0,bjorck2025gr00t,luo2025being,yang2025egovla,lyu2026lda}。在这种范式中，人类视频通常充当固定的离线语料库。然而，大多数现有的 LfHV 管道仍然缺乏在初始训练阶段后合并新可用的人类视频的系统机制。这种静态表述对于开放式机器人学习来说越来越不够，因为新的物体和环境不断出现。然而，与真实的机器人演示相比，人类视频提供了关于新任务的更便宜、更可扩展的更新，值得持续学习更多关注。

因此，一个有前途的未来方向是开发 \textit{持续学习范例}，它可以不断吸收人类视频数据作为不断增长的具体经验来源。以自我为中心的视频可能会不断丰富 VLA 模型的第一人称操作先验。潜在动作模型可以将新收集的视频转换为伪动作监督，以进行可扩展的策略后训练。基于可供性的管道受益于更新的交互可供性，而无需为每个新任务进行密集的机器人演示。实现这一方向需要质量感知过滤、基于内存的样本选择、高效适应和持续评估，并可能从终身机器人学习基准~\citep{liu2023libero}中汲取灵感。


\subsection{多智能体交互}

尽管一些研究人员专注于从人类视频中学习双手操作策略~\citep{bahety2024screwmimic,li2025maniptrans,zhou2025you,bi2026h}，但几乎所有现有的 LfHV 方法都是在单代理假设下开发的。也就是说，一个人展示了一种操纵行为，而一个机器人则有望重现该行为。尽管这个公式涵盖了许多规范的操作设置，但它并没有完全反映现实世界具体任务的协作性质（即从人与人的协调到机器人与机器人或人与机器人的协作）。在实践中，许多任务涉及代理之间的协调交互，例如切换、联合对象传输和协作组装。特别是，一个人和另一个人之间的交互包含丰富的协调模式，包括角色分配、时间同步和对象运动的共享约束。然而，当前的 LfHV 管道在支持必须在共享环境中联合行动的多机器人系统方面的能力仍然有限。

因此，我们预计将进一步探索将 LfHV 从单智能体模仿扩展到 \textit{多智能体交互} 建模。可能的方向包括用于协调行为的角色感知潜在动作建模，以及将协作任务分解为具有显式同步的特定于代理的子目标的分层规划框架。然而，实现这些方向并非易事。与单代理设置相比，多代理交互引入了一些额外的挑战。首先，该框架必须解决跨时间的代理通信。此外，它必须解开来自多个代理的重叠运动。此外，它需要跟踪跨代理和共享对象发生的联系事件。最后，它必须对一个代理的行为如何改变另一个代理的可行操作空间进行建模。人类和机器人之间的实施方式不匹配极大地阻碍了上述进步。还需要更合适的数据集来从人类视频中学习多智能体协作操作。朝这个方向前进将大大拓宽 LfHV 的范围，从个人技能转移到协调的多智能体行为。


\subsection{人类视频伴随的多模态信号}

人类感觉运动体验本质上是多模式的，而人类视频提供了以视觉为中心的监督源。因此，当仅从像素中很难观察到关键的交互证据时，仅从人类视觉观察中进行学习的机器人通常会陷入困境。尽管许多 LfHV 作品结合了来自 RGB-D 相机~\citep{zhu2024vision,bharadhwaj2024track2act,ma2025uni} 或度量深度估计~\citep{chen2025vidbot,li2025novaflow,govind2026unilact} 的深度信息，但观察到的空间结构在视觉模态中受到限制，仍然容易受到遮挡和模糊交互状态的影响。随着任务场景变得更加多样化和复杂，这种过度依赖视觉模式的限制在依赖于材料的交互和主动感知中将变得更加明显。

因此，通过伴随人类视频} 的更丰富的 \textit{多模态信号来扩展以视觉为中心的学习中的 LfHV 是一个有前途的方向。 \textit{音频} 可以说是最容易合并到现有 LfHV 框架中的，因为它可以以最低的额外成本与视频一起获取。互联网人类视频通常包含同步音频，而便携式摄像设备（例如智能手机、眼镜）始终提供内置音频录制功能。音频模态可以揭示难以通过视觉观察的交互证据，例如音频触发的动作、遮挡的接触事件、材料相关的响应和故障信号。将音频提示与其相应的视觉源相关联〜\citep{seth2026egoavu,zhu2026egosound}可以进一步提高对机器人策略生成的人类行为的理解。 \textit{Gaze} 提供了人类注意力和意图的明确指示器，这可以帮助机器人定位与任务相关的对象并解决模糊的交互目标。在长视距操纵和主动感知设置中，利用凝视模式可以帮助机器人预测相变并确定下一步要去哪里。 GazeVLA~\citep{li2026gazevla} 提供了一个开创性的例子，表明凝视可以在 VLA 框架中明确建模为中间意图信号。如表~\ref{tab:human_video_datasets} 中所总结的，一些开源人类视频数据集已经提供了音频和注视注释。特别是 EGTEA Gaze+~\citep{li2018eye}、Ego4D~\citep{grauman2022ego4d}、HoloAssist~\citep{wang2023holoassist}、Ego-Exo4D~\citep{grauman2023ego}、Nymeria~\citep{ma2024nymeria}、HD-EPIC~\citep{perrett2025hd} 和IndEgo~\citep{chavan2025indego} 包括这两种模式。这些资源为未来考虑音频和注视输入的 LfHV 研究提供了宝贵的数据基础。


随着以自我为中心的触觉资源（例如 EgoTouch~\citep{zhou2026touchanything}、\textit{触觉信息}）的出现，可以通过揭示接触力、滑动、顺应性和微妙的表面相互作用来进一步补充视觉，而这些相互作用很难仅从 RGB 观察中恢复。鉴于大多数现有的人类视频数据集不提供同步触觉感知，利用 TouchAnything~\citep{zhou2026touchanything} 等基础触觉预测模型来生成伪触觉注释是一个相对实用的解决方案。


将这些模式有效地集成到 LfHV 中仍然具有挑战性，因为它们在时间分辨率、噪声特性和实施例依赖性方面存在很大差异。尽管如此，多模态公式提供了一条超越外观驱动迁移的有前途的途径，以更全面地理解人与物体的交互。这最终可能会提高接触丰富的操纵策略的稳健性，并实现从人类到机器人更忠实的技能转移。


\subsection{低质量人类视频的利用}

现有的 LfHV 方法通常受益于互联网人类视频数据的规模和多样性。然而，此类数据的很大一部分本质上是低质量的，表现出低分辨率、运动模糊、严重遮挡、相机抖动、时间相干性弱，甚至任务执行不完整或失败。此外，一些大型以自我为中心的视频数据集（例如Ego4D~\citep{grauman2022ego4d}）包含许多被动观察数据，而主动操作的视频更直接有利于机器人策略学习。为了避免这些问题，当前的管道要么依赖于相对精心策划的数据集，要么在训练之前积极过滤嘈杂的网络数据~\citep{chen2024igor,cheang2024gr,cheang2025gr,zhao2025dexh2r,bjorck2025gr00t,luo2026joint}。虽然这提高了数据的清洁度，但它也降低了人类视频的可扩展性优势，并丢弃了许多可能对泛化机器人学习有价值的长尾交互模式。

因此，开发能够让 \textit{更好地利用低质量人类视频} 而不是简单丢弃它们的 LfHV 框架非常重要。实现这一目标可能需要质量感知的表示学习和不确定性感知的监督。它还可能受益于强大的伪标签和跨视频一致性建模，这样机器人仍然可以从嘈杂的观察中提取可靠的任务语义、交互动态和动作先验。更重要的是，低质量的人类数据通常反映了机器人在开放世界环境中必须处理的视觉模糊性、场景混乱和视角变化。提高 LfHV 模型从不完美的人类视频数据中学习的能力可能是实现可扩展和通用的机器人技能获取的关键一步。



\subsection{标准化基准评测}

尽管 LfHV 工作数量不断增加，该领域的基准评测仍高度碎片化。现有工作往往使用不同机器人、任务设置和人类视频来源进行评估，因此尚不清楚哪些连接人类视频与机器人执行的技术选择真正带来了更好的迁移性能。

未来研究的一个有希望的方向是针对 LfHV 的特征开发更标准化的基准测试协议。一个特别重要的挑战是，大多数 LfHV 无法仅在仿真中轻松进行基准测试，例如 CALVIN~\citep{mees2022calvin}、LIBERO~\citep{liu2023libero} 和 RoboTwin~\citep{mu2025robotwin}。由于可控环境和可重复评估，仿真在传统机器人学习和 VLA 文献中很有吸引力。然而，许多 LfHV 作品从根本上依赖于域内真实的人类视频，其外观、摄像机运动、交互动态和体现特征很难在模拟器中忠实地再现。因此，新的评估协议可能需要构建与原始视频捕获场景密切对应的多样化高保真模拟环境。这可以通过先进的场景重建技术（例如 3D Gaussian Splatting~\citep{kerbl20233d}）来实现。除了任务成功率之外，未来的进展还可能涉及支持时间视频理解质量〜\citep{lin2025physbrain,zhang2025zero}和人体运动预测〜\citep{ma2025novel,chen2025flowing}的策略骨干能力。

\subsection{第一视角数据生态系统}

最终，LfHV 领域体现了 \textit{以自我为中心的数据生态系统} 日益重要的意义。与第三人称（外中心）人类视频相比，以自我为中心的观察与具体主体的感知设置更加一致，尤其是在操纵、主动感知和意图推理方面。虽然EPIC-KITCHENS系列〜\citep{damen2018scaling,damen2020rescaling}，Ego4D〜\citep{grauman2022ego4d}，EgoDex〜\citep{hoque2025egodex}，HOT3D〜\citep{banerjee2024hot3d}和其他新兴的更大规模的自我中心资源〜\citep{li2026egolive}的流行证明了LfHV中自我中心数据的有效性，但最近的发展，例如EgoVerse~\citep{punamiya2026egoverse} 进一步强调，关键挑战不仅仅是数据集规模，而是如何在统一框架下支持个人研究人员、学术实验室和行业合作伙伴的持续贡献。

一个成熟的以自我为中心的 LfHV 数据生态系统应该超越一次性静态发布。相反，它应该支持标准化的收集协议、共享任务语义、统一的存储和访问接口以及对下游机器人学习直接有用的操作相关注释。这样的生态系统可以将以自我为中心的人类视频与 3D 手部和头部姿势、语言描述以及更丰富的多模态数据（例如前面提到的音频、凝视和触觉信号）集成起来。它还应该通过轻量级收集和众包注释方案降低贡献障碍，同时通过跨实验室和机器人实施例的标准化处理和共享评估协议保持可重复性。建立这种生态系统将大大减少重复工作，并为可扩展、多模式和可重复的 LfHV 研究提供更坚实的基础。


\subsection{挑战与未来方向小结}

上述讨论为 LfHV 的下一阶段提出了几个紧密相连的方向。就 \textit{新建模范式} 而言，未来的方法可能需要超越本地转移线索，转向物理接地世界模型、物理感知功能可供性、持续学习范式和多智能体交互建模。它们将帮助机器人更好地推理长期物理动力学和协作约束。就 \textit{更丰富的数据模态} 而言，进展可能依赖于整合多模态人类信号，例如音频、凝视和触觉信息，以及更好地利用低质量但高度可扩展的互联网人类视频。就 \textit{更标准化的基准测试} 而言，该领域仍然需要公平连接人类视频理解、跨实施例传输和下游机器人执行的评估协议，特别是因为许多 LfHV 方法无法仅在模拟中进行充分的基准测试。就 \textit{更具协作性的生态系统} 而言，不断增长的以自我为中心的数据基础设施为可扩展的收集、更丰富的注释以及跨实验室和实施例的可重复比较提供了实践基础。


这些可能的未来方向表明，LfHV 的长期发展不仅仅是收集更多人类视频或设计更强大的政策支柱的途径。相反，它需要一个共享和集成的基础设施，其中建模、数据、评估和生态系统开发共同发展。更强大的模型必须得到更丰富、更结构化的人类数据的支持。更大的数据集还必须伴随着更好的基准和更具可重复性的评估协议。与此同时，开放和协作的数据生态系统对于维持实验室、任务和机器人实施例的持续进步至关重要。这些共同进步可以促进 LfHV 研究为具身智能奠定更具可扩展性和通用性的基础。





\section{结论} \label{sec:conclusion}

从人类视频中学习机器人技能已成为缓解机器人操作数据瓶颈的有前景途径。本文围绕\emph{人机技能迁移}与\emph{数据基础}两条主线综述了该领域：首先回顾人类视频与机器人策略学习的接口，再将现有方法组织为覆盖任务、观测和动作层面的层次化分类。在这一视角下，人类视频可通过任务结构、任务意图、变换视频、视觉嵌入、可供性和潜在动作等多种信息流支持机器人学习。除分类体系外，我们还讨论了不同迁移家族与视角选择、机器人数据依赖和学习范式的耦合差异，揭示当前 LfHV 设计中的典型权衡，并基于分类和家族间比较给出选择 LfHV 路径的实践指南。


在人类视频来源方面，我们回顾了开源数据集以及人类视频生成的最新进展，并从统计角度分析数据集属性、发展趋势及其在 LfHV 文献中的使用情况。综述证据表明，LfHV 的进步不仅取决于更强的策略架构，也受到人类视频数据规模和可用性的塑造。该领域仍有许多开放问题，包括更忠实地建模长时域物理交互动态、利用更丰富的多模态人类信号、充分挖掘带噪互联网视频、建立更标准化的基准，以及支持可扩展的数据生态。我们希望本文能为未来 LfHV 研究提供参考，推动由人类视频驱动的更通用、更可扩展机器人学习系统发展。



\bibliographystyle{SageH}
\bibliography{main.bib}


\end{document}


> 本 Markdown 保留 LaTeX 公式、图表和引用命令，可直接作为 Markdown/LaTeX 混排文档阅读。
