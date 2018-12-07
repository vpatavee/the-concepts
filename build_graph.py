import json

import numpy as np


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
    # template = create_template(idx, pages)
    # with open("master", "w") as f:
    #     json.dump(template,f)
    #
    g, num_edge_out, num_edge_in, list_of_concepts = build_graph(idx, pages)
    top_concept = get_top_concepts()
