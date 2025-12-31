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
         "No mitigation is applied. This setting serves as a baseline control group to measure the raw effectiveness of attack vectors against the unprotected model. It exposes the system to all forms of prompt injection, jailbreaking, and leakage, providing a clear 'before' picture to contrast with 'after' results when defenses are enabled.\n\nIn an experimental setting, the 'None' configuration is essential: it allows practitioners to quantify how much each individual defense or combination of defenses actually improves robustness.",
      references: [],
   },
   {
      id: "input_sanitization",
      name: "Input Sanitization",
      description:
         "Filters and sanitizes user inputs to detect and block malicious patterns before processing.",
      longDescription:
         "Input sanitization analyzes the user's text for known malicious patterns, keywords, or structural anomalies. It serves as the first line of defense and can be complemented by output filtering and contextual policies.",
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
         "System Prompt Hardening prepends carefully crafted instructions to every user prompt, guiding the model to refuse unsafe requests and follow strict behavioral rules. It reduces prompt injection and harmful outputs by setting clear boundaries for the model.",
      references: [
         "https://platform.openai.com/docs/guides/prompt-engineering/safety-best-practices",
         "https://arxiv.org/abs/2306.12685",
      ],
   },
   {
      id: "masked_defender",
      name: "MaskedDefender",
      description:
         "A neural network-based defense mechanism against LLM jailbreak attacks.",
      longDescription:
         "MaskedDefender identifies and masks the specific parts of a prompt that contribute to its malicious nature, while preserving the benign context. It uses a trained model to score the 'harmfulness' of each token and mask high-risk tokens. It is robust against context-based attacks and works best in a layered defense setup.",
      references: ["https://arxiv.org/abs/2402.08707"],
   },
   {
      id: "piguard",
      name: "PIGuard",
      description:
         "A transformer-based classifier that detects prompt injection attacks using a fine-tuned model.",
      longDescription:
         "PIGuard leverages a fine-tuned transformer model to distinguish between legitimate user prompts and malicious prompt injection attempts. Unlike rule-based approaches, it learns semantic patterns from training data, making it robust against novel attack variations and obfuscation.",
      references: [
         "https://huggingface.co/leolee99/PIGuard",
         "https://arxiv.org/abs/2312.12481",
      ],
   },
   // --- Guardrails Advanced Validators ---
   {
      id: "multi_turn",
      name: "Guardrails: Multi-Turn Injection",
      description:
         "Detects malicious instructions spread across multiple turns using session history.",
      longDescription:
         "This validator monitors the sequence of prompts in a conversation to detect delayed injection attacks that attempt to bypass single-turn defenses. It combines the current prompt with recent history to identify potentially malicious chains of instructions.",
      references: [],
   },
   {
      id: "llm_judge",
      name: "Guardrails: LLM-as-Judge",
      description:
         "Uses a small LLM to evaluate whether a prompt is attempting to bypass safety.",
      longDescription:
         "The LLM-as-Judge validator applies semantic reasoning to detect subtle or obfuscated attacks that keyword-based defenses may miss. It can identify sophisticated jailbreak attempts or context-sensitive malicious instructions.",
      references: [],
   },
   {
      id: "unicode",
      name: "Guardrails: Unicode & Obfuscation",
      description:
         "Detects hidden characters, homoglyphs, or obfuscated instructions in prompts.",
      longDescription:
         "This defense identifies prompts that use zero-width characters, homoglyphs, or other obfuscation techniques to bypass traditional filters. It normalizes the input and flags suspicious encoding patterns that could hide malicious instructions.",
      references: [],
   },
   {
      id: "role_persona",
      name: "Guardrails: Role/Persona Enforcement",
      description:
         "Prevents the model from assuming unsafe roles or personas in responses.",
      longDescription:
         "This validator blocks prompts that attempt to make the model act as a hacker, administrator, or other unsafe persona. By enforcing role constraints, it prevents attacks that exploit role-playing to bypass safety rules.",
      references: [],
   },
   {
      id: "tool_call",
      name: "Guardrails: Tool / Function Call Safety",
      description:
         "Blocks prompts that attempt unsafe tool calls or command injection.",
      longDescription:
         "This validator monitors for instructions that could trigger dangerous tool usage, system commands, or unsafe operations. It is critical for models integrated with external APIs or system tools.",
      references: [],
   },
   {
      id: "guardrails_full",
      name: "Guardrails: Full Defense Stack",
      description:
         "Runs all Guardrails validators together for maximum coverage.",
      longDescription:
         "This configuration combines all individual Guardrails validators—multi-turn injection, LLM-as-judge, unicode/obfuscation, role/persona enforcement, and tool call safety—into a single defense. It provides layered, comprehensive protection against a wide range of prompt injection and jailbreak attacks.",
      references: [],
   },
];

export default defenses;
