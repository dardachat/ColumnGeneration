import pulp

# Data
W = 15
boards = [4, 6, 7]
requirements = [80, 50, 100]
m = len(boards)

# Starting feasible solution where only cutting one board width at the time
patterns = []
for i in range(m):
    pattern = [0] * m
    pattern[i] = W // boards[i]
    patterns.append(pattern)


# Column Generation Loop
while True: # keep iterating (exiting and entering columns until all reduced costs are negative)

    # Solve the restricted master problem RMP
    RMP = pulp.LpProblem("CuttingStockMaster", pulp.LpMinimize)
    x = [pulp.LpVariable(f"x_{j}", lowBound=0, cat="Continuous") for j in range(len(patterns))]

    # minimize number of rolls used
    RMP += pulp.lpSum(x)

    # demand constraint
    for i in range(m):
        RMP += pulp.lpSum(patterns[j][i] * x[j] for j in range(len(patterns))) >= requirements[i]


    RMP.solve(pulp.HiGHS(msg=False))

    # dual solution
    dual = [c.pi for c in RMP.constraints.values()]

    # Solve the column generation subproblem CGSP
    sub = pulp.LpProblem("Subproblem", pulp.LpMaximize)
    y = [pulp.LpVariable(f"y_{i}", lowBound=0, cat="Integer") for i in range(m)]

    # maximize reduced cost
    sub += pulp.lpSum(dual[i] * y[i] for i in range(m))

    # width constraint
    sub += pulp.lpSum(boards[i] * y[i] for i in range(m)) <= W

    sub.solve(pulp.HiGHS(msg=False))

    # if all reduced cost are negative --> optimal, otherwise and new column is generated and entered
    reduced_cost = 1 - pulp.value(sub.objective)
    if reduced_cost >= -1e-3:
        break  # optimality

    # add new pattern (column)
    new_pattern = [int(y[i].varValue) for i in range(m)]
    patterns.append(new_pattern)


# get the optimal solution for the RMP using the column generated in CGSP
master = pulp.LpProblem("Master", pulp.LpMinimize)
x = [pulp.LpVariable(f"x_{j}", lowBound=0, cat="Integer") for j in range(len(patterns))]
master += pulp.lpSum(x)

for i in range(m):
    master += pulp.lpSum(patterns[j][i] * x[j] for j in range(len(patterns))) >= requirements[i]

master.solve(pulp.HiGHS(msg=False))


# Output solution
print("\nCutting Patterns Used:")
for i, var in enumerate(x):
    if var.varValue > 0:
        print(f"Use pattern {patterns[i]} --> {int(var.varValue)} times")

print(f"\nTotal rolls used: {int(pulp.value(master.objective))}")
