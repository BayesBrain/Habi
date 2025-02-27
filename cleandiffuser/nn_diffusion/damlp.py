from typing import Optional

import torch
import torch.nn as nn

from cleandiffuser.nn_diffusion import BaseNNDiffusion


class DAMlp(BaseNNDiffusion):
    def __init__(
        self, 
        obs_dim: int,
        act_dim: int,
        emb_dim: int = 16, 
        hidden_dim: int = 256,
        timestep_emb_type: str = "positional",
        timestep_emb_params: Optional[dict] = None
    ):
        super().__init__(emb_dim, timestep_emb_type, timestep_emb_params)
        
        self.time_mlp = nn.Sequential(
            nn.Linear(emb_dim, emb_dim * 2), nn.Mish(), nn.Linear(emb_dim * 2, emb_dim))
        
        self.mid_layer = nn.Sequential(
            nn.Linear(obs_dim * 2 + act_dim + emb_dim, hidden_dim), nn.Mish(),
            nn.Linear(hidden_dim, hidden_dim), nn.Mish(),
            nn.Linear(hidden_dim, hidden_dim), nn.Mish())
        
        self.final_layer = nn.Linear(hidden_dim, act_dim)
        
    def forward(self,
                x: torch.Tensor, noise: torch.Tensor,
                condition: torch.Tensor = None):
        """
        Input:
            x:          (b, act_dim)
            noise:      (b, )
            condition:  (b, obs_dim * 2)

        Output:
            y:          (b, act_dim)
        """
        t = self.time_mlp(self.map_noise(noise))
        x = torch.cat([x, t, condition], -1)
        x = self.mid_layer(x)
        
        return self.final_layer(x)
        
class DAGoalMlp(BaseNNDiffusion):
    def __init__(
        self, 
        plan_obs_dim: int,
        obs_dim: int,
        act_dim: int,
        emb_dim: int = 16, 
        timestep_emb_type: str = "positional",
        timestep_emb_params: Optional[dict] = None
    ):
        super().__init__(emb_dim, timestep_emb_type, timestep_emb_params)
        
        self.time_mlp = nn.Sequential(
            nn.Linear(emb_dim, emb_dim * 2), nn.Mish(), nn.Linear(emb_dim * 2, emb_dim))
        
        self.mid_layer = nn.Sequential(
            nn.Linear(obs_dim + plan_obs_dim * 2 + act_dim + emb_dim, 256), nn.Mish(),
            nn.Linear(256, 256), nn.Mish(),
            nn.Linear(256, 256), nn.Mish())
        
        self.final_layer = nn.Linear(256, act_dim)
        
    def forward(self,
                x: torch.Tensor, noise: torch.Tensor,
                condition: torch.Tensor = None):
        """
        Input:
            x:          (b, act_dim)
            noise:      (b, )
            condition:  (b, obs_dim + plan_dim * 2)

        Output:
            y:          (b, act_dim)
        """
        t = self.time_mlp(self.map_noise(noise))
        x = torch.cat([x, t, condition], -1)
        x = self.mid_layer(x)
        
        return self.final_layer(x)
