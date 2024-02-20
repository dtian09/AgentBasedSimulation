# Cessation ABM

ABM software simulates the smoking behaviours of agents using regular smoking theory, 
quit attempt theory, quit success theory and relapse probabilities (STPM).

## Installation

The following instructions installs the smokingcessation package and all dependencies into a new python environment
using Anaconda.

1. Install [Anaconda](https://www.anaconda.com/)
2. Create a new environment with python installed. Note: Python >= 3.8 is required.
```
conda create -n smoking_cessation_env python=3.8
```
3. Activate the environment
```
conda activate smoking_cessation_env
```
4. Clone the repository
```
git clone https://bitbucket.org/cessation-abm/abm-software-all-versions.git
```
5. Move into the repository directory
```
cd abm-software-all-version
```
6. Install the package and dependencies
```
pip install -e .
```

## Run the ABM model

The following command will run the ABM model with the parameters/settings specified in the props/model.yaml file.
In model.yaml, each line specifies a parameter (left hand side of ":") and its value (right hand side of ":").
```
python smokingcessation/run_abm.py props/model.yaml
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