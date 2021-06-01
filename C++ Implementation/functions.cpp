#include "functions.hpp"
#include <algorithm>


bool cmp(std::pair<Node*, float>& a, std::pair<Node*, float>& b) {
    return a.second > b.second;
}

std::vector<int> adjust_shell(std::unordered_map<Node*, float> &shell_in_map, int k) {
    std::vector<std::pair<Node*, float> > A;
    for (auto& it : shell_in_map) {
        A.push_back(it);
    }
    std::sort(A.begin(), A.end(), cmp);
    std::vector<int> output;

    k = std::min(k, (int)shell_in_map.size());
    for(int i = 0; i < k; i++) {
        output.push_back(A[i].first->get_id());
    }
    return output;
}