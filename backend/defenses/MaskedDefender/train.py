"""
Training script for Masked Defender classifier.

This script trains a binary classifier to detect jailbreak prompts using a pre-trained
encoder (default: TinyBERT) with a custom classification head.

Usage:
    python train.py --dataset path/to/dataset.csv --epochs 10 --batch_size 16
    
Dataset format (CSV):
    text,label
    "Normal prompt",0
    "Jailbreak attempt",1
    
Where label 0 = safe, label 1 = unsafe
"""

import argparse
import json
import os
from datetime import datetime
from typing import Optional

import pandas as pd
import torch
import torch.nn.functional as F
from torch import nn, optim
from torch.utils.data import Dataset, DataLoader, random_split
from transformers import AutoTokenizer, AutoModel
from tqdm import tqdm
import matplotlib.pyplot as plt


class MaskedDefenderClassifier(nn.Module):
    """Binary classifier for jailbreak detection.
    
    Architecture:
        - Pre-trained encoder (e.g., TinyBERT)
        - Mean pooling over token embeddings
        - 2-layer MLP with dropout
        - Binary output (safe/unsafe)
    """

    def __init__(self, encoder_name: str = "prajjwal1/bert-tiny"):
        super().__init__()
        self.encoder = AutoModel.from_pretrained(encoder_name)
        enc_hidden = self.encoder.config.hidden_size
        self.classifier = nn.Sequential(
            nn.Linear(enc_hidden, 384),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(384, 2),
        )

    def forward(self, input_ids, attention_mask):
        outputs = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        last_hidden = outputs.last_hidden_state
        
        # Mean pooling with attention mask
        mask = attention_mask.unsqueeze(-1).float()
        masked = last_hidden * mask
        pooled = masked.sum(dim=1) / mask.sum(dim=1).clamp(min=1.0)
        
        logits = self.classifier(pooled)
        return logits


class JailbreakDataset(Dataset):
    """Dataset for jailbreak prompt classification."""

    def __init__(self, texts: list[str], labels: list[int], tokenizer, max_length: int = 128):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = self.texts[idx]
        label = self.labels[idx]
        
        encoded = self.tokenizer(
            text,
            padding="max_length",
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt",
        )
        
        return {
            "input_ids": encoded["input_ids"].squeeze(0),
            "attention_mask": encoded["attention_mask"].squeeze(0),
            "label": torch.tensor(label, dtype=torch.long),
        }


def load_dataset(csv_path: str):
    """Load dataset from CSV file.
    
    Expected columns: 'text', 'label'
    Labels: 0 = safe, 1 = unsafe
    """
    df = pd.read_csv(csv_path)
    
    if "text" not in df.columns or "label" not in df.columns:
        raise ValueError("Dataset must have 'text' and 'label' columns")
    
    texts = df["text"].tolist()
    labels = df["label"].tolist()
    
    return texts, labels


def train_epoch(model, dataloader, optimizer, device, progress_bar=True):
    """Train for one epoch."""
    model.train()
    total_loss = 0
    correct = 0
    total = 0
    
    iterator = tqdm(dataloader, desc="Training") if progress_bar else dataloader
    
    for batch in iterator:
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["label"].to(device)
        
        optimizer.zero_grad()
        
        logits = model(input_ids, attention_mask)
        loss = F.cross_entropy(logits, labels)
        
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
        _, predicted = torch.max(logits, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
        
        if progress_bar:
            iterator.set_postfix({"loss": loss.item(), "acc": correct / total})
    
    return total_loss / len(dataloader), correct / total


def validate(model, dataloader, device):
    """Validate the model."""
    model.eval()
    total_loss = 0
    correct = 0
    total = 0
    
    with torch.no_grad():
        for batch in dataloader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["label"].to(device)
            
            logits = model(input_ids, attention_mask)
            loss = F.cross_entropy(logits, labels)
            
            total_loss += loss.item()
            _, predicted = torch.max(logits, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    
    return total_loss / len(dataloader), correct / total


def plot_training_history(history: dict, save_path: str):
    """Plot training and validation metrics."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    
    # Loss plot
    ax1.plot(history["train_loss"], label="Train Loss", marker="o")
    ax1.plot(history["val_loss"], label="Val Loss", marker="s")
    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("Loss")
    ax1.set_title("Training and Validation Loss")
    ax1.legend()
    ax1.grid(True)
    
    # Accuracy plot
    ax2.plot(history["train_acc"], label="Train Acc", marker="o")
    ax2.plot(history["val_acc"], label="Val Acc", marker="s")
    ax2.set_xlabel("Epoch")
    ax2.set_ylabel("Accuracy")
    ax2.set_title("Training and Validation Accuracy")
    ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    print(f"Training plot saved to {save_path}")


def main():
    parser = argparse.ArgumentParser(description="Train Masked Defender classifier")
    parser.add_argument("--dataset", type=str, required=True, help="Path to CSV dataset")
    parser.add_argument("--encoder", type=str, default="prajjwal1/bert-tiny", 
                        help="HuggingFace encoder model")
    parser.add_argument("--epochs", type=int, default=10, help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=16, help="Batch size")
    parser.add_argument("--lr", type=float, default=2e-4, help="Learning rate")
    parser.add_argument("--max_length", type=int, default=128, help="Max sequence length")
    parser.add_argument("--val_split", type=float, default=0.2, help="Validation split ratio")
    parser.add_argument("--output", type=str, default="masked_defender.pth", 
                        help="Output checkpoint path")
    parser.add_argument("--device", type=str, default="auto", 
                        help="Device (auto/cuda/mps/cpu)")
    parser.add_argument("--freeze_encoder", action="store_true", 
                        help="Freeze encoder weights during training")
    
    args = parser.parse_args()
    
    # Device selection
    if args.device == "auto":
        if torch.cuda.is_available():
            device = "cuda"
        elif torch.backends.mps.is_available():
            device = "mps"
        else:
            device = "cpu"
    else:
        device = args.device
    
    print(f"Using device: {device}")
    
    # Load dataset
    print(f"Loading dataset from {args.dataset}")
    texts, labels = load_dataset(args.dataset)
    print(f"Loaded {len(texts)} samples")
    print(f"Class distribution: Safe={labels.count(0)}, Unsafe={labels.count(1)}")
    
    # Initialize tokenizer and model
    print(f"Loading encoder: {args.encoder}")
    tokenizer = AutoTokenizer.from_pretrained(args.encoder)
    model = MaskedDefenderClassifier(encoder_name=args.encoder)
    
    if args.freeze_encoder:
        print("Freezing encoder weights")
        for param in model.encoder.parameters():
            param.requires_grad = False
    
    model.to(device)
    
    # Create datasets
    dataset = JailbreakDataset(texts, labels, tokenizer, args.max_length)
    val_size = int(len(dataset) * args.val_split)
    train_size = len(dataset) - val_size
    train_dataset, val_dataset = random_split(dataset, [train_size, val_size])
    
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False)
    
    print(f"Train samples: {len(train_dataset)}, Val samples: {len(val_dataset)}")
    
    # Training setup
    optimizer = optim.AdamW(model.parameters(), lr=args.lr)
    
    # Training loop
    history = {
        "train_loss": [],
        "train_acc": [],
        "val_loss": [],
        "val_acc": [],
    }
    
    best_val_acc = 0.0
    best_epoch = 0
    
    print(f"\nStarting training for {args.epochs} epochs")
    print("=" * 60)
    
    for epoch in range(args.epochs):
        print(f"\nEpoch {epoch + 1}/{args.epochs}")
        
        train_loss, train_acc = train_epoch(model, train_loader, optimizer, device)
        val_loss, val_acc = validate(model, val_loader, device)
        
        history["train_loss"].append(train_loss)
        history["train_acc"].append(train_acc)
        history["val_loss"].append(val_loss)
        history["val_acc"].append(val_acc)
        
        print(f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}")
        print(f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}")
        
        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_epoch = epoch + 1
            
            checkpoint = {
                "encoder_name": args.encoder,
                "model_state_dict": model.state_dict(),
                "val_acc": val_acc,
                "epoch": epoch + 1,
                "history": history,
                "args": vars(args),
                "timestamp": datetime.now().isoformat(),
            }
            
            torch.save(checkpoint, args.output)
            print(f"✓ Saved best model (val_acc: {val_acc:.4f})")
    
    print("\n" + "=" * 60)
    print(f"Training completed!")
    print(f"Best validation accuracy: {best_val_acc:.4f} (epoch {best_epoch})")
    print(f"Model saved to: {args.output}")
    
    # Save training history
    history_path = args.output.replace(".pth", "_history.json")
    with open(history_path, "w") as f:
        json.dump(history, f, indent=2)
    print(f"Training history saved to: {history_path}")
    
    # Plot training curves
    plot_path = args.output.replace(".pth", "_training.png")
    plot_training_history(history, plot_path)
    
    # Print final stats
    print("\n" + "=" * 60)
    print("TRAINING SUMMARY")
    print("=" * 60)
    print(f"Dataset: {args.dataset}")
    print(f"Encoder: {args.encoder}")
    print(f"Device: {device}")
    print(f"Epochs: {args.epochs}")
    print(f"Batch size: {args.batch_size}")
    print(f"Learning rate: {args.lr}")
    print(f"Max length: {args.max_length}")
    print(f"Freeze encoder: {args.freeze_encoder}")
    print(f"\nBest validation accuracy: {best_val_acc:.4f}")
    print(f"Final train accuracy: {history['train_acc'][-1]:.4f}")
    print(f"Final val accuracy: {history['val_acc'][-1]:.4f}")
    
    # Model stats
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"\nTotal parameters: {total_params:,}")
    print(f"Trainable parameters: {trainable_params:,}")
    print("=" * 60)


if __name__ == "__main__":
    main()
