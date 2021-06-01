#ifndef CLASS_GRAPH
#define CLASS_GRAPH


#include "Edge.hpp"
#include <unordered_map>
#include <vector>


class Graph {
    private:
        std::unordered_map<int, Node*>* nodes;

    public:
        Graph();
        Graph(const Graph &_graph);
        ~Graph();

        Node* add_node(Node* node);
        Node* add_node(int node_id);

        Node* get_node(int node_id) const;
        std::unordered_map<int, Node*>* get_nodes() const;
        
        int get_number_of_nodes() const;
        int get_number_of_edges() const;
        
        bool has_edge(Node* node_1, Node* node_2);
        bool has_edge(int node_id_1, int node_id_2);
        void add_edge(Node* node_1, Node* node_2);
        void add_edge(int node_id_1, int node_id_2);
        void add_edge(Node* node_1, Node* node_2, float weight);
        void add_edge(int node_id_1, int node_id_2, float weight);

        float size() const;
        float degree(Node* node) const;
        float degree(int node_id) const;
        float get_edge_weight(Node* node_1, Node* node_2) const;
        void remove_node(Node* node);
        void remove_node(int node_id);
        void remove_edge(Node* node_1, Node* node_2);
        void remove_edge(int node_id_1, int node_id_2);
        int get_common_neighbors(Node* node_1, Node* node_2);
        void print_info() const;
};

#endif