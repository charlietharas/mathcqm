# The Cure & The Cause

Source code & more for the Williams College Mathematics Colloquium on Nov 11, 2026.

## Setup

To install dependencies:

```bash
conda env create -f environment.yml
conda activate manim
```

You'll need a standard installation of LaTeX (including `dvisvgm`).

## Build and present

Run `python deck.py --help` for commands, options, examples, and rebuild behavior. In the typical case, you'll use:

```bash
python deck.py build # usually works
python deck.py serve # host the slideshow locally
```

Access the video deck at **http://localhost:8000/** and picture mode at
**http://localhost:8000/img/**.

Black is recommended (and used here) for local Python formatting.

## Publish

```bash
python deck.py deploy
```

Pushes to GitHub pages. I really only use this to get slides live at [https://charliemax.dev/mathcqm](https://charliemax.dev/mathcqm).

## Files

```text
environment.yml       Conda environment and dependencies
deck.toml             Presentation order + other misc. config
manim.cfg             Render quality and background
deck.py               Core CLI for building, serving, etc.
_helpers.py           Shared layout, graph, network, and animation library
scenes/               One Python file per slide
slides/               Clips and metadata (auto-generated)
media/                Manim render cache (auto-generated)
dist/                 Files for serving the website (auto-generated)
```

Generated files are ignored by Git.
