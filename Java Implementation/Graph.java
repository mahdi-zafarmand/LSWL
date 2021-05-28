import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;

public class Graph implements GraphInterface{

	private HashMap<Integer, Node> nodes;
	
	public Graph() {
		this.nodes = new HashMap<Integer, Node>();
	}

	public Node addNode(Node node) {
		int nodeId = node.getId();
		if(!(this.nodes.containsKey(nodeId))) {
			Node newNode = new Node(nodeId);
			this.nodes.put(nodeId, newNode);
		}
		return this.nodes.get(nodeId);
	}
	
	public Node addNode(int nodeId) {
		if(!(this.nodes.containsKey(nodeId))) {
			Node newNode = new Node(nodeId);
			this.nodes.put(nodeId, newNode);
		}
		return this.nodes.get(nodeId);		
	}
	
	public Node getNode(int nodeId) {
		if(this.nodes.containsKey(nodeId)) {
			return this.nodes.get(nodeId);
		}
		return null;
	}
	
	public ArrayList<Node> nodes(){
		ArrayList<Node> nodes = new ArrayList<>();
		
		for(int nodeId : this.nodes.keySet()) {
			nodes.add(this.nodes.get(nodeId));
		}
		return nodes;
	}

	public ArrayList<Node> sortedNodes(){
		ArrayList<Integer> sortedIDs = new ArrayList<>();
		ArrayList<Node> sortedNodes = new ArrayList<>();
		
		for(int nodeId : this.nodes.keySet()) {
			sortedIDs.add(nodeId);
		}
		sortedIDs.sort(null);
		for(int nodeId : sortedIDs) {
			sortedNodes.add(this.nodes.get(nodeId));
		}
		return sortedNodes;
	}

	
	public int getNumberOfNodes() {
		return this.nodes.size();
	}
	
	
	public boolean hasEdge(Node node1, Node node2) {
		return node1.hasEdge(node2);
	}
	
	public boolean hasEdge(int nodeId1, int nodeId2) {
		return this.hasEdge(getNode(nodeId1), getNode(nodeId2));
	}

	public void addEdge(Node node1, Node node2) {
//		to make sure node1 and node2 exist in the graph.
		Node n1 = this.addNode(node1);
		Node n2 = this.addNode(node2);
		
//		if the new is a self-loop.
		if(n1.equals(n2)) {
			n1.addConnection(n2);
			return;
		}
		n1.addConnection(n2);
		n2.addConnection(n1);
	}
	
	public void addEdge(int nodeId1, int nodeId2) {
//		to make sure node1 and node2 exist in the graph.
		Node n1 = this.addNode(nodeId1);
		Node n2 = this.addNode(nodeId2);
		
//		if the new is a self-loop.
		if(n1.equals(n2)) {
			n1.addConnection(n2);
			return;
		}
		n1.addConnection(n2);
		n2.addConnection(n1);		
	}

	public void addEdge(Node node1, Node node2, double weight) {
//		to make sure node1 and node2 exist in the graph.
		Node n1 = this.addNode(node1);
		Node n2 = this.addNode(node2);
		
//		if the new is a self-loop.
		if(n1.equals(n2)) {
			n1.addConnection(n2, weight);
			return;
		}
		n1.addConnection(n2, weight);
		n2.addConnection(n1, weight);
	}

	public void addEdge(int nodeId1, int nodeId2, double weight) {
//		to make sure node1 and node2 exist in the graph.
		Node n1 = this.addNode(nodeId1);
		Node n2 = this.addNode(nodeId2);
		
//		if the new is a self-loop.
		if(n1.equals(n2)) {
			n1.addConnection(n2, weight);
			return;
		}
		n1.addConnection(n2, weight);
		n2.addConnection(n1, weight);
	}

	public ArrayList<Edge> edges(){
		ArrayList<Edge> allEdges= new ArrayList<>();
		HashMap<Integer, Double> neighbors;
		
		for(Node node : this.nodes()) {
			neighbors = node.neighbors();
			for(int neighborId : neighbors.keySet()) {
				if(node.getId() <= neighborId) {
					allEdges.add(new Edge(node, this.getNode(neighborId), neighbors.get(neighborId)));
				}
			}
//			if(neighbors.keySet().contains(node.getId())) {
//				allEdges.add(new Edge(node, node, neighbors.get(node.getId())));
//			}
		}
		return allEdges;
	}
	
	public int getNumberOfEdges() {
		int numberOfEdges = 0;
		HashMap<Integer, Double> neighbors;
		for(int nodeId : this.nodes.keySet()) {
			neighbors = this.nodes.get(nodeId).neighbors();
//			if node has a self-loop
			if(neighbors.containsKey(nodeId)) {
				numberOfEdges += 1;
			}
			numberOfEdges += neighbors.size();
		}
		return numberOfEdges / 2;
	}
	
	public Graph copy() {
		Graph duplicate = new Graph();
		HashMap<Integer, Double> neighbors;

		for(int nodeId : this.nodes.keySet()) {
			duplicate.addNode(nodeId);
			neighbors = this.nodes.get(nodeId).neighbors();
			for(int neighborId : neighbors.keySet()) {
				duplicate.addEdge(nodeId, neighborId, neighbors.get(neighborId));
			}
		}		
		return duplicate;
	}
	
	public double size() {
		double totalWeight = 0.0;
		HashMap<Integer, Double> neighbors;

		for(Map.Entry<Integer, Node> node : nodes.entrySet()) {
			neighbors = node.getValue().neighbors();
			if(neighbors.containsKey(node.getKey())) {
				totalWeight += node.getValue().edgeWeight(node.getKey());
			}
			for(Map.Entry<Integer, Double> neighbor : neighbors.entrySet()) {
				totalWeight += neighbor.getValue();
			}
		}
		return totalWeight / 2.0;
	}
	
	public double degree(Node node) {
		return this.degree(node.getId());
	}

	public double degree(int nodeId) {
		double degree = 0.0;
		HashMap<Integer, Double> neighbors = this.nodes.get(nodeId).neighbors();

		if(neighbors.containsKey(nodeId)) {
			degree += neighbors.get(nodeId);
		}
		for(int neighbor : neighbors.keySet()) {
			degree += neighbors.get(neighbor);
		}
		return degree;
	}

	public double edgeWeight(int nodeId1, int nodeId2) {
		Node node1 = this.getNode(nodeId1);
		Node node2 = this.getNode(nodeId2);
		
		if(node1 != null && node2 != null) {
			return node1.edgeWeight(node2);
		}
		return 0.0;
	}
	
	public double edgeWeight(Node node1, Node node2) {
		return this.edgeWeight(node1.getId(), node2.getId());
	}
	
	public void removeNode(Node node) {
		for(int neighborId : node.neighbors().keySet()) {
			this.getNode(neighborId).removeNeighbor(node);
			this.nodes.remove(node.getId());
		}
	}
	
	public void removeNode(int nodeId) {
		this.removeNode(this.getNode(nodeId));
	}
	
	public void removeEdge(Node node1, Node node2) {
		node1.removeNeighbor(node2);
		// if(node1.neighbors().size() == 0) {
		// 	this.nodes.remove(node1.getId());
		// }
		node2.removeNeighbor(node1);
		// if(node2.neighbors().size() == 0) {
		// 	this.nodes.remove(node2.getId());
		// }
	}
	
	public HashSet<Integer> getCommonNeighbors(Node node1, Node node2) {
		HashSet<Integer> commonNeighbors = new HashSet<>();
		HashSet<Integer> neighbors1 = new HashSet<>();
		
		for(int neighborId : node1.neighbors().keySet()) {
			neighbors1.add(neighborId);
		}
		for(int neighborId : node2.neighbors().keySet()) {
			if(neighbors1.contains(neighborId)) {
				commonNeighbors.add(neighborId);
			}
		}
		return commonNeighbors;
	}
}
