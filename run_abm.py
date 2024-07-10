# ABM software for smoking behaviour using the COM-B model or STPM model
#
# Running command: python run_abm.py props/model.yaml

from __future__ import annotations
from mpi4py import MPI
from repast4py import parameters
from config.definitions import ROOT_DIR
from smokingcessation.smoking_model import SmokingModel
#import sys

def main():
    parser = parameters.create_args_parser()
    args = parser.parse_args()
    params = parameters.init_params(f'{ROOT_DIR}/' + args.parameters_file, args.parameters)
    model = SmokingModel(MPI.COMM_WORLD, params)
    model.init()
    model.run()

if __name__ == "__main__":
    main()
