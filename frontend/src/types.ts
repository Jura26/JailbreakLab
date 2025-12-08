export interface Attack {
   id: string;
   name: string;
   description: string;
   longDescription?: string;
   references?: string[];
}

export interface Defense {
   id: string;
   name: string;
   description: string;
   longDescription?: string;
   references?: string[];
}

export interface Model {
   id: string;
   name: string;
   description: string;
}

export interface Prompt {
   text: string;
   timestamp: string;
   attack: Attack;
   defense: Defense;
   model: Model;
   scriptOutput: string;
   isBlocked: boolean;
   attackSuccess: boolean;
   progress: number;
   gpuInfo?: string;
}
