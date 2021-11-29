#include "Graph.hpp"
#include <iostream>
#include <string>
#include <algorithm>
#include <unordered_set>


Graph::Graph() {
    this->nodes = new std::unordered_map<int, Node*>;
}

Graph::Graph(const Graph &_graph) : nodes(_graph.nodes) {}

Graph::~Graph() {
    for(auto node : *nodes) {
        delete node.second;
    }
    delete nodes;
}

Node* Graph::add_node(Node* node) {
    int node_id = node->get_id();
    return add_node(node_id);
}

Node* Graph::add_node(int node_id) {
    auto new_node_it = this->nodes->find(node_id);
    if(new_node_it == this->nodes->end()){
        this->nodes->insert(std::make_pair(node_id, new Node(node_id)));
        return this->nodes->at(node_id);
    }
    return new_node_it->second;
}

Node* Graph::get_node(int node_id) const{
    return this->nodes->at(node_id);
}

std::unordered_map<int, Node*>* Graph::get_nodes() const{
    return this->nodes;
}

int Graph::get_number_of_nodes() const{
    return this->nodes->size();
}

int Graph::get_number_of_edges() const{
    int number_of_edges = 0;
    std::unordered_map<Node*, float>* neighbors;

    for(auto node : *(this->nodes)){
        neighbors = node.second->neighbors();
        if(neighbors->find(node.second) != neighbors->end()){
            number_of_edges++;
        }
        number_of_edges += neighbors->size();
    }
    return number_of_edges / 2;
}

bool Graph::has_edge(Node* node_1, Node* node_2) {
    return node_1->has_edge(node_2);
}

bool Graph::has_edge(int node_id_1, int node_id_2) {
    return this->has_edge(nodes->at(node_id_1), nodes->at(node_id_2));
}

void Graph::add_edge(Node* node_1, Node* node_2) {
    Node* n1 = add_node(node_1);
    Node* n2 = add_node(node_2);

    if(n1->get_id() == n2->get_id()){
        n1->add_connection(n2);
        return;
    }

    n1->add_connection(n2);
    n2->add_connection(n1);
}

void Graph::add_edge(int node_id_1, int node_id_2) {
    Node* n1 = add_node(node_id_1);
    Node* n2 = add_node(node_id_2);

    if(n1->get_id() == n2->get_id()){
        n1->add_connection(n2);
        return;
    }

    n1->add_connection(n2);
    n2->add_connection(n1);
}

void Graph::add_edge(Node* node_1, Node* node_2, float weight) {
    Node* n1 = add_node(node_1);
    Node* n2 = add_node(node_2);

    if(n1->get_id() == n2->get_id()){
        n1->add_connection(n2, weight);
        return;
    }

    n1->add_connection(n2, weight);
    n2->add_connection(n1, weight);
}

void Graph::add_edge(int node_id_1, int node_id_2, float weight) {
    Node* n1 = add_node(node_id_1);
    Node* n2 = add_node(node_id_2);

    if(n1->get_id() == n2->get_id()){
        n1->add_connection(n2, weight);
        return;
    }

    n1->add_connection(n2, weight);
    n2->add_connection(n1, weight);
}

float Graph::size() const{
    float total_weight = 0.0;
    std::unordered_map<Node*, float>* neighbors;

    for(auto node : *(this->nodes)){
        neighbors = node.second->neighbors();
        if(neighbors->find(node.second) != neighbors->end()){
            total_weight += node.second->get_edge_weight(node.second);
        }
        for(auto neighbor : *neighbors){
            total_weight += neighbor.second;
        }
    }
    return total_weight / 2.0;
}

float Graph::degree(Node* node) const{
    return node->degree();
}

float Graph::degree(int node_id) const{
    if(this->nodes->find(node_id) == this->nodes->end()) {
        return 0.0;
    }
    return this->get_node(node_id)->degree();
}

float Graph::get_edge_weight(Node* node_1, Node* node_2) const{
    if(node_1 != NULL && node_2 != NULL){
        return node_1->get_edge_weight(node_2);
    }
    return 0.0;
}

void Graph::remove_node(Node* node) {
    for(auto neighbor : *(node->neighbors())) {
        neighbor.first->remove_neighbor(node);
    }
    this->nodes->erase(node->get_id());
}

void Graph::remove_node(int node_id) {
    remove_node(get_node(node_id));
}

void Graph::remove_edge(Node* node_1, Node* node_2) {
    node_1->remove_neighbor(node_2);
    // if(node_1->neighbors().size() == 0) {
    //     this->nodes->erase(node_1->get_id());
    // }
    node_2->remove_neighbor(node_1);
    // if(node_2->neighbors().size() == 0) {
    //     this->nodes->erase(node_2->get_id());
    // }    
}

void Graph::remove_edge(int node_id_1, int node_id_2) {
    this->remove_edge(this->get_node(node_id_1), this->get_node(node_id_2));
}

int Graph::get_common_neighbors(Node* node_1, Node* node_2) {
    std::unordered_set<Node*> common_neighbors;
    std::unordered_set<Node*> neighbor_ids_node_1;
    for(auto neighbor : *(node_1->neighbors())) {
        neighbor_ids_node_1.insert(neighbor.first);
    }
    for(auto neighbor : *(node_2->neighbors())) {
        if(neighbor_ids_node_1.find(neighbor.first) != neighbor_ids_node_1.end()) {
            common_neighbors.insert(neighbor.first);
        }
    }
    return common_neighbors.size();
}

void Graph::print_info() const{
    std::cout << "Printing graph info:\n";
    std::cout << "\t-This graph has " << std::to_string(get_number_of_nodes()) << " node(s).\n";
    std::cout << "\t-This graph has " << std::to_string(get_number_of_edges()) << " edge(s).\n" << std::endl;
}