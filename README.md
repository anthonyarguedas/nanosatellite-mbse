# An MBSE-Based Framework for the Design of Nanosatellite Electrical Power Systems (and various other related tools and mini-projects)

## Clone with Git LFS

Install Git LFS before cloning. This prepares the checkout for large retrieval index files.

- Windows: install Git for Windows with Git LFS enabled.
- macOS: run `brew install git-lfs`.
- Ubuntu or Debian: run `sudo apt install git-lfs`.

Then clone the repository:

```bash
git lfs install
git clone https://github.com/DeltaLabo/nanosatellite-mbse.git
cd nanosatellite-mbse
git lfs pull
```

For an existing clone, run `git lfs install` followed by `git lfs pull`.

## How to use the nanosatellite EPS paper database

1. Open a terminal window at the root of this repository.
2. Run the command: `cd embeddings`
3. Run the command: `winget install --id astral-sh.uv -e`, only when using for the first time on Windows
4. `$env:UV_CACHE_DIR = ".cache\uv"`, only on Windows
5. `uv sync`, only when using for the first time
3. Run the command: `.\.venv\Scripts\python.exe search.py --serve --open` for Windows or `.venv/bin/python search.py --serve --open` for Linux/Mac
