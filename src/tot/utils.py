from dotenv import dotenv_values
import openai
from neo4j import GraphDatabase
from dotenv import dotenv_values, load_dotenv
import json
import networkx as nx
import matplotlib.pyplot as plt


load_dotenv()
config = dotenv_values(".env")


def read_json(path):
    with open(path) as f:
        d = json.load(f)
    return d


def parse_nodes_code(nodes):
    nodes_list = []
    s = "".join(nodes).split("[")[1].split("]")[0]
    for node in s.split(","):
        node = node.split('"')
        if len(node) != 3:
            continue
        clean_node = node[1]
        nodes_list.append(clean_node)
    return nodes_list


def parse_edges_code(edges):
    clean_edges = []
    edges = "".join(edges.split("\n"))
    edges = edges.split("[")[1].split("]")[0]
    # edges = edges.split(")")[:-1]
    edges = edges.split(",         ")
    for edge in edges:
        edge = edge.split(",")
        if len(edge) != 3:
            continue
        src = edge[0].split('"')[1]
        dst = edge[1].split('"')[1]
        attribute = edge[2].split('"')[-2]
        clean_edges.append((src, dst, attribute))    
    return clean_edges


def parse_completion(completion):
    content = completion["choices"][0]["message"]["content"]
    """if len(content.split("```")) > 1:
        raw_code = content.split("```")[1].split("# Define the Nodes\n")[1]
    else:
        raw_code = content.split("# Define the Nodes\n")[1]"""
    if len(content.split("# Define the Nodes\n")) > 1:
        raw_code = content.split("# Define the Nodes\n")[1]
    else:
        raw_code = content.split("# Define the Nodes \n")[1]
    if len(raw_code.split("# Define the Edges and their attributes\n")) > 1:
        raw_code = raw_code.split("# Define the Edges and their attributes\n")
    else:
        raw_code = raw_code.split("# Define the Edges and their attributes \n")
    nodes_code = raw_code[0]
    edges_code = raw_code[1].split("# Creating the Graph\n")[0]
    nodes = parse_nodes_code(nodes_code)
    edges = parse_edges_code(edges_code)
    return nodes, edges


def text_to_kg(text, save_path="completion.json"):
    context = "You will help me create knowledge graphs from scientific papers in python. The papers will be written in Latex"
    prompt = "from the below text, create in python a knowledge graph by creating two lists one for edges and one for nodes, give attributes to the edges, put the comment '# Define the Nodes' before defining the nodes list and the comment '# Define the Edges and their attributes' before defining the edges list and the comment '# Creating the Graph' before creating the graph, the nodes list takes this form [\"node1\", \"node2\"] and the edges list takes this form edges = [(\"Human Action Recognition\", \"Sensor Types\", {\"Type\": \"Depends_on\"}),\n         (\"Sensor Types\", \"Visual Data\", {\"Type\": \"Generates\"})]: \n" + text
    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": context},
            {"role": "user", "content": prompt}
        ]
    )
    with open(save_path, "w") as f:
        json.dump(completion, f, indent=4)
    nodes, edges = parse_completion(completion)
    return nodes, edges


def create_node_query(node):
    query = """CREATE ({}:{})""".format(node[0], node[1])
    return query


def create_edge_query(edge):
    query = """CREATE {}-[:{}]->{}""".format(edge[0], edge[2], edge[1])
    return query


def add_graph(nodes, edges, database="neo4j"):
    driver = GraphDatabase.driver(config["NEO4J_URL"], auth=(config["NEO4J_USER"], config["NEO4J_PASSWORD"]), encrypted=False)
    for node in nodes:
        node = (node, "feature")
        node_query = create_node_query(node)
        records, summary, keys = driver.execute_query(node_query, database=database)
    for edge in edges:
        edge_query = create_edge_query(edge)
        records, summary, keys = driver.execute_query(edge_query, database=database)
    driver.close()
    