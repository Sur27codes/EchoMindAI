# Examples

This directory contains example scripts to test the RAG Agent.

## Graph Generation Test
`test_graph_generation.py` demonstrates how to use the agent to generate plots and graphs.

### Usage
From the project root:

```bash
# Ensure you have your virtual environment set up and .env file populated
./.venv/bin/python examples/test_graph_generation.py
```

This script will:
1. Initialize the RAG Agent.
2. Ask for a Sine Wave plot (Matplotlib).
3. Ask for a Network Graph (NetworkX).
