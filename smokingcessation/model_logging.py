from mbssm.theory import Theory
from smokingcessation.person import Person
from smokingcessation.smoking_model import SmokingModel


def log_data(theory: Theory, agent: Person, model: SmokingModel):

    debug_theory = theory.theory_info()
    debug_agent = agent.agent_info()
    debug_model = model.model_info()
    debug_list = debug_agent + debug_theory + debug_model

    return debug_list
