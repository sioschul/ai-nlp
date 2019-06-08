import subprocess
from collections import Counter

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

def minie_processing(text, entity, target_tuple):
    proc = subprocess.Popen(['java', '-jar', '.\\minie-0.0.1-SNAPSHOT.jar'],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    relations = []
    for x in text:
        proc.stdin.write((x + '\n').encode())
        proc.stdin.flush()
        line = proc.stdout.readline()
        while not line.decode().startswith('('):
            line = proc.stdout.readline()
            if (line.decode().startswith('No')):
                break
        while line.decode() != '\n':
            if (line.decode().startswith('No')):
                break
            result = line.decode()
            split = result.split(';')
            split[0] = split[0].replace('(', '')
            if len(split) == 3:
                second_split = split[2].split(')')
                second_split[0].replace(')', '')
                entry = [split[0], split[1], second_split[0]]
            else:
                second_split = split[1].split(')')
                second_split[0].replace(')', '')
                entry = [split[0], second_split[0]]
            relations.append(entry)
            line = proc.stdout.readline()
    proc.terminate()
    relations_entity = [x for x in relations if any(s in x[0] for s in target_tuple)]
    c = Counter(map(tuple, relations_entity))
    center_count=Counter([x[0] for x in relations_entity])

    relations_df = pd.DataFrame(relations_entity)
    center = max(center_count.keys(), key=(lambda k: center_count[k]))
    print(center)
    draw_graph(relations_df, c, center)
    return relations_df

def draw_graph(relations_df, c, center):
    g = nx.Graph()

    for id, x in relations_df.iterrows():
        if x[2] is not None:
            g.add_edge(x[0], x[2], color='g', weight=c[tuple(x)], relation=x[1])
        else:
            x1 = [x[0], x[1]]
            g.add_edge(x[0], x[1], color='b', weight=c[tuple(x1)], relation='')

    pos = nx.circular_layout(g)
    pos[center] = [0, 0]
    edges = g.edges()
    colors = [g[u][v]['color'] for u, v in edges]
    weights = [g[u][v]['weight'] for u, v in edges]
    edge_labels = nx.get_edge_attributes(g, 'relation')
    plt.figure(figsize=(50, 25))
    nx.draw(g, pos, edges=edges, edge_color=colors, width=weights, with_labels=True, font_size=10)
    nx.draw_networkx_edge_labels(g, pos, edge_labels=edge_labels, font_size=10)
    plt.show()
