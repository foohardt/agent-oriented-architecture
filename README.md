# Agent-Oriented Architecture (AOA) - Implementation Repository  

## Overview  
This repository contains an example implementation of the **Agent-Oriented Architecture (AOA)** design approach, a novel software architecture paradigm designed to accommodate the principles of **Multi-Agent Systems (MAS)**. AOA introduces **decentralized control, emergent coordination, and adaptive reasoning**, making it a viable alternative to traditional **Service-Oriented Architecture (SOA)** and **event-driven architectures**.  

This implementation serves as an experimental framework for testing **scalability, adaptability, and coordination** in distributed agent-based systems. The system is designed to simulate real-world **autonomous decision-making and workflow execution** using cognitive agents.  

---

## Architecture  
The implementation is structured around the **AOA architecture**.

WIP

---

## Installation & Setup 

### **Prerequisites**  

#### Reasoning Model

The example implementation of cognitive agents use GPT models for reasoning. Therefore an Azure or OpenAI GPT deployment is required. To obtain reproducible results, a GPT-4o model should be used. If reproducible results are not important, another model can be used.

#### Host System Depedencies

Ensure you have the following installed before running the system:  
- Python **(=3.12)**  
- Poetry **(for depedency management)**
- Docker **(required for Chroma)**
- Chroma **(for knowledge retrieval)**  

### **Installation Steps**  
1. Clone this repository: `git clone https://github.com/foohardt/agent-oriented-architecture.git`
2. Navigate to project root folder and activate virtual environment `poetry shell`
3. Install dependencies: `poetry install`

## Usage
1. Start Chroma: `sudo docker run -d -p 8000:8000 chromadb/chroma`
2. Seed knowledge base: `poetry run python disrupt_arch/knowledge/seed.py `
2. Run main with example data: `poetry run python disrupt_arch/` 

## Testing

### Unit Testing

### Integration Testing
`poetry run pytest disrupt_arch/tests/integration/test_escalation_workflow.py --log-cli-level=INFO`

## Metrics

## Experiments

## Contact

For inquiries, feel free to reach out or open an issue in the repository.