\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{sagej}[2026/09/09 Local compatibility class]
\LoadClass[UTF8,a4paper,11pt]{ctexart}
\RequirePackage{geometry}
\RequirePackage{graphicx}
\RequirePackage{caption}
\geometry{margin=2.2cm}
\newcommand{\affilnum}[1]{\textsuperscript{#1}}
\newcommand{\corrauth}[1]{\par\textbf{通讯作者：}#1}
\newcommand{\affiliation}[1]{\par\textit{#1}}
\newcommand{\email}[1]{\par\texttt{#1}}
\newcommand{\runninghead}[1]{}
\newcommand{\keywords}[1]{\par\textbf{关键词：}#1}
\newcommand{\citep}[1]{[\textsuperscript{#1}]}
\providecommand{\cite}[1]{[\textsuperscript{#1}]}
\newcommand{\citeauthor}[1]{#1}
\newcommand{\citeyearpar}[1]{#1}
\renewcommand{\maketitle}{\@maketitle}
\makeatletter
\renewcommand{\includegraphics}[2][]{\fbox{\parbox[c][3cm][c]{0.8\linewidth}{\centering 图片占位：#2}}}
\makeatother
