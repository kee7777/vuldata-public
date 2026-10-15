# GUIDE: Experiment Environment for Python & UQ Model



This guide helps you set up a reproducible environment to run Python experiments and the UQ (Uncertainty Quantification) model for the CISC 4900/5001 project. It includes **local (Windows)** setup with Miniconda, **cluster (Linux)** access and environment setup, verification steps, and troubleshooting.



---



## 0) Prerequisites



* Windows 10/11 (local dev) and access to the college Linux cluster (for heavy jobs)

* Git & GitHub repository cloned locally



---



## 1) Local Setup (Windows with Miniconda)


### 1.1 Installing Miniconda
```bash

# Download and install Miniconda according to your machine

https://www.anaconda.com/docs/getting-started/miniconda/install


```

### 1.2 Create and activate the environment



```bash

# Open Anaconda Prompt (Windows)

conda create -n defect-pred python=3.10 -y

conda activate defect-pred

```



### 1.3 Install core packages



```bash

conda install -y numpy pandas scikit-learn matplotlib jupyter

```



### 1.4 Verify installation



```bash

python -c "import numpy, pandas, sklearn, matplotlib; print('Local env OK')"

```



### 1.5 Launch Jupyter Notebook



```bash

jupyter notebook

```



Create a new Python 3 notebook and run:



```python

import numpy as np

import pandas as pd

from sklearn.linear_model import LogisticRegression

import matplotlib.pyplot as plt

print("Jupyter working ✅")

```



### 1.6 Export the environment (for reproducibility)



```bash

# Inside the (defect-pred) env

conda env export > environment.yml

```



Commit `environment.yml` to the repo so others can recreate the same env.



---



## 2) Cluster Access (Linux)



### 2.1 SSH into the cluster



From off campus you may need to log in to one or more gateway hosts before reaching the compute nodes. On campus, direct node access may work.



```bash

# Example (multi-step)

ssh <username>@<first-gateway>

ssh <username>@<second-gateway>

# then hop to a compute node

ssh <username>@node2    # or node4, etc.

```



On success you should see a prompt like:



```

<username>@node2:~$

```



### 2.2 Quick Python check on cluster



```bash

python3 --version

python3 -c "print('Cluster Python OK')"

```


---



## 3) Cluster Environment Setup

We will use Conda for cluster environment setup.  
Note: Conda is required for installing `git` and `screen` on the cluster.  
Please follow the Conda instructions in the next section.


### Conda on Cluster (recommended)


```bash

# Download and install Miniconda according to your machine

wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
source ~/.bashrc


# Accept ToS if prompted (newer conda)

conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main

conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r

conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/msys2



# Create & activate env

conda create -n defect-pred python=3.10 -y

conda activate defect-pred



# Install core packages

conda install -y numpy pandas scikit-learn matplotlib jupyter



# (Optional) Recreate from repo file

conda env create -f environment.yml

```



---



## 4) Automating Cluster Access (on Windows)



To avoid having to enter each IP and password to access the cluster, we can automate the process using SSH Public Key Authentication.

Note: ensure GitBash is installed on your machine



### 4.1 Generate SSH key



```bash


# ~/.ssh/nsicluster

ssh-keygen -t ed25519 -C "NSI Cluster Access" -f ~/.ssh/nsicluster

# generates a private and public key in ~/.ssh/nsicluster directory



```



To avoid SSH permission errors, run: 

```bash

chmod 600 ~/.ssh/nsicluster/id_ed25519
# ensures only you can read/write

```



### 4.2 Copying Public Key



Using GitBash, copy public key to Jump host

```bash

ssh-copy-id -i path/to/id_ed25519 <user>@<jump-host.example.edu>

```


If successful, you shouldn’t be prompted for a password.

```bash
ssh -i path/to/id_ed25519 <user>@<jump-host.example.edu>

# Example (Brooklyn College):
# <user>@wellfleet.sci.brooklyn.cuny.edu
```



### 4.3 Shortcut SSH


In the `.ssh` directory, edit/create the config file:



```config

# ~/.ssh/config
Host *
    ForwardAgent yes

Host jump_host
    HostName <jump-host.example.edu>
    Port 22
    User <user>
    IdentityFile ~/.ssh/nsicluster/id_ed25519
```



Accessing Jump Host can now be done with:

```bash
ssh jump_host
```



### 4.4 Passing Public Key to Cluster



To copy key to cluster, create shortcut to server using jump_host as an intermediary with ProxyJump



```config

# ~/.ssh/config
Host cluster_head
    HostName <cluster-head.example.edu>
    Port 22
    User <user>
    ProxyJump jump_host

# Example (Brooklyn College):
# <user>@wellfleet.sci.brooklyn.cuny.edu
```


To send key to cluster, enter:

```bash
ssh-copy-id -i path/to/id_ed25519 <user>@<cluster-head.example.edu>
# will ask for password
```



Test if successfully copied

```bash
ssh -i path/to/id_ed25519 cluster_head
# should not ask for password
```



If successful, in config file add:

```config

# ~/.ssh/config
# add to cluster_head host
Host cluster_head
    IdentityFile ~/.ssh/nsicluster/id_ed25519

```



Now cluster can be accessed from your machine with:

```bash
ssh cluster_head
```



### 4.5 Automating Specific Node Access



Running tasks on head node is discouraged, therefore we need to switch between nodes

Since all nodes share the home directory, you don’t need to copy the key again—just add the node to your SSH config file.




```config

# ~/.ssh/config
Host <cluster_node>
    HostName <nodeName>
    Port 22
    User <user>
    ProxyJump cluster_head


# repeat for any other nodes you want to access

```



Now a specific node can be accessed from your machine with:

```bash
ssh cluster_node
```



### 4.6 Copying files to the Cluster



```bash
scp <file> <cluster_node>:<path>
```



---




## 5) Python Experimentation



### 5.1 Project layout (example)



```

repo/
├─ data/
├─ notebooks/
│   └─ 01_env_check.ipynb
├─ src/
│   ├─ data_utils.py
│   ├─ models/
│   │   ├─ uq_baseline.py
│   │   └─ __init__.py
│   └─ __init__.py
├─ environment.yml
└─ GUIDE.md


```



### 5.2 Run a baseline script (CLI)



```bash

# Local (Windows, Anaconda Prompt)

conda activate defect-pred

python -m src.models.uq_baseline --dataset data/train.csv --epochs 5 --out results/baseline

```



Example arguments your script might support:



\* `--dataset <path>`: training data file

\* `--epochs <int>`: number of epochs

\* `--seed <int>`: random seed for reproducibility

\* `--out <dir>`: output directory for metrics/plots



### 5.3 Run from a notebook (snippet)



```python

from src.models.uq_baseline import train_and_eval

metrics = train_and_eval(
    dataset_path="data/train.csv",
    epochs=5,
    seed=42,
    out_dir="results/baseline"
)
metrics


```



---



## 6) Reproducibility & Versioning



\* Pin Python version to 3.10.

\* Keep `environment.yml` updated when adding/removing packages.

\* Record seeds (e.g., `numpy`, `random`, `torch` if used) inside your scripts.

\* Save metrics and plots under `results/<run_name>` with timestamps.



---


## 7) UQ Model on Cluster

> Purpose:

> These steps show how to set up, download data, and run the Uncertainty Quantification (UQ) model on the cluster.
 
> The goal is to help you move from simply connecting to the cluster to actually running long ML jobs reproducibly and efficiently.

---




### 7.1 Git Setup


Before running the model, make sure Git is available on the cluster.  
If not installed, you can add it in your active conda environment:

```bash
conda install anaconda::git
```


Set up your SSH key:

If you already created an SSH key in Section 4.1 and added it to GitHub, skip this step. 

Otherwise, follow Section 4.1 to generate a new SSH key and link it to your GitHub account.


Clone repo:

```bash
git clone git@github.com:cunymasslab/vulnewdata.git
```


### 7.2 UQ Model Dependencies



Install dependencies listed in `requirements.txt` inside the `uncertainty/model` directory.



```bash
cd vulnewdata/uncertainty/model

pip install -r requirements.txt

```



### 7.3 UQ Model Data



Follow the instructions in `data/README.md` to download data.

If the `curl` command is not installed on your machine, in an activated conda environment run:


```bash
conda install anaconda::curl
```



### 7.4 Running UQ Model



Once finished with setup, in root of repository run:

```bash

# from the repository root (vulnewdata/)

uncertainty/scripts/run_htsc_bertvcm_activelearn_ext_main.sh
```


### 7.5 Choosing Nodes

Running projects on nodes with existing processes will lead to slow performance.
You should run project on nodes with no other processes running.

To check the GPU, run:

```bash
nvidia-smi          # one-time check
nvidia-smi -l 5     # refresh every 5 seconds
```

Look for Volatile GPU-Util ~ 0% and sufficient free memory.


## 8) Running Computational Tasks Persistently

Purpose:
Long jobs on clusters can run for hours. Using screen ensures your job continues even if you disconnect.




### 8.1 Install Screen



In activated conda environment:

```bash
conda install conda-forge::screen
```



### 8.2 Using Screen

Run:

```bash
screen -S <screenName>
```

Activate the defect-pred environment and run the UQ model (see 7.4).


### 8.3 Useful Screen Commands



```bash


# list all screens
screen -ls

# detach screen
screen -d <screen>

# reattach screen
screen -r <screen>

# list processes
ps -u <user>

# detach screen (when inside screen)
CTRL-A CTRL-D
```



## 9) Common Issues & Fixes



### 9.1 Conda ToS error (Windows)



```

CondaToSNonInteractiveError: Terms of Service have not been accepted

```



Fix:



```bash

conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main

conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r

conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/msys2

```



Re‑run `conda create ...`.



### 9.2 Using PATH vs Anaconda Prompt (Windows)



If `conda` isn’t recognized in Command Prompt, open Anaconda Prompt or re-install Miniconda and select “Add to PATH”.




### 9.3 Jupyter doesn’t open



It runs at a URL like `http://localhost:8888`. If a browser doesn’t open, copy the printed URL (with token) into your browser.



### 9.4 SSH from home fails



Run a verbose log and attach it to support:



```bash

ssh -vvv <username>@<gateway-or-node> > ssh_log.txt 2>&1

```



Ask IT whether VPN is required for off‑campus access.



### 9.5 First‑time SSH host key warning



Seeing “authenticity of host can’t be established” is normal the first time. Type `yes`. The key is saved to `~/.ssh/known_hosts`.



---



## 10) Git Commands to Commit & Push



Run these in the repo root (after creating/updating this guide and environment):



```bash

git add GUIDE.md environment.yml notebooks/01_env_check.ipynb

git commit -m "Add GUIDE for experiment environment and UQ model baseline"

git push origin main   # or your working branch

git pull origin main   # ensure you’re up-to-date

```



---



## 11) Status Summary (for progress reports)



* ✅ Miniconda installed locally

* ✅ `defect-pred` env created with core packages

* ✅ Jupyter verified

* ✅ SSH to cluster verified (nodes reachable; Python 3.10 available)

* ✅ Cluster env via Conda when starting heavy runs

* ✅ UQ repository cloned

* ✅ UQ model running on screen



---



**Maintainers:** Thrust 2 team (e.g., Vitaliy Tei & Josemar Ochoa)

**Course:** CISC 4900/5001 — project

**Topic:** Measuring Performance Gains with Small Scale Human Labeling in Software Vulnerability Detection - labeling commit patches from Open-Source projects.




