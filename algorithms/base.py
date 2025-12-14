from abc import ABC, abstractmethod
import networkx as nx

class IAlgorithm(ABC):
    @abstractmethod
    def execute(self, G: nx.Graph, start_node: str, end_node: str) -> dict:
        pass
