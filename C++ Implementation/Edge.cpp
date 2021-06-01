#ifndef CLASS_EDGE
#define CLASS_EDGE


#include "Edge.hpp"


Edge::Edge(Node* _start, Node* _end) : start(_start), end(_end), weight(1.0) {}
Edge::Edge(Node* _start, Node* _end, float _weight) : start(_start), end(_end), weight(_weight) {}
Edge::Edge(const Edge &_edge) : start(_edge.start), end(_edge.end), weight(_edge.weight) {}

#endif