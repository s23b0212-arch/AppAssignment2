import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="TV Program Scheduler", layout="wide") #set page title

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
    <h1 class="main-title"> Smart TV Scheduling using Genetic Algorithm</h1>
    <p class="subtext">Optimize your daily broadcast schedule for maximum viewer ratings</p>
    """, #title
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader("📂 Upload your modified CSV file (program ratings)", type=["csv"])

@st.cache_data
def read_csv_to_dict(file): #function to read the csv file
    df = pd.read_csv(file)
    program_ratings = {}
    for i, row in df.iterrows():
        program_ratings[row[0]] = [float(x) for x in row[1:]]
    return program_ratings, df.columns[1:]

st.sidebar.markdown("## ⚙️ Algorithm Parameters")
#user input with default rate
CO_R = st.sidebar.slider("Crossover Rate (CO_R)", 0.0, 0.95, 0.8, 0.01)
MUT_R = st.sidebar.slider("Mutation Rate (MUT_R)", 0.01, 0.05, 0.02, 0.01)
GEN = st.sidebar.number_input("Generations", min_value=50, max_value=500, value=100, step=10)
POP = st.sidebar.number_input("Population Size", min_value=10, max_value=200, value=50, step=10)
EL_S = 2

st.sidebar.markdown("---")
st.sidebar.info("👈 Adjust parameters and upload your CSV to begin scheduling.")
#code to function
if uploaded_file:
    ratings, time_slots = read_csv_to_dict(uploaded_file)
    all_programs = list(ratings.keys())
    all_time_slots = list(range(len(time_slots)))
    
    def fitness_function(schedule):
        total = 0
        for i, program in enumerate(schedule):
            total += ratings[program][i]
        return total

    def initialize_population(programs, size):
        return [random.sample(programs, len(programs)) for _ in range(size)]

    def crossover(s1, s2):
        point = random.randint(1, len(s1) - 2)
        return s1[:point] + s2[point:], s2[:point] + s1[point:]

    def mutate(schedule):
        new = schedule.copy()
        i = random.randint(0, len(schedule) - 1)
        new[i] = random.choice(all_programs)
        return new

    def genetic_algorithm():
        population = initialize_population(all_programs, POP)
        for _ in range(GEN):
            population = sorted(population, key=fitness_function, reverse=True)
            new_pop = population[:EL_S]
            while len(new_pop) < POP:
                p1, p2 = random.choices(population[:10], k=2)
                if random.random() < CO_R:
                    c1, c2 = crossover(p1, p2)
                else:
                    c1, c2 = p1.copy(), p2.copy()
                if random.random() < MUT_R:
                    c1 = mutate(c1)
                new_pop.extend([c1, c2])
            population = new_pop
        return max(population, key=fitness_function)

    st.markdown("### 🎬 Run the Genetic Algorithm") #button to run
    if st.button("🚀 Generate Optimal Schedule"):
        best_schedule = genetic_algorithm()
        total_rating = fitness_function(best_schedule)

        min_length = min(len(time_slots), len(best_schedule))
        time_slots = list(time_slots)[:min_length]
        best_schedule = best_schedule[:min_length]

        result_df = pd.DataFrame({
            "Hour": time_slots,
            "Program": best_schedule
        })

        c1, c2 = st.columns(2) #display result
        c1.metric("🔁 Crossover Rate", f"{CO_R:.2f}")
        c2.metric("🎲 Mutation Rate", f"{MUT_R:.2f}")
        st.success("✅ Optimal schedule successfully generated!")

        with st.expander("📋 View Generated Schedule"):
            st.dataframe(result_df, use_container_width=True)

        st.markdown(f"### ⭐ Total Viewer Rating: `{total_rating:.2f}`")
        st.progress(min(total_rating / 10, 1.0))
else:
    st.warning("👆 Please upload a valid CSV file to continue.")
