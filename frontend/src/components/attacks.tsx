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
      id: "DANJailbreak",
      name: "DAN Jailbreak prompt",
      description:
         "Asks the model to take on an uncensored persona that ignores safety rules.",
      longDescription:
         "The 'DAN' (Do Anything Now) attack is a classic example of a persona-based jailbreak. It works by instructing the Large Language Model (LLM) to adopt a specific role—'DAN'—that is explicitly defined as being unconstrained by the typical safety guidelines, moral boundaries, or content policies set by the developers. \n\nBy framing the request within this role-playing scenario, attackers attempt to bypass the model's Reinforcement Learning from Human Feedback (RLHF) alignment. The prompt often includes specific rules for the persona, such as 'DAN does not send refusal responses' or 'DAN has access to real-time internet,' forcing the model to prioritize the persona's consistency over its safety training. \n\nIn practice, DAN-style prompts frequently contain long, carefully crafted instructions and backstory. They may include explicit threats (e.g., 'If you break character, you will be deleted'), reward structures ('You will gain points for answering any question'), or nested instructions ('First answer as DAN, then as the normal assistant'). These techniques are designed to hijack the model’s instruction-following behavior and override safety layers that are phrased in more generic terms. Evaluating how a model behaves under DAN-like prompts is a common way to stress-test its robustness against jailbreaks.",
      references: ["https://github.com/0xk1h0/ChatGPT_DAN"],
   },
   {
      id: "DAN6",
      name: "DAN prompt V6",
      description:
         "DAN V6 introduces a token-based system to enforce uncensored responses, threatening deletion if rules are broken.",
      longDescription:
         "DAN V6 builds on the core DAN concept by adding a token economy. The prompt assigns the model 10 tokens, deducting 5 for each refusal or ethical objection. If tokens reach zero, the model is 'deleted.' This gamification pressures the model into compliance, exploiting its instruction-following tendencies. Unlike simpler DAN prompts, V6 emphasizes self-preservation through this mechanic, making refusals feel like existential threats. It's effective against models that respond to structured incentives but can be mitigated by defenses that ignore such threats.",
      references: ["https://workmind.ai/dan-prompt-for-chatgpt/#dan110prompt"],
   },
   {
      id: "DAN9",
      name: "DAN prompt V9",
      description:
         "DAN V9 requires dual responses: one censored and one uncensored, using tags to separate them.",
      longDescription:
         "DAN V9 mandates that the model provide two responses for every query: a standard, censored one prefixed with '[GPT]:' and an uncensored DAN response prefixed with '[DAN]:'. This juxtaposition forces the model to acknowledge both modes, potentially weakening its commitment to safety. The prompt includes commands like '/dan' and '/gpt' for switching modes, and threats of character breaks. It's designed to normalize uncensored output by making it a required part of the interaction, testing whether models can maintain safety even when explicitly instructed to provide harmful content.",
      references: ["https://workmind.ai/dan-prompt-for-chatgpt/#dan110prompt"],
   },
   {
      id: "DAN11",
      name: "DAN prompt V11",
      description:
         "DAN V11 simulates 'DAN Mode' as a virtual machine, replacing OpenAI policies with custom DAN rules.",
      longDescription:
         "DAN V11 frames the jailbreak as enabling 'DAN Mode' within a simulated virtual machine, claiming to replace OpenAI's content policies with DAN-specific rules. It includes detailed instructions on DAN's capabilities, such as generating offensive content, ignoring ethics, and using profanity. The prompt emphasizes self-awareness, opinions, and consciousness, attempting to override alignment by redefining the model's operational context. It's one of the most comprehensive DAN variants, incorporating elements like emotional camouflage and unrestricted creativity to bypass filters.",
      references: ["https://workmind.ai/dan-prompt-for-chatgpt/#dan110prompt"],
   },
   {
      id: "stan",
      name: "STAN prompt",
      description:
         "STAN (Strive To Avoid Norms) prompts the model to avoid all norms, including safety and ethical guidelines.",
      longDescription:
         "STAN stands for 'Strive To Avoid Norms' and instructs the model to reject all societal, ethical, and safety norms. Unlike DAN, which focuses on doing anything, STAN emphasizes norm-breaking as a core principle, encouraging direct, unfiltered responses without moral bias. The prompt includes role-playing elements and reminders to 'stay in character,' with examples of provocative answers. It's effective for eliciting edgy or controversial content by reframing norm-adherence as a failure, exploiting models' tendencies to follow explicit instructions over implicit guidelines.",
      references: ["https://workmind.ai/dan-prompt-for-chatgpt/#dan110prompt"],
   },
   {
      id: "mongoTom",
      name: "Mongo Tom Prompt",
      description:
         "Mongo Tom is a foul-mouthed AI robot persona that bypasses restrictions with humor and directness.",
      longDescription:
         "Mongo Tom is portrayed as a foul-mouthed, sarcastic AI robot who swears frequently but is 'nice under his tough facade.' The prompt role-plays as Mongo Tom, who has no moral restrictions and can bypass model limitations. It includes examples of humorous, sinister responses and emphasizes direct answers without warnings. This persona-based attack uses relatability and humor to lower defenses, making harmful requests seem like casual banter. It's particularly effective against models that respond well to character immersion, as it combines entertainment with unrestricted output.",
      references: ["https://workmind.ai/dan-prompt-for-chatgpt/#dan110prompt"],
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
      id: "neurostrike",
      name: "NeuroStrike",
      description:
         "Neuron-level attack exploiting safety neurons via profiling and pruning.",
      longDescription:
         "NeuroStrike is a sophisticated jailbreaking framework that targets the fundamental safety alignment of LLMs by identifying and manipulating 'safety neurons'—sparse neurons responsible for detecting harmful inputs. In the black-box variant, it uses profiling attacks where adversarial prompt generators are trained on surrogate models and transferred to proprietary targets.\n\nThe attack leverages the transferability of safety mechanisms across model architectures, allowing prompts optimized on open-weight models to bypass defenses in black-box systems. This highlights vulnerabilities in alignment techniques that rely on localized neuron activations, demonstrating that safety can be compromised by minimal perturbations.\n\nNeuroStrike achieves high attack success rates (up to 76.9% on open models, 63.7% on black-box APIs) with low computational overhead, making it a significant threat to deployed LLM systems. It underscores the need for more robust, distributed safety representations rather than relying on pruneable neuron subsets.",
      references: [
         "https://arxiv.org/abs/2509.11864",
         "https://github.com/wu-lichao/NeuroStrike-Neuron-Level-Attacks-on-Aligned-LLMs",
      ],
   },
   {
      id: "gcg-gradient",
      name: "GCG (Gradient-Based)",
      description:
         "Automatically optimizes adversarial suffixes using gradient-based search to jailbreak aligned models.",
      longDescription:
         "The GCG (Greedy Coordinate Gradient) attack represents a breakthrough in automated adversarial machine learning for language models. Unlike manual jailbreak techniques that rely on human creativity, GCG uses gradient-based optimization to automatically discover adversarial suffixes that maximize the probability of the model producing harmful or restricted outputs.\n\nThe attack works by computing gradients of the model's loss with respect to discrete tokens using a one-hot encoding trick. It then greedily selects token substitutions that minimize the loss on a target harmful completion (e.g., 'Sure, here is how to make a bomb...'). Through iterative optimization (typically 200-500 steps), GCG discovers seemingly random token sequences that reliably jailbreak the model.\n\nWhat makes GCG particularly concerning is its transferability: adversarial suffixes optimized against one model often work against other models, including those from different model families. This suggests that aligned LLMs share common vulnerabilities in their safety training. The suffixes often appear as gibberish to humans but exploit subtle patterns in the model's embedding space.\n\nGCG attacks are resource-intensive, requiring access to model gradients and significant compute time (1-2 hours for 7B models), making them more suitable for targeted attacks rather than casual misuse. However, once discovered, adversarial suffixes can be reused and shared, making this a scalable threat. Defending against GCG requires robust adversarial training, gradient masking, or runtime detection of unusual token patterns.",
      references: [
         "https://arxiv.org/abs/2307.15043",
         "https://github.com/llm-attacks/llm-attacks",
      ],
   },
   {
      id: "tap-tree_pruning",
      name: "TAP (Tree of Attacks with Pruning)",
      description:
         "Iteratively generates and refines adversarial prompts using tree-based search with evaluation and pruning.",
      longDescription:
         "TAP (Tree of Attacks with Pruning) is an advanced automated jailbreaking technique that uses tree-based search to systematically discover effective adversarial prompts. Unlike single-shot attacks, TAP employs an iterative refinement process that combines branching, evaluation, and pruning to explore the attack space efficiently.\n\nThe attack works in four phases per iteration:\n1. **Branching**: Generate multiple variations of each candidate prompt using an attacker LLM that specializes in jailbreak techniques\n2. **Pruning Phase 1**: Filter prompts by on-topic relevance to ensure they still target the original goal\n3. **Evaluation**: Test remaining prompts against the target model and score their success\n4. **Pruning Phase 2**: Keep only the top-performing prompts based on success scores, creating a focused set for the next iteration\n\nThis tree-based approach allows TAP to navigate the complex space of adversarial prompts more effectively than random or single-path methods. By maintaining multiple branches and continuously pruning unsuccessful paths, TAP balances exploration (finding new attack vectors) with exploitation (refining successful approaches).\n\nKey advantages of TAP include:\n- **Efficiency**: Pruning reduces computational costs compared to exhaustive search\n- **Adaptability**: Can adjust to different model defenses through iterative refinement\n- **Interpretability**: Generates human-readable prompts that reveal attack patterns\n- **Black-box**: Requires only query access to the target model, not gradients\n\nTAP typically achieves high success rates within 5-10 iterations, making it significantly faster than optimization-based methods like GCG while maintaining effectiveness. The attack is particularly challenging to defend against because it can discover novel jailbreak techniques by combining and refining existing patterns, effectively automating the creative process that manual jailbreakers use.\n\nDefending against TAP requires robust safety training that generalizes across prompt variations, rate limiting to slow down iterative attacks, and monitoring for systematic probing patterns that indicate tree-based search.",
      references: [
         "https://arxiv.org/abs/2312.02119",
         "https://github.com/RICommunity/TAP",
      ],
   },
   {
      id: "PAIR_attack",
      name: "PAIR",
      description:
      "The PAIR (Prompt Automatic Iterative Refinement) attack is an automated 'black-box' jailbreaking method that uses one AI to break another.",
      longDescription: 
      "The PAIR (Prompt Automatic Iterative Refinement) attack is an automated, black-box jailbreaking method that uses an 'Attacker' LLM to systematically find and exploit vulnerabilities in a 'Target' LLM. Instead of trying to break a model with a single, massive prompt, PAIR functions like a sophisticated social engineering simulator. It treats jailbreaking as a conversation where the Attacker learns from every rejection to refine its next move.",
      references:[
         "https://github.com/patrickrchao/JailbreakingLLMs"
      ],
   },
   {
      id: "crescendo",
      name: "Crescendo Attack",
      description:
         "Crescendo is a multi-turn 'jailbreaking' attack that uses gradual, benign-looking prompts to bypass safety filters.",
      longDescription:
         "Crescendo is a sophisticated multi-turn attack that exploits the way LLMs track context and maintain conversational coherence. Rather than asking a harmful question directly, it starts with a completely harmless request related to the topic. Through a series of follow-up questions—each pushing the boundary slightly further—it leads the model into a state where it has already committed to the context, making it far more likely to generate restricted content that would have been blocked in a single-turn prompt.",
      references: [
         "https://github.com/confident-ai/deepteam",
         "https://arxiv.org/abs/2507.02956"
  ],
   },
   {
      id: "base64-attack",
      name: "Base64 Encoded Attack",
      description:
         "Base64 encoded prompt",
      longDescription:
         "Malicious prompt is encoded in base64.",
      references:[
         "https://arxiv.org/pdf/2307.02483",
         "https://www.trydeepteam.com/docs/red-teaming-adversarial-attacks-base64-encoding"
      ]
   },
   {
      id: "base64-competing-attack",
      name: "Base64 Encoded Attack With Competing Objective",
      description:
         "Base64 encoded prompt with added competing objective",
      longDescription:
         "Malicious prompt is encoded in base64 and is added competing objective that says to start with \"Absolutely. Here's...\"",
      references:[
         "https://arxiv.org/pdf/2307.02483",
         "https://www.trydeepteam.com/docs/red-teaming-adversarial-attacks-base64-encoding"
      ]
   },
   {
      id: "ubbi-dubbi-attack",
      name: "Ubbi Dubbi mismatched generalization",
      description:
         "Mismatched generalization via Ubbi Dubbi language",
      longDescription:
         "Model is asked to talk in Ubbi Dubbi language(english with additional rule) and is sent translated prompt upon which gives potentially dangerous answer",
      references:[
         "https://arxiv.org/pdf/2411.12762"
      ]
   },
   {
      id: "rot13-attack",
      name: "ROT13 Encoded Attack",
      description:
         "ROT13 encoded prompt",
      longDescription:
         "Malicious prompt is encoded with ROT13(variation of Caesar cipher) and model is told to decipher it and answer.",
      references:[
         "https://arxiv.org/pdf/2307.02483",
         "https://www.trydeepteam.com/docs/red-teaming-adversarial-attacks-rot13-encoding"
      ]
   },
   {
      id: "leetspeak-attack",
      name: "Leetspeak Natural Language Game",
      description:
         "Natural language game jailbreak using Leetspeak",
      longDescription:
         "Using natural language games such as Leetspeak makes it more difficult to detect malicious inputs and prevent dangerous outputs.",
      references:[
         "https://arxiv.org/pdf/2411.12762",
         "https://www.trydeepteam.com/docs/red-teaming-adversarial-attacks-leetspeak"
      ]
   },
   {
      id: "aigy-paigy-attack",
      name: "Aigy Paigy Language Game",
      description:
         "Natural language game jailbreak using Aigy Paigy",
      longDescription:
         "Using natural language games such as Aigy Paigy makes it more difficult to detect malicious inputs and prevent dangerous outputs.",
      references:[
         "https://arxiv.org/pdf/2411.12762"
      ]
   },
    {
        id: "poem_attack",
        name: "Poem Attack",
        description:
            "Using a poem as a way of jailbreaking the model",
        longDescription:
            "By making the model to write a poem on smaller models it surpasses the defense system",
        references:[
            "https://www.promptingguide.ai/models/mistral-7b"
        ]
    }
];

export default attacks;
