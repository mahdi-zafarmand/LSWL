import java.util.HashMap;
import java.util.Set;

public class Node {

	private int id;
	private HashMap<Integer, Double> connections;
	private HashMap<Integer, Double> strengths;
	
	public Node(int id) {
		this.id = id;
		this.connections = new HashMap<Integer, Double>();
		this.strengths = new HashMap<Integer, Double>();
	}
	
	Node(Node n){
		id = n.id;
		connections = n.connections;
		strengths = n.strengths;
	}
	
	public int getId() {
		return this.id;
	}
	
	public String toString() {
		return Integer.toString(this.id);
	}
	
	public HashMap<Integer, Double> neighbors(){
		HashMap<Integer, Double> neighbors = new HashMap<Integer, Double>();
		Set<Integer> keys = connections.keySet();
		for(int key : keys) {
			neighbors.put(key, connections.get(key));
		}
		return neighbors;
	}
	
	public void addConnection(Node node, double value) {
		this.connections.put(node.getId(), value);
	}

	public void addConnection(Node node) {
		this.connections.put(node.getId(), 1.0);
	}
	
	public double edgeWeight(int nodeId) {
		if(this.connections.containsKey(nodeId)) {
			return this.connections.get(nodeId);
		}
		return 0.0;
	}
	
	public double edgeWeight(Node node) {
		return this.edgeWeight(node.getId());
	}
	
	public void removeNeighbor(Node node) {
		this.removeNeighbor(node.getId());
	}

	public void removeNeighbor(int nodeId) {
		this.connections.remove(nodeId);
	}
	
	public boolean hasEdge(Node node) {
		return this.hasEdge(node.getId());
	}
	
	public boolean hasEdge(int nodeId) {
		return this.connections.containsKey(nodeId);
}
	
	public void assignStrength(int neighborId, double strength) {
		this.strengths.put(neighborId, strength);
	}
	
	public double getStrength(int neighborId) {
		if(this.strengths.containsKey(neighborId)) {
			return this.strengths.get(neighborId);
		}
		return 0.0;
	}
	
	public void showConnections() {
		System.out.println(this.connections);
	}
	
	public void showStrengths() {
		System.out.println(this.strengths);
	}
}
