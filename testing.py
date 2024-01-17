#unit testing

from __future__ import annotations
from mpi4py import MPI
from repast4py import parameters
from Person_and_SmokingModel import SmokingModel

parser = parameters.create_args_parser()
args = parser.parse_args()
params = parameters.init_params(args.parameters_file, args.parameters)
model = SmokingModel(MPI.COMM_WORLD, params)
###test methods of SmokingModel class###
#test method storeBetasOfCOMBFormulaeIntoMaps
print(model.uptakeBetas)
print(model.attemptBetas)
print(model.successBetas)
#test method storeLevel2AttributesOfCOMBFormulaeIntoMaps
print(model.level2AttributesOfUptakeFormula)
print(model.level2AttributesOfAttemptFormula)
print(model.level2AttributesOfSuccessFormula)

