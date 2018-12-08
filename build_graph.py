import json


import networkx as nx
import matplotlib.pyplot as plt
import numpy as np


def build_di_edge_list(concept_page, w1=2, w2=1, w3=1):
    """
    :param concept_page: output from get_index()
    :param w1 weight title -> main bullet
    :param w2 weight title -> sub bullet
    :param w3 weight main bullet -> sub bullet
    :return: list of edges that can input to add_edges_from(). [(v1, v2, {'weight': w}), (), ...]
    """

    edges_list = []
    for page in concept_page:
        topic_concept = set()
        for concept in concept_page[page]:
            if concept["location"] == 'title':
                topic_concept.add(concept['concept'])

        upper_concept = []
        for i, concept in enumerate(concept_page[page]):
            if concept["location"] == 'title':
                continue

            if concept["sub_location"] == 0:
                # add edges from concepts in title to this concept
                for e in topic_concept:
                    if e != concept['concept']:
                        edges_list.append((e, concept['concept'], {"weight": w1}))

                upper_concept.append(concept["concept"])

            if concept["sub_location"] > 0:
                # add edges from concept in main bullet to its sub bullet
                for c in upper_concept:
                    if c != concept['concept']:
                        edges_list.append((c, concept['concept'], {"weight": w2}))

                # add edges from concept in title to sub bullet
                for e in topic_concept:
                    if e != concept['concept']:
                        edges_list.append((e, concept['concept'], {"weight": w3}))

                # If this is the last concept in sub bullet, clear the upper_concept
                if i + 1 < len(concept_page[page]) and concept_page[page][i + 1]["sub_location"] == 0:
                    upper_concept = []

    return edges_list


def get_related(g):
    concepts_with_related = {}
    for v in g.nodes():
        concepts_with_related[v] = [a for a in g.neighbors(v)]
    return concepts_with_related


def create_template(idx_json, g):
    concepts_master = {}
    concepts_with_related = get_related(g)
    stat = get_stat(g)
    for concept in idx_json:
        concept_info = {}
        concept_info["location"] = idx_json[concept]
        if concept in concepts_with_related:
            concept_info["related_concepts"] = concepts_with_related[concept]
            concept_info["statistics"] = stat[concept]
        else:
            concept_info["related_concepts"] = []
            concept_info["statistics"] = ""

        concepts_master[concept] = concept_info

    return concepts_master


def get_top_concepts(list_of_concepts, g, n):
    top_concepts = []
    for i in np.argsort(np.sum(g, axis=0))[-n:]:
        top_concepts.append((list_of_concepts[i], np.sum(g, axis=0)[i]))
    return top_concepts


def get_stat(g):
    stat = {}
    page_cen = nx.pagerank(g)
    mean = np.average([e[1] for e in page_cen.items()])
    sd = np.std([e[1] for e in page_cen.items()])
    for v in g.nodes():
        if page_cen[v] > mean + sd:
            imp = "important"
        else:
            imp = "not very important"
        stat[v] = "This concept is linked from others with degree = {}.\n".format(g.in_degree[v]) + \
            "This concept links to others with degree = {}.\n".format(g.out_degree[v]) + \
            "This concept is {}.".format(imp)

    return stat


def create_di_graph(pages, plot=False):
    edge_list = build_di_edge_list(pages)
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
    if plot:
        sub = [e[0] for e in top_ten]
        H = G.subgraph(sub)
        plt.figure(num=None, figsize=(20, 20), dpi=80)
        nx.draw(H, node_size=1700, with_labels=True, font_size=15)
        plt.show()
    return G


if __name__ == "__main__":
    idx = json.load(open("index_with_level.json", "r"))
    pages = json.load(open("concept_pages.json", "r"))
    g = create_di_graph(pages)
    with open("master", "w") as f:
        json.dump(create_template(idx, g), f)









