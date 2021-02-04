# LSWL
A NetworkX implementation of "Local Community Discovery in Complex Networks: Relying on the Strength of Links" (submitted for KDD 2021).

### Abstract
Community detection methods aim to find nodes connected to each other more than the other nodes in a graph. Despite the advantages of global methods, as they explore the entire network, they suffer from severe limitations due to large networks' sizes or a global criterion used indiscriminately throughout the whole network. Thus, some have focused on another fundamental problem, local community discovery, an egocentric function aiming to find the community that contains a query node. There are various local community search algorithms, including motif-based methods and modularity-based methods. Despite the advantages of the local modularity based practices, they recently obtained less attention due to two significant issues. These methods add many outliers to the community, especially when using on large dense networks. They are also sensitive to which query node of a particular community is used to start the expansion. We introduce a novel approach that can locally discover the communities precisely, deterministically, and quickly. It can also be used iteratively to detect the entire partitioning of a network with or without considering overlapping communities and concurrently identify outliers. This method works in a one-node-expansion model based on a notion of strong and weak links in a graph.


This repository provides Networkx implementation for LSWL and LSWL+ described in
> Local Community Discovery in Complex Networks: Relying on the Strength of Links, submitted for KDD 2021.

The original codes are *lswl_offline.py*, which finds the communities of nodes in a given network, *lswl_online.py*, which does the same thing for cases when the intended network is too large and extensive memory consumption needs to be avoided. The last is *lswl_plus.py*, which uses our novel local discovery framework to detect the entire community structure of a given network by iteratively applying the *LSWL* approach to the unexplored parts of the network. The *LSWL+* is capable of finding a partition with overlapping communities or without them, based on user preferences. This method can also find outliers (peripheral nodes of the graph that are marginally connected to communities) and hubs (nodes that bridge the communities). Modularity R and Modularity M are two methods originally presented in [[1]] (#1) and [[2]] (#2), which we implemented for the evaluation purposes.

#### References
<a id="1">[1]</a>
@article{Clauset2005,
	title = {Finding local community structure in networks},
	volume = {72},
	number = {2},
	journal = {Physical Review E},
	author = {Clauset, Aaron},
	year = {2005},
	pages = {026132},
}
<a id="2">[2]</a>
@inproceedings{Luo2006,
  year = {2006},
  author = {Feng Luo and James Wang and Eric Promislow},
  title = {Exploring Local Community Structures in Large Networks},
  booktitle = {2006 {IEEE}/{WIC}/{ACM} International Conference on Web Intelligence ({WI}{\textquotesingle}06)},
  pages = {233--239},
}

### Requirements
The codebase is implemented in Python 3.8.5 package versions used for development are just below.
```
networkx          2.5
argparse          1.1
```

### Datasets

This repository also contains the synthetic networks, we generated via the *LFR benchmark*, for the evaluation section of our paper. Any code in this repository takes the **edge list** of a graph, in which any line indicates an edge between two nodes separated by *\t*. In addition to the network file, a file containing all **query nodes** should exists. In this file, each line contains a node that is used as the start node to discover its community. 

#### Input and output options
```
--strength_type   STR   '1': strengths between [-1,+1] and '2': strengths between [0,1].   Default is '2'.
--network         STR   The address of the network in form of edge list.                   No default value.
--timeout         INT   The maximum time in which LSWL can retreive the community.         Default is 2.
--output          STR   The address of the file to store the results.                      Default is './community.dat'.

for [lswl_offline.py] and [lswl_online.py]:
--query_nodes     STR   The address of the list of query nodes.                            No default value.

for [lswl_plus.py]:
--outlier         STR   If outliers need to merge into communities (y/n).                  Default is 'y'.
--overlap         STR   If overlapping communities need to be detected (y/n).              Default is 'n'.
```

#### Examples

The following commands run different codes in this repository:
```
$ python lswl_offline.py -n karate_edge_list.txt -q query_nodes.txt -s 1
$ python lswl_online.py -n karate_edge_list.txt -q query_nodes.txt -s 2
$ python lswl_plus.py -n karate_edge_list.txt -i y
$ python mod_r.py -n karate_edge_list.txt -q query_nodes.txt
$ python mod_m.py -n karate_edge_list.txt -q query_nodes.txt
```







