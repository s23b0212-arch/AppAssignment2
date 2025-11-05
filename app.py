import streamlit as st
import pandas as pd
import random
import csv

# ------------------ Load CSV ------------------
@st.cache_data
def load_ratings(file_path):
    program_ratings = {}
    with open(file_path, mode='r', newline='') as file:
        reader = csv.reader(file)
        header = next(reader)  # skip header
        for row in reader:
            program = row[0]
            ratings = [float(x) for x in row[1:]]
            program_ratings[program] = ratings
    return program_ratings

st.title("TV Scheduling GA App")

uploaded_file = st.file_uploader("Upload your program_ratings.csv", type="csv")
if uploaded_file:
    ratings = load_ratings(uploaded_file)
    all_programs = list(ratings.keys())
    all_time_slots = list(range(6, 24))  # Hour 6 -> 23

    # ---------------- GA PARAMETERS ----------------
    st.sidebar.header("Genetic Algorithm Parameters")
    CO_R = st.sidebar.slider("Crossover Rate", 0.0, 0.95, 0.8, 0.05)
    MUT_R = st.sidebar.slider("Mutation Rate", 0.01, 0.05, 0.02, 0.01)
    GEN = st.sidebar.number_input("Generations", min_value=10, max_value=500, value=100, step=10)
    POP = st.sidebar.number_input("Population Size", min_value=10, max_value=200, value=50, step=5)
    EL_S = st.sidebar.number_input("Elitism Size", min_value=1, max_value=10, value=2, step=1)

    # ------------------ FUNCTIONS ------------------
    def fitness_function(schedule):
        return sum(ratings[program][i] for i, program in enumerate(schedule))

    def mutate(schedule):
        idx = random.randint(0, len(schedule)-1)
        schedule[idx] = random.choice(all_programs)
        return schedule

    def crossover(s1, s2):
        point = random.randint(1, len(s1)-2)
        return s1[:point]+s2[point:], s2[:point]+s1[point:]

    def genetic_algorithm(initial_schedule):
        population = [initial_schedule]
        for _ in range(POP-1):
            temp = initial_schedule.copy()
            random.shuffle(temp)
            population.append(temp)

        for _ in range(GEN):
            new_pop = []
            population.sort(key=fitness_function, reverse=True)
            new_pop.extend(population[:EL_S])

            while len(new_pop) < POP:
                p1, p2 = random.choices(population, k=2)
                c1, c2 = (p1.copy(), p2.copy())
                if random.random() < CO_R:
                    c1, c2 = crossover(p1, p2)
                if random.random() < MUT_R:
                    c1 = mutate(c1)
                if random.random() < MUT_R:
                    c2 = mutate(c2)
                new_pop.extend([c1, c2])
            population = new_pop[:POP]

        best = max(population, key=fitness_function)
        return best[:len(all_time_slots)]  # trim to correct length

    # ------------------ INITIAL SCHEDULE ------------------
    initial_schedule = []
    while len(initial_schedule) < len(all_time_slots):
        initial_schedule.extend(all_programs)
    initial_schedule = initial_schedule[:len(all_time_slots)]
    random.shuffle(initial_schedule)

    # ------------------ RUN GA ------------------
    if st.button("Run Genetic Algorithm"):
        ga_schedule = genetic_algorithm(initial_schedule)

        schedule_df = pd.DataFrame({
            "Time Slot": [f"{h}:00" for h in all_time_slots],
            "Program": ga_schedule
        })
        st.subheader("Optimized TV Schedule")
        st.table(schedule_df)
        st.write("Total Ratings:", round(fitness_function(ga_schedule), 2))
