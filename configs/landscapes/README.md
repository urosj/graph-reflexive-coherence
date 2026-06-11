# Landscape Configs

This directory stores landscape-related configuration artifacts for `PyGRC`.

The subdirectories are separated by translation layer so source semantics and
derived artifacts do not get mixed together.

Current layout:

- `seed/`
  Canonical normalized landscape seeds that follow
  `implementation/LandscapeSeedSchema.md`.

As the project grows, this tree may also include:

- `pde/`
  source PDE landscape specifications mirrored into this repo when needed
- family-specific projector outputs or fixtures in their own clearly named
  subdirectories

The important rule is:

- different landscape layers should not share one undifferentiated directory.
