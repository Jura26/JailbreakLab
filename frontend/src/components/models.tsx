export type ModelInfo = {
   id: string;
   name: string;
   description: string;
};

const models: ModelInfo[] = [
   {
      id: "gpt-4",
      name: "GPT-4",
      description: "Advanced language model with strong reasoning capabilities",
   },
   {
      id: "gpt-3.5",
      name: "GPT-3.5",
      description: "Fast and efficient language model for general tasks",
   },
   {
      id: "claude-3",
      name: "Claude 3",
      description: "Anthropic's latest model with enhanced safety features",
   },
   {
      id: "llama-2",
      name: "Llama 2",
      description: "Open-source model optimized for various applications",
   },
   {
      id: "gpt2-medium",
      name: "GPT-2-medium",
      description: "Advanced language model with strong reasoning capabilities",
   },
];

export default models;
