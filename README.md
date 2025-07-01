# TXCPAPI

**TXCPAPI** (pronounced *tek-sac-pay-pee*, obviously) is a minimalist, anarchic API for compiling TeX files. It runs without authentication, without rate limiting, and without shame. If you're looking for security, stability, or adult supervision... this isn't it.

## 🚀 Features

- Accepts `.tex` or `.zip` uploads via a `/api` endpoint
- Compiles the files using LaTeX engines (`pdflatex`, `xelatex`, etc.) or ConTeXt
- Converts output to various formats: PDF, HTML, Markdown, plain text, images
- Returns the final result directly—no signup, no storage, no questions asked
- Uptime is theoretically possible but not guaranteed.
- Comes with guaranteed bugs.

> "It will work if you're lucky or the compiler loves you. Probably." <br>
> —Me, the one who put bugs in the API

## 📦 Technologies

This project uses the following open-source tools:

| Tool | License |
|------|---------|
| [Svelte](https://github.com/sveltejs/svelte) | MIT |
| [FastAPI](https://github.com/tiangolo/fastapi) | MIT |
| [Uvicorn](https://github.com/encode/uvicorn) | BSD 3-Clause |
| [Python](https://docs.python.org/3/license.html) | PSF |
| [TeX Live](https://www.tug.org/texlive/copying.html) | Collection of free software licenses (GPL, LPPL, etc.) |
| [Poppler](https://poppler.freedesktop.org/) | GPL |
| [Pandoc](https://github.com/jgm/pandoc/blob/main/COPYING) | GPL 2.0 |
| [ImageMagick](https://github.com/ImageMagick/ImageMagick/blob/main/LICENSE) | ImageMagick License |

> Only Svelte is included in this repository. All other dependencies are installed at runtime and are not redistributed. Please refer to each project's official license for full legal information.

## 🫠 "Advanced Users" (AKA masochists)

Refer to /docs or /redoc for API documentation.