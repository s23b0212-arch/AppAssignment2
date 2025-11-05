# Streamlit TV Scheduling GA App
import streamlit as st
import pandas as pd
import csv
import random

st.title("TV Scheduling Optimization Using Genetic Algorithm")
st.markdown("Adjust GA parameters in the sidebar and see optimized TV schedules.")

# ------------------- Sidebar -------------------
st.sidebar.header("GA Parameters")
co_r = st.sidebar.slider("Crossover Rate (CO_R)", 0.0, 0.95, 0.8, 0.05)
mut_r = st.sidebar.slider("Mutation Rate (MUT_R)", 0.01, 0.05, 0.02, 0.01)
trials = st.sidebar.number_input("Number of Trials", min_value=1, max_value=5, value=3)

# ------------------- Read CSV -------------------
@st.cache_data
def read_csv_to_dict(file_path):
    program_ratings = {}
    with open(file_path, mode='r', newline='') as file:
        reader = csv.reader(file)
        header = next(reader)  # skip header
        for row in reader:
            program = row[0]
            ratings = [float(x) for x in row[1:]]
            program_ratings[program] = ratings
    return program_ratings

file_path = 'program_ratings.csv'  # Upload your CSV in the same folder
ratings = read_csv_to_dict(file_path)
all_programs = list(ratings.keys())
all_time_slots = list(range(6, 24))

# ------------------- GA Functions -------------------
GEN = 100
POP = 50
EL_S = 2

def fitness_function(schedule):
    total_rating = 0
    for time_slot, program in enumerate(schedule):
        total_rating += ratings[program][time_slot]
    return total_rating

def initialize_pop(programs, time_slots):
    if not programs:
        return [[]]
    all_schedules = []
    for i in range(len(programs)):
        for schedule in initialize_pop(programs[:i] + programs[i + 1:], time_slots):
            all_schedules.append([programs[i]] + schedule)
    return all_schedules

def finding_best_schedule(all_schedules):
    best_schedule = []
    max_ratings = 0
    for schedule in all_schedules:
        total_ratings = fitness_function(schedule)
        if total_ratings > max_ratings:
            max_ratings = total_ratings
            best_schedule = schedule
    return best_schedule

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

def genetic_algorithm(initial_schedule, generations=GEN, population_size=POP, crossover_rate=co_r, mutation_rate=mut_r, elitism_size=EL_S):
    population = [initial_schedule]
    for _ in range(population_size - 1):
        random_schedule = initial_schedule.copy()
        random.shuffle(random_schedule)
        population.append(random_schedule)

    for generation in range(generations):
        new_population = []
        population.sort(key=lambda s: fitness_function(s), reverse=True)
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

    return population[0]

# ------------------- Run GA -------------------
all_possible_schedules = initialize_pop(all_programs, all_time_slots)
initial_best_schedule = finding_best_schedule(all_possible_schedules)

st.header("Optimized Schedules")
ratings_list = []

for t in range(trials):
    ga_schedule = genetic_algorithm(initial_best_schedule)
    
    # Adjust schedule length
    if len(ga_schedule) < len(all_time_slots):
        ga_schedule += ga_schedule[:len(all_time_slots) - len(ga_schedule)]
    elif len(ga_schedule) > len(all_time_slots):
        ga_schedule = ga_schedule[:len(all_time_slots)]

    schedule_df = pd.DataFrame({
        "Time Slot": [f"{h}:00" for h in all_time_slots],
        "Program": ga_schedule
    })

    st.subheader(f"Trial {t+1}")
    st.table(schedule_df)
    total = fitness_function(ga_schedule)
    st.write("Total Ratings:", total)
    ratings_list.append(total)

# ------------------- Bar Chart -------------------
st.header("Total Ratings Across Trials")
st.bar_chart(pd.DataFrame({"Total Ratings": ratings_list}, index=[f"Trial {i+1}" for i in range(trials)]))

# ------------------- Optional: Color-coded Table -------------------
def color_program(program):
    colors = {
        "news": "background-color: lightblue",
        "live_soccer": "background-color: lightgreen",
        "movie_a": "background-color: lightpink",
        "movie_b": "background-color: lightyellow",
        "reality_show": "background-color: lightgray",
        "tv_series_a": "background-color: lightcoral",
        "tv_series_b": "background-color: lightcyan",
        "music_program": "background-color: lightgoldenrodyellow",
        "documentary": "background-color: lightsteelblue",
        "Boxing": "background-color: lightsalmon"
    }
    return colors.get(program, "")

st.subheader("Trial 1 Color-coded Schedule")
st.dataframe(schedule_df.style.applymap(color_program, subset=['Program']))
