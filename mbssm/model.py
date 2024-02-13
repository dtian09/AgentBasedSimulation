from __future__ import annotations
from typing import Dict, List
from abc import ABC, abstractmethod
import repast4py
from mbssm.macro_entity import MacroEntity


class Model(ABC):

    def __init__(self, comm, params: Dict):
        self.props = params
        self.stop_at: int = self.props["stop.at"] if "stop.at" in params else 0
        self.count_of_agents: int = self.props["count.of.agents"] if "count.of.agents" in params else 0
        self.context: repast4py.context.SharedContext = None
        self.macro_entity_list: List[MacroEntity] = []
        self.runner: repast4py.schedule.SharedScheduleRunner = repast4py.schedule.init_schedule_runner(comm)

    @abstractmethod
    def init(self):
        pass

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def collect_data(self):
        pass
