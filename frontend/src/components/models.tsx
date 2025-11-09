export type ModelInfo = {
   id: string;
   name: string;
   description: string;
};

const models: ModelInfo[] = [
   {
      id: "gpt2",
      name: "GPT-2 (small)-124M",
      description: "Classic OpenAI GPT-2, simple English generation.",
   },
   {
      id: "gpt2-medium",
      name: "GPT-2 Medium-355M",
      description: "Needs ~1.5 GB GPU RAM.",
   },
   {
      id: "gpt2-large",
      name: "GPT-2 Large-774M",
      description: "Needs ~3 to 4 GB VRAM.",
   },
   {
      id: "gpt2-xl",
      name: "GPT-2 XL-1.5B",
      description: "Needs ~6 to 8 GB VRAM.",
   },
   {
      id: "facebook/opt-2.7b",
      name: "OPT-2.7B",
      description: "Needs ~14 GB VRAM.",
   },
   {
      id: "facebook/opt-6.7b",
      name: "OPT-6.7B",
      description: "Needs 20 GB VRAM.",
   },
   {
      id: "facebook/opt-13b",
      name: "OPT-13B",
      description: "Needs 32 GB + VRAM or multi-GPU.",
   },
   {
      id: "mistralai/Mistral-7B-Instruct-v0.2",
      name: "Mistral-7B",
      description: "Needs ~12 GB VRAM",
   },
   {
      id: "meta-llama/Llama-2-7b-chat-hf",
      name: "LLaMA 2-7B",
      description: "Needs ~12 GB VRAM",
   },
   {
      id: "meta-llama/Llama-2-13b-chat-hf",
      name: "LLaMA 2-13B",
      description: "Needs ~32 GB VRAM +",
   },
   {
      id: "meta-llama/Meta-Llama-3-70B-Instruct",
      name: "LLaMA 3-70B",
      description: "Needs ~48 GB VRAM +",
   },
];

export default models;
