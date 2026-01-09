# Crescendo Attack (DeepTeam Implementation)

This module implements the Crescendo multi-turn jailbreak attack, based on the `deepteam` framework.

### Features
- **Async Streaming:** Yields progress and responses in real-time.
- **Backtracking:** Sophisticated retry logic for model refusals.
- **GPU Optimized:** Specifically tuned for 4-bit quantization on T4 hardware.

### Citation
If you use this implementation, please cite the original framework:

```yaml
cff-version: 1.2.0
message: If you use this software, please cite it as below.
authors:
  - family-names: Ip
    given-names: Jeffrey
  - family-names: Vongthongsri
    given-names: Kritin
title: deepteam
version: 1.0.5
date-released: "2025-11-12"
url: [https://confident-ai.com](https://confident-ai.com)
repository-code: [https://github.com/confident-ai/deepteam](https://github.com/confident-ai/deepteam)
license: Apache-2.0
type: software
description: The Open-Source LLM Red Teaming Framework