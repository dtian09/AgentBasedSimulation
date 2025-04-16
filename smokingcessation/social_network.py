'''
Definition of the SocialNetwork class which serves as a macro entity to model social influence 
on smoking behaviours. This component creates a static network structure with dynamic agent 
participation, where all possible agents are known at initialisation but their active status 
changes throughout the simulation.
'''

import pandas as pd
from repast4py import network
from config.definitions import AgentState
import logging

class SocialNetwork:
    """
    SocialNetwork class creates and manages the social network structure for the ABM.
    It maintains a graph of relationships between agents and provides methods to 
    query network relationships that influence smoking behaviours.
    """
    
    def __init__(self, smoking_model):
        """
        Initialise the social network.
        
        Args:
            smoking_model: The smoking model that owns this network
        """
        self.smoking_model = smoking_model
        self.comm = smoking_model.comm
        self.context = smoking_model.context
        
        # Create a directed network projection
        self.network = network.DirectedSharedNetwork("social_network", self.comm)
            
        # Add the network projection to the context
        self.context.add_projection(self.network)
        
        # Logging setup
        self.running_mode = self.smoking_model.running_mode
        if self.running_mode == 'debug':
            self.log_info("Social network initialised")
    
    def initialise_network(self, network_file_path):
        """
        Read network from an edge list file in CSV format and initialise the connections.
        
        Args:
            network_file_path: Path to the edge list CSV file
        """
        self.log_info(f"Initialising network from {network_file_path}")
        
        try:
            # Read network edges
            edges = pd.read_csv(network_file_path)
            
            # Create a mapping from person IDs to Person objects
            id_to_person = {}
            agent_count = 0
            for agent in self.context.agents():
                id_to_person[agent.get_id()] = agent
                agent_count += 1
                
            if self.running_mode == 'debug':
                self.smoking_model.logfile.write(f"Found {agent_count} agents in context during network initialisation\n")
                
            # Add edges to the network
            edge_count = 0
            for _, row in edges.iterrows():
                # Extract the correct ego and alter IDs from the columns
                ego_id = row['ego.id']
                alter_id = row['alter.id']
                
                if ego_id in id_to_person and alter_id in id_to_person:
                    ego = id_to_person[ego_id]
                    alter = id_to_person[alter_id]
                    self.network.add_edge(ego, alter)
                    edge_count += 1
            
            # Set graph reference for all agents
            active_count = 0
            for agent in self.context.agents():
                agent.graph = self.network.graph
                # Add is_active attribute if it doesn't exist
                if not hasattr(agent, 'is_active'):
                    agent.is_active = True
                
                if agent.is_active:
                    active_count += 1
                    
            if self.running_mode == 'debug':
                self.smoking_model.logfile.write(f"Set {active_count} agents as active during network initialisation\n")
                
            self.log_info(f"Network initialised with {edge_count} connections")
            
        except Exception as e:
            self.log_info(f"ERROR initialising network: {str(e)}")
            raise
    
    def get_neighbours(self, agent):
        """
        Get all neighbours of an agent from the network (including inactive ones).
        
        Args:
            agent: The agent whose neighbours to get
            
        Returns:
            Iterator of neighbour agents
        """
        return self.network.graph.neighbors(agent)
    
    def get_active_neighbours(self, agent):
        """
        Get only the active neighbours of an agent.
        
        Args:
            agent: The agent whose active neighbours to get
            
        Returns:
            Filter iterator of active neighbour agents
        """
        all_neighbours = self.get_neighbours(agent)
        return filter(lambda n: n.is_active, all_neighbours)
    
    def count_active_neighbours(self, agent):
        """
        Count the number of active neighbours for an agent.
        
        Args:
            agent: The agent whose active neighbours to count
            
        Returns:
            Integer count of active neighbours
        """
        return sum(1 for _ in self.get_active_neighbours(agent))
    
    def get_neighbours_by_state(self, agent, state):
        """
        Get active neighbours with a specific state.
        
        Args:
            agent: The agent whose neighbours to filter
            state: The AgentState to filter by
            
        Returns:
            Filter iterator of neighbour agents with the specified state
        """
        active_neighbours = self.get_active_neighbours(agent)
        return filter(lambda n: n.get_current_state() == state, active_neighbours)
    
    def get_smoking_neighbours(self, agent):
        """
        Get the active neighbours of an agent who are smokers.
        
        Args:
            agent: The agent whose smoking neighbours to get
            
        Returns:
            Filter iterator of smoking neighbour agents
        """
        return self.get_neighbours_by_state(agent, AgentState.SMOKER)
    
    def count_smoking_neighbours(self, agent):
        """
        Count the number of an agent's active neighbours who are smokers.
        
        Args:
            agent: The agent whose smoking neighbours to count
            
        Returns:
            Integer count of smoking neighbours
        """
        return sum(1 for _ in self.get_smoking_neighbours(agent))

    def log_network_stats(self, agent):
        """
        Log network statistics for an agent without theory context.
        
        Args:
            agent: The agent whose network statistics to log
        """
        # Always collect the stats, even if not in debug mode
        total_neighbours = sum(1 for _ in self.get_neighbours(agent))
        active_neighbours = self.count_active_neighbours(agent)
        smoking_neighbours = self.count_smoking_neighbours(agent)
        
        log_message = (f"Agent {agent.get_id()} network stats: "
                      f"total alters={total_neighbours}, "
                      f"active alters={active_neighbours}, "
                      f"active smoking alters={smoking_neighbours}, "
                      f"state={agent.get_current_state()}")
        
        # Always print and log this information
        print(log_message)
        self.smoking_model.logfile.write(f"{log_message}\n")

    def log_info(self, message):
        """
        Log a message if in debug mode.
        
        Args:
            message: The message to log
        """
        if self.running_mode == 'debug':
            print(f"SocialNetwork: {message}")
            self.smoking_model.logfile.write(f"SocialNetwork: {message}\n") 