
import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="TV Scheduling GA", layout="wide")
st.title("TV Scheduling using Genetic Algorithm")

# -------------------- FILE UPLOAD --------------------
uploaded_file = st.file_uploader("Upload your program ratings CSV", type=["csv"])
if uploaded_file is not None:
    try:
        # Read CSV
        df = pd.read_csv(uploaded_file)
        st.subheader("Uploaded Ratings Data")
        st.dataframe(df)
        
        # Convert CSV to dict
        ratings = {}
        time_slots = [f"Hour {i}" for i in range(6, 24)]
        for _, row in df.iterrows():
            ratings[row[0]] = [float(row[h]) for h in time_slots]

        all_programs = list(ratings.keys())

    except Exception as e:
        st.error(f"Error reading CSV: {e}")
        st.stop()
else:
    st.warning("Please upload a CSV file to continue.")
    st.stop()

# -------------------- GA PARAMETERS --------------------
st.sidebar.header("Genetic Algorithm Parameters")

CO_R = st.sidebar.slider("Crossover Rate (CO_R)", 0.0, 0.95, 0.8, 0.01)
MUT_R = st.sidebar.slider("Mutation Rate (MUT_R)", 0.01, 0.05, 0.02, 0.01)
GEN = st.sidebar.number_input("Generations", min_value=10, max_value=500, value=100, step=10)
POP = st.sidebar.number_input("Population Size", min_value=10, max_value=200, value=50, step=5)
EL_S = st.sidebar.number_input("Elitism Size", min_value=1, max_value=10, value=2, step=1)

# -------------------- GA FUNCTIONS --------------------
def fitness_function(schedule):
    return sum(ratings[program][i] for i, program in enumerate(schedule))

def crossover(s1, s2):
    point = random.randint(1, len(s1) - 2)
    return s1[:point] + s2[point:], s2[:point] + s1[point:]

def mutate(schedule):
    idx = random.randint(0, len(schedule) - 1)
    schedule[idx] = random.choice(all_programs)
    return schedule

def genetic_algorithm(initial_schedule, generations=GEN, population_size=POP,
                      crossover_rate=CO_R, mutation_rate=MUT_R, elitism_size=EL_S):
    
    # Initialize population
    population = [initial_schedule.copy()]
    for _ in range(population_size - 1):
        temp = initial_schedule.copy()
        random.shuffle(temp)
        population.append(temp)
    
    for _ in range(generations):
        # Sort by fitness
        population.sort(key=fitness_function, reverse=True)
        new_population = population[:elitism_size]  # elitism

        while len(new_population) < population_size:
            parent1, parent2 = random.choices(population, k=2)
            if random.random() < crossover_rate:
                child1, child2 = crossover(parent1.copy(), parent2.copy())
            else:
                child1, child2 = parent1.copy(), parent2.copy()

            if random.random() < mutation_rate:
                child1 = mutate(child1)
            if random.random() < mutation_rate:
                child2 = mutate(child2)

            new_population.extend([child1, child2])

        population = new_population[:population_size]

    return population[0]

# -------------------- RUN GA --------------------
if st.button("Run Genetic Algorithm"):
    # Initial schedule (random)
    initial_schedule = all_programs.copy()
    random.shuffle(initial_schedule)

    best_schedule = genetic_algorithm(initial_schedule)
    
    # Display schedule
    schedule_df = pd.DataFrame({
        "Time Slot": [f"{h}:00" for h in range(6, 24)],
        "Program": best_schedule
    })
    
    st.subheader("Optimal Schedule")
    st.dataframe(schedule_df)

    st.write("Total Ratings:", round(fitness_function(best_schedule), 2))
