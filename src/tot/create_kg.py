import openai
from dotenv import load_dotenv
import json


load_dotenv()


def parse_nodes_code(nodes):
    nodes_list = []
    s = "".join(nodes).split("[")[1].split("]")[0]
    for node in s.split(","):
        clean_node = node.split('"')[1]
        nodes_list.append(clean_node)
    return nodes_list


def parse_edges_code(edges):
    clean_edges = []
    edges = "".join(edges)
    edges = edges.split("[")[1].split("]")[0]
    edges = edges.split(")")[:-1]
    for edge in edges:
        edge = edge.split("(")[1].split(",")
        src = edge[0].split('"')[1]
        dst = edge[1].split('"')[1]
        attribute = edges[2].split('"')[-2]
        clean_edges.append((src, dst, attribute))    
    return clean_edges


def parse_completion(completion):
    content = completion["choices"][0]["message"]["content"]
    raw_code = content.split("```")[1].split("# Define the Nodes \n")[1]
    raw_code = raw_code.split("# Define the Edges and their attributes\n")
    nodes_code = raw_code[0]
    edges_code = raw_code[1].split("# Creating the Graph\n")[0]
    nodes = parse_nodes_code(nodes_code)
    edges = parse_edges_code(edges_code)
    return nodes, edges


def text_to_kg(text):
    context = "You will help me create knowledge graphs from scientific papers. The papers will be written in Latex"
    prompt = "from the following text, create in python a knowledge graph by creating two lists one for edges and one for nodes, give attributes to the edges: \\n{}".format(text)
    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": context},
            {"role": "user", "content": prompt}
        ]
    )
    with open("completion_method.json", "w") as f:
        json.dump(completion, f, indent=4)
    nodes, edges = parse_completion(completion)
    return nodes, edges
