from typing import Dict, List, Union

import torch
import torch.nn as nn
import torch.nn.functional as F
import pytorch_lightning as pl


class ConvBranch(nn.Module):
    """
    Одинаковые параметры свёртки на всех слоях:
      - in_channels: входные каналы (3 для RGB)
      - n_layers: число блоков
      - out_channels: фильтры на каждом слое
      - kernel_size: размер ядра (int или tuple)
    Блок: Conv2d→BatchNorm2d→ReLU→MaxPool2d(stride=2). В конце — AdaptiveAvgPool2d(1).
    TODO: переписать доку
    """
    
    def __init__(self, in_channels, n_layers, out_channels, kernel_size) -> None:
        super().__init__()
        pad = kernel_size//2 if isinstance(kernel_size, int) else tuple(k//2 for k in kernel_size)
        layers, prev = [], in_channels
        
        for _ in range(n_layers):
            layers += [
                nn.Conv2d(prev, out_channels, kernel_size=kernel_size, padding=pad),
                nn.BatchNorm2d(out_channels),
                nn.ReLU(inplace=True),
                nn.MaxPool2d(2)
            ]
            prev = out_channels

        self.conv = nn.Sequential(*layers)
        self.global_pool = nn.AdaptiveAvgPool2d(1)

    def forward(self, x):
        x = self.conv(x)               
        x = self.global_pool(x)        
        return x.view(x.size(0), -1) 


class MLPBranch(nn.Module):
    """
    Параметризуемая MLP-ветка:
      - in_features: входная размерность
      - hidden_sizes: список скрытых слоёв
      - out_features: выходная размерность
    Архитектура: [Linear→ReLU]×len(hidden_sizes) → Linear(out_features).
    TODO: переписать доку
    """

    def __init__(self, in_features, hidden_sizes, out_features) -> None:
        super().__init__()
        layers, prev = [], in_features
        
        for h in hidden_sizes:
            layers += [nn.Linear(prev, h), nn.ReLU(inplace=True)]
            prev = h
        layers.append(nn.Linear(prev, out_features))
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x)


class ArchitectureEyeTrackingModel(pl.LightningModule):
    def __init__(self, config: Dict[str, Union[float, int, List[int]]]) -> None:
        super().__init__()
        self.save_hyperparameters()

        # CNN-ветви
        self.face_branch = ConvBranch(
            3, config["n_conv_face"], config["filters_face"], config["kernel_face"]
        )
        self.pos_branch = ConvBranch(
            3, config["n_conv_face_pos"], config["filters_face_pos"], config["kernel_face_pos"]
        )
        self.leye_branch = ConvBranch(
            3, config["n_conv_eye"], config["filters_eye"], config["kernel_eye"]
            )
        self.reye_branch = ConvBranch(
            3, config["n_conv_eye"], config["filters_eye"], config["kernel_eye"]
        )

        # MLP-ветви для табличных данных
        self.left_eye_geom_branch = MLPBranch(13, config["eye_geom_hidden"], config["eye_geom_out"])
        self.right_eye_geom_branch = MLPBranch(13, config["eye_geom_hidden"], config["eye_geom_out"])
        self.head_pose_branch= MLPBranch(3, config["head_pose_hidden"], config["head_pose_out"])

        # Финальный регрессор
        fusion_dim = (
            config["filters_face"] +
            config["filters_face_pos"] +
            2*config["filters_eye"] +
            2*config["eye_geom_out"] +
            config["head_pose_out"]
        )
        self.regressor = nn.Sequential(
            nn.Linear(fusion_dim, config["dense_nodes"]), nn.ReLU(), nn.Dropout(config["dropout"]),
            nn.Linear(config["dense_nodes"], config["dense_nodes"]//2), nn.ReLU(), nn.Dropout(config["dropout"]),
            nn.Linear(config["dense_nodes"]//2, 2)
        )
        self.lr = config["lr"]

    def forward(self, face, face_pos, l_eye, r_eye, l_geom, r_geom, hpose):
        f  = self.face_branch(face)
        p  = self.pos_branch(face_pos)
        l  = self.leye_branch(l_eye)
        r  = self.reye_branch(r_eye)
        l_ge = self.left_eye_geom_branch(l_geom)
        r_ge = self.right_eye_geom_branch(r_geom)
        gh = self.head_pose_branch(hpose)
        x  = torch.cat([f,p,l,r,l_ge,r_ge,gh], dim=1)
        return self.regressor(x)


    def training_step(self, batch, _):
        face, pos, le, re, l_geom, r_geom, hpose, tgt = batch
        pred = self(face,pos,le,re,l_geom,r_geom,hpose)
        loss = F.mse_loss(pred, tgt)
        self.log("train_loss", loss)
        return loss


    def validation_step(self, batch, _):
        face, pos, le, re, l_geom, r_geom, hpose, tgt = batch
        loss = F.mse_loss(self(face,pos,le,re,l_geom, r_geom,hpose), tgt)
        self.log("val_loss", loss, prog_bar=True)


    def test_step(self, batch, _):
        face, pos, le, re, l_geom, r_geom, hpose, tgt = batch
        pred = self(face, pos, le, re, l_geom, r_geom, hpose)
        loss = F.mse_loss(pred, tgt)
        self.log("test_loss", loss)


    def configure_optimizers(self):
        return torch.optim.AdamW(self.parameters(), lr=self.lr)