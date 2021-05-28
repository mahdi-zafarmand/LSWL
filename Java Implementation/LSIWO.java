import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;

public class LSIWO {
	
    double __MIN = 0.000001;

    public Graph graph;
    public boolean strengthType;
    public int startingNode;
    public ArrayList<Integer> community;
    public HashSet<Integer> shell;
    public HashMap<Integer, HashMap<Integer, Integer>> commonNeighbors;
    public HashMap<Integer, Integer> maxCommonNeighbors;
    public HashSet<Integer> strengthAssignedNodes;
    public double timeout;
    
    public LSIWO(Graph _graph, boolean _strengthType, double _timeout) {
    	this.graph = _graph;
    	this.strengthType = _strengthType;
    	this.timeout = _timeout;
    	this.startingNode = -1;
    	this.community = new ArrayList<>();
    	this.shell = new HashSet<>();
    	this.commonNeighbors = new HashMap<>();
    	this.maxCommonNeighbors = new HashMap<>();
    	this.strengthAssignedNodes = new HashSet<>();
    	this.removeSelfLoops();
    }
    
//    resets the LSIWO object for the next round of community search while keeping graph and strength data intact.
    public void reset() {
    	this.community.clear();
    	this.shell.clear();
    }
    
//    removes any edges that connect a node to itself (we call them loops or self-loops) prior to investigate the graph.
    public void removeSelfLoops() {
    	for(Node node : this.graph.nodes()) {
    		if(this.graph.hasEdge(node, node)) {
    			this.graph.removeEdge(node, node);
    		}
    	}
    }
    
//    makes sure if the given query node exists inside the graph, then assign it as the start node for the discovered community.
    public void setStartingNode(Node startNode) {
    	if(this.graph.nodes().contains(startNode)) {
    		this.startingNode = startNode.getId();
    		this.community.add(startNode.getId());
    		for(int neighborId : startNode.neighbors().keySet()) {
    			this.shell.add(neighborId);
    		}
    	} else {
    		System.out.println("Invalid starting node! Try with another one.");
    		System.exit(-1);
    	}
    }
    
//    updates community and shell according to the best node that is found to expand the community.
    public void updateSetsWhenNodeJoins(Node node) {
    	this.community.add(node.getId());
    	this.updateShellWhenNodeJoins(node);
    }
    
//    updates the shell set according to the best node that is found to expand the community. 
    public void updateShellWhenNodeJoins(Node node) {
    	for(int neighborId : node.neighbors().keySet()) {
    		this.shell.add(neighborId);
    	}
    	for(int nodeId : this.community) {
    		if(this.shell.contains(nodeId)) {    			
        		this.shell.remove(nodeId);
    		}
    	}
    }
    
//    updates the HashSets with information of common neighbors between any two adjacent nodes of the graph.
    public void updateDictsOfCommonNeighborsInfo(Node node) {
    	
//    	if a node doesn't exist in one HashSet, it doesn't exist in the other, so we initialize both HashSets for this node.
    	if(this.commonNeighbors.containsKey(node.getId()) == false) {
    		this.commonNeighbors.put(node.getId(), new HashMap<Integer, Integer>());
    		this.maxCommonNeighbors.put(node.getId(), -1);
    	}
    	
    	int numberCommonNeighbors;
    	for(int neighborId : node.neighbors().keySet()) {
    		
//    		these computations are done only if a neighbor is not considered before because (*) below.
    		if(this.commonNeighbors.get(node.getId()).containsKey(neighborId) == false) {
    			if(this.commonNeighbors.containsKey(neighborId) == false) {
    				this.commonNeighbors.put(neighborId, new HashMap<Integer, Integer>());
    				this.maxCommonNeighbors.put(neighborId, -1);
    			}
    			
//    			(*) this is the reason, as the number of common neighbors is found, it is assigned for nodes of both ends of that edge.
//    			this makes the total number of calculations in half.
    			numberCommonNeighbors = graph.getCommonNeighbors(node, graph.getNode(neighborId)).size();
//    			System.out.println(node.getId() + " -> " + neighborId + " : " + numberCommonNeighbors);
    			this.commonNeighbors.get(node.getId()).put(neighborId, numberCommonNeighbors);
    			this.commonNeighbors.get(neighborId).put(node.getId(), numberCommonNeighbors);
    			
//    			finds the maximum number of common numbers with any neighbor of the node, will be used for normalization in strength formula.
    			if(numberCommonNeighbors > this.maxCommonNeighbors.get(node.getId())) {
    				this.maxCommonNeighbors.put(node.getId(), numberCommonNeighbors);
    			}
    			if(numberCommonNeighbors > this.maxCommonNeighbors.get(neighborId)) {
    				this.maxCommonNeighbors.put(neighborId, numberCommonNeighbors);
    			}
    		}
    	}
    }
    
//    based on common neighbors information that is computed before, a normalized strength value is assigned to each edge of the graph.
    public void assignLocalStrength(Node node) {
    	if(this.strengthAssignedNodes.contains(node.getId()) == false) {
    		this.updateDictsOfCommonNeighborsInfo(node);
    		int maxMutualNode = this.maxCommonNeighbors.get(node.getId()), maxMutualNeighbor = 0, strength = 0;
//    		System.out.println(node.getId() + "  " + maxMutualNode);
//    		once a node is fully analyzed (for its strength values), all edges incident to that can be assigned with proper strength value.
    		for(int neighborId : node.neighbors().keySet()) {
    			maxMutualNeighbor = this.maxCommonNeighbors.get(neighborId);
    			strength = this.commonNeighbors.get(node.getId()).get(neighborId);
    			
    			double s1 = 0.0, s2 = 0.0, finalStrength;
    			
    			if(maxMutualNode != 0) {
    				s1 = ((double) strength) / maxMutualNode;
    			}
    			if(maxMutualNeighbor != 0) {
    				s2 = ((double) strength) / maxMutualNeighbor;
    			}
    			
//    			a conditional assignment if any of the two formulas is intended.
    			finalStrength = (this.strengthType == false) ? (s1 + s2 - 1.0) : ((s1 + s2) / 2.0);
    			
//    			the strength is stored in attributes of both end nodes of an edge.
    			node.assignStrength(neighborId, finalStrength);
    			this.graph.getNode(neighborId).assignStrength(node.getId(), finalStrength);
    		}
    		
//    		adds the analyzed node to this hashset in order to avoid unnecessary calculations in the next rounds.
    		this.strengthAssignedNodes.add(node.getId());
    	}
    }
    
//    finds the best candidate node from the shell set to be used for community expansion.
    public int findBestNextNode(HashMap<Integer, Double> improvements) {
    	int newNodeId = this.community.get(this.community.size() - 1);
    	for(int nodeId : this.shell) {
    		if(improvements.containsKey(nodeId) == false) {
    			improvements.put(nodeId, this.graph.getNode(nodeId).getStrength(newNodeId));
    		} else if(this.graph.hasEdge(nodeId, newNodeId)) {
    			improvements.put(nodeId, improvements.get(nodeId) + this.graph.getNode(nodeId).getStrength(newNodeId));    			
    		}
    	}
    	
    	if(improvements.containsKey(newNodeId)) {
    		improvements.remove(newNodeId);
    	}
    	
//    	since we made sure this.shell.size() > 0, the final value for bestCandidate cannot remain -1, and will definitely change to a proper value.
    	int bestCandidate = -1;
    	double bestImprovement = Double.NEGATIVE_INFINITY;
    	for(int candidate : this.shell) {
    		if(improvements.get(candidate) > bestImprovement) {
    			bestCandidate = candidate;
    			bestImprovement = improvements.get(candidate);
    		}
    	}
    
    	return bestCandidate;
    }
    
//    merges any dangling nodes from the neighborhood of the community to the community if exist.
//    dangling nodes are nodes with only one connection to the rest of the graph, so their respective community would easily be detected.
    public void mergeDanglingNodes() {
    	HashSet<Integer> neighborhood = new HashSet<>();
    	for(int nodeId : this.community) {
    		for(int neighborId : this.graph.getNode(nodeId).neighbors().keySet()) {
    			neighborhood.add(neighborId);
    		}
    	}
    	
//    	to avoid searching through the whole ArrayList, we use a temporary HashSet, then put it back to the this.community.
    	HashSet<Integer> tempCommunity = new HashSet<>(this.community);
    	for(int nodeId : neighborhood) {
    		if(this.graph.degree(nodeId) == 1.0) {
    			tempCommunity.add(nodeId);    				
    		}
    	}
    	
    	this.community = new ArrayList<Integer>(tempCommunity);
    }
    
//    this method only shows its value when a node far from the rest of the graph is investigated, 
//    as without it such nodes remain alone and they may be considered as noise.
    public void amendSmallCommunities() {
    	if(this.community.size() < 3) {
    		if(this.shell.size() > 0) {
    			int startNodeForAmend = -1;
    	    	double tempDegree = 0.0, largestDegree = Double.NEGATIVE_INFINITY;
    			for(int nodeId : this.shell) {
    				tempDegree = this.graph.degree(nodeId);
    				if(tempDegree > largestDegree) {
    					startNodeForAmend = nodeId;
    					largestDegree = tempDegree;
    				}
    			}
    			
//    			a new round of search, this time without amend so we assure there will be no indefinite cycle of running code.
    			LSIWO nextCommunitySearcher = new LSIWO(this.graph, this.strengthType, this.timeout);
    			ArrayList<Integer> newMembers = nextCommunitySearcher.communitySearch(startNodeForAmend, false);
    			
//    	    	to avoid searching through the whole ArrayList, we use a temporary HashSet, then put it back to the this.community.
    	    	HashSet<Integer> tempCommunity = new HashSet<>(this.community);
    			for(int newMember : newMembers) {
    				tempCommunity.add(newMember);
    			}
    	    	this.community = new ArrayList<Integer>(tempCommunity);
    		}
    	}
    }
    
//    searches and discovers the local community corresponds to the given start node. shouldAmend -> merges to another community around it if small.
    public ArrayList<Integer> communitySearch(int startNodeId, boolean shouldAmend){
    	long startTime = System.currentTimeMillis();
    	Node startNode = this.graph.getNode(startNodeId);
    	this.setStartingNode(startNode);
    	this.assignLocalStrength(startNode);
    	
//    	contains information of the candidates for selection of the next best node.
    	HashMap<Integer, Double> improvements = new HashMap<>();
    	
    	while(this.community.size() < this.graph.getNumberOfNodes() && this.shell.size() > 0) {
    		
//    		exits if the required time to find the community exceeds the desired timeout.
    		if(System.currentTimeMillis() - startTime > 1000 * this.timeout) {
    			System.out.println("Timeout!");
    			return new ArrayList<Integer>();
    		}
    		
    		for(int nodeId : this.shell) {
    			this.assignLocalStrength(this.graph.getNode(nodeId));
    		}
    		
    		int bestNextNode = this.findBestNextNode(improvements);
//    		System.out.println(improvements);
//    		System.out.println("bestNextNode = " + bestNextNode + "\n\n");
    		if(this.strengthType == false && improvements.get(bestNextNode) < this.__MIN) {
    			break;
    		}
    		if(this.strengthType == true) {
    			if(this.community.size() > 3 && improvements.get(bestNextNode) < this.__MIN + 1.0) {
    				break;
    			} else if (this.community.size() < 3 && improvements.get(bestNextNode) < this.__MIN) {
    				break;
    			}
    		}
    		
    		this.updateSetsWhenNodeJoins(this.graph.getNode(bestNextNode));
    	}
    	
//    	amends if the community is small and this is desired. Then dangling nodes join the community.
    	if(shouldAmend == true) {
    		this.amendSmallCommunities();
    	}
    	this.mergeDanglingNodes();
    	
//    	the next line can be switched off to increase performance.
    	Collections.sort(this.community);
    	return this.community;
    }

//    reads the graph's edge list and load it to the program.
    public static Graph loadDataSet(String datasetPath, String delimiter) {
    	Graph graph = new Graph();
    	try {
    		BufferedReader br = new BufferedReader(new FileReader(datasetPath));
    		String line = br.readLine();
    		int n1, n2;
    		
    		while(line != null) {
    			n1 = Integer.parseInt(line.split(delimiter)[0]);
    			n2 = Integer.parseInt(line.split(delimiter)[1]);
    			graph.addEdge(n1, n2);
    			line = br.readLine();
    		}
    		br.close();
    	} catch(FileNotFoundException ex) {
            System.out.println("Error: file "  + datasetPath + " not found! ");
            ex.printStackTrace();
            System.exit(-1);
    	} catch(IOException ex) {
            System.out.println("Error: problems with file "  + datasetPath + "! ");
            ex.printStackTrace();
            System.exit(-1);
    	}
    	return graph;
    }
    
//    reads the list of query nodes which their communities are desired. In each search one query would be investigated.
    public static ArrayList<Integer> readQueryNodes(String path){
    	ArrayList<Integer> queryNodes = new ArrayList<>();
    	try {
    		BufferedReader br = new BufferedReader(new FileReader(path));
    		String line = br.readLine();
    		
    		while(line != null) {
    			queryNodes.add(Integer.parseInt(line));
    			line = br.readLine();
    		}
    		br.close();
    	} catch(FileNotFoundException ex) {
            System.out.println("Error: file "  + path + " not found! ");
            ex.printStackTrace();
            System.exit(-1);
    	} catch(IOException ex) {
            System.out.println("Error: problems with file "  + path + "! ");
            ex.printStackTrace();
            System.exit(-1);
    	}
    	return queryNodes;
    }

//    can be used via terminal ...    
	public static void main(String[] args) {
//	    args[0]: path to graph's edge list file,
//	    args[1]: path to query nodes file,
//	    args[2]: strength type based on formula (1) or (2),
//	    args[3]: time to stop the discovery process if it runs for too long,
//	    args[4]: path to the output file.

//    	long startTime = System.currentTimeMillis();
//    	Graph graph = loadDataSet(args[0], " ");
//    	ArrayList<Integer> queryNodes = readQueryNodes(args[1]);
//    	boolean strngthType = (args[2] == "1") ? false : true;
//    	double timeOut = Double.parseDouble(args[3]);
//    	String outputPath = args[4];

    	long startTime = System.currentTimeMillis();
    	Graph graph = loadDataSet("network_10000_8_5_0.1_20.edgeList", " ");
    	ArrayList<Integer> queryNodes = readQueryNodes("query_nodes.txt");
    	boolean strngthType = false;
    	double timeOut = 1.0;
    	String outputPath = "output2.txt";

    	
    	LSIWO communitySearch = new LSIWO(graph, strngthType, timeOut);
    	
    	try {
			PrintWriter writer = new PrintWriter(outputPath);
			
	    	ArrayList<Integer> discoveredCommunity;
	    	for(int queryNode : queryNodes) {
	    		discoveredCommunity = communitySearch.communitySearch(queryNode, true);
//	        	System.out.println(queryNode + " -> " + discoveredCommunity.size() + " nodes");
//	    		String text = Integer.toString(queryNode) + " : " + discoveredCommunity.toString() + " (" + Integer.toString(discoveredCommunity.size()) + ")\n";
	        	System.out.println(queryNode);
//	        	writer.print(text);
	    		discoveredCommunity.clear();
	        	communitySearch.reset();
	    	}
	    	writer.close();
		} catch (FileNotFoundException e) {
			e.printStackTrace();
		}
    	long elapsedTime = System.currentTimeMillis() - startTime;
    	System.out.println("Elapsed time = " + elapsedTime + " miliseconds.");
	}

}
