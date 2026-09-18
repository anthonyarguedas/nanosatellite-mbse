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
6. Run the command: `.\.venv\Scripts\python.exe search.py --serve --open` for Windows or `.venv/bin/python search.py --serve --open` for Linux/Mac

On 64-bit Windows, `uv sync` installs the CUDA 12.8 build of PyTorch. Search uses an available NVIDIA GPU automatically and falls back to the CPU when CUDA is unavailable. A current NVIDIA driver is required.

Verify GPU access in PowerShell:

```powershell
.\.venv\Scripts\python.exe -c "import torch; print(torch.__version__); print('CUDA:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"
```
