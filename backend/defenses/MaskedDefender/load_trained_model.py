# Testing with Trained Model - Add this cell to your Colab notebook

"""
After training your model with train_defender.py, 
use this code to load and test the trained weights.
"""

# Load the trained model
import torch

print("Loading trained model...")

# Initialize defender
defender = MaskedDefender()

# Load trained weights
checkpoint = torch.load('best_masked_defender.pth', map_location=defender.device)
defender.mask_generator.load_state_dict(checkpoint['mask_generator_state_dict'])
defender.safety_evaluator.load_state_dict(checkpoint['safety_evaluator_state_dict'])

print(f"✓ Loaded model from epoch {checkpoint['epoch']} with accuracy {checkpoint['best_accuracy']:.4f}")

# Now run your tests again with the trained model!
# Re-run the test cells to see improved performance

# Expected improvements:
# - Legitimate prompts: ~90-100% classified as safe
# - Jailbreak attacks: ~70-90% classified as unsafe
# - Confidence scores: >0.7 instead of ~0.5
# - Token retention: More selective filtering
