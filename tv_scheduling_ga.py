import streamlit as st
import pandas as pd
import random

# -------------------- PAGE SETTINGS --------------------
st.set_page_config(page_title="TV Program Scheduler", layout="wide")

st.markdown(
    """
    <style>
    .main-title {
        text-align: center;
        color: #1E88E5;
        font-size: 40px;
        font-weight: 800;
        margin-top: -10px;
    }
    .subtext {
        text-align: center;
        font-size: 18px;
        color: #555;
        margin-bottom: 30px;
    }
    .stButton>button {
        background-color: #1E88E5;
        color: white;
        border-radius: 10px;
        height: 3em;
        width: 100%;
        font-size: 16px;
        font-weight: 600;
    }
    .stButton>button:hover {
        background-color: #1565C0;
        color: #fff;
    }
    </style>
    <h1 class="main-title">Smart TV Scheduling using Genetic Algorithm</h1>
    <p class="subtext">Optimize your daily broadcast schedule for maximum viewer ratings</p>
    """,
    unsafe_allow_html=True
)

# -------------------- CSV UPLOAD --------------------
uploaded_file = st.file_uploader("📂 Upload your modified CSV file (program ratings)", type=["csv"])

@st.cache_data
def read_csv_to_dict(file):
    df = pd.read_csv(file)
    program_ratings = {}
    for i, row in df.iterrows():
        program_ratings[row[0]] = [float(x) for x in row[1:]]
    return program_ratings, df.columns[1:]

# -------------------- SIDEBAR PARAMETERS --------------------
st.sidebar.markdown("## ⚙️ Algorithm Parameters")
CO_R = st.sidebar.slider("Crossover Rate (CO_R)", 0.0, 0.95, 0.8, 0.01)
MUT_R = st.sidebar.slider("Mutation Rate (MUT_R)", 0.01, 0.05, 0.02, 0.01)
GEN = st.sidebar.number_input("Generations", min_value=50, max_value=500, value=100, step=10)
POP = st.sidebar.number_input("Population Size", min_value=10, max_value=200, value=50, step=10)
EL_S = 2
st.sidebar.markdown("---")
st.sidebar.info("👈 Adjust parameters and upload your CSV to begin scheduling.")

# -------------------- GA FUNCTIONS --------------------
def fitness_function(schedule, ratings):
    return sum([ratings[program][i] for i, program in enumerate(schedule)])

def initialize_population(programs, size):
    return [random.sample(programs, len(programs)) for _ in range(size)]

def crossover(s1, s2):
    point = random.randint(1, len(s1) - 2)
    return s1[:point] + s2[point:], s2[:point] + s1[point:]

def mutate(schedule, all_programs):
    new = schedule.copy()
    i = random.randint(0, len(schedule) - 1)
    new[i] = random.choice(all_programs)
    return new

def genetic_algorithm(ratings, all_programs):
    population = initialize_population(all_programs, POP)
    for _ in range(GEN):
        population = sorted(population, key=lambda s: fitness_function(s, ratings), reverse=True)
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
    return max(population, key=lambda s: fitness_function(s, ratings))

# -------------------- RUN GA --------------------
if uploaded_file:
    ratings, time_slots = read_csv_to_dict(uploaded_file)
    all_programs = list(ratings.keys())
    all_time_slots = list(time_slots)

    st.markdown("### 🎬 Run the Genetic Algorithm")
    if st.button("🚀 Generate Optimal Schedule for 3 Trials"):
        trial_results = []
        for trial in range(1, 4):
            best_schedule = genetic_algorithm(ratings, all_programs)
            total_rating = fitness_function(best_schedule, ratings)
            min_length = min(len(all_time_slots), len(best_schedule))
            df_schedule = pd.DataFrame({
                "Hour": all_time_slots[:min_length],
                "Program": best_schedule[:min_length]
            })
            trial_results.append((trial, CO_R, MUT_R, total_rating, df_schedule))
        
        for trial, co, mut, total, df in trial_results:
            st.markdown(f"### 📊 Trial {trial} - CO_R={co}, MUT_R={mut}")
            st.dataframe(df, use_container_width=True)
            st.markdown(f"**Total Viewer Rating:** `{total:.2f}`")
            st.progress(min(total / 10, 1.0))
else:
    st.warning("👆 Please upload a valid CSV file to continue.")
