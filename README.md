# ColumnGeneration
My attempts to implement column generation algorithm

The cutting stock problem involves cutting larger, standard-sized materials into smaller, required pieces while minimizing waste. Column generation is an effective method for solving this problem, especially for large instances.

### The Problem

The goal of the  **cutting stock problem**  is to find the most efficient way to cut a set of standard-width raw materials into smaller pieces of various widths to meet a specific demand. The "efficiency" is typically measured by minimizing the number of standard widths used, which directly minimizes waste. The problem can be formulated as a mixed integer linear program (MILP), but the number of possible cutting patterns can be enormous, making it computationally intractable to list all of them beforehand.

----------

### Column Generation Approach

**Column generation**  is an iterative algorithm that addresses the large number of possible cutting patterns by not listing them all at the beginning. Instead, it starts with a small subset of patterns and then, in each iteration, adds a new, more optimal pattern to the set. This is a type of decomposition method that breaks the large problem into two smaller, more manageable subproblems:

-   **Restricted Master Problem (RMP):**  This is the main problem. It's a linear programming (LP) relaxation of the original ILP, but it only considers a  **restricted subset of all possible cutting patterns**. It seeks to find the best combination of these available patterns to meet the demand. The solution to the RMP provides dual variables (shadow prices) for each required width.
    
-   **Column Generation Subproblem (CGSP):**  This is where the magic happens. The subproblem uses the dual variables from the RMP to find a  **new, promising cutting pattern**  that, if added to the RMP, could improve the solution. This is done by finding a pattern that has a negative reduced cost. For the cutting stock problem, the subproblem is a  **knapsack problem**. It tries to "pack" the required pieces into one standard-width raw material to find the most "valuable" new pattern to add to the RMP.
    

----------

### The Process

The column generation algorithm proceeds as follows:

1.  **Initialization:**  Start with an initial set of valid cutting patterns (columns) for the RMP.
    
2.  **Solve the RMP:**  Solve the current RMP to get an optimal solution and the corresponding dual variables.
    
3.  **Solve the CGSP:**  Use the dual variables as item values and solve the knapsack problem to find a new pattern with a negative reduced cost.
    
4.  **Check for Termination:**
    
    -   If a new pattern with a negative reduced cost is found, add it to the basis of RMP and go back to step 2.
        
    -   If no new pattern with a negative reduced cost can be found, the algorithm terminates because no new variable can enter the basis. The current solution to the RMP is optimal for the LP relaxation of the full problem.
        
5.  **Integer Solution:**  After the LP relaxation is solved, an integer solution can be obtained by rounding or by using a branch-and-bound algorithm, which uses the column generation process within each node of the branching tree.


This code is direct implementation of the example explained by **Professor Sergiy Butenko** that can be found [here](https://www.youtube.com/watch?v=O918V86Grhc) 

The model is written using [PuLP : A Linear Programming Toolkit for Python](https://coin-or.github.io/pulp/main/index.html) 

The solver used is # [HiGHS - High Performance Optimization Software](https://ergo-code.github.io/HiGHS/dev/#HiGHS-High-Performance-Optimization-Software)
