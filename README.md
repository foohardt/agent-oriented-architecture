# Agent-Oriented Architecture (AOA) - Implementation Repository  

## Overview  
This repository contains the implementation of the **Agent-Oriented Architecture (AOA)**, a novel software architecture paradigm designed to accommodate the principles of **Multi-Agent Systems (MAS)**. AOA introduces **decentralized control, emergent coordination, and adaptive reasoning**, making it a viable alternative to traditional **Service-Oriented Architecture (SOA)** and **event-driven architectures**.  

This implementation serves as an experimental framework for testing **scalability, adaptability, and coordination** in distributed agent-based systems. The system is designed to simulate real-world **autonomous decision-making and workflow execution** using cognitive agents.  

---

## Features  
- **Agent-Based Decentralization:** Agents interact dynamically without a central orchestrator.  
- **Emergent Coordination:** Workflows adapt in real time based on inter-agent negotiations.  
- **Adaptive Reasoning:** Agents retrieve domain knowledge and make probabilistic decisions.  
- **Event-Driven Communication:** The system leverages an event-driven model to enhance responsiveness.  
- **Scalability & Fault Tolerance:** Redundant agent roles allow seamless recovery from failures.  

---

## Architecture  
The implementation is structured around the **AOA architecture**, consisting of four core layers:  

1. **Knowledge Base Layer:** Agents retrieve context-aware knowledge dynamically.  
2. **Communication Layer:** Asynchronous message queues facilitate inter-agent communication.  
3. **Agent Coordination Layer:** A dynamic registry enables adaptive role assignment.  
4. **Execution Layer:** Task execution is handled by domain-specific agents.  

This model ensures that **agents dynamically negotiate, execute tasks efficiently, and scale based on workload demands**.  

---

## Installation & Setup  
### **Prerequisites**  
Ensure you have the following installed before running the system:  
- Python **(=3.12)**  
- Chroma **(for knowledge retrieval)**  

### **Installation Steps**  
1. Clone this repository: `git clone https://github.com/foohardt/agent-oriented-architecture.git`
2. Install dependencies

## Usage
1. Start Chroma: `sudo docker run -d -p 8000:8000 chromadb/chroma`
2. Start system with default data


## Testing

### Unit Testing

### Integration Testing
`poetry run pytest disrupt_arch/tests/integration/test_escalation_workflow.py --log-cli-level=INFO`

### Testing

## Challenges & Limitations



While AOA demonstrates scalability and adaptability, its implementation presents challenges:

    Debugging & Observability: The decentralized nature complicates workflow monitoring.
    Computational Overhead: Increased agent communication may introduce latency.
    Explainability of Decisions: Probabilistic reasoning mechanisms require improved transparency.

Future improvements will focus on optimizing message exchanges, enhancing debugging tools, and integrating hybrid deterministic reasoning models.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contact

For inquiries, feel free to reach out or open an issue in the repository.