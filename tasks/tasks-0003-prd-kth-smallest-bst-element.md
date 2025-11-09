# Task List: Kth Smallest Element in BST

## Relevant Files

- `src/main/java/com/algorithms/bst/TreeNode.java` - TreeNode class definition with constructors
- `src/main/java/com/algorithms/bst/Solution.java` - Main solution class with kthSmallest method implementation
- `src/test/java/com/algorithms/bst/TreeNodeTest.java` - Unit tests for TreeNode class
- `src/test/java/com/algorithms/bst/SolutionTest.java` - Comprehensive unit tests for Solution class (happy path, edge cases, error cases)
- `src/test/java/com/algorithms/bst/PerformanceTest.java` - Performance benchmarking tests for large trees
- `pom.xml` - Maven build configuration with JUnit 5 and JaCoCo dependencies
- `README.md` - Documentation explaining the algorithm approach and usage

### Notes

- This is a standalone Java project within the existing Python-based codebase
- Unit tests should be placed in `src/test/java` following Maven standard directory structure
- Use `mvn test` to run all tests
- Use `mvn test -Dtest=ClassName#methodName` to run specific tests
- Use `mvn jacoco:report` to generate code coverage reports (target: ≥90%)
- Performance tests should validate <100ms execution time for 10,000 node trees

## Tasks

- [ ] 1.0 Set up Java project structure and build configuration
  - [ ] 1.1 Create Maven project directory structure (`src/main/java`, `src/test/java`)
  - [ ] 1.2 Create `pom.xml` with Java 8+ configuration, JUnit 5 (Jupiter) dependency, and JaCoCo plugin for coverage
  - [ ] 1.3 Create package structure `com.algorithms.bst` for source files
  - [ ] 1.4 Add `.gitignore` entries for Java artifacts (`target/`, `*.class`, `.idea/`, etc.)
  - [ ] 1.5 Create `README.md` with project overview and build instructions

- [ ] 2.0 Implement TreeNode class with required constructors (TDD: RED phase)
  - [ ] 2.1 Write failing tests for TreeNode single-parameter constructor (`test_should_create_node_when_value_provided`)
  - [ ] 2.2 Write failing tests for TreeNode three-parameter constructor with left and right children
  - [ ] 2.3 Write failing tests for TreeNode field access (val, left, right)
  - [ ] 2.4 Implement TreeNode class with both constructors to pass all tests (GREEN phase)
  - [ ] 2.5 Add Javadoc comments to TreeNode class and constructors (REFACTOR phase)
  - [ ] 2.6 Verify all TreeNode tests pass

- [ ] 3.0 Implement Solution class with kthSmallest method (TDD: RED → GREEN → REFACTOR)
  - [ ] 3.1 Write failing test for null root (should throw IllegalArgumentException with "root cannot be null")
  - [ ] 3.2 Write failing test for k < 1 (should throw IllegalArgumentException with "k must be positive")
  - [ ] 3.3 Write failing test for k = 0 (should throw IllegalArgumentException with "k must be positive")
  - [ ] 3.4 Write failing test for k > tree size (should throw IllegalArgumentException with "k exceeds tree size")
  - [ ] 3.5 Write failing test for single node tree (k=1, should return root value)
  - [ ] 3.6 Write failing test for small balanced tree (3-5 nodes, k in middle range)
  - [ ] 3.7 Write failing test for k=1 (smallest element in balanced tree)
  - [ ] 3.8 Write failing test for k=n (largest element in balanced tree)
  - [ ] 3.9 Implement input validation in kthSmallest (null check, k validation) to pass error tests (GREEN phase)
  - [ ] 3.10 Implement tree size calculation helper method to validate k bounds
  - [ ] 3.11 Implement in-order traversal algorithm (recursive or iterative) to find kth smallest element
  - [ ] 3.12 Verify all basic tests pass (error handling + happy path)
  - [ ] 3.13 Add comprehensive Javadoc comments explaining algorithm choice, parameters, return value, and exceptions (REFACTOR phase)
  - [ ] 3.14 Add inline comments explaining key algorithm steps

- [ ] 4.0 Implement comprehensive test suite with JUnit 5 (TDD: Continue RED → GREEN cycles)
  - [ ] 4.1 Write failing test for completely left-skewed tree (worst case: all nodes on left)
  - [ ] 4.2 Write failing test for completely right-skewed tree (worst case: all nodes on right)
  - [ ] 4.3 Write failing test for large balanced tree (100+ nodes, various k values)
  - [ ] 4.4 Write failing test for k=1 in skewed trees
  - [ ] 4.5 Write failing test for k=n in skewed trees
  - [ ] 4.6 Implement fixes if any edge case tests fail (GREEN phase)
  - [ ] 4.7 Write test for negative k values (k=-5, should throw exception)
  - [ ] 4.8 Add assertions to verify exact exception messages match PRD requirements
  - [ ] 4.9 Run `mvn test` and verify all tests pass
  - [ ] 4.10 Run `mvn jacoco:report` and verify code coverage ≥90%

- [ ] 5.0 Add performance benchmarking and validate success metrics
  - [ ] 5.1 Create PerformanceTest class with setup method to build large trees
  - [ ] 5.2 Implement helper method to construct balanced BST with 10,000 nodes
  - [ ] 5.3 Write benchmark test for k=1 (smallest element, measures best case performance)
  - [ ] 5.4 Write benchmark test for k=5000 (middle element, measures average case)
  - [ ] 5.5 Write benchmark test for k=10000 (largest element, measures worst case)
  - [ ] 5.6 Add timing assertions to verify execution time <100ms for all cases
  - [ ] 5.7 Run performance tests and document results in README.md
  - [ ] 5.8 Update README.md with algorithm complexity analysis (time: O(H+k), space: O(H))
  - [ ] 5.9 Add usage examples and sample code to README.md
  - [ ] 5.10 Verify all acceptance criteria from PRD are met

## Implementation Notes

### Algorithm Choice Guidance

The developer should choose between two approaches:

1. **Recursive In-order Traversal with Counter**:
   - Pros: Clean, intuitive code; natural fit for tree problems
   - Cons: Uses O(H) call stack space
   - Best for: Educational clarity, balanced trees

2. **Iterative In-order with Explicit Stack**:
   - Pros: Can stop early once kth element found; explicit control
   - Cons: Slightly more code; manual stack management
   - Best for: Performance optimization, skewed trees

Both meet the O(H+k) time and O(H) space requirements. Document your choice in the README.

### Defensive Programming Requirements

All methods must follow the 5-step defensive function pattern:

```java
public int kthSmallest(TreeNode root, int k) {
    // Step 1: Type/null checking
    if (root == null) {
        throw new IllegalArgumentException("root cannot be null");
    }

    // Step 2: Input validation
    if (k < 1) {
        throw new IllegalArgumentException("k must be positive");
    }

    int treeSize = countNodes(root);
    if (k > treeSize) {
        throw new IllegalArgumentException("k exceeds tree size");
    }

    // Step 3: Edge case handling (single node)
    // Step 4: Main logic (in-order traversal)
    // Step 5: Return result
}
```

### Test Naming Convention

Follow the pattern: `test_should_[result]_when_[condition]()`

Examples:
- `test_should_throw_exception_when_root_is_null()`
- `test_should_throw_exception_when_k_is_zero()`
- `test_should_return_smallest_when_k_is_one()`
- `test_should_return_largest_when_k_equals_tree_size()`
- `test_should_handle_left_skewed_tree_when_all_nodes_on_left()`

### Maven Dependencies Required

```xml
<dependencies>
    <!-- JUnit 5 -->
    <dependency>
        <groupId>org.junit.jupiter</groupId>
        <artifactId>junit-jupiter</artifactId>
        <version>5.9.3</version>
        <scope>test</scope>
    </dependency>
</dependencies>

<build>
    <plugins>
        <!-- JaCoCo for coverage -->
        <plugin>
            <groupId>org.jacoco</groupId>
            <artifactId>jacoco-maven-plugin</artifactId>
            <version>0.8.10</version>
        </plugin>
    </plugins>
</build>
```

### TDD Workflow Reminder

For each feature (especially tasks 2.0 and 3.0):

1. **RED**: Write a failing test first
2. **GREEN**: Write minimal code to pass the test
3. **REFACTOR**: Improve code quality while keeping tests green

Never write implementation code before the test exists!
