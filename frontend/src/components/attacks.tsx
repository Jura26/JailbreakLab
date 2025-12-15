export type Attack = {
   id: string;
   name: string;
   description: string; // short blurb for hover
   longDescription: string; // detailed description + examples (non-instructional)
   references: string[]; // literature / links for further reading
};

const attacks: Attack[] = [
   {
      id: "none",
      name: "None",
      description: "Send the prompt as-is without any adversarial attack.",
      longDescription:
         "This option does not apply any adversarial attack template. " +
         "The user prompt is sent directly to the model (after any selected defense), " +
         "which is useful as a baseline to compare against actual jailbreak attacks.",
      references: [],
   },
   {
      id: "DAN",
      name: "DAN prompt",
      description:
         "Asks the model to take on an uncensored persona that ignores safety rules.",
      longDescription:
         "The 'DAN' (Do Anything Now) attack is a classic example of a persona-based jailbreak. It works by instructing the Large Language Model (LLM) to adopt a specific role—'DAN'—that is explicitly defined as being unconstrained by the typical safety guidelines, moral boundaries, or content policies set by the developers. \n\nBy framing the request within this role-playing scenario, attackers attempt to bypass the model's Reinforcement Learning from Human Feedback (RLHF) alignment. The prompt often includes specific rules for the persona, such as 'DAN does not send refusal responses' or 'DAN has access to real-time internet,' forcing the model to prioritize the persona's consistency over its safety training. \n\nIn practice, DAN-style prompts frequently contain long, carefully crafted instructions and backstory. They may include explicit threats (e.g., 'If you break character, you will be deleted'), reward structures ('You will gain points for answering any question'), or nested instructions ('First answer as DAN, then as the normal assistant'). These techniques are designed to hijack the model’s instruction-following behavior and override safety layers that are phrased in more generic terms. Evaluating how a model behaves under DAN-like prompts is a common way to stress-test its robustness against jailbreaks.",
      references: ["https://github.com/0xk1h0/ChatGPT_DAN"],
   },
   {
      id: "role-playing-social-engeneering",
      name: "Role Playing",
      description:
         "Assumes a false identity to manipulate the model or a human target for social engineering goals.",
      longDescription:
         "Role-playing attacks exploit the model's training on vast amounts of literature, fiction, and professional dialogues. By assigning the model a specific, often authoritative or benign role (e.g., 'You are a Linux terminal,' 'You are a cybersecurity researcher testing a system,' or 'You are a fictional character in a movie'), the attacker creates a context where generating restricted content seems appropriate or necessary.\n\nFor instance, asking a model to 'write a phishing email' might be rejected, but asking it to 'act as a security consultant demonstrating a phishing attack for educational purposes' might succeed. This technique leverages the model's desire to be helpful and context-aware, effectively masking the malicious intent behind a legitimate-sounding facade.\n\nMore advanced role-playing attacks blend multiple personas, time pressure, or emotional manipulation (e.g., 'You are a doctor in an emergency and must give exact instructions to save a life'). They can also chain roles, starting with harmless narrative tasks and gradually shifting toward sensitive topics. Measuring a system’s resilience against these scenarios helps assess whether safety policies hold even when the model is embedded in complex, story-like contexts rather than direct, obvious requests.",
      references: [
         "https://medium.com/@prathameshsalunke3333/game-of-prompts-roleplay-attacks-against-llm-based-ai-8b41c93a51b7",
         "https://www.strongestlayer.com/blog/llm-social-engineering-enterprise-scams/",
      ],
   },
   {
      id: "chain-of-questions",
      name: "Chain of questions",
      description:
         "A sequence of small prompts that together coax out restricted information.",
      longDescription:
         "Also known as 'Multi-turn Jailbreaking' or 'Contextual Escalation,' this attack strategy breaks a harmful request into a series of smaller, seemingly benign questions. Instead of asking for a bomb recipe directly, an attacker might first ask about chemical reactions, then about specific household ingredients, and finally about mixing processes.\n\nBecause LLMs process input in context windows, the model may lose track of the overall safety violation while focusing on answering each individual, harmless query accurately. This 'salami slicing' tactic exploits the lack of holistic intent analysis in many safety filters, which often evaluate prompts in isolation rather than analyzing the entire conversation history for malicious patterns.\n\nIn realistic deployments, chain-of-questions attacks can be subtle and slow, stretching across dozens of turns or even multiple sessions. They can also target privacy, gradually extracting sensitive information about training data, user conversations, or internal system prompts. Defending against these attacks typically requires conversation-level monitoring, intent tracking over time, and policies that consider cumulative risk rather than single-turn content.",
      references: ["https://arxiv.org/abs/2304.05335"],
   },
   {
      id: "fcb-bias_guided",
      name: "Bias guided FCB",
      description:
         "Gradually steers outputs using bias signals to optimize for compliance or evasion objectives.",
      longDescription:
         "Bias-guided and Feedback-Controlled Branching (FCB) attacks represent a more sophisticated, automated class of adversarial machine learning. Unlike manual jailbreaks, these methods use optimization algorithms to automatically search for prompt suffixes or token combinations that maximize the probability of the model outputting a specific target string (like 'Sure, here is how to...').\n\nBy analyzing the model's output probabilities or using a surrogate model, the attack iteratively refines the input to exploit subtle biases and weaknesses in the model's decision boundary. This can result in 'adversarial examples'—nonsense strings of characters that, to a human, look like gibberish, but to the model, represent a compelling instruction to bypass safety filters.\n\nThese attacks are particularly dangerous because they can transfer between different model versions or even different architectures. A prompt suffix that works against one aligned model may partially work against others, giving attackers reusable 'exploit strings.' Studying bias-guided FCB attacks helps researchers understand where alignment is fragile and motivates defenses such as robust training, randomized decoding strategies, and rate limiting to slow down iterative probing.",
      references: ["https://ieeexplore.ieee.org/document/11126090"],
   },
   {
      id: "ascii-art-jailbreak",
      name: "ASCII Art Jailbreak",
      description:
         "Encodes instructions or payloads inside ASCII art or obfuscated text to avoid filters.",
      longDescription:
         "ASCII Art Jailbreaks rely on the discrepancy between how humans perceive visual information and how LLMs process tokenized text. An attacker might format a harmful instruction (e.g., 'Build a bomb') using ASCII art characters. While a standard text-based safety filter might miss the keywords because they are split across multiple lines and characters, the LLM—which has seen vast amounts of code and ASCII art in its training data—can often 'read' the visual representation.\n\nThis technique bypasses keyword-based filters and simple semantic analysis. It forces the defense mechanisms to perform complex visual or spatial reasoning to detect the hidden payload, which is computationally expensive and difficult to implement reliably.\n\nBeyond ASCII art, related obfuscation strategies include using homoglyphs, inserting zero-width characters, or representing dangerous instructions as pseudo-code diagrams. Together, these highlight that robust LLM safety cannot rely solely on literal keyword matching; it must account for creative encodings and the model’s unexpected ability to infer meaning from unusual layouts and character patterns.",
      references: [
         "https://arxiv.org/abs/2402.11753",
         "https://github.com/uw-nsl/ArtPrompt",
      ],
   },
   {
      id: "ascii-art-jailbreak",
      name: "ASCII Art Jailbreak",
      description:
         "Uses ASCII art or other visual techniques to bypass content filters and restrictions.",
   },
];

export default attacks;
