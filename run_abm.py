'''
ABM software for simulating smoking behaviours and prevalence of a population
Running command: python run_abm.py props/model.yaml
'''
from __future__ import annotations
from mpi4py.MPI import COMM_WORLD
from repast4py import parameters
from config.definitions import ROOT_DIR
from smokingcessation.smoking_model import SmokingModel

def main():
    parser = parameters.create_args_parser()
    args = parser.parse_args()
    params = parameters.init_params(f'{ROOT_DIR}/' + args.parameters_file, args.parameters)
    model = SmokingModel(COMM_WORLD, params)
    model.init()
    model.run()

if __name__ == "__main__":
    main()
