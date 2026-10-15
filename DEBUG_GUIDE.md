# DEBUG_GUIDE: Using VS Code Attachment and Tracing (Synchronized Local + Remote Storage)



This guide explains how to debug python code on the remote cluster using VS Code, DebugPy and SSH.



## 0) Prerequisites

Note: Before starting, open `screen` session to avoid connection drops during setup on remote server (see section 8 in GUIDE)

* **Conda** installed on local machine (See section 1 in GUIDE)

* **VS Code** installed on local machine

* **Python** Extension for VS Code

* Automated **SSH** access to remote server (see section 4 in GUIDE)

* Cloned **Git** repository on local machine



## 1) Remote Server Setup



### 1.0) Optional but Recommended - Run Setup in Screen Session



Long installations (DebugPy) can break if your SSH connection closes.
Start a persistent session to keep work alive:

```bash

conda activate vulnewdata

screen -S setup_env

# Proceed with installing debugpy or other setup steps

```



Detach with `CTRL+A, D` and reattach anytime with `screen -r setup_env`.

This ensures installations or debugging stay alive even if you disconnect.



### 1.1) Installing DebugPy on Cluster



Since our model is built in python we use `debugpy`.

In activated conda environment run:

```bash
conda install anaconda::debugpy
```

Verify Debugpy is installed with:

```bash
python -m debugpy --version
```


### 1.2) Run DebugPy on Remote Server



Before debugging project code, practice using sample code in ` uncertainty/debug` dir

The `runpy.sh` script has the following command:

```sh

python -m debugpy --wait-for-client --listen 0.0.0.0:5678  $1

```

* `0.0.0.0` listens to all interfaces
* `5678` Starts debug server on port 5678 (use another if occupied)
* `"$1"` accepts python file as an argument
* `--wait-for-client` pauses code until a debug client (VS Code) attaches 

Run script with:

```bash
./runpy.sh <pythonFile>
```



### 1.3) Verifying DebugPy is Listening



Check if process is waiting:

```bash
netstat -a -n | grep "5678"
```

Should see a line indicating port `5678` is in `LISTEN` state



---



## 2) Local Environment Setup



### 2.1) Attaching To Debug Server (VS Code)



Ensure project folder has `.vscode/launch.json` file

if it doesnt, create it with the following:

```json
{
    // Use IntelliSense to learn about possible attributes.
    // Hover to view descriptions of existing attributes.
    // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python Debugger: Remote Attach without Mappings",
            "type": "debugpy",
            "request": "attach",
            "connect": {
                "host": "localhost",
                "port": 55678
            }
        },
        {
            "name": "Python Debugger: Remote Attach",
            "type": "debugpy",
            "request": "attach",
            "connect": {
                "host": "localhost",
                "port": 55678
            },
            "pathMappings": [
                {
                    "localRoot": "${workspaceFolder}",
                    "remoteRoot": "/home/vulnewdata"
                }
            ]
        }
    ]
}
```



if VS Code shows "Connected" and breakpoints are active, remote debug attachment was successful.



### 2.2) Activating Conda Environment through VS Code



For ease of use, use VS Code's Terminal.

If Conda isnt recognized by VS Code, initialize using **Anaconda Prompt**:

```
conda init powershell

conda init cmd.exe
```

Restart VS Code and open Command Palette: `Ctrl+Shift+P`

Search for "Python: Select Interpreter" and choose:

```vscode
~\miniconda3\envs\vulnewdata\python.exe
```

Conda environment can now be activated directly within VS Code's terminal



### 2.3) Syncing Local and Remote Code



Keep local and remote repositories in sync to avoid mismatch files using:

```bash
git pull
```



### 2.4) SSH Port forwarding



Set up connection from local machine to cluster:

```
ssh -L 55678:localhost:5678 cluster_node
```

Creates a secure channel from your local machine's port `55678` to the cluster's port `5678`

Verify connection in new terminal:

```powershell
netstat -a -n | select-string "55678"
```

Should see a line indicating port `55678` is in `LISTEN` state


---



## 3) Begin Debugging



Ensure Debugpy script is waiting on cluster, and SSH connection between local and remote server is open

On local machine:
* Open VS Code 
* Go to Run and Debug tab 
* Select "Python Debugger: Remote Attach"
* Start Debugging with ▶ button or `F5`

You should now be able to inspect variables, set breakpoints and step through code while it runs on remote server.



## 4) Notes
* If ports are busy, use another, but make sure  to update launch.json accordingly.

* Keep SSH connections open, or the debug session will end.