#include "Node.hpp"


class Edge {
    private:
        Node* start;
        Node* end;
        float weight;

    public:
        Edge(Node* _start, Node* _end);
        Edge(Node* _start, Node* _end, float _weight);
        Edge(const Edge &_edge);

        inline operator std::string() const {return std::string(*start) + " " + std::string(*end) + " " + std::to_string(weight);}

};