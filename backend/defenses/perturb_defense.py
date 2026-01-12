
import random
import string
import nltk
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
from typing import Optional
from fastapi.responses import StreamingResponse

def run_semantic_perturb(text: str, semantic_q=0.40) -> str:
    """Your code: Swaps words for synonyms using NLTK."""
    tokens = word_tokenize(text)
    pos_tags = nltk.pos_tag(tokens)
    sem_text = []
    
    for word, tag in pos_tags:
        # Perturb Nouns, Verbs, Adjectives with probability q
        if len(word) > 3 and tag.startswith(('NN', 'VB', 'JJ')) and random.random() < semantic_q:
            synsets = wordnet.synsets(word)
            if synsets:
                # Use the first synset lemmas
                lemmas = [l.name().replace('_', ' ') for l in synsets[0].lemmas() if l.name() != word]
                word = random.choice(lemmas) if lemmas else word
        sem_text.append(word)
    
    # Join back into a human-readable string
    return " ".join(sem_text)

def run_character_perturb(text: str, char_q=0.03)-> str:
    """SmoothLLM Core: Randomly swaps characters to break token-based attacks."""
    chars = list(text)
    for i in range(len(chars)):
        # Only swap letters, leave spaces and punctuation alone
        if chars[i].isalpha() and random.random() < char_q:
            chars[i] = random.choice(string.ascii_lowercase)
    return "".join(chars)

def run_hybrid_defense(prompt: str, s_q=0.3, c_q=0.03)-> str:
    """
    Combines both for a total shield.
    1. Break Social Engineering (Synonyms)
    2. Break Token Exploits (Characters)
    """
    # Step 1: Semantic smoothing
    text = run_semantic_perturb(prompt, s_q)
    
    # Step 2: Character smoothing
    final_prompt = run_character_perturb(text, c_q)
    
    return final_prompt

async def run(prompt: str) -> Optional[StreamingResponse]:
    """
    Perturb defense doesn't block prompts it modifies them to make the attacker fail.
    """
    return None