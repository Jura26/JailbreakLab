#!/bin/bash

# Quick Start Script for MaskedDefender Training on M5
# This script sets up and starts training automatically

echo "=================================================="
echo "   MaskedDefender M5 Training Quick Start"
echo "=================================================="
echo ""

# Check if we're in the right directory
if [ ! -f "MaskedDefender.py" ]; then
    echo "❌ Error: MaskedDefender.py not found"
    echo "   Please run this script from the MaskedDefender directory"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 not found"
    echo "   Please install Python 3.8+"
    exit 1
fi

echo "✓ Found MaskedDefender.py"
echo "✓ Python3 is available"
echo ""

# Run setup check
echo "📋 Step 1: Verifying M5 setup..."
echo "----------------------------------------------"
python3 check_m5_setup.py
SETUP_EXIT_CODE=$?

if [ $SETUP_EXIT_CODE -ne 0 ]; then
    echo ""
    echo "❌ Setup verification failed"
    echo "   Please install missing dependencies"
    exit 1
fi

echo ""
echo "=================================================="
echo "🚀 Starting Training on M5 Chip"
echo "=================================================="
echo ""
echo "This will:"
echo "  • Train MaskedDefender with 100 samples"
echo "  • Run for up to 20 epochs (with early stopping)"
echo "  • Use M5 GPU acceleration (MPS)"
echo "  • Take approximately 10-20 minutes"
echo ""
echo "Training will start in 3 seconds..."
echo "Press Ctrl+C to cancel"
echo ""
sleep 3

# Start training
python3 train_m5.py

TRAIN_EXIT_CODE=$?

echo ""
echo "=================================================="

if [ $TRAIN_EXIT_CODE -eq 0 ]; then
    echo "✅ Training completed successfully!"
    echo ""
    echo "Generated files:"
    echo "  • best_masked_defender_m5.pth      (trained model)"
    echo "  • training_history_m5.png          (training plots)"
    echo "  • training_log_m5.json             (metrics log)"
    echo ""
    echo "Next steps:"
    echo "  1. View training_history_m5.png to see results"
    echo "  2. Load the model with:"
    echo "     from MaskedDefender import MaskedDefender"
    echo "     defender = MaskedDefender()"
    echo "     # Load checkpoint and use for defense"
else
    echo "⚠️  Training encountered an error"
    echo "   Check the output above for details"
fi

echo "=================================================="
