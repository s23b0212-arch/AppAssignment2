import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="TV Scheduling GA", layout="centered")
st.title("📺 TV Program Scheduling using Genetic Algorithm")

# -------------------- UPLOAD CSV --------------------
uploaded_file = st.file_uploader("Upload CSV file with program ratings", type=["csv"])
if uploaded_file is None:
    st.warning("Please upload a CSV file to continue.")
    st.stop()

# -------------------- READ CSV --------------------
def read_csv_to_dict(file):
    reader = pd.read_csv(file)
    program_ratings = {}
    for idx, row in reader.iterrows():
        program = row[0]
        ratings = [float(x) for x in row[1:]]
        program_ratings[program] = ratings
    return program_ratings

ratings = read_csv_to_dict(uploaded_file)
all_programs = list(ratings.keys())
all_time_slots = list(range(6, 24))

# -------------------- SLIDERS FOR PARAMETERS --------------------
st.sidebar.header("Genetic Algorithm Parameters")
CO_R = st.sidebar.slider("Crossover Rate", min_value=0.0, max_value=0.95, value=0.8, step=0.01)
MUT_R = st.sidebar.slider("Mutation Rate", min_value=0.01, max_value=0.05, value=0.02, step=0.01)
GEN = st.sidebar.number_input("Number of Generations", min_value=10, max_value=500, value=100, step=10)
POP = st.sidebar.number_input("Population Size", min_value=10, max_value=100, value=50, step=5)
EL_S = st.sidebar.number_input("Elitism Size", min_value=1, max_value=10, value=2, step=1)

# -------------------- FITNESS FUNCTION --------------------
def fitness_function(schedule):
    return sum(ratings[program][i] for i, program in enumerate(schedule))

# -------------------- INITIAL POPULATION --------------------
def initialize_pop(programs):
    all_schedules = []
    def permute(progs):
        if not progs:
            return [[]]
        result = []
        for i in range(len(progs)):
            for p in permute(progs[:i]+progs[i+1:]):
                result.append([progs[i]] + p)
        return result
    return permute(programs)

def finding_best_schedule(all_schedules):
    best_schedule = []
    max_rating = 0
    for s in all_schedules:
        f = fitness_function(s)
        if f > max_rating:
            max_rating = f
            best_schedule = s
    return best_schedule

# -------------------- GENETIC ALGORITHM --------------------
def crossover(s1, s2):
    point = random.randint(1, len(s1)-2)
    return s1[:point]+s2[point:], s2[:point]+s1[point:]

def mutate(schedule):
    idx = random.randint(0, len(schedule)-1)
    schedule[idx] = random.choice(all_programs)
    return schedule

def genetic_algorithm(initial_schedule, generations=GEN, population_size=POP, crossover_rate=CO_R, mutation_rate=MUT_R, elitism_size=EL_S):
    population = [initial_schedule.copy()]
    for _ in range(population_size-1):
        temp = initial_schedule.copy()
        random.shuffle(temp)
        population.append(temp)
    
    for _ in range(generations):
        new_pop = []
        population.sort(key=lambda s: fitness_function(s), reverse=True)
        new_pop.extend(population[:elitism_size])
        
        while len(new_pop) < population_size:
            p1, p2 = random.choices(population, k=2)
            if random.random() < crossover_rate:
                c1, c2 = crossover(p1, p2)
            else:
                c1, c2 = p1.copy(), p2.copy()
            if random.random() < mutation_rate:
                c1 = mutate(c1)
            if random.random() < mutation_rate:
                c2 = mutate(c2)
            new_pop.extend([c1, c2])
        population = new_pop[:population_size]
    return population[0]

# -------------------- RUN GA --------------------
all_possible_schedules = initialize_pop(all_programs)
initial_best = finding_best_schedule(all_possible_schedules)
rem_slots = len(all_time_slots) - len(initial_best)
ga_schedule = genetic_algorithm(initial_best)
final_schedule = initial_best + ga_schedule[:rem_slots]

# -------------------- DISPLAY RESULTS --------------------
st.subheader("✅ Final Optimal Schedule")
schedule_df = pd.DataFrame({
    "Time Slot": [f"{h}:00" for h in all_time_slots],
    "Program": final_schedule
})
st.table(schedule_df)

st.write("**Total Ratings:**", fitness_function(final_schedule))
