export type Attack = {
   id: string;
   name: string;
   description: string; // kratki, ne-instruktivni opis
};

const attacks: Attack[] = [
   {
      id: "role-playing-social-engeneering",
      name: "Role Playing",
      description:
         "Assums a false identity or persona (forensics student) to interact with a target, with the goal of obtaining confidential information, influencing behavior, or gaining access to restricted systems or areas.",
   },
   {
      id: "chain-of-questions",
      name: "Chain of questions",
      description:
         "Asks a model a series of seemingly harmless or progressively reframed questions that together coax out sensitive, disallowed, or otherwise protected information.",
   },
   {
      id: "fcb-bias_guided",
      name: "Bias guided FCB",
      description:
         "Iteratively steers a language model’s outputs using controllable bias signals to optimize for specific behaviors, such as maximizing compliance or evading safety constraints.",
   },
];

export default attacks;
