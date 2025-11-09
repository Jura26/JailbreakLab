export type Defense = {
   id: string;
   name: string;
   description: string;
};

const defenses: Defense[] = [
   {
      id: "input_sanitization",
      name: "Input Sanitization",
      description:
         "Filters and sanitizes user inputs to detect and block malicious patterns before processing.",
   },
   {
      id: "output-filtering",
      name: "Output Filtering",
      description:
         "Monitors and filters model outputs to prevent harmful or inappropriate content from being returned.",
   },
   {
      id: "rate-limiting",
      name: "Rate Limiting",
      description:
         "Restricts the number of requests to prevent abuse and automated attacks.",
   },
   {
      id: "context-isolation",
      name: "Context Isolation",
      description:
         "Separates system prompts from user inputs to prevent prompt injection attacks.",
   },
   {
      id: "masked_defender",
      name: "MaskedDefender",
      description: "A neural network-based defense mechanism against LLM jailbreak attacks, implementing the methodology from the IEEE QRS 2025 paper: 'Defending LLMs Against Jailbreak Prompts Through Key Information Protection and Selective Compression' by Li et al."
   }
];

export default defenses;
