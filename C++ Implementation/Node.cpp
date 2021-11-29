#include "Node.hpp"


Node::Node(int _id) : id(_id) {
    this->connections = new std::unordered_map<Node*, float>;
    this->strengths = new std::unordered_map<Node*, float>;
}

Node::Node(const Node &_node): id(_node.id), connections(_node.connections), strengths(_node.strengths) {}

Node::~Node() {
    delete connections;
    delete strengths;
}

int Node::get_id(){
    return this->id;
}

float Node::degree() {
    float degree = 0.0;
    auto it = connections->find(this);
    if(it != connections->end()){
        degree += it->second;
    }
    for(auto neighbor : *connections){
        degree += neighbor.second;
    }
    return degree;
}

std::unordered_map<Node*, float>* Node::neighbors(){
    return this->connections;
}

void Node::add_connection(Node *node, float value){
    if(this->connections->find(node) != this->connections->end()) {
        this->connections->at(node) = value;
        return;
    }
    this->connections->insert(std::make_pair(node, value));
}

void Node::add_connection(Node *node){
    if(this->connections->find(node) != this->connections->end()) {
        this->connections->at(node) = 1.0;
        return;
    }
    this->connections->insert(std::make_pair(node, 1.0));
}

void Node::assign_strength(Node* neighbor, float strength_value) {
    if(this->strengths->find(neighbor) != this->strengths->end()) {
        this->strengths->at(neighbor) = strength_value;
        return;
    }
    this->strengths->insert(std::make_pair(neighbor, strength_value));
}

float Node::get_strength(Node* neighbor) {
    auto it = this->strengths->find(neighbor);
    if(it != this->strengths->end()) {
        return it->second;
    }
    return 0.0;
}

bool Node::has_edge(Node* node) {
    return this->connections->find(node) != this->connections->end();
}

float Node::get_edge_weight(Node* node) const{
    auto it = this->connections->find(node);
    if(it != this->connections->end()){
        return it->second;
    }
    return 0.0;
}

void Node::remove_neighbor(Node* node){
    this->connections->erase(node);
}
