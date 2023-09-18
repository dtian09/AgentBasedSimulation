""" ABM Software V0.1 for smoking behaviours
usage:
 python main.py props/model.yaml
"""
from __future__ import annotations
from mpi4py import MPI
from repast4py import parameters
import repast4py
import sys

from Person_and_SmokingModel import SmokingModel

def main():
    # Command line argument parsing
    parser = repast4py.parameters.create_args_parser()
    args = parser.parse_args()
    params = repast4py.parameters.init_params(args.parameters_file, args.parameters)
    # If multiple MPI ranks have been used, terminate with an error message
    if (MPI.COMM_WORLD.Get_size() > 1):
        if MPI.COMM_WORLD.Get_rank() == 0:
            print(f"Error: This tutorial only supports use of a single MPI rank ({MPI.COMM_WORLD.Get_size()} requested).", file=sys.stderr)
        sys.exit(1)
    model = SmokingModel(MPI.COMM_WORLD, params)
    model.init_agents()
    model.init_schedule()
    model.run()

if __name__ == "__main__":
    main()
