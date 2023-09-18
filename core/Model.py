from __future__ import annotations
from typing import Dict, List
from abc import abstractmethod, ABCMeta
import repast4py
from repast4py import context, schedule
from .StructuralEntity import StructuralEntity
from .MicroAgent import MicroAgent

class Model(metaclass=ABCMeta):

    def __init__(self, comm, params: Dict):
        self.props = params
        self.stop_at: int = self.props["stop.at"] if "stop.at" in params else 0
        self.count_of_agents: int = self.props["count.of.agents"] if "count.of.agents" in params else 0
        self.context: repast4py.context.SharedContext = None
        self.structural_entity_list: List[StructuralEntity] = []
        self.runner: repast4py.schedule.SharedScheduleRunner = repast4py.schedule.init_schedule_runner(comm)

    @abstractmethod
    def init_agents(self):
        pass

    def init_schedule(self):
        self.runner.schedule_repeating_event(1, 1, self.do_per_tick)
        self.runner.schedule_stop(self.stop_at)

    def do_situational_mechanisms(self):
        for agent in self.context.agents(MicroAgent.TYPE, shuffle=False):
            agent.do_situation()
    
    def do_action_mechanisms(self):
        for agent in self.context.agents(MicroAgent.TYPE, shuffle=False):
            agent.do_action()
    
    def do_transformational_mechanisms(self):
        for structural_entity in self.structural_entity_list:
            structural_entity.do_transformation()
    
    def do_per_tick(self):
        self.do_situational_mechanisms()
        self.do_action_mechanisms()
        self.do_transformational_mechanisms()

    def run(self):
        self.runner.execute()