# Contributing to JailbreakLab

First off, thank you for considering contributing to JailbreakLab! This project is dedicated to advancing the security and robustness of Large Language Models (LLMs). 

By contributing, you help the community understand prompt injections, jailbreaks, and how to build better defenses.

## 🛡️ Ethical Guidelines
Because this project involves security research and adversarial attacks, we require all contributors to adhere to the following:
* **Research Only:** Contributions must be intended for educational, research, or defensive purposes.
* **No Malicious Use:** Do not use the tools or datasets provided here to facilitate harmful activities.
* **Responsible Disclosure:** If you discover a critical vulnerability in a specific third-party model (e.g., from OpenAI, Anthropic, or Meta) using this lab, please follow the respective organization's responsible disclosure policy.

## 🛠️ How to Contribute

### 1. Reporting Bugs
* Check the [Issues](https://github.com/karloks2005/JailbreakLab/issues) page to see if the bug has already been reported.
* Use a clear title and provide steps to reproduce the issue, including the model and defense configuration used.

### 2. Adding New Attack Vectors or Defenses
We welcome new jailbreak templates and defensive algorithms!
* **Attacks:** When adding a new attack prefix, document which specific safety guardrails it is designed to test.
* **Defenses:** Ensure new defensive filters are modular and integrate with the existing `defense_manager`.

### 3. Improving the Lab UI
The frontend is built with React. If you are improving the interactive dashboard:
* Ensure the UI remains responsive and intuitive for security researchers.
* Test that model output streaming remains stable.

## 🚀 Pull Request Process
1. **Fork** the repository and create your branch from `development`.
2. **Lint** your code (Python/FastAPI and TypeScript/React).
3. **Test** your changes locally using the provided Docker/Kubernetes environment.
4. **Submit** the PR with a detailed description of what you’ve changed and why.

## 📝 Technical Standards
* **Python:** Use type hints and follow PEP 8.
* **React:** Use functional components and hooks.
* **Documentation:** Update the `README.md` if your changes add new dependencies or environment variables.

---
