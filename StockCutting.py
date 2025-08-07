import pulp


def initialize_patterns(W, boards):
    # Starting feasible solution where only cutting one board width at the time

    m = len(boards)
    patterns = []
    for i in range(m):
        pattern = [0] * m
        pattern[i] = W // boards[i]
        patterns.append(pattern)
    return patterns


def solve_master(patterns, requirements, m):
    # Solve the restricted master problem RMP

    rmp = pulp.LpProblem("CuttingStockMaster", pulp.LpMinimize)
    x = [pulp.LpVariable(f"x_{j}", lowBound=0, cat="Continuous") for j in range(len(patterns))]

    # Objective: minimize rolls
    rmp += pulp.lpSum(x)

    # Demand constraints
    for i in range(m):
        rmp += pulp.lpSum(patterns[j][i] * x[j] for j in range(len(patterns))) >= requirements[i]

    rmp.solve(pulp.HiGHS(msg=False))
    dual = [c.pi for c in rmp.constraints.values()]
    return dual, rmp


def solve_subproblem(dual, boards, W):
    # Solve the column generation subproblem CGSP

    m = len(boards)
    sub = pulp.LpProblem("Subproblem", pulp.LpMaximize)
    y = [pulp.LpVariable(f"y_{i}", lowBound=0, cat="Integer") for i in range(m)]

    # Objective: maximize dual value
    sub += pulp.lpSum(dual[i] * y[i] for i in range(m))

    # Width constraint
    sub += pulp.lpSum(boards[i] * y[i] for i in range(m)) <= W

    sub.solve(pulp.HiGHS(msg=False))

    reduced_cost = 1 - pulp.value(sub.objective)
    pattern = [int(y[i].varValue) for i in range(m)]
    return reduced_cost, pattern


def solve_final_integer_master(patterns, requirements, m):
    # get the optimal solution for the RMP using the column generated in CGSP

    master = pulp.LpProblem("FinalMaster", pulp.LpMinimize)
    x = [pulp.LpVariable(f"x_{j}", lowBound=0, cat="Integer") for j in range(len(patterns))]

    master += pulp.lpSum(x)

    for i in range(m):
        master += pulp.lpSum(patterns[j][i] * x[j] for j in range(len(patterns))) >= requirements[i]

    master.solve(pulp.HiGHS(msg=False))
    return x, master


def get_solution(x, patterns):
    # display solution

    print("\nCutting Patterns Used:")
    for i, var in enumerate(x):
        if var.varValue > 0:
            print(f"Use pattern {patterns[i]} --> {int(var.varValue)} times")
    print(f"\nTotal rolls used: {int(pulp.value(pulp.lpSum(var for var in x)))}")


if __name__ == "__main__":

    W = 15
    boards = [4, 6, 7]
    requirements = [80, 50, 100]
    m = len(boards)

    patterns = initialize_patterns(W, boards)

    while True:  # keep iterating (exiting and entering columns until all reduced costs are negative)
        dual, RMP = solve_master(patterns, requirements, m)
        reduced_cost, new_pattern = solve_subproblem(dual, boards, W)

        if reduced_cost >= -1e-3:
            break  # optimality

        patterns.append(new_pattern)

    x, master = solve_final_integer_master(patterns, requirements, m)

    get_solution(x, patterns)
