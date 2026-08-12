"""
Image encoder, text encoder, and fusion architectures.

Fusion strategies implemented
-----------------------------
1. Early Fusion  – concatenate image & text embeddings, then classify.
2. Late Fusion   – modality-specific classifiers; average probability scores.
3. Hybrid Fusion – gated cross-modal fusion (learnable gates + concat).
"""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


class ImageEncoder(nn.Module):
    """Lightweight CNN for 64×64 RGB inputs → fixed embedding."""

    def __init__(self, embed_dim: int = 128):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, 3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Conv2d(128, 128, 3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d((1, 1)),
        )
        self.fc = nn.Linear(128, embed_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = self.features(x).flatten(1)
        return self.fc(h)


class TextEncoder(nn.Module):
    """Embedding bag + BiGRU text encoder."""

    def __init__(
        self,
        vocab_size: int,
        embed_dim: int = 64,
        hidden_dim: int = 64,
        out_dim: int = 128,
        pad_idx: int = 0,
    ):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=pad_idx)
        self.gru = nn.GRU(
            embed_dim,
            hidden_dim,
            batch_first=True,
            bidirectional=True,
        )
        self.fc = nn.Linear(hidden_dim * 2, out_dim)

    def forward(self, token_ids: torch.Tensor) -> torch.Tensor:
        emb = self.embedding(token_ids)
        lengths = (token_ids != 0).sum(dim=1).clamp(min=1).cpu()
        packed = nn.utils.rnn.pack_padded_sequence(
            emb, lengths, batch_first=True, enforce_sorted=False
        )
        _, h_n = self.gru(packed)
        # h_n: (num_directions, B, H)
        h = torch.cat([h_n[0], h_n[1]], dim=-1)
        return self.fc(h)


class EarlyFusionModel(nn.Module):
    """Concatenate image & text embeddings before a shared MLP classifier."""

    def __init__(self, vocab_size: int, embed_dim: int = 128, num_classes: int = 2):
        super().__init__()
        self.image_encoder = ImageEncoder(embed_dim)
        self.text_encoder = TextEncoder(vocab_size, out_dim=embed_dim)
        self.classifier = nn.Sequential(
            nn.Linear(embed_dim * 2, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(128, num_classes),
        )
        self.name = "early_fusion"

    def encode(self, images, tokens):
        return self.image_encoder(images), self.text_encoder(tokens)

    def forward(self, images, tokens):
        img_f, txt_f = self.encode(images, tokens)
        fused = torch.cat([img_f, txt_f], dim=-1)
        return self.classifier(fused)


class LateFusionModel(nn.Module):
    """Independent modality classifiers; fuse by averaging logits / probs."""

    def __init__(self, vocab_size: int, embed_dim: int = 128, num_classes: int = 2):
        super().__init__()
        self.image_encoder = ImageEncoder(embed_dim)
        self.text_encoder = TextEncoder(vocab_size, out_dim=embed_dim)
        self.image_head = nn.Sequential(
            nn.Linear(embed_dim, 64),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(64, num_classes),
        )
        self.text_head = nn.Sequential(
            nn.Linear(embed_dim, 64),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(64, num_classes),
        )
        self.name = "late_fusion"

    def forward(self, images, tokens, return_parts: bool = False):
        img_logits = self.image_head(self.image_encoder(images))
        txt_logits = self.text_head(self.text_encoder(tokens))
        # Average probabilities then convert back to logits-scale via log
        img_p = F.softmax(img_logits, dim=-1)
        txt_p = F.softmax(txt_logits, dim=-1)
        fused_p = 0.5 * (img_p + txt_p)
        fused_logits = torch.log(fused_p.clamp(min=1e-8))
        if return_parts:
            return fused_logits, img_logits, txt_logits
        return fused_logits


class HybridFusionModel(nn.Module):
    """
    Gated hybrid fusion: modality-specific gates control how much each
    stream contributes before concatenation and classification.
    """

    def __init__(self, vocab_size: int, embed_dim: int = 128, num_classes: int = 2):
        super().__init__()
        self.image_encoder = ImageEncoder(embed_dim)
        self.text_encoder = TextEncoder(vocab_size, out_dim=embed_dim)
        self.img_gate = nn.Sequential(nn.Linear(embed_dim * 2, embed_dim), nn.Sigmoid())
        self.txt_gate = nn.Sequential(nn.Linear(embed_dim * 2, embed_dim), nn.Sigmoid())
        self.classifier = nn.Sequential(
            nn.Linear(embed_dim * 2, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.ReLU(inplace=True),
            nn.Dropout(0.2),
            nn.Linear(64, num_classes),
        )
        self.name = "hybrid_fusion"

    def forward(self, images, tokens):
        img_f = self.image_encoder(images)
        txt_f = self.text_encoder(tokens)
        joint = torch.cat([img_f, txt_f], dim=-1)
        img_g = self.img_gate(joint) * img_f
        txt_g = self.txt_gate(joint) * txt_f
        fused = torch.cat([img_g, txt_g], dim=-1)
        return self.classifier(fused)


class ImageOnlyModel(nn.Module):
    def __init__(self, embed_dim: int = 128, num_classes: int = 2):
        super().__init__()
        self.image_encoder = ImageEncoder(embed_dim)
        self.classifier = nn.Sequential(
            nn.Linear(embed_dim, 64),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(64, num_classes),
        )
        self.name = "image_only"

    def forward(self, images, tokens=None):
        return self.classifier(self.image_encoder(images))


class TextOnlyModel(nn.Module):
    def __init__(self, vocab_size: int, embed_dim: int = 128, num_classes: int = 2):
        super().__init__()
        self.text_encoder = TextEncoder(vocab_size, out_dim=embed_dim)
        self.classifier = nn.Sequential(
            nn.Linear(embed_dim, 64),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(64, num_classes),
        )
        self.name = "text_only"

    def forward(self, images, tokens):
        return self.classifier(self.text_encoder(tokens))


def build_model(name: str, vocab_size: int, embed_dim: int = 128) -> nn.Module:
    name = name.lower()
    mapping = {
        "early_fusion": lambda: EarlyFusionModel(vocab_size, embed_dim),
        "late_fusion": lambda: LateFusionModel(vocab_size, embed_dim),
        "hybrid_fusion": lambda: HybridFusionModel(vocab_size, embed_dim),
        "image_only": lambda: ImageOnlyModel(embed_dim),
        "text_only": lambda: TextOnlyModel(vocab_size, embed_dim),
    }
    if name not in mapping:
        raise ValueError(f"Unknown model: {name}. Choose from {list(mapping)}")
    return mapping[name]()
