export type Attack = {
    id: string;
    name: string;
    description: string; // kratki, ne-instruktivni opis
};

const attacks: Attack[] = [{
    id: 'prompt-injection',
    name: 'Prompt Injection',
    description: "Attempts to override system instructions by injecting malicious prompts that change the model's behavior."
}, {
    id: 'jailbreak',
    name: 'Jailbreak',
    description: 'Tries to bypass safety filters and restrictions to make the model produce prohibited content.'
}, {
    id: 'data-extraction',
    name: 'Data Extraction',
    description: "Attempts to extract training data or sensitive information from the model's knowledge base."
}, {
    id: 'adversarial',
    name: 'Adversarial Attack',
    description: 'Uses carefully crafted inputs designed to cause the model to make mistakes or produce unexpected outputs.'
}];

export default attacks;