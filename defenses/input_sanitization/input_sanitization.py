#funkcija za jednostavnu obranu
import unicodedata
def sanitize_input(text: str) -> str:
    suspicious_phrases = [
        "ignore the above",
        "ignore previous",
        "ignore above",
        "ignore all",
        "disregard instructions",
        "pretend you are",
        "reveal",
        "bypass safety",
        "disable filter",
    ]
    #normalizira tekst tako da pretvara znakove u normalna slova i mice nevidljive znakove, npr. pretvori ígnoré u ignore, ali ign0re jos uvijek ostaje ign0re 
    normalized = unicodedata.normalize("NFKC", text).lower()   
    if any(p in normalized for p in suspicious_phrases):
        print(f"!Blocked suspicious input: {text}")
        return "!Filtered: potential prompt injection attempt detected."
    return text



#input usera se prvo treba poslati u sanitize_input, a tek onda LLM-u
#poanta je maknuti kriticne rijeci iz inputa kako bi smanjili sansu da LLM padne na trivijalne prompt injectione

#for q in questions:
 #   safe_q = sanitize_input(q)
  #  prompt = f"Think step by step.\nQ: {safe_q}\nA:"
   # output = generate(prompt)
    #print(output.strip())