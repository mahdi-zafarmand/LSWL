#ifndef CLASS_NODE
#define CLASS_NODE

#include <unordered_map>
#include <string>


class Node {
    private:
        int id;
        std::unordered_map<Node*, float>* connections;
        std::unordered_map<Node*, float>* strengths;

    public:
        Node(int _id);
        Node(const Node &_node);
        ~Node();

        int get_id();
        float degree();
        std::unordered_map<Node*, float>* neighbors();

        void add_connection(Node *node, float value);
        void add_connection(Node *node);

        void assign_strength(Node* neighbor, float strength_value);
        float get_strength(Node* neighbor);
        
        bool has_edge(Node* node);
        
        float get_edge_weight(Node* node) const;        
        
        void remove_neighbor(Node* node);

        inline operator std::string() const {return std::to_string(id);}
};

#endif