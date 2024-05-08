# Cessation ABM

ABM software simulates the smoking behaviours of agents using the COM-B regular smoking theory, 
COM-B quit attempt theory, COM-B quit success theory and relapse probabilities (STPM).

## Installation

The ABM software runs on Linux or MacOS operating systems (OS). The ABM software can also be run on Windows 10 or 11 OS by firstly installing the Windows Subsystem for Linux (WSL) on the Windows OS and secondly running the ABM software on WSL (see links below). 

- https://en.wikipedia.org/wiki/Windows_Subsystem_for_Linux
- https://learn.microsoft.com/en-us/windows/wsl/about

The ABM software has the dependencies: Repast4py, numpy and pandas. Repast4py has the dependency MPI. Install Python 3, pip, MPI and venv (virtual environment tool); then, create a virtual environment and install Repast4py, numpy and pandas into the virtual environment.

### 1. Install Python 3, pip, MPI and venv

1. Update your Ubuntu Linux with the latest packages by running the following two commands:
```
sudo apt update 
```
```
sudo apt upgrade
```
2. Install [python 3](https://www.makeuseof.com/install-python-ubuntu/) 
```
sudo apt install python3
```
3.	Install pip for python 3:
```  
apt install python3-pip
```
4.	Install [MPI](https://repast.github.io/repast4py.site/guide/user_guide.html)
```
sudo apt install mpich
```
5.	Install venv for creating a virtual environment
```
apt install python3-venv
```
### 2. Create a virtual environment and install Repast4py, numpy and pandas into the virtual environment
1. Create a [virtual environment](https://linuxopsys.com/topics/create-python-virtual-environment-on-ubuntu) called my_env: 
```
python3 -m venv my_env
```
2.	Activate my_env
```  
source my_env/bin/activate
```
3. Install Repast4py in my_env
```
env CC=mpicxx pip install repast4py
```
4. Install the numpy and pandas python packages in my_env
```
pip install numpy pandas
```
## Run the ABM software

1. Activate the virtual environment my_env as described above.
2. Move into the repository directory.
```
cd abm-software-all-version
```
3. Use the following command to run the ABM model with the parameters/settings specified in the props/model.yaml file.
In model.yaml, each line specifies a parameter (left hand side of ":") and its value (right hand side of ":").
```
python run_abm.py props/model.yaml
```

The output files are:
- logfile.txt (debugging information including the agents' statistics at each time step when the ABM is in debug mode)
- prevalence_of_smoking.csv (the smoking prevalence at each time step)

To deactivate the virtual environment, use the following command 
```
deactivate
```
## Licenses

This software is Copyright (C) 2024 The University of Sheffield (www.sheffield.ac.uk)

This program is free software (software libre); you can redistribute it and/or modify it under
the terms of the GNU General Public License (GPL) version 3 as published by the Free Software
Foundation. Please review the following information to ensure the GNU Lesser General Public
License version 3 requirements will be met: https://www.gnu.org/licenses/gpl-3.0.html.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

This software uses repast4py package, and their license is stated in LICENSE_Repast4Py.