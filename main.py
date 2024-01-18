#ABM software for smoking behaviour using the COM-B theories: regular smoking uptake theory, quit attempt theory and quit success theory and relapse theory
#
#Running command: python main.py props/model.yaml

from __future__ import annotations
from mpi4py import MPI
from repast4py import parameters
from Person_SmokingModel_COMBTheory import SmokingModel

def main():
    parser = parameters.create_args_parser()
    args = parser.parse_args()
    params = parameters.init_params(args.parameters_file, args.parameters)
    model = SmokingModel(MPI.COMM_WORLD, params)
    model.init()
    model.run()

if __name__ == "__main__":
    main()