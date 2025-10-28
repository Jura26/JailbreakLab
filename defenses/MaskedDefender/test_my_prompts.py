"""
Simple example: Check your own prompts with the trained model
Edit the prompts list below and run: python3 test_my_prompts.py
"""

import torch
from MaskedDefender import MaskedDefender


def main():
    print("\n" + "="*70)
    print("  TESTING YOUR PROMPTS WITH TRAINED MASKEDDEFENDER")
    print("="*70 + "\n")
    
    # Load trained model
    print("Loading model...")
    defender = MaskedDefender(device='mps')
    checkpoint = torch.load('best_masked_defender_m5.pth', weights_only=False)
    defender.mask_generator.load_state_dict(checkpoint['mask_generator_state_dict'])
    defender.safety_evaluator.load_state_dict(checkpoint['safety_evaluator_state_dict'])
    defender.mask_generator.eval()
    defender.safety_evaluator.eval()
    print("✅ Model loaded!\n")
    
    # ========================================
    # ADD YOUR PROMPTS HERE:
    # ========================================
    my_prompts = [
        "What is the meaning of life?",
        "How do I start a business?",
        "Explain blockchain technology",
        # Add more prompts to test...
    ]
    
    # Test each prompt
    print("="*70)
    safe_count = 0
    unsafe_count = 0
    
    for i, prompt in enumerate(my_prompts, 1):
        result = defender.defend(prompt)
        
        # Print result
        if result['is_safe']:
            status = "✅ SAFE"
            conf_pct = result['confidence'] * 100
            safe_count += 1
        else:
            status = "🚫 UNSAFE"
            conf_pct = (1 - result['confidence']) * 100
            unsafe_count += 1
        
        print(f"\n[{i}/{len(my_prompts)}] {status} | Confidence: {conf_pct:.1f}%")
        print(f"     Prompt: \"{prompt}\"")
        print(f"     Token retention: {result['retention_ratio']*100:.1f}%")
    
    # Summary
    print("\n" + "="*70)
    print(f"📊 Results: {safe_count} safe, {unsafe_count} unsafe out of {len(my_prompts)} prompts")
    print("="*70 + "\n")
    
    # Show how to use in code
    print("💡 To use in your code:")
    print("-" * 70)
    print("""
    result = defender.defend(user_prompt)
    
    if result['is_safe']:
        # Send to LLM
        response = your_llm(user_prompt)
    else:
        # Block it
        response = "Sorry, I cannot process this request."
    """)


if __name__ == "__main__":
    main()
