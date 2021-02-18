import json
import networkx as nx
import matplotlib.pyplot as plt


NONE_NODE = '*'


def grammar_check(g):
    for i in range(0, len(g['VN'])):
        non_term = g['VN'][i]
        if non_term.islower():
            g['VN'][i] = non_term.upper()

    for i in range(0, len(g['VT'])):
        term = g['VT'][i]
        if term.isupper():
            g['VT'][i] = term.lower()

    start_symbol_status = False
    for char in g['VN']:
        if g['start_symbol'] == char:
            start_symbol_status = True
            break

    if not start_symbol_status:
        return False, "start_symbol: {} not in VN".format(g['start_symbol'])

    for key in g['P']:
        for char in key:
            if char in g['VN'] or char in g['VT']:
                continue

            return False, "{} => {}: wrong character in left side".format(key, g['P'][key][0])

        for value in g['P'][key]:
            for char in value:
                if char in g['VN'] or char in g['VT']:
                    continue

                return False, "{} => {}: wrong character in right side".format(key, value)

    return True, None


def get_edges(VN, VT, P):
    edges = []
    edge_lines = []

    for key in P:
        for value in P[key]:
            is_edge_line = False
            for char in value:
                if char in VT:
                    edge_lines.append(char)
                    is_edge_line = True
                    continue

                if char in VN:
                    edges.append((key, char))
                    is_edge_line = False
                    continue

            if is_edge_line:
                edges.append((key, NONE_NODE))

    return edges, edge_lines


def path_check(path, VT, P, start_symbol):
    for char in path:
        if char not in VT:
            return False, "{}: not in VT".format(char)

    is_start_correct = False
    last_terminal = None
    for start_symbols in P[start_symbol]:
        if path[0] in start_symbols:
            is_start_correct = True
            last_terminal = start_symbols[-1]

    if not is_start_correct:
        return False, None

    shorter_path = path[1:]
    is_middle_correct = False
    for char in shorter_path:
        for middle_symbols in P[last_terminal]:
            if char in middle_symbols:
                last_terminal = middle_symbols[-1]
                is_middle_correct = True

        if not is_middle_correct:
            return False, "Trouble in middle nodes."

        if char == last_terminal:
            return True, "Full path is correct."

        is_middle_correct = False

    return False, "Path bad finish characters."


if __name__ == "__main__":

    with open('gram.json') as json_file:
        grammar = json.load(json_file)

    is_grammar, err = grammar_check(grammar)
    if not is_grammar:
        print(err)
        exit()

    VN = grammar['VN']
    VT = grammar['VT']
    P = grammar['P']
    start_symbol = grammar['start_symbol']

    edges, edge_lines = get_edges(VN, VT, P)
    edge_labels = {}
    for i in range(0, len(edges)):
        edge_labels[edges[i]] = edge_lines[i]

    G = nx.Graph()
    for edge in edges:
        G.add_edge(edge[0], edge[1])

    pos = nx.spring_layout(G)
    plt.figure()
    nx.draw(G, pos, edge_color='r', width=1, linewidths=1,
            node_size=500, node_color='grey', alpha=0.9,
            labels={node: node for node in G.nodes()})
    nx.draw_networkx_edge_labels(G, pos=pos, edge_labels=edge_labels)
    plt.show()

    path = input("Input PATH here: ")
    if path:
        path_status, info = path_check(path, VT, P, start_symbol)
        print("Is PATH correct: {}\nInfo: {}".format(path_status, info))
