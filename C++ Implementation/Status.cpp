#include "Status.hpp"
#include<iostream>


Status::Status() : total_weight(0.0) {
    this->node2com = new std::unordered_map<int, int>;
    this->degrees = new std::unordered_map<int, float>;
    this->gdegrees = new std::unordered_map<int, float>;
    this->internals = new std::unordered_map<int, float>;
    this->loops = new std::unordered_map<int, float>;
}

Status::Status(const Status &_status) : node2com(_status.node2com),
                                        degrees(_status.degrees), gdegrees(_status.gdegrees),
                                        internals(_status.internals), loops(_status.loops), total_weight(0.0) {}

Status::Status(const Graph &graph) {
    Status();
    this->init(graph);
}

template <typename T>
std::string Status::map_to_string(const std::unordered_map<int, T>& map_attribute) const {
    int size = map_attribute.size(), counter = 0;
    std::string output = ""; 

    for(auto elem : map_attribute){
        output.append(std::to_string(elem.first) + ":" + std::to_string(elem.second));
        if(counter < size - 1) {
            output.append(", ");
            counter++;
        }
    }
    output.append("\n");
    return output;
}

void Status::init(const Graph &graph) {
    int count = 0;
    total_weight = graph.size();

    float deg, looptmp;
    std::unordered_map<int, Node*>* nodes = graph.get_nodes();
    for(auto node : *nodes) {
        node2com->insert({node.first, count});
        deg = graph.degree(node.second);
        degrees->insert({count, deg});
        gdegrees->insert({node.first, deg});
        looptmp = graph.get_edge_weight(node.second, node.second);
        loops->insert({node.first, looptmp});
        internals->insert({count, loops->at(node.first)});
        count++;
    }
}

void Status::init(const Graph &graph, std::unordered_map<int, int>& partition) {
    int count = 0;
    total_weight = graph.size();

    float deg, inc;
    std::unordered_map<Node*, float>* neighbors;
    std::unordered_map<int, Node*>* nodes = graph.get_nodes();
    for(auto node : *nodes) {
        int com = partition[node.first];
        node2com->insert({node.first, com});
        deg = graph.degree(node.second);
        degrees->insert({count, deg + degrees->at(com)});
        gdegrees->insert({node.first, deg});
        inc = 0.0;
        neighbors = node.second->neighbors();
        for(auto neighbor : *neighbors) {
            if(partition.at(neighbor.first->get_id()) == com) {
                inc += neighbor.second;
            } else {
                inc += neighbor.second / 2.0;
            }
        }
        internals->insert({com, internals->at(com) + inc});
    }
}
