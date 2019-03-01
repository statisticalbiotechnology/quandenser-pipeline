# Author: Aric Hagberg <aric.hagberg@gmail.com>

#    Copyright (C) 2011-2018 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
import json
import os

import flask
import networkx as nx
from networkx.readwrite import json_graph
G = nx.Graph()
tree_map = {0: {6:7},
            1: {5:4, 7:8},
            2: {8:2, 4:1},
            3: {1:0, 2:0, 3:0},
            4: {0:1, 0:2, 0:3},
            5: {1:4, 2:8},
            6: {4:5, 8:7},
            7: {7:6} }
G.add_nodes_from([i for i in range(9)])
for i in range(2):
    map = tree_map[i]
    for node1 in map.keys():
        node2 = map[node1]
        G.add_edge(node1, node2)

# this d3 example uses the name attribute for the mouse-hover value,
# so add a name to each node
for n in G:
    G.nodes[n]['name'] = n

# write json formatted data
d = json_graph.node_link_data(G)  # node-link format to serialize
# write json
json.dump(d, open('force/force_1.json', 'w'))
print('Wrote node-link JSON data to force/force.json')

# Serve the file over http to allow for cross origin requests
app = flask.Flask(__name__, static_folder="force")

@app.route('/<path:path>')
def static_proxy(path):
    return app.send_static_file(path)

print('\nGo to http://localhost:8000/force.html to see the example\n')
app.run(port=8000)
