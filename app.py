import streamlit as st
import pandas as pd
import csv
import random

# -------------------- CSV UPLOAD --------------------
st.title("TV Scheduling using Genetic Algorithm")

uploaded_file = st.file_uploader("Upload Program Ratings CSV", type="csv")
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("Program Ratings")
    st.dataframe(df)

    # Convert CSV to dictionary
    ratings = {}
    programs = df['Type of Program'].tolist()
    for i, row in df.iterrows():
        ratings[row['Type of Program']] = list(row[1:].astype(float))

    time_slots = list(range(6, 24))

    # -------------------- USER PARAMETERS --------------------
    st.sidebar.header("GA Parameters")
    trials = []
    for i in range(1, 4):
        st.sidebar.subheader(f"Trial {i}")
        co_r = st.sidebar.slider(f"Crossover Rate (Trial {i})", 0.0, 0.95, 0.8)
        mut_r = st.sidebar.slider(f"Mutation Rate (Trial {i})", 0.01, 0.05, 0.02)
        trials.append((co_r, mut_r))

    GEN = 100
    POP = 50
    EL_S = 2

    # -------------------- GA FUNCTIONS --------------------
    def fitness_function(schedule):
        return sum(ratings[program][i] for i, program in enumerate(schedule))

    def crossover(schedule1, schedule2):
        pt = random.randint(1, len(schedule1) - 2)
        return schedule1[:pt] + schedule2[pt:], schedule2[:pt] + schedule1[pt:]

    def mutate(schedule):
        idx = random.randint(0, len(schedule)-1)
        schedule[idx] = random.choice(list(ratings.keys()))
        return schedule

    def genetic_algorithm(initial_schedule, co_r, mut_r):
        population = [initial_schedule]
        for _ in range(POP-1):
            s = initial_schedule.copy()
            random.shuffle(s)
            population.append(s)

        for _ in range(GEN):
            population.sort(key=lambda s: fitness_function(s), reverse=True)
            new_pop = population[:EL_S]

            while len(new_pop) < POP:
                p1, p2 = random.choices(population, k=2)
                if random.random() < co_r:
                    c1, c2 = crossover(p1, p2)
                else:
                    c1, c2 = p1.copy(), p2.copy()

                if random.random() < mut_r:
                    c1 = mutate(c1)
                if random.random() < mut_r:
                    c2 = mutate(c2)

                new_pop.extend([c1, c2])

            population = new_pop[:POP]

        return population[0]

    def best_schedule_bruteforce(programs):
        # Generate all permutations (can be huge; for small sets only)
        from itertools import permutations
        best, best_score = [], 0
        for s in permutations(programs):
            score = fitness_function(s)
            if score > best_score:
                best_score, best = score, s
        return list(best)

    # -------------------- RUN TRIALS --------------------
    st.subheader("GA Trial Results")

    for i, (co_r, mut_r) in enumerate(trials, 1):
        st.write(f"**Trial {i}: CO_R={co_r}, MUT_R={mut_r}**")

        initial_best = best_schedule_bruteforce(list(ratings.keys()))
        ga_schedule = genetic_algorithm(initial_best, co_r, mut_r)

        schedule_df = pd.DataFrame({
            "Time Slot": [f"{h}:00" for h in time_slots],
            "Program": ga_schedule
        })
        st.table(schedule_df)
        st.write("Total Ratings:", round(fitness_function(ga_schedule), 2))
