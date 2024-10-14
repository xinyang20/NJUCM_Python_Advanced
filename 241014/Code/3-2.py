import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import re

G=nx.Graph()
node_list=[]
lnum=0
with open(r"../第三次实验材料/Jazz_test.txt","r") as file:
    while True:
        lines=file.readline()
        if not lines:
            break
        lnum+=1
        if lnum>=4:
            temp=' '.join(re.split(' +|\n+',lines)).strip()
            line=re.split(' ',temp.strip())
            first=line[0]
            second=line[1]
            node_list.append(np.append(first,second))

print(len(node_list))

for i in range(len(node_list)):
    G.add_edge(node_list[i][0],node_list[i][1])

pos = nx.spring_layout(G)
plt.figure(figsize=(10, 10))
nx.draw(G, pos, node_color='r', node_size=20, edge_color='gray', alpha=0.5, with_labels=False)
plt.show()