import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="TV Program Scheduler", layout="wide")

# --- HEADER ---
st.markdown("""
    <h1 style='text-align:center; color:#1E88E5; font-size:45px;'>TV Program Scheduler</h1>
    <p style='text-align:center; color:#555; font-size:18px;'>Optimize your broadcast schedule for maximum viewer ratings using Genetic Algorithm</p>
""", unsafe_allow_html=True)

# --- FILE UPLOAD ---
uploaded_file = st.file_uploader("📂 Upload your CSV file with program ratings", type=["csv"])

# --- SIDEBAR PARAMETERS ---
st.sidebar.header("⚙️ GA Parameters")
CO_R = st.sidebar.slider("Crossover Rate", 0.0, 0.95, 0.8, 0.01)
MUT_R = st.sidebar.slider("Mutation Rate", 0.01, 0.05, 0.02, 0.01)
GEN = st.sidebar.number_input("Generations", 50, 500, 100, 10)
POP = st.sidebar.number_input("Population Size", 10, 200, 50, 10)
EL_S = 2
st.sidebar.info("Adjust parameters and upload your CSV to start scheduling.")

# --- READ CSV ---
@st.cache_data
def read_csv(file):
    df = pd.read_csv(file)
    ratings = {row[0]: [float(x) for x in row[1:]] for _, row in df.iterrows()}
    time_slots = df.columns[1:]
    return ratings, list(time_slots)

# --- FITNESS FUNCTION ---
def fitness(schedule, ratings):
    return sum(ratings[prog][i] for i, prog in enumerate(schedule))

# --- GA FUNCTIONS ---
def initialize_population(programs, size):
    return [random.sample(programs, len(programs)) for _ in range(size)]

def crossover(p1, p2):
    point = random.randint(1, len(p1)-2)
    return p1[:point] + p2[point:], p2[:point] + p1[point:]

def mutate(schedule, all_programs):
    i = random.randint(0, len(schedule)-1)
    schedule[i] = random.choice(all_programs)
    return schedule

def genetic_algorithm(all_programs, ratings):
    population = initialize_population(all_programs, POP)
    for _ in range(GEN):
        population = sorted(population, key=lambda s: fitness(s, ratings), reverse=True)
        new_pop = population[:EL_S]
        while len(new_pop) < POP:
            p1, p2 = random.choices(population[:10], k=2)
            if random.random() < CO_R:
                c1, c2 = crossover(p1, p2)
            else:
                c1, c2 = p1.copy(), p2.copy()
            if random.random() < MUT_R:
                c1 = mutate(c1, all_programs)
            if random.random() < MUT_R:
                c2 = mutate(c2, all_programs)
            new_pop.extend([c1, c2])
        population = new_pop
    return max(population, key=lambda s: fitness(s, ratings))

# --- RUN GA ---
if uploaded_file:
    ratings, time_slots = read_csv(uploaded_file)
    all_programs = list(ratings.keys())
    
    if st.button("🚀 Generate Optimal Schedule"):
        schedule = genetic_algorithm(all_programs, ratings)
        total_rating = fitness(schedule, ratings)

        # Trim if mismatch
        min_len = min(len(schedule), len(time_slots))
        schedule = schedule[:min_len]
        time_slots_trim = time_slots[:min_len]

        # Result DataFrame
        df_result = pd.DataFrame({"Hour": time_slots_trim, "Program": schedule})

        # --- COLORFUL STYLING ---
        colors = ["#FFCDD2","#C5E1A5","#BBDEFB","#FFE082","#F8BBD0","#B2EBF2",
                  "#D1C4E9","#FFF59D","#A7FFEB","#FFAB91"]
        program_colors = {prog: colors[i % len(colors)] for i, prog in enumerate(all_programs)}

        def highlight_row(prog):
            return [f'background-color: {program_colors.get(prog, "#E0E0E0")}' for prog in df_result["Program"]]

        # --- DISPLAY RESULTS ---
        st.success(f"✅ Optimal schedule generated! Total Rating: {total_rating:.2f}")
        st.dataframe(df_result.style.apply(highlight_row, axis=1), use_container_width=True)

else:
    st.info("👆 Upload your CSV file to start scheduling.")
