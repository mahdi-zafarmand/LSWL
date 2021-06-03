#include "SIWO.hpp"
#include <iostream>
#include <fstream>
#include <vector>
#include <chrono>


Graph* load_graph(std::string dataset_path) {
    Graph* g = new Graph();
    std::ifstream infile(dataset_path);
    int node_1_name, node_2_name;
    while (infile >> node_1_name >> node_2_name) {
        g->add_edge(node_1_name, node_2_name);
    }
    infile.close();
    return g;
}

std::vector<int> read_query_nodes(std::string query_nodes_file_path) {
    std::vector<int> query_nodes;
    std::ifstream infile(query_nodes_file_path);
    int query_node_name;
    while (infile >> query_node_name) {
        query_nodes.push_back(query_node_name);
    }
    infile.close();
    return query_nodes;
}

template <typename T>
std::string vector_to_string(std::vector<T> the_vector) {
    if(the_vector.size() == 0) {
        return "[] (0)";
    }
    std::string output = "[";
    for(size_t i = 0; i < the_vector.size()-1; i++) {
        output += (std::to_string(the_vector[i]) + ", ");
    }
    output += std::to_string(the_vector[the_vector.size() - 1]);
    output += "] (";
    output += std::to_string(the_vector.size()) + ")";
    return output;
}

int main() {
    Graph* graph = load_graph("karate.txt");
    std::vector<int> query_nodes = read_query_nodes("query_nodes_karate.txt");

    graph->print_info();
    std::cout << "There are " << query_nodes.size() << " query nodes in this file." << std::endl;

    SIWO community_search = SIWO(graph, false, 10.0);

    auto start_time = std::chrono::high_resolution_clock::now();
    std::vector<int> discovered_community;
    std::ofstream outfile;
    outfile.open("output.txt");
    
    for(int query_node : query_nodes) {
        discovered_community = community_search.community_search(query_node, true);
        std::cout << query_node << "\t" << discovered_community.size() << std::endl ;
        outfile << (std::to_string(query_node) + " : " + vector_to_string(discovered_community) + "\n");
        discovered_community.clear();
        community_search.reset();
    }
    outfile.close();
    std::cout << std::endl;

    delete graph;
    
    auto current_time = std::chrono::high_resolution_clock::now();
    auto duration_time = std::chrono::duration<float> (current_time - start_time);
    std::cout << "Elapsed time = " << duration_time.count() << std::endl;
    
    return 0;
}