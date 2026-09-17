# CUHK Beamer Template

An English-first, 16:9 Beamer theme inspired by the supplied template and the colours of
The Chinese University of Hong Kong crest.

## Compile

```bash
xelatex slides.tex
xelatex slides.tex
```

## Use

1. Keep `CUHKBeamer.sty` and `assets/CUHK_Logo.png` with your presentation.
2. Set the title metadata near the top of `slides.tex`.
3. Compile with XeLaTeX.

To use a different crest file, add this after loading the theme:

```latex
\setcuhklogo{assets/your-logo-file.png}
```

The theme automatically inserts an outline frame at the start of each section.
