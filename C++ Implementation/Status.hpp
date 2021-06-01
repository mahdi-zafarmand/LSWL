#ifndef CLASS_STATUS
#define CLASS_STATUS


#include <unordered_map>
#include "Graph.hpp"
#include <string>


struct Status {
    std::unordered_map<int, int>* node2com;
    std::unordered_map<int, float>* degrees;
    std::unordered_map<int, float>* gdegrees;
    std::unordered_map<int, float>* internals;
    std::unordered_map<int, float>* loops;
    float total_weight;

    Status();
    Status(const Status &_status);

    Status(const Graph &graph);
    inline operator std::string() const {
        return map_to_string(*node2com) + "\n" + 
               map_to_string(*degrees) + "\n" + 
               map_to_string(*gdegrees) + "\n" + 
               map_to_string(*internals) + "\n" + 
               map_to_string(*loops) + "\n" + 
               std::to_string(total_weight);}

    template <typename T>
    std::string map_to_string(const std::unordered_map<int, T>& map_attribute) const;

    void init(const Graph &graph);
    void init(const Graph &graph, std::unordered_map<int, int>& partition);

};

#endif