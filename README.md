# ABM Version 0.8

ABM version 0.8 runs:
- 1) the COM-B regular smoking theory or STPM initiation probabilities for initiating regular smoking;
- 2) COM-B quit attempt theory or STPM quitting probabilities for making a quit attempt;
- 3) COM-B quit success theory or STPM quitting probabilities for quitting successfully;
- 4) STPM relapse probabilities for relapse and
- 5) e-cigarette diffusion models of the subgroups: 
  - ex-smoker < 1940
  - ex-smoker1941-1960
  - ex-smoker1961-1980
  - ex-smoker1981-1990
  - ex-smoker1991+
  - smoker < 1940 
  - smoker1941-1960
  - smoker1961-1980
  - smoker1981-1990
  - smoker1991+
  - neversmoked1991+

The non-disposable e-cigarette diffusion models start on January 2010. The disposable e-cigarette diffusion models start on March (quarter 1) 2022. The subgroups which used both non-disposable and disposable e-cigarette from January 2022 are ex-smoker1961-1980, ex-smoker1981-1990, ex-smoker1991+, smoker1941-1960, smoker1961-1980, smoker1981-1990 and smoker1991+. The subgroups which only used non-disposable e-cigarette from January 2010 are ex-smoker <1940, ex-smoker1941-1960 and smoker <1940. The neversmoked1991+ only used disposable e-cigarette from January 2022. 

Reference: [diffusion_parameters.csv](https://drive.google.com/file/d/1oZKEOfHmTnquZi_8lStQP7RuIGoLA_2Z/view)

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
1. Download the following [data files](https://drive.google.com/drive/u/1/folders/1HVtjLumfBiwaYsj0k9p_YA8DKIror6Jx) under the 'data' folder:

- testdata_STPM2011_encriched_with_STS_data.csv
- testdata_STS2010_Jan_enriched_with_STPM_data.csv
- initiation_prob1month_STPM.csv
- relapse_prob1month_STPM.csv
- quit_prob1month_STPM.csv

2. Activate the virtual environment my_env as described above.

3. Move into the repository directory.
```
cd abm-software-all-version
```

4. Specify the behaviour model to use for initiating regular smoking, making a quit attempt and quitting successfully.

For example, to use the STPM initiation probabilities for initiating regular smoking, COM-B quit attempt theory for making a quit attempt, COM-B quit success theory for quitting successfully and run the ABM in debug mode, set the following parameters in model.yaml: 

- regular_smoking_behaviour: "STPM"
- quitting_behaviour: "COMB"
- ABM_mode: "debug"

5. Specify the parameters settings of the ABM in the props/model.yaml file. In model.yaml, each line specifies a parameter (left hand side of ":") and its value (right hand side of ":"). The following are example parameters settings of the disposable e-cigarette diffusion model for the subgroup ex-smoker 1961-1980 (Reference: [diffusion_parameters.csv](https://drive.google.com/file/d/1oZKEOfHmTnquZi_8lStQP7RuIGoLA_2Z/view)):

- disp_diffusion_exsmoker_1961_1980.p: 0.022498286
- disp_diffusion_exsmoker_1961_1980.q: 0.212213813
- disp_diffusion_exsmoker_1961_1980.m: 0.066939661
- disp_diffusion_exsmoker_1961_1980.d: 0
- disp_diffusion_exsmoker_1961_1980.deltaEt: 0 # or 3 

In particular, deltaEt can be set to 0 (default value) or the actual number ('3' for ex-smoker 1961-1980) of the disposable (non-disposable) e-cigarette users of this subgroup at the starting time of the diffusion process (i.e. the quarter 1 2022 STS population for disposable diffusion models and quarter 1 2010 STS population for non-disposable diffusion models).

6. Use the following command to run the ABM model.

```
python run_abm.py props/model.yaml
```
 
## Outputs of ABM

ABM outputs calibration targets in the following files under the 'output' folder:
		1) whole_population_counts.csv, 
		2) Initiation_sex.csv, 
		3) Initiation_IMD.csv,
		4) Quit_age_sex.csv,
		5) Quit_IMD.csv.
Additionally, when running in the 'debug mode', the following 2 files are output:

- logfile.txt (debugging information including the agents' statistics at each time step when the ABM is in debug mode)
- prevalence_of_smoking.csv (the smoking prevalence at each time step)
- plots (e.g. ecig_prevalence_Smoker_over1991.jpeg) of the e-cigarette prevalence predicted by the diffusion models.
- Exsmoker1981_1990.csv etc. (the e-cigarette prevalence predicted by the diffusion models)

## Generate 2-D Plots of E-cigarette Prevalence (Output of Diffusion Models)

To generate plots (ecig_prevalence_Smoker_over1991.jpeg etc.) from Exsmoker1981_1990.csv etc. run the command:
```
python plot_annual_ecig_diffusions.py
```
The generated plots are saved under a folder 'output/plots'.

## Save the Outputs of the ABM for Future Analysis

To avoid the outputs of the ABM being overwritten when running the ABM with different parameters settings, rename the 'output' folder to a different meaningful name e.g. 'output(deltaEt=0 at tick0)'.

- Note: To generate plots using plot_annual_ecig_diffusions.py in the future, in the function plot_prevalence, set 'dir' to the folder containing the outputs e.g. dir='./output(deltaEt = 0 at tick0)/'.

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