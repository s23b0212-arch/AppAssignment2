import streamlit as st
import csv
import random
import pandas as pd

# ---------------------------------------------
# READ CSV DATA
# ---------------------------------------------
def read_csv_to_dict(file_path):
    program_ratings = {}
    with open(file_path, mode='r', newline='') as file:
        reader = csv.reader(file)
        header = next(reader)
        for row in reader:
            program = row[0]
            ratings = [float(x) for x in row[1:]]
            program_ratings[program] = ratings
    return program_ratings

# Load dataset
file_path = "program_ratings.csv"
ratings = read_csv_to_dict(file_path)

# ---------------------------------------------
# STREAMLIT INTERFACE
# ---------------------------------------------
st.title("📺 TV Program Scheduling using Genetic Algorithm")
st.write("Adjust the parameters below and find the best schedule!")

GEN = st.slider("Generations (GEN)", 10, 200, 100)
POP = st.slider("Population Size (POP)", 10, 100, 50)
CO_R = st.slider("Crossover Rate (CO_R)", 0.0, 1.0, 0.8)
MUT_R = st.slider("Mutation Rate (MUT_R)", 0.0, 1.0, 0.2)
EL_S = st.slider("Elitism Size (EL_S)", 1, 5, 2)

# ---------------------------------------------
# GENETIC ALGORITHM FUNCTIONS
# ---------------------------------------------
all_programs = list(ratings.keys())
all_time_slots = list(range(6, 24))

def fitness_function(schedule):
    total_rating = 0
    for time_slot, program in enumerate(schedule):
        total_rating += ratings[program][time_slot]
    return total_rating

def crossover(schedule1, schedule2):
    crossover_point = random.randint(1, len(schedule1) - 2)
    child1 = schedule1[:crossover_point] + schedule2[crossover_point:]
    child2 = schedule2[:crossover_point] + schedule1[crossover_point:]
    return child1, child2

def mutate(schedule):
    mutation_point = random.randint(0, len(schedule) - 1)
    new_program = random.choice(all_programs)
    schedule[mutation_point] = new_program
    return schedule

def genetic_algorithm(generations, population_size, crossover_rate, mutation_rate, elitism_size):
    initial_schedule = random.sample(all_programs, len(all_programs))
    population = [initial_schedule]
    for _ in range(population_size - 1):
        random_schedule = initial_schedule.copy()
        random.shuffle(random_schedule)
        population.append(random_schedule)

    for generation in range(generations):
        new_population = []
        population.sort(key=lambda schedule: fitness_function(schedule), reverse=True)
        new_population.extend(population[:elitism_size])

        while len(new_population) < population_size:
            parent1, parent2 = random.choices(population, k=2)
            if random.random() < crossover_rate:
                child1, child2 = crossover(parent1, parent2)
            else:
                child1, child2 = parent1.copy(), parent2.copy()
            if random.random() < mutation_rate:
                child1 = mutate(child1)
            if random.random() < mutation_rate:
                child2 = mutate(child2)
            new_population.extend([child1, child2])
        population = new_population

    best = max(population, key=lambda s: fitness_function(s))
    return best, fitness_function(best)

# ---------------------------------------------
# RUN GA
# ---------------------------------------------
if st.button("Run Genetic Algorithm"):
    with st.spinner("Running optimization..."):
        best_schedule, total_rating = genetic_algorithm(GEN, POP, CO_R, MUT_R, EL_S)
        result_df = pd.DataFrame({
            "Hour": [f"{hour}:00" for hour in all_time_slots[:len(best_schedule)]],
            "Program": best_schedule
        })

        st.success("✅ Optimization Complete!")
        st.write(f"**Total Ratings:** {round(total_rating, 2)}")
        st.dataframe(result_df)
