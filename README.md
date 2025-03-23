
# ABM Version 0.9
The ABM v0.9:
- runs the following smoking behavior models (chosen by the user):
   - 1) COM-B regular smoking theory or STPM initiation probabilities
   - 2) COM-B quit attempt theory or STPM quitting probabilities
   - 3) COM-B quit maintenance theory or STPM quitting probabilities
   - 4) STPM relapse probabilities
- runs e-cigarette diffusion models (non-disposable and disposable e-cigarette models) of the following population subgroups: 
  - 1) ex-smoker < 1940
  - 2) ex-smoker1941-1960
  - 3) ex-smoker1961-1980
  - 4) ex-smoker1981-1990
  - 5) ex-smoker1991+
  - 6) smoker < 1940 
  - 7) smoker1941-1960
  - 8) smoker1961-1980
  - 9) smoker1981-1990
  - 10) smoker1991+
  - 11) neversmoked1991+
- initializes new 16 years old agents on each January from 2012 (tick 13).
- reads in regional smoking prevalence between 2011 and 2019 from a regional smoking prevalence data file
- runs a mortality model on each December from 2011 (tick 12).
- implements the exogenous dynamics:
   - oReceiveGPAdvice (COM-B quit attempt theory)
   - pPrescriptionNRT (COM-B quit attempt theory)
   - pPrescriptionNRT (COM-B quit maintenance theory)
   - cUseOfBehavioralSupport (COM-B quit maintenance theory)  
   - pVareniclineUse (COM-B quit maintenance theory)  

The non-disposable e-cigarette diffusion models start on January 2010. The disposable e-cigarette diffusion models start on January 2021. The subgroups which used both non-disposable and disposable e-cigarette from January 2021 are ex-smoker1961-1980, ex-smoker1981-1990, ex-smoker1991+, smoker1941-1960, smoker1961-1980, smoker1981-1990 and smoker1991+. The subgroups which only used non-disposable e-cigarette from January 2010 are ex-smoker <1940, ex-smoker1941-1960 and smoker <1940. The neversmoked1991+ only used disposable e-cigarette from January 2021. 

Reference: [monthly_diffusion_parameters.csv](https://drive.google.com/drive/u/1/folders/1BL8bcnzSBpwPEKwiWj5TXH5-MRyNwOx2)

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
### 3. Download input data files
1. Download the following [data files](https://drive.google.com/drive/u/1/folders/1HVtjLumfBiwaYsj0k9p_YA8DKIror6Jx) under the 'data' folder:

- data_synth20_03_2025_v2.csv
- initiation_prob1month_STPM.csv
- quit_prob1month_STPM.csv
- relapse_prob1month_STPM.csv
- regional_smoking_trends_data.csv
- death_probs_abm_integers.csv
- sts_cig_consumption_percentiles20_03_25.csv
- table_attempts_dynamic_extended_integers.csv
- table_maintenance_dynamic_extended_integers.csv

2. Download the [monthly_diffusion_parameters.csv](https://drive.google.com/drive/u/1/folders/1BL8bcnzSBpwPEKwiWj5TXH5-MRyNwOx2) and [monthly_bass_observed_predicted.csv](https://drive.google.com/drive/u/1/folders/1BL8bcnzSBpwPEKwiWj5TXH5-MRyNwOx2) under the 'monthly diffusion models' folder.

## Run the ABM

1. Activate the virtual environment my_env as described above if it is not activated.

2. Move into the repository directory:

```
cd smokingABM
```
### Set the Parameters of the ABM using Model.yaml 
Set the weights (betas) of the Level 2 attributes of the COM-B regular smoking model (uptake), quit attempt model and quit maintenance (success) model:

- uptake.cAlcoholConsumption.beta: 0.46
- uptake.oSocialHousing.beta: 0.57
- attempt.mIntentionToQuit.beta: 0.52
...

Set the smoking behavior model for initiating regular smoking, making a quit attempt and quitting successfully.

For example, to use the STPM initiation probabilities for initiating regular smoking, COM-B quit attempt theory for making a quit attempt, COM-B quit maintenance theory for quitting successfully and run the ABM in 'debug' mode (output logfile.txt containing detailed information about the simulation) or 'normal' mode (no logfile.txt), set the following parameters: 

- regular_smoking_behaviour: "STPM"
- quitting_behaviour: "COMB"
- ABM_mode: "debug"

In model.yaml, each line specifies a parameter (left hand side of ":") and its value (right hand side of ":"). The following are example parameters settings of the disposable e-cigarette diffusion model for the subgroup ex-smoker 1961-1980 (Reference: [diffusion_parameters.csv](https://drive.google.com/file/d/1oZKEOfHmTnquZi_8lStQP7RuIGoLA_2Z/view)):

- disp_diffusion_exsmoker_1961_1980.p: 0.022498286
- disp_diffusion_exsmoker_1961_1980.q: 0.212213813
- disp_diffusion_exsmoker_1961_1980.m: 0.066939661
- disp_diffusion_exsmoker_1961_1980.d: 0

Set any other parameters of the ABM.
### The Running Command

Use the following command to run the ABM model.

```
python run_abm.py props/model.yaml
```

## Outputs of ABM

ABM outputs calibration targets in the following files under the 'output' folder:
- 1) whole_population_counts.csv
- 2) Initiation_sex.csv
- 3) Initiation_IMD.csv
- 4) Quit_age_sex.csv
- 5) Quit_IMD.csv

Additionally, when running in the 'debug mode', the following files are output:

- logfile.txt (detailed information of the simulation including the agents' statistics)
- prevalence_of_smoking.csv (the smoking prevalence at each time step)
- Exsmoker1981_1990.csv etc. (the e-cigarette prevalence predicted by the diffusion models)

## Generate 2-D Plots of E-cigarette Prevalence (Output of Diffusion Models)

To generate plots (ecig_prevalence_Smoker_over1991.jpeg etc.) from Exsmoker1981_1990.csv etc. (outputs of 'debug mode') run the command:
```
python plot_annual_ecig_diffusions.py
```
The generated plots ecig_prevalence_Smoker_over1991.jpeg etc. are saved under a folder 'output/plots'.

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
