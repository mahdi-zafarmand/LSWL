#include "SIWO.hpp"
#include "functions.hpp"
#include <iostream>
#include <algorithm>
#include <chrono>


template <typename T>
void print_map(std::unordered_map<int, T>* my_map) {
    std::vector<int> keys;
    for(auto item : *my_map) {
        keys.push_back(item.first);
    }
    std::sort(keys.begin(), keys.end());
    for(size_t i = 0; i < keys.size(); i++) {
        std::cout << keys[i] << ":" << my_map->at(keys[i]) << "\t";
    }
    std::cout << std::endl;
}


SIWO::SIWO(Graph* _graph, bool _strength_type, float _timeout) : graph(_graph), strength_type(_strength_type), timeout(_timeout) {
    this->remove_self_loops();
    starting_node = -1;
    community = new std::vector<int>;
    shell = new std::unordered_set<int>;
    common_neighbors = new std::unordered_map<int, std::unordered_map<int, int>* >;
    max_common_neighbors = new std::unordered_map<int, int>;
    strength_assigned_nodes = new std::unordered_set<int>;
}

SIWO::~SIWO() {
    delete community;
    delete shell;

    for(auto item : *common_neighbors) {
        delete item.second;
    }
    delete common_neighbors;
    delete max_common_neighbors;
    delete strength_assigned_nodes;
}

void SIWO::update_sets_when_node_joins(Node* new_node) {
    community->push_back(new_node->get_id());
    this->update_shell_when_node_joins(new_node);
}

void SIWO::update_shell_when_node_joins(Node* new_node) {
    for(auto neighbor : *(new_node->neighbors())) {
        this->shell->insert(neighbor.first->get_id());
    }
    for(auto node_id : *(this->community)) {
        if(this->shell->find(node_id) != this->shell->end()) {
            this->shell->erase(node_id);
        }
    }
}

void SIWO::update_dicts_of_common_neighbors_info(Node* node) {
    int node_id = node->get_id();
    if(this->common_neighbors->find(node_id) == this->common_neighbors->end()) {
        this->common_neighbors->insert({node_id, new std::unordered_map<int, int>});
        this->max_common_neighbors->insert({node_id, -1});
    }

    int number_common_neighbors;
    for(auto neighbor : *(node->neighbors())) {
        int neighbor_id = neighbor.first->get_id();
        std::unordered_map<int, int> temp_neighbors = *(this->common_neighbors->at(node_id));
        if(temp_neighbors.find(neighbor_id) == temp_neighbors.end()) {
            if(this->common_neighbors->find(neighbor_id) == this->common_neighbors->end()) {
                this->common_neighbors->insert({neighbor_id, new std::unordered_map<int, int>});
                this->max_common_neighbors->insert({neighbor_id, -1});
            }

            number_common_neighbors = this->graph->get_common_neighbors(node, this->graph->get_node(neighbor_id));
            this->common_neighbors->at(node_id)->insert({neighbor_id, number_common_neighbors});
            this->common_neighbors->at(neighbor_id)->insert({node_id, number_common_neighbors});

            if(number_common_neighbors > this->max_common_neighbors->at(node_id)) {
                this->max_common_neighbors->at(node_id) = number_common_neighbors;
            }
            if(number_common_neighbors > this->max_common_neighbors->at(neighbor_id)) {
                this->max_common_neighbors->at(neighbor_id) = number_common_neighbors;
            }
        }
    }
}

void SIWO::assign_local_strength(Node* node) {
    int node_id = node->get_id();
    if(this->strength_assigned_nodes->find(node_id) == this->strength_assigned_nodes->end()) {
        this->update_dicts_of_common_neighbors_info(node);
        int max_mutual_node = this->max_common_neighbors->at(node_id), max_mutual_neighbor = 0, strength = 0;

        for(auto neighbor : *(node->neighbors())) {
            int neighbor_id = neighbor.first->get_id();
            max_mutual_neighbor = this->max_common_neighbors->at(neighbor_id);
            strength = this->common_neighbors->at(node_id)->at(neighbor_id);

            float s1 = 0.0, s2 = 0.0, final_strength;
            if(max_mutual_node != 0) {
                s1 = (float)strength / (float)max_mutual_node;
            }
            if(max_mutual_neighbor != 0) {
                s2 = (float)strength / (float)max_mutual_neighbor;
            }
            final_strength = (this->strength_type == false) ? (s1 + s2 - 1.0) : ((s1 + s2) / 2.0);
            node->assign_strength(neighbor.first, final_strength);
            neighbor.first->assign_strength(node, final_strength);
        }
        this->strength_assigned_nodes->insert(node_id);
    }
}

int SIWO::find_best_next_node(std::unordered_map<int, float>* improvements) {
    int new_node_id = this->community->at(this->community->size() - 1);
    Node* new_node = this->graph->get_node(new_node_id);
    for(int node_id : *(this->shell)) {
        if(improvements->find(node_id) == improvements->end()) {
            improvements->insert({node_id, this->graph->get_node(node_id)->get_strength(new_node)});
        } else if (this->graph->has_edge(node_id, new_node_id)) {
            improvements->at(node_id) = improvements->at(node_id) + this->graph->get_node(node_id)->get_strength(new_node);
        }
    }
    improvements->erase(new_node_id);

    int best_candidate = -1;
    float best_improvement = - std::numeric_limits<float>::infinity();
    for(int candidate_id : *(this->shell)) {
        if(improvements->at(candidate_id) > best_improvement) {
            best_candidate = candidate_id;
            best_improvement = improvements->at(candidate_id);
        }
    }
    return best_candidate;
}

void SIWO::merge_dangling_nodes() {
    std::unordered_set<int> neighborhood;
    for(int node_id : *(this->community)) {
        for(auto neighbor : *(this->graph->get_node(node_id)->neighbors())) {
            neighborhood.insert(neighbor.first->get_id());
        }
    }

    std::unordered_set<int> temp_community;
    for(int node_id : *(this->community)) {
        temp_community.insert(node_id);
    }
    for(int node_id : neighborhood) {
        if(this->graph->degree(node_id) == 1.0) {
            temp_community.insert(node_id);
        }
    }
    for(int node_id : *(this->community)) {
        temp_community.erase(node_id);
    }
    for(int node_id : temp_community) {
        this->community->push_back(node_id);
    }
}

void SIWO::amend_small_communities() {
    if(this->community->size() < 3) {
        if(this->shell->size() > 0) {
            int start_node_for_amend = -1;
            float temp_degree = 0.0, largest_degree = - std::numeric_limits<float>::infinity();
            for(int node_id : *(this->shell)) {
                temp_degree = this->graph->degree(node_id);
                if(temp_degree > largest_degree) {
                    start_node_for_amend = node_id;
                    largest_degree = temp_degree;
                }
            }

            SIWO next_community_searcher = SIWO(this->graph, this->strength_type, this->timeout);
            std::vector<int> new_members = next_community_searcher.community_search(start_node_for_amend, false);

            std::unordered_set<int> temp_community;
            for(int node_id : *(this->community)) {
                temp_community.insert(node_id);
            }
            for(int new_member : new_members) {
                temp_community.insert(new_member);
            }
            for(int node_id : *(this->community)) {
                temp_community.erase(node_id);
            }
            for(int node_id : temp_community) {
                this->community->push_back(node_id);
            }
        }
    }
}

void SIWO::reset() {
    this->community->clear();
    this->shell->clear();
}

void SIWO::remove_self_loops() {
    for(auto node : *(graph->get_nodes())) {
        if(this->graph->has_edge(node.second, node.second)) {
            this->graph->remove_edge(node.second, node.second);
        }
    }
}

void SIWO::set_start_node(Node* start_node) {
    std::unordered_map<int, Node*>* nodes = this->graph->get_nodes();
    if(nodes->find(start_node->get_id()) != nodes->end()) {
        this->starting_node = start_node->get_id();
        this->community->push_back(this->starting_node);
        for(auto neighbor : *(start_node->neighbors())) {
            this->shell->insert(neighbor.first->get_id());
        }
    } else {
        std::cout << "Invalid starting node! Try with another one." << std::endl;
        std::exit(1);
    }
}

std::vector<int> SIWO::community_search(int start_node_id, bool amend=true) {
    auto start_time = std::chrono::high_resolution_clock::now();
    Node* start_node = this->graph->get_node(start_node_id);
    this->set_start_node(start_node);
    this->assign_local_strength(start_node);

    // std::unordered_map<Node*, float> shell_in_map;
    // std::vector<int> temp_shell;
    std::unordered_map<int, float>* improvments = new std::unordered_map<int, float>;
    while((int)this->community->size() < this->graph->get_number_of_nodes() && this->shell->size() > 0) {
        auto current_time = std::chrono::high_resolution_clock::now();
        auto duration_time = std::chrono::duration<float> (current_time - start_time);
        if(duration_time.count() > this->timeout) {
            std::cout << "Timeout!" << std::endl;
            delete improvments;
            // return std::vector<int>();
            std::sort(this->community->begin(), this->community->end());
            return *(this->community);
        }

        // for(int node_id : *(this->shell)) {
        //     Node* node_in_shell = this->graph->get_node(node_id);
        //     shell_in_map.insert({node_in_shell, node_in_shell->degree()});
        // }
        // temp_shell= adjust_shell(shell_in_map, 20);
        // shell_in_map.clear();

        for(int node_id : *(this->shell)) {
            this->assign_local_strength(this->graph->get_node(node_id));
        }
        // temp_shell.clear();

        int best_next_node_id = this->find_best_next_node(improvments);

        if(this->strength_type == false && improvments->at(best_next_node_id) < __SIWO_MIN_IMPROV) {
            break;
        }
        if(this->strength_type == true) {
            if(this->community->size() > 3 && improvments->at(best_next_node_id) < __SIWO_MIN_IMPROV + 1.0) {
                break;
            } else if(this->community->size() < 3 && improvments->at(best_next_node_id) < __SIWO_MIN_IMPROV) {
                break;
            }
        }
        this->update_sets_when_node_joins(this->graph->get_node(best_next_node_id));
    }
    delete improvments;
 
    if(amend == true) {
        this->amend_small_communities();
    }
    this->merge_dangling_nodes();
    std::sort(this->community->begin(), this->community->end());
    return *(this->community);
}
        
