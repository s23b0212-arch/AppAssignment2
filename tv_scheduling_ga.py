import streamlit as st
import pandas as pd
import random
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="TV Program Scheduler", layout="wide")

# --- PAGE HEADER ---
st.markdown("""
    <h1 style='text-align:center; color:#1E88E5; font-size:45px;'>Smart TV Scheduler</h1>
    <p style='text-align:center; color:#555; font-size:18px;'>Optimize your daily broadcast schedule with Genetic Algorithm</p>
""", unsafe_allow_html=True)

# --- CSV UPLOAD ---
uploaded_file = st.file_uploader("📂 Upload your CSV file with program ratings", type=["csv"])

# --- SIDEBAR PARAMETERS ---
st.sidebar.header("⚙️ GA Parameters")
CO_R = st.sidebar.slider("Crossover Rate", 0.0, 0.95, 0.8, 0.01)
MUT_R = st.sidebar.slider("Mutation Rate", 0.01, 0.05, 0.02, 0.01)
GEN = st.sidebar.number_input("Generations", 50, 500, 100, 10)
POP = st.sidebar.number_input("Population Size", 10, 200, 50, 10)
EL_S = 2

st.sidebar.markdown("---")
st.sidebar.info("👈 Adjust parameters and upload your CSV to begin scheduling.")

# --- CSV TO DICT ---
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
        
        # trim if mismatch
        min_len = min(len(schedule), len(time_slots))
        schedule = schedule[:min_len]
        time_slots_trim = time_slots[:min_len]
        df_result = pd.DataFrame({"Hour": time_slots_trim, "Program": schedule})

        # --- COLORS FOR PROGRAMS ---
        program_colors = {
            "news":"#FFCDD2",
            "live_soccer":"#C5E1A5",
            "movie_a":"#BBDEFB",
            "movie_b":"#FFE082",
            "reality_show":"#F8BBD0",
            "tv_series_a":"#B2EBF2",
            "tv_series_b":"#D1C4E9",
            "music_program":"#FFF59D",
            "documentary":"#A7FFEB",
            "Boxing":"#FFAB91"
        }

        def highlight_program(prog):
            return [f'background-color: {program_colors.get(prog, "#E0E0E0")}' for prog in df_result["Program"]]

        # --- DISPLAY ---
        c1, c2 = st.columns(2)
        c1.metric("🔁 Crossover Rate", f"{CO_R:.2f}")
        c2.metric("🎲 Mutation Rate", f"{MUT_R:.2f}")
        st.success("✅ Optimal schedule generated!")

        with st.expander("📋 View Schedule"):
            st.dataframe(df_result.style.apply(highlight_program, axis=1), use_container_width=True)

        # --- BAR CHART ---
        rating_values = [ratings[prog][i] for i, prog in enumerate(schedule)]
        fig, ax = plt.subplots(figsize=(10,4))
        sns.barplot(x=time_slots_trim, y=rating_values, palette=list(program_colors.get(p, "#E0E0E0") for p in schedule), ax=ax)
        ax.set_ylabel("Viewer Rating")
        ax.set_xlabel("Hour")
        ax.set_title("Viewer Ratings per Time Slot")
        st.pyplot(fig)

        st.markdown(f"### ⭐ Total Viewer Rating: `{total_rating:.2f}`")
        st.progress(min(total_rating / 10, 1.0))

else:
    st.warning("👆 Please upload a valid CSV file to continue.")
