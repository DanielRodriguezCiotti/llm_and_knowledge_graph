# LLMs and Knowledge Graphs
## 1- Introduction
In this project, we explore how to create a Kowledge Graph from a scientific paper and how to connect a LLM (GPT4 in particular) to the graph for Q&A tasks.

Once the graph is created, we employ two differents methods to exploit the graph: 
1. Text search using similarity
2. A ToT-inspired method

## 2- Creating the Knowledge Graph
The graph is a tree where the root is the title the leafs are the concepts, and in the middle we put the sections abd the subsections according to the hierarchy in the paper.
## 3- Exploiting the Graph:
### 3.1- Text search:
We use chatgpt API to create embeddings for the input question and for each node in the graph. Next we select the most relevant nodes based on cosine similarity and extract a subgraph.
These results and the question are then fed to the LLM to formulate the answer.
### 3.2- ToT-based approach
The graph is a tree where the root is the title the leafs are the concepts, and in the middle we put the sections abd the subsections according to the hierarchy in the paper.
In this approach, we put the question in the prompt and each level in the hierarchy, we extract all the nodes, we feed them to chatgpt and we ask it to score each node out of 10 where 10 means that this section definitely contains the needed informations, and 0 means the the section is not important at all for the question at hand. And we select the top-k highest scorers. We repeat the same method at each level until reaching the leafs which contains the concepts. We extract all the concepts as well as the edges between them from the selected sections and we feed them to chatgpt. This gives it a sufficient context to answer the question.