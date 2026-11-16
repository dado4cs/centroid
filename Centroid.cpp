#include <bits/stdc++.h>
using namespace std;

const int N = 2 * 100000 + 5;
vector<vector<int>> G(N);
vector<int> sizes(N, -1);

int dfs(int u) {
  sizes[u] = 1;
  for (int &v : G[u]) {
    if (sizes[v] != -1)
      continue;
    sizes[u] += dfs(v);
  }
  return sizes[u];
}

int n;
int main() {
  cin.tie(0)->sync_with_stdio(false);
  cin >> n;
  for (int i = 0; i < n - 1; ++i) {

    int u, v;
    cin >> u >> v;
    G[u].push_back(v);
    G[v].push_back(u);
  }
  dfs(1);
  int u = 1, p = -1;
  while (true) {
    int next = -1;
    for (int &v : G[u]) {
      if (sizes[v] > n / 2 && v != p) {
        next = v;
        break;
      }
    }
    if (next == -1) {
      cout << "Centroide: " << u << '\n';
      return 0;
    }
    p = u;
    u = next;
  }
}
