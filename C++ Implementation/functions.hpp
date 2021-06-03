#ifndef __FUNCTIONS__
#define __FUNCTIONS__

#include "Node.hpp"
#include <vector>
#include <unordered_map>
#include <string>

#define __A_REASONABLE_MAX_LINE_LENGTH 10000


bool cmp(std::pair<Node*, float>& a, std::pair<Node*, float>& b);
std::vector<int> adjust_shell(std::unordered_map<Node*, float> &shell_in_map, int k);
std::string read_nth_line(const std::string &filename, int n);


#endif
