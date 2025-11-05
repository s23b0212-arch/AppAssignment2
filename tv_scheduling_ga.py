# ==========================================
# TV Scheduling using Genetic Algorithm
# ==========================================

import csv
import random
import pandas as pd

# -----------------------------
# STEP 1: Read CSV
# -----------------------------
def read_csv_to_dict(file_path):
    """
    Reads a CSV file and converts it to a dictionary.
    CSV must have program types as the first column and ratings in subsequent columns.
    """
    df = pd.read_csv(file_path, index_col=0)  # first column = program name
    program_ratings_dict = df.to_dict(orient='index')
    
    # Convert inner dict values to list of floats
    for program in program_ratings_dict:
        program_ratings_dict[program] = [float(v) for v in program_ratings_dict[program].values()]
    
    return program_ratings_dict

# -----------------------------
# STEP 2: GA PARAMETERS
# -----------------------------
GEN = 100         # generations
POP = 50          # population size
CO_R = 0.8        # crossover rate
MUT_R = 0.2       # mutation rate
EL_S = 2          # elitism size

# -----------------------------
# STEP 3: FITNESS FUNCTION
# -----------------------------
def fitness_function(schedule, ratings_dict):
    total_rating = 0
    for time_slot, program in enumerate(schedule):
        total_rating += ratings_dict[program][time_slot]
    return total_rating

# -----------------------------
# STEP 4: INITIAL POPULATION
# -----------------------------
def initialize_population(programs, population_size):
    population = []
    base_schedule = programs.copy()
    for _ in range(population_size):
        random.shuffle(base_schedule)
        population.append(base_schedule.copy())
    return population

# -----------------------------
# STEP 5: SELECTION - BEST SCHEDULE
# -----------------------------
def finding_best_schedule(all_schedules, ratings_dict):
    best_schedule = []
    max_ratings = -1
    for schedule in all_schedules:
        total_ratings = fitness_function(schedule, ratings_dict)
        if total_ratings > max_ratings:
            max_ratings = total_ratings
            best_schedule = schedule
    return best_schedule

# -----------------------------
# STEP 6: GA OPERATORS
# -----------------------------
def crossover(schedule1, schedule2):
    point = random.randint(1, len(schedule1) - 2)
    child1 = schedule1[:point] + schedule2[point:]
    child2 = schedule2[:point] + schedule1[point:]
    return child1, child2

def mutate(schedule, all_programs):
    point = random.randint(0, len(schedule) - 1)
    new_program = random.choice(all_programs)
    schedule[point] = new_program
    return schedule

# -----------------------------
# STEP 7: GENETIC ALGORITHM
# -----------------------------
def genetic_algorithm(initial_schedule, ratings_dict, generations=GEN, population_size=POP, crossover_rate=CO_R, mutation_rate=MUT_R, elitism_size=EL_S):
    all_programs = initial_schedule.copy()
    population = initialize_population(initial_schedule, population_size)
    
    for _ in range(generations):
        new_population = []
        
        # Elitism
        population.sort(key=lambda s: fitness_function(s, ratings_dict), reverse=True)
        new_population.extend(population[:elitism_size])
        
        while len(new_population) < population_size:
            parent1, parent2 = random.choices(population, k=2)
            
            if random.random() < crossover_rate:
                child1, child2 = crossover(parent1, parent2)
            else:
                child1, child2 = parent1.copy(), parent2.copy()
            
            if random.random() < mutation_rate:
                child1 = mutate(child1, all_programs)
            if random.random() < mutation_rate:
                child2 = mutate(child2, all_programs)
            
            new_population.extend([child1, child2])
        
        population = new_population[:population_size]
    
    # Return best schedule
    return finding_best_schedule(population, ratings_dict)

# -----------------------------
# STEP 8: MAIN EXECUTION
# -----------------------------
if __name__ == "__main__":
    # Replace with your CSV file path
    file_path = "program_ratings.csv"
    
    # Load ratings
    ratings_dict = read_csv_to_dict(file_path)
    
    all_programs = list(ratings_dict.keys())
    all_time_slots = list(range(6, 24))  # 6:00 to 23:00
    
    # Run GA
    best_schedule = genetic_algorithm(all_programs, ratings_dict)
    
    # Display results
    print("\nFinal Optimal Schedule:")
    for i, program in enumerate(best_schedule):
        print(f"Time Slot {all_time_slots[i]:02d}:00 - Program {program}")
    
    print("Total Ratings:", fitness_function(best_schedule, ratings_dict))
