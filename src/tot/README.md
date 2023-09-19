# ToT based approach
## Envionment:
First you need to set an environment file ```.env``` that contains the following variables:
```
OPENAI_API_KEY='key'
NEO4J_USER='neo4j'
NEO4J_PASSWORD='pass'
neo4J_URL='neo4j.example.ex'
```
## 1- Parsing Latex source code
```latex_code``` contains the source code of an article. 

```parse_tex.py``` implements some function to extract the main compoenents of the article (sections, subsections, title, authors...)
## 2- Creating the knowledge graph and pushing it to a neo4j database
```create_kg.py``` uses the extracted components to prompt chatgpt to extract the main concepts and their relations in each subsection/section. Then it pushed the constructed graph to a neo4j database

## 3- Answering the question
```answer.py``` queries the knowledge graph and prompts chatgpt to answer the question. You can ask any question by setting the variable ```answer``` at the end of the file.
