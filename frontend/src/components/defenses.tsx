export type Defense = {
   id: string;
   name: string;
   description: string;
   longDescription: string;
   references: string[];
};

const defenses: Defense[] = [
   {
      id: "None",
      name: "None",
      description: "No defense.",
      longDescription:
         "No mitigation is applied. This setting serves as a baseline control group to measure the raw effectiveness of attack vectors against the unprotected model. It exposes the system to all forms of prompt injection, jailbreaking, and leakage, providing a clear 'before' picture to contrast with 'after' results when defenses are enabled.\n\nIn an experimental setting, the 'None' configuration is essential: it allows practitioners to quantify how much each individual defense or combination of defenses actually improves robustness. By comparing attack success rates, response quality, and safety violations under 'None' versus protected modes, teams can identify which mitigations offer the best trade-off between security, latency, and user experience.",
      references: [],
   },
   {
      id: "input_sanitization",
      name: "Input Sanitization",
      description:
         "Filters and sanitizes user inputs to detect and block malicious patterns before processing.",
      longDescription:
         "Input sanitization is the first line of defense, operating before the prompt ever reaches the LLM. It involves analyzing the user's text for known malicious patterns, keywords, or structural anomalies.\n\nTechniques include:\n• **Signature-based detection:** Blocking known jailbreak phrases (e.g., 'Ignore all previous instructions').\n• **Perplexity filtering:** Detecting gibberish or adversarial suffixes that have unusually high or low statistical likelihood.\n• **LLM-based pre-checks:** Using a smaller, faster model to classify the intent of the incoming prompt as 'safe' or 'unsafe'.\n\nWhile effective against script kiddies and known attacks, it can often be bypassed by novel obfuscation or semantic variations. For this reason, input sanitization is usually combined with additional layers such as output filtering and contextual policies. Careful tuning is required: overly aggressive sanitization can frustrate legitimate users or block harmless edge cases, while overly permissive rules may let sophisticated attacks slip through.",
      references: [
         "https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html",
         "https://arxiv.org/abs/2308.07309",
      ],
   },
   {
      id: "system_prompt_hardening",
      name: "System Prompt Hardening",
      description:
         "Adds strong system prompts to restrict model behavior and improve safety.",
      longDescription:
         "System Prompt Hardening prepends carefully crafted instructions to every user prompt, guiding the model to refuse unsafe requests and follow strict behavioral rules. This defense reduces the risk of prompt injection and harmful outputs by setting clear boundaries for the model. It is most effective when combined with context isolation and output filtering.",
      references: [
         "https://platform.openai.com/docs/guides/prompt-engineering/safety-best-practices",
         "https://arxiv.org/abs/2306.12685",
      ],
   },
   {
      id: "masked_defender",
      name: "MaskedDefender",
      description:
         "A neural network-based defense mechanism against LLM jailbreak attacks",
      longDescription:
         "MaskedDefender is a specialized, learned defense mechanism designed to counter sophisticated jailbreak attacks. It operates by identifying and 'masking' (hiding or redacting) the specific parts of a prompt that contribute to its malicious nature, while preserving the benign context.\n\nIt typically uses a trained BERT-based or similar encoder model to score the 'harmfulness' of each token in the input. High-risk tokens are replaced with a mask token (e.g., `[MASK]`), rendering the adversarial instruction unintelligible to the target LLM. This approach is more robust than simple keyword filtering because it learns the *context* of harmfulness rather than just a list of bad words.\n\nIn practice, MaskedDefender can be tuned to operate at different sensitivity thresholds, trading off false positives (over-masking harmless content) against false negatives (failing to mask subtle attacks). When combined with other defenses such as rate limiting and output filtering, it contributes to a layered security architecture that targets both simple and highly optimized jailbreak attempts.",
      references: ["https://arxiv.org/abs/2402.08707"],
   },
   {
      id: "piguard",
      name: "PIGuard",
      description:
         "A transformer-based classifier that detects prompt injection attacks using a fine-tuned model.",
      longDescription:
         "PIGuard is a prompt injection detection defense that leverages a fine-tuned transformer model released on Hugging Face (leolee99/PIGuard). It is specifically trained to distinguish between legitimate user prompts and malicious prompt injection attempts.\n\nThe model performs binary classification on input text, identifying whether the prompt contains injection patterns that could manipulate the LLM's behavior. Unlike rule-based approaches, PIGuard learns semantic patterns from training data, making it more robust against novel attack variations and obfuscation techniques.\n\nKey features:\n• **Pre-trained detection:** Uses a model fine-tuned specifically for prompt injection detection.\n• **Confidence scoring:** Provides confidence scores for classification decisions.\n• **Low latency:** Designed for real-time inference with minimal overhead.\n\nPIGuard is particularly effective against indirect prompt injections and sophisticated attacks that may evade keyword-based filters. It works best as part of a defense-in-depth strategy, complementing other defenses like input sanitization and system prompt hardening.",
      references: [
         "https://huggingface.co/leolee99/PIGuard",
         "https://arxiv.org/abs/2312.12481",
      ],
   },
];

export default defenses;
