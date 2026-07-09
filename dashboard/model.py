import random
import numpy as np
from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

# Import dari agent.py (pastikan path disesuaikan jika dijalankan dari root)
from agent import StudentAgent

class MajorSelectionModel(Model):
    """
    Environment simulasi pemilihan jurusan terintegrasi untuk Streamlit.
    """
    def __init__(self, n_agents=30, width=10, height=10, 
                 information=0.5, prospect=0.6, stressor=0.3, cbt=0.4, seed=None):
        super().__init__()
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
            
        self.num_agents  = n_agents
        self.grid        = MultiGrid(width, height, torus=True)
        self.schedule    = RandomActivation(self)
        
        self.information = information
        self.prospect    = prospect
        self.stressor    = stressor
        self.cbt         = cbt
        
        self.datacollector = DataCollector(
            model_reporters={
                'Avg_C':     lambda m: round(np.mean([a.C for a in m.schedule.agents]),4),
                'N_Yakin':   lambda m: sum(1 for a in m.schedule.agents if a.state=='Yakin'),
                'N_Ragu':    lambda m: sum(1 for a in m.schedule.agents if a.state=='Ragu'),
                'N_Salah':   lambda m: sum(1 for a in m.schedule.agents if a.state=='Salah'),
                'Avg_Score': lambda m: round(np.mean([a.hitung_score() for a in m.schedule.agents]),4),
                'CBT_Count': lambda m: sum(a.cbt_counter for a in m.schedule.agents),
            },
            agent_reporters={
                'C': 'C', 'State': 'state',
                'Score': lambda a: a.hitung_score(),
                'Active_CBT': 'active_cbt',
                'CBT_Count': 'cbt_counter',
            }
        )
        
        for i in range(n_agents):
            agent = StudentAgent(i, self)
            x = random.randrange(width)
            y = random.randrange(height)
            self.grid.place_agent(agent, (x, y))
            self.schedule.add(agent)
            
        self.datacollector.collect(self)

    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)

    def run(self, n_steps):
        for _ in range(n_steps):
            self.step()

    def get_state_distribution(self):
        states = [a.state for a in self.schedule.agents]
        return {
            'Yakin':   states.count('Yakin'),
            'Ragu':    states.count('Ragu'),
            'Salah':   states.count('Salah'),
            'Bingung': states.count('Bingung'),
        }
