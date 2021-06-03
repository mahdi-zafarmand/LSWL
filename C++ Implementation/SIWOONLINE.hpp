#ifndef CLASS_SIWO_ONLINE_
#define CLASS_SIWO_ONLINE_


#include "Graph.hpp"
#include <vector>
#include <unordered_map>
#include <unordered_set>


#define __SIWO_MIN_IMPROV 0.000001
#define __DELIMITER ' '
// #define __DELIMITER '\t'
#define __START_FROM_ONE true


class SiwoOnline {
    private:
        Graph* graph;
        std::string adjlist_filename;
        bool strength_type;
        int starting_node;
        std::vector<int>* community;
        std::unordered_set<int>* shell;
        std::unordered_map<int, std::unordered_map<int, int>* >* common_neighbors;
        std::unordered_map<int, int>* max_common_neighbors; 
        std::unordered_set<int>* strength_assigned_nodes;
        float timeout;

        void initialize(int node_id);
        std::vector<int> read_neighbors_from_file(int node_id);
        void add_new_edges(int node_id, std::vector<int> const &neighbor_ids);
        void add_edges_before_strength_assignment();
        void update_sets_when_node_joins(Node* new_node);
        void update_shell_when_node_joins(Node* new_node);
        void update_dicts_of_common_neighbors_info(Node* node);

        void assign_local_strength(Node* node);
        int find_best_next_node(std::unordered_map<int, float>* improvements);
        void merge_dangling_nodes();
        void amend_small_communities();

    public:
        SiwoOnline(std::string _adjlist_filename, bool _strength_type, float _timeout);
        ~SiwoOnline();
        
        void reset();
        void remove_self_loops();
        void set_start_node(Node* start_node);
        std::vector<int> community_search(int start_node, bool amend);
        
};

#endif