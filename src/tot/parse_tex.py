import os
import networkx as nx
import matplotlib.pyplot as plt
from clean import text_to_kg
import pickle


def flatten_list(l):
    a = []
    for i in l:
        a += i
    return a


def read_text(path):
    with open(path) as f:
        text = f.read()
    return text


def find_title(main_tex):
    lines = main_tex.split("\n")
    for line in lines:
        if line.startswith("\\title"):
            title = clean_title(line)
            return title
    return None


def find_authors(main_tex):
    lines = main_tex.split("\n")
    for line in lines:
        if line.startswith("\\author{"):
            authors = clean_title(line).split(",")
            return authors
    return None


def find_keywords(main_tex):
    keywords = main_tex.split("\\begin{IEEEkeywords}\n")[1].split("\n\\end{IEEEkeywords}")[0].split(", ")
    return keywords


def find_abstract(main_tex):
    abstract = main_tex.split("\\begin{abstract}\n")[1].split("\n\\end{abstract}")[0]
    return abstract


def clean_title(title):
    clean_title = title.split("{")[1].split("}")[0]
    return clean_title


def find_subsections(section):
    subs = section.split("\\subsection")
    lines = section.split("\n")
    sub_titles = []
    for line in lines:
        if line.startswith("\\subsection"):
            sub_titles.append(clean_title(line))
    if not section.startswith("\\subsection") and len(subs) > 1:
        subs = subs[1:] 
    subs = ["\n".join(sub.split("\n")[1:]) for sub in subs]
    subs = [sub for sub in subs if sub != ""]
    return subs, sub_titles


def find_sections(main_tex):
    sections = []
    inputs = []
    lines = main_tex.split("\n")
    for line in lines:
        if line.startswith("\\section"):
            title = clean_title(line)
            sections.append(title)
        if line.startswith("\\input"):
            input_path = clean_title(line)
            inputs.append(input_path)
    return sections, inputs


def create_subsection_edge(section, subs, relation="subsection"):
    edges = [(section, sub, relation) for sub in subs]
    return edges


def parse_main(main_tex):
    # \title{}
    title = find_title(main_tex)
    # \author{}
    authors = find_authors(main_tex)
    # \begin{abstract} .... \end{abstract}
    abstract = find_abstract(main_tex)
    # \begin{IEEEkeywords} .... \end{IEEEkeywords}
    keywords = find_keywords(main_tex)
    # \section{} \n \input{} 
    sections, inputs = find_sections(main_tex)
    subsections_titles = []
    subsections_text = []
    for path in inputs:
        if not path.endswith(".tex"):
            path = path + ".tex"
        path = os.path.join("tex", path)
        text = read_text(path)
        subs_text, sub_titles = find_subsections(text)
        subsections_titles.append(sub_titles)
        subsections_text.append(subs_text)
    intrasection_nodes = []
    intrasection_edges = []
    for i in range(len(sections)):
        if len(subsections_titles[i]) == 0:
            text = read_text(os.path.join("tex", inputs[i]))
            path = os.path.join("completion_2", inputs[i].split(".")[0]) + ".json"
            section_nodes, section_edges = text_to_kg(text, path)
            intrasection_nodes += section_nodes
            intrasection_edges += [(sections[i], n, "mentions") for n in section_nodes]
            intrasection_edges += section_edges
        else:
            for j, sub in enumerate(subsections_text[i]):
                path = os.path.join("completion_2", inputs[i].split(".")[0]) + "_" + subsections_titles[i][j] + ".json"
                subsection_nodes, subsection_edges = text_to_kg(sub, path)
                intrasection_nodes += subsection_nodes
                intrasection_edges += [(subsections_titles[i], n, "mentions") for n in subsection_nodes]
                intrasection_edges += subsection_edges

    nodes = [title]
    nodes += keywords
    nodes += authors
    nodes += sections
    nodes += flatten_list(subsections_titles)
    nodes += intrasection_nodes
    sections_edges = [(title, section, "section") for section in sections]
    authors_edges = [(title, author, "author") for author in authors]
    keywords_edges = [(title, keyword, "keyword") for keyword in keywords]
    subsections_edges = [create_subsection_edge(sections[i], subsections_titles[i], "subsection") for i in range(len(sections))]
    edges = sections_edges + authors_edges + keywords_edges + flatten_list(subsections_edges) + intrasection_edges
    return nodes, edges


def create_graph(nodes, edges):
    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    nx_edges = [(edge[0], edge[1], {"relations": edge[2]}) for edge in edges]
    G.add_edges_from(nx_edges)
    return G


with open("tex/Main.tex") as f:
    text = f.read()


nodes, edges = parse_main(text)

with open("nodes_list", "wb") as fp:
    pickle.dump(nodes, fp)

with open("edges_list", "wb") as fp:
    pickle.dump(edges, fp)

"""g = create_graph(nodes, edges)
nx.draw(g)
plt.savefig("fig.png")"""