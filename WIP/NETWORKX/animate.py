import sys
import re

def main():
    add_connection = ("""setTimeout(function() {
                          graph.addLink('X', 'Y', '20');
                          keepNodesOnTop();
                      }, nextval());\n""")
    add_node = ("""graph.addNode('X');\n""")

    with open('alignment.txt','r') as file:
        tree = {}
        max_nodes = 0
        for line in file:
            file1 = re.search('alignment ([0-9]+)->', line).group(1)
            file2 = re.search('->([0-9]+) ', line).group(1)
            round = re.search('round (.*).', line).group(1)
            if round not in tree.keys():
                tree[round] = []
            tree[round].append({file1:file2})
            if max_nodes <= max([int(file1), int(file2)]):
                max_nodes = max([int(file1), int(file2)])
        max_rounds = max([int(i) for i in tree.keys()])

    with open('animate_template.html', 'r') as file:
        template = file.readlines()

    # Nodes
    all_nodes = ''
    for node in range(max_nodes + 1):
        node_string = add_node.replace('X', f"{node}")
        all_nodes += node_string

    # Connections
    all_connections = ''
    for round in range(max_rounds + 1):
        connections = tree[str(round)]
        for connection in connections:
            file1 = list(connection.keys())[0]
            file2 = connection[file1]
            connection_string = add_connection.replace('X', f"{file1}").replace('Y', f"{file2}")
            all_connections += connection_string

    with open('animate.html', 'w') as file:
        for i, line in enumerate(template):
            if "NODES HERE" in line:
                template[i] = all_nodes
            if 'CONNECTIONS HERE' in line:
                template[i] = all_connections
            file.write(template[i])


if __name__ == '__main__':
    main()
