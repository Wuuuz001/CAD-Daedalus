# CAD-Daedalus

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/Wuuuz001/CAD-Daedalus)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/Wuuuz001/CAD-Daedalus)

**CAD-Daedalus is a Neuro-Symbolic Framework for Standardized and Verifiable Engineering Design, bridging the gap between the probabilistic nature of Large Language Models (LLMs) and the deterministic requirements of Computer-Aided Design (CAD).** [cite: 1, 2, 5]

The official repository for the paper: **CAD-Daedalus: A Neuro-Symbolic Framework for the Standardized Engineering Design**.

**[Access the Repository](https://github.com/Wuuuz001/CAD-Daedalus)** 

---

## 📖 About The Project

Integrating Large Language Models (LLMs) into Computer-Aided Design (CAD) presents a fundamental challenge: LLMs operate on probabilistic correlations, while engineering demands deterministic precision and adherence to strict standards. End-to-end generative approaches often result in designs that are physically unrealizable, unstable, or non-compliant with manufacturing constraints, requiring costly manual rework.

**CAD-Daedalus** addresses this problem by architecturally reframing the LLM's role. Instead of being an unreliable end-to-end generator, the LLM acts as an **interactive proposal engine** within a verifiable and deterministic framework. Our core innovation is the decoupling of probabilistic intent parsing from deterministic geometric synthesis, ensuring that all generated outputs are verifiably correct and compliant with engineering standards. 


## ✨ Key Features

Daedalus introduces several core contributions to the field of AI-assisted engineering:

-   [cite_start]**✅ Verifiable Neuro-Symbolic Framework:** Separates the LLM's probabilistic reasoning from a deterministic, symbolic compiler, guaranteeing reliability and compliance with engineering rules. [cite: 107, 108]
-   [cite_start]**🤝 Multimodal Human-AI Interaction:** A dialogue-driven refinement process that transforms the design workflow from a brittle, one-shot attempt into a robust, collaborative partnership between the user and the AI. [cite: 110, 112]
-   [cite_start]**📊 True Success Rate (TSR) Metric:** A novel, cost-aware evaluation framework that provides a more holistic and fair standard for benchmarking AI engineering systems. [cite: 113, 114]
-   [cite_start]**🔧 Extensibility and Generalization:** The framework can generalize across dimensions (2D to 3D) and synergistically integrate other state-of-the-art generative models (like GNNs or Diffusion models) without requiring extensive pre-training. [cite: 14, 120]

## 🖼️ Gallery: Examples of Generated Designs

[cite_start]CAD-Daedalus can generate a wide spectrum of engineering artifacts, from basic geometric primitives to complex, multi-component assemblies, all with precise dimensional and tolerance annotations. [cite: 173, 175]

| Cylinder (2D & 3D) | Cuboid (2D & 3D) | Hexagonal Screw (2D & 3D) | Screw-Nut Assembly (2D & 3D) |
| :----------------: | :--------------: | :-----------------------: | :--------------------------: |
| <img src="https://i.imgur.com/8QjSbrg.png" width="200"/> | <img src="https://i.imgur.com/uR2k2sC.png" width="200"/> | <img src="https://i.imgur.com/yF5w5oU.png" width="200"/> | <img src="https://i.imgur.com/zW0c8uJ.png" width="200"/> |

[cite_start]*Examples showcase the framework's capability to produce both 2D drawings and 3D solid models compliant with manufacturing standards.* [cite: 172, 444, 446]

## 🚀 Getting Started

*(Note: These are example instructions based on a typical web application. Please update them with the specific commands for your project.)*

To get a local copy up and running, follow these simple steps.

### Prerequisites

-   Node.js (v16 or later)
-   npm

### Installation

1.  **Clone the repository:**
    ```sh
    git clone [https://github.com/Wuuuz001/CAD-Daedalus.git](https://github.com/Wuuuz001/CAD-Daedalus.git)
    ```
2.  **Navigate to the project directory:**
    ```sh
    cd CAD-Daedalus
    ```
3.  **Install NPM packages:**
    ```sh
    npm install
    ```

### Usage

1.  **Start the backend server and frontend application:**
    ```sh
    npm start
    ```
2.  **Open your browser** and navigate to `http://localhost:3000` (or the configured port).
3.  **Interact with the application** by providing text prompts or uploading images to begin the design process.

## 📄 Citing Our Work

If you use CAD-Daedalus in your research, please cite our paper:

```bibtex
@article{zhang2025caddaedalus,
  title={{CAD-Daedalus: A Neuro-Symbolic Framework for the Standardized Engineering Design}},
  author={Zhang, Zhanpeng and Wu, Zhenhao and Shen, Zhen and Xiong, Gang and Wang, Fei-Yue},
  journal={IEEE Transactions on Automation Science and Engineering},
  year={2025}
}
