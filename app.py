import streamlit as st
import random

# Example fitness function
def fitness(x):
    return x**2

# Simple Genetic Algorithm Example
def genetic_algorithm(pop_size, generations, CO_R, MUT_R):
    population = [random.uniform(-10, 10) for _ in range(pop_size)]

    for gen in range(generations):
        # Sort by fitness
        population = sorted(population, key=lambda x: -fitness(x))
        next_gen = population[:2]

        while len(next_gen) < pop_size:
            p1, p2 = random.sample(population[:10], 2)

            # Crossover
            if random.random() < CO_R:
                child = (p1 + p2) / 2
            else:
                child = p1

            # Mutation
            if random.random() < MUT_R:
                child += random.uniform(-1, 1)

            next_gen.append(child)

        population = next_gen

    best = max(population, key=fitness)
    return best

# Streamlit Interface
st.title("🌿 Genetic Algorithm Optimizer")
st.write("Adjust crossover and mutation rates to test performance.")

# User Inputs
CO_R = st.slider("Crossover Rate (CO_R)", 0.0, 0.95, 0.8)
MUT_R = st.slider("Mutation Rate (MUT_R)", 0.01, 0.05, 0.02)

# Run Button
if st.button("Run Algorithm"):
    best = genetic_algorithm(10, 20, CO_R, MUT_R)
    st.success(f"Best result: {best}")
