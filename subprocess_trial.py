import subprocess
from collections import Counter

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import pprint as pp

proc = subprocess.Popen(['java', '-jar', '.\\minie-0.0.1-SNAPSHOT.jar'],
                           stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
text =["Mr. Ollivander had come so close that he and Harry were almost nose to nose.",
"\"And that's where...\"",
"Mr. Ollivander touched the lightning scar on Harry's forehead with a long, white finger.",
"said Mr. Ollivander, suddenly stern.",
"said Mr. Ollivander sharply.",
"No two Ollivander wands are the same, just as no two unicorns, dragons, or phoenixes are quite the same.",
"Mr. Ollivander was flitting around the shelves, taking down boxes.",
"Harry took the wand and (feeling foolish) waved it around a bit, but Mr. Ollivander snatched it out of his hand almost at once.",
"Try --\"",
"Harry tried -- but he had hardly raised the wand when it, too, was snatched back by Mr. Ollivander.",
"He had no idea what Mr. Ollivander was waiting for.",
"The pile of tried wands was mounting higher and higher on the spindly chair, but the more wands Mr. Ollivander pulled from the shelves, the happier he seemed to become.",
"Hagrid whooped and clapped and Mr. Ollivander cried, \"Oh, bravo!",
"He paid seven gold Galleons for his wand, and Mr. Ollivander bowed them from his shop."]
entity = 'Ollivander'
relations=[]
for x in text:
    proc.stdin.write((x+'\n').encode())
    proc.stdin.flush()
    line=proc.stdout.readline()
    while not line.decode().startswith('('):
        line=proc.stdout.readline()
        if(line.decode().startswith('No')):
            break
    while line.decode() != '\n':
        if(line.decode().startswith('No')):
            break
        result = line.decode()
        split= result.split(';')
        split[0] = split[0].replace('(', '')
        if len(split) == 3:
            second_split = split[2].split(')')
            second_split[0].replace(')', '')
            entry = [split[0], split[1], second_split[0]]
        else:
            second_split = split[1].split(')')
            second_split[0].replace(')','')
            entry = [split[0], second_split[0]]
        relations.append(entry)
        line = proc.stdout.readline()
proc.terminate()

relations_entity = [x for x in relations if x[0] == entity]

c = Counter(map(tuple,relations_entity))

relations_df = pd.DataFrame(relations_entity)

g = nx.Graph()

for id, x in relations_df.iterrows():
    if x[2] is not None:
        g.add_edge(x[0],x[2],color='g',weight=c[tuple(x)]*2, relation=x[1])
    else:
        x1 = [x[0],x[1]]
        g.add_edge(x[0],x[1],color='b',weight=c[tuple(x1)]*2, relation='')

pos = nx.circular_layout(g, scale=2)
pos[entity] = [0,0]
edges = g.edges()
colors = [g[u][v]['color'] for u,v in edges]
weights = [g[u][v]['weight'] for u,v in edges]
edge_labels = nx.get_edge_attributes(g,'relation')
plt.figure(figsize =(20,10))
nx.draw(g, pos, edges=edges, edge_color=colors, width=weights, with_labels=True,node_size=4000, font_size=12)
nx.draw_networkx_edge_labels(g, pos, edge_labels = edge_labels)
plt.show()

'''
print('writing')
proc.stdin.write(b'Harry is stupid\n')
proc.stdin.flush()
print('waiting')
print(proc.stdout.readline())
print(proc.stdout.readline())
print(proc.stdout.readline())
print(proc.stdout.readline())
print('writing')
proc.stdin.write(b'Harry is stupid\n')
proc.stdin.flush()
print('waiting')
print(proc.stdout.readline())
print(proc.stdout.readline())
print(proc.stdout.readline())
print(proc.stdout.readline())
'''