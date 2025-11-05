import streamlit as st
import pandas as pd
import random
import csv

st.title("TV Scheduling GA App")

# ------------------ Load CSV ------------------
def load_ratings(file):
    program_ratings = {}
    reader = csv.reader(file.read().decode("utf-8").splitlines())
    header = next(reader)  # skip header
    for row in reader:
        if len(row) < 2:  # skip empty rows
            continue
        program = row[0].strip()
        ratings = [float(x) for x in row[1:]]
        program_ratings[program] = ratings
    return program_ratings

uploaded_file = st.file_uploader("Upload your program_ratings.csv", type="csv")

if uploaded_file:
    ratings = load_ratings(uploaded_file)
    all_programs = list(ratings.keys())
    all_time_slots = list(range(6, 24))  # 18 slots

    # ---------------- GA PARAMETERS ----------------
    st.sidebar.header("GA Parameters")
    CO_R = st.sidebar.slider("Crossover Rate", 0.0, 0.95, 0.8, 0.05)
    MUT_R = st.sidebar.slider("Mutation Rate", 0.01, 0.05, 0.02, 0.01)
    GEN = st.sidebar.number_input("Generations", min_value=10, max_value=500, value=100, step=10)
    POP = st.sidebar.number_input("Population Size", min_value=10, max_value=200, value=50, step=5)
    EL_S = st.sidebar.number_input("Elitism Size", min_value=1, max_value=10, value=2, step=1)

    # ---------------- GA FUNCTIONS ----------------
    def fitness(schedule):
        return sum(ratings[schedule[i]][i] for i in range(len(all_time_slots)))

    def mutate(schedule):
        idx = random.randint(0, len(schedule)-1)
        schedule[idx] = random.choice(all_programs)
        return schedule

    def crossover(s1, s2):
        point = random.randint(1, len(s1)-2)
        return s1[:point]+s2[point:], s2[:point]+s1[point:]

    def genetic_algorithm(initial):
        population = []
        for _ in range(POP):
            temp = initial.copy()
            random.shuffle(temp)
            population.append(temp)

        for _ in range(GEN):
            population.sort(key=fitness, reverse=True)
            new_pop = population[:EL_S]  # elitism
            while len(new_pop) < POP:
                p1, p2 = random.choices(population, k=2)
                c1, c2 = p1.copy(), p2.copy()
                if random.random() < CO_R:
                    c1, c2 = crossover(p1, p2)
                if random.random() < MUT_R:
                    c1 = mutate(c1)
                if random.random() < MUT_R:
                    c2 = mutate(c2)
                new_pop.extend([c1, c2])
            population = new_pop[:POP]
        best = max(population, key=fitness)
        return best[:len(all_time_slots)]

    # ---------------- RUN GA ----------------
    if st.button("Run Genetic Algorithm"):
        # initial schedule: repeat programs until 18 slots
        initial_schedule = []
        while len(initial_schedule) < len(all_time_slots):
            initial_schedule.extend(all_programs)
        initial_schedule = initial_schedule[:len(all_time_slots)]
        random.shuffle(initial_schedule)

        ga_schedule = genetic_algorithm(initial_schedule)

        schedule_df = pd.DataFrame({
            "Time Slot": [f"{h}:00" for h in all_time_slots],
            "Program": ga_schedule
        })

        st.subheader("Optimized TV Schedule")
        st.table(schedule_df)
        st.write("Total Ratings:", round(fitness(ga_schedule), 2))
