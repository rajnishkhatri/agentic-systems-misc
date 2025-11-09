# PRD: Kth Smallest Element in BST

## Introduction/Overview

This feature implements an algorithm to find the kth smallest value in a Binary Search Tree (BST). The primary use case is for educational purposes, helping software engineers practice and understand BST traversal algorithms and problem-solving techniques commonly encountered in coding interviews.

**Problem Statement:** Given the root node of a binary search tree and an integer k (1-indexed), return the kth smallest value in the tree.

**Goal:** Provide a clean, well-tested Java implementation that demonstrates understanding of BST properties and efficient tree traversal techniques.

## Goals

1. Implement a function that correctly returns the kth smallest element in any valid BST
2. Handle edge cases gracefully with appropriate error handling
3. Balance time and space complexity for optimal performance
4. Achieve ≥90% test coverage with comprehensive test cases
5. Provide clear, readable code suitable for educational review and learning

## User Stories

1. **As a** software engineer practicing for coding interviews, **I want to** solve the kth smallest BST problem **so that** I can demonstrate my understanding of tree traversal algorithms.

2. **As a** developer, **I want** clear error messages when providing invalid input **so that** I can quickly debug my code.

3. **As a** code reviewer, **I want** well-documented and type-safe code **so that** I can easily understand the implementation approach.

4. **As a** student learning algorithms, **I want** to see a balanced approach between time and space complexity **so that** I can learn trade-offs in algorithm design.

## Functional Requirements

### Core Functionality

1. The system must implement a `TreeNode` class with the following structure:
   ```java
   class TreeNode {
       int val;
       TreeNode left;
       TreeNode right;
       TreeNode(int val) { this.val = val; }
       TreeNode(int val, TreeNode left, TreeNode right) {
           this.val = val;
           this.left = left;
           this.right = right;
       }
   }
   ```

2. The system must implement a method `int kthSmallest(TreeNode root, int k)` that returns the kth smallest value in the BST.

3. The method must correctly handle BSTs of varying sizes (1 node to 10,000+ nodes).

4. The method must support k values from 1 to n, where n is the total number of nodes in the tree.

5. The implementation must leverage BST properties (left subtree < node < right subtree) for efficient traversal.

### Error Handling

6. The method must throw `IllegalArgumentException` with message "k must be positive" when k < 1.

7. The method must throw `IllegalArgumentException` with message "k exceeds tree size" when k is greater than the total number of nodes.

8. The method must throw `IllegalArgumentException` with message "root cannot be null" when root is null.

### Performance Requirements

9. The solution must balance time and space complexity:
   - Target time complexity: O(H + k) where H is tree height
   - Target space complexity: O(H) for recursive call stack or O(1) for iterative approach with stack

10. The implementation should work efficiently for both balanced and skewed BSTs.

### Code Quality

11. The code must follow Java naming conventions and style guidelines.

12. The code must include appropriate inline comments explaining the algorithm approach.

13. All public methods must have Javadoc comments.

## Non-Goals (Out of Scope)

1. **BST Construction Utilities**: This feature does not include helper methods for building BSTs from arrays or other input formats. Users are expected to construct their own test trees.

2. **BST Validation**: The implementation assumes the input is a valid BST. It will not validate BST properties.

3. **kth Largest Element**: Only kth smallest is in scope. Finding the kth largest element is a separate feature.

4. **Tree Modification**: The function is read-only and does not modify the tree structure.

5. **Multiple Language Implementations**: Only Java implementation is in scope.

6. **Visualization/Printing**: No tree visualization or pretty-printing utilities will be provided.

7. **Concurrent Access**: Thread-safety is out of scope for this implementation.

## Design Considerations

### Implementation Approach Options

The developer may choose between two common approaches:

1. **In-order Traversal with Counter**: Perform in-order traversal (left → root → right) and count nodes until reaching the kth element.

2. **Iterative In-order with Stack**: Use an explicit stack to perform iterative in-order traversal, stopping when k elements have been visited.

Both approaches are acceptable as long as they meet the performance and correctness requirements.

### Code Structure

```java
public class Solution {
    /**
     * Finds the kth smallest element in a binary search tree.
     *
     * @param root the root node of the BST
     * @param k the 1-indexed position of the element to find
     * @return the kth smallest value in the tree
     * @throws IllegalArgumentException if k is invalid or root is null
     */
    public int kthSmallest(TreeNode root, int k) {
        // Implementation here
    }
}
```

## Technical Considerations

1. **Language Version**: Java 8+ (to allow use of modern Java features if needed)

2. **Dependencies**: No external dependencies required. Use only Java standard library.

3. **Testing Framework**: JUnit 5 for unit testing

4. **Build System**: The solution should be compatible with standard Java build tools (Maven/Gradle)

5. **Algorithm Choice**: Developer should document which traversal approach was chosen and why (recursive vs. iterative)

## Success Metrics

1. **Correctness**: All test cases pass, including edge cases and large trees

2. **Test Coverage**: ≥90% code coverage measured by JaCoCo or similar tool

3. **Performance**: Solution completes in under 100ms for BSTs with 10,000 nodes

4. **Code Quality**: Passes static analysis checks (no warnings from Java compiler, passes Checkstyle/SpotBugs if configured)

5. **Educational Value**: Code is clear enough that a junior developer can understand the algorithm by reading the implementation

## Test Cases (Examples)

The implementation must pass these categories of tests:

### Happy Path Tests
- Small tree (3-5 nodes), k in middle range
- Balanced tree with k = 1 (smallest element)
- Balanced tree with k = n (largest element)

### Edge Cases
- Single node tree (k = 1)
- Completely left-skewed tree
- Completely right-skewed tree
- Large tree (1000+ nodes)

### Error Cases
- k = 0 (should throw exception)
- k = -5 (should throw exception)
- k > tree size (should throw exception)
- root = null (should throw exception)

### Performance Tests
- Tree with 10,000 nodes, verify execution time
- Various k values (1, n/2, n) to test different scenarios

## Open Questions

1. Should the solution include both recursive and iterative implementations for educational comparison?

2. Is there a preference for which implementation approach (recursive vs. iterative) should be the primary solution?

3. Should we provide example test cases in a separate test file, or just document expected behavior?

4. Are there specific Java code style guidelines (Google Style, Oracle conventions, etc.) that should be followed?

## Acceptance Criteria

The feature is considered complete when:

- [ ] `TreeNode` class is implemented with proper constructors
- [ ] `kthSmallest` method correctly returns kth smallest element for all valid inputs
- [ ] All four types of `IllegalArgumentException` are properly thrown with correct messages
- [ ] Test coverage is ≥90%
- [ ] All test cases (happy path, edge cases, error cases) pass
- [ ] Performance benchmark for 10,000 node tree completes in <100ms
- [ ] Code includes Javadoc comments for public methods
- [ ] Code follows Java naming and style conventions
