import json


import networkx as nx
import matplotlib.pyplot as plt
import numpy as np


def build_edge_list(concept_page):
    edges_list = []
    for page in concept_page:
        topic_concept = []
        for concept in concept_page[page]:
            if concept["location"] == 'title':
                topic_concept.append(concept['concept'])

        for concept in concept_page[page]:
            if concept["location"] == 'body':
                for topic_con in topic_concept:
                    if topic_con != concept['concept']:
                        edges_list.append((topic_con, concept['concept']))

        upper_concept = []
        for i, concept in enumerate(concept_page[page]):
            if concept["location"] == 'title':
                continue

            if concept["sub_location"] == 0:
                upper_concept.append(concept["concept"])

            if concept["sub_location"] > 0:
                for c in upper_concept:
                    if c != concept['concept']:
                        edges_list.append((c, concept['concept']))
                if i + 1 < len(concept_page[page]) and concept_page[page][i + 1]["sub_location"] == 0:
                    upper_concept = []

    return edges_list


def build_graph(idx, pages):
    """
    :param idx:
    :param pages:
    :return:
    [ a00 a01
      a10 a11]
    a01 = link from word 0 in topic to word 1 in body
    """
    list_of_concepts = list(idx.keys())
    num_edge_out = [0] * len(list_of_concepts)
    num_edge_in = [0] * len(list_of_concepts)
    g = np.zeros((len(list_of_concepts), len(list_of_concepts)), dtype=float)
    for i, concept in enumerate(list_of_concepts):
        concept_info = idx[concept]
        for p in concept_info:
            # only consider if it is title
            if p["type"] != "title":
                # print p["type"]
                continue

            page = pages[str(p["page"])]
            for concept_in_page in page:
                concept_name = concept_in_page["concept"]
                if concept_name == concept:
                    continue
                j = list_of_concepts.index(concept_name)
                num_edge_out[i] += 1
                num_edge_in[j] += 1
                if "sub_location" not in concept_in_page:
                    # print concept_in_page
                    continue
                if concept_in_page["sub_location"] == 0:
                    g[i, j] += 2
                elif concept_in_page["sub_location"] == 1:
                    g[i, j] += 1
                else:
                    print "ERROR"
    return g, num_edge_out, num_edge_in, list_of_concepts


def get_related(list_of_concepts, g):
    """
    :param concepts: concepts template
    :param g: graph represented in Numpy Array
    :param list_of_concepts: list of concepts used to index the graph
    :return:
    """
    concepts_with_related = {}
    for i, concept in enumerate(list_of_concepts):
        related_concepts = []
        concepts_with_related[concept] = related_concepts
        for j in np.argsort(g[:, i])[-4:]:
            if g[j, i] == 0:
                continue
            related_concepts.append(list_of_concepts[j])
    return concepts_with_related


def create_template(idx_json, pages_json):
    concepts_master = {}
    g, num_edges_out, num_edges_in, list_of_concepts = build_graph(idx_json, pages_json)
    concepts_with_related = get_related(list_of_concepts, g)
    for concept in idx_json:
        concept_info = {}
        concept_info["location"] = idx_json[concept]
        concept_info["related_concepts"] = concepts_with_related[concept]
        concept_info["statistics"] = {}
        concepts_master[concept] = concept_info

    return concepts_master


def get_top_concepts(list_of_concepts, g, n):
    top_concepts = []
    for i in np.argsort(np.sum(g, axis=0))[-n:]:
        top_concepts.append((list_of_concepts[i], np.sum(g, axis=0)[i]))
    return top_concepts


if __name__ == "__main__":
    idx = json.load(open("index_with_level.json", "r"))
    pages = json.load(open("concept_pages.json", "r"))
    g, num_edge_out, num_edge_in, list_of_concepts = build_graph(idx, pages)
    top_concept = get_top_concepts(list_of_concepts, g, 10)
    edge_list = build_edge_list(pages)
    G = nx.DiGraph()
    G.add_edges_from(edge_list)

    print(nx.info(G))
    print('Density', nx.density(G))
    print('In Degree', sorted(G.in_degree(), key=lambda x: -x[1])[0:10])
    print('Out Degree', sorted(G.out_degree(), key=lambda x: -x[1])[0:10])

    page_cen = nx.pagerank(G)
    top_ten = sorted(page_cen.items(), key=lambda x: -x[1])[0:50]
    for e in top_ten[0:20]:
        print("term:", e[0], "page_rank:", e[1])

    sub = [e[0] for e in top_ten]
    H = G.subgraph(sub)
    plt.figure(num=None, figsize=(20, 20), dpi=80)
    nx.draw(H, node_size=1700, with_labels=True, font_size=15)
    plt.show()