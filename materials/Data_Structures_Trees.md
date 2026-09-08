# Data Structures & Algorithms: Trees, Graphs & Traversal

## 1. Trees and Hierarchical Data Structures
A tree is a non-linear hierarchical data structure consisting of nodes connected by edges, without cycles.
- **Root**: The topmost node with no parent.
- **Leaf Node**: A node with no children.
- **Height of Tree**: The length of the longest path from the root to a leaf node.

## 2. Binary Search Trees (BST)
A binary tree where each node has at most two children, and for every node $X$:
- All nodes in the left subtree have values strictly less than $X$'s value.
- All nodes in the right subtree have values strictly greater than $X$'s value.
- **Time Complexity**: $O(\log n)$ average for search, insertion, and deletion; $O(n)$ worst-case when the tree is degenerate (skewed).

## 3. Self-Balancing Binary Search Trees (AVL Trees)
To avoid $O(n)$ degeneration, self-balancing trees maintain balance factors:
- **Balance Factor**: $\text{BF} = \text{Height}(\text{LeftSubtree}) - \text{Height}(\text{RightSubtree})$.
- For every node, $\text{BF} \in \{-1, 0, 1\}$.
- **Rotations for Rebalancing**:
  - LL (Single Right Rotation)
  - RR (Single Left Rotation)
  - LR (Left-Right Double Rotation)
  - RL (Right-Left Double Rotation)
- Guarantees worst-case $O(\log n)$ time for search, insertion, and deletion.

## 4. Graph Traversals
- **Breadth-First Search (BFS)**: Explores neighboring vertices level by level using a FIFO Queue. Finds shortest paths in unweighted graphs. Time: $O(V + E)$.
- **Depth-First Search (DFS)**: Traverses deeply along each branch before backtracking using recursion or a LIFO Stack. Useful for topological sorting and cycle detection. Time: $O(V + E)$.
