import streamlit as st
import pandas as pd
import random

# --- PAGE SETUP ---
st.set_page_config(page_title="Ultimate TV Scheduler", layout="wide")

# --- STYLING ---
st.markdown("""
<style>
.main-title {
    text-align: center;
    color: #FF5722;
    font-size: 42px;
    font-weight: 900;
}
.subtext {
    text-align: center;
    font-size: 18px;
    color: #333;
    margin-bottom: 25px;
}
.stButton>button {
    background-color: #FF5722;
    color: white;
    border-radius: 10px;
    height: 3em;
    width: 100%;
    font-size: 16px;
    font-weight: 600;
}
.stButton>button:hover {
    background-color: #E64A19;
    color: #fff;
}
</style>
<h1 class="main-title">📺 Ultimate TV Scheduler GA</h1>
<p class="subtext">Maximize your viewers' happiness with optimized scheduling</p>
""", unsafe_allow_html=True)

# --- CSV UPLOAD ---
uploaded_file = st.file_uploader("📂 Upload your modified CSV file (program ratings)", type=["csv"])

@st.cache_data
def read_csv_to_dict(file):
    df = pd.read_csv(file)
    ratings = {}
    for i, row in df.iterrows():
        ratings[row[0]] = [float(x) for x in row[1:]]
    return ratings, df.columns[1:]

# --- SIDEBAR PARAMETERS ---
st.sidebar.markdown("## ⚙️ Genetic Algorithm Parameters")
CO_R = st.sidebar.slider("Crossover Rate", 0.0, 0.95, 0.8, 0.01)
MUT_R = st.sidebar.slider("Mutation Rate", 0.01, 0.05, 0.02, 0.01)
GEN = st.sidebar.number_input("Generations", 50, 500, 100, 10)
POP = st.sidebar.number_input("Population Size", 10, 200, 50, 10)
EL_S = 2
st.sidebar.markdown("---")
st.sidebar.info("👈 Adjust parameters and upload CSV to start scheduling.")

# --- FUNCTIONS ---
if uploaded_file:
    ratings, time_slots = read_csv_to_dict(uploaded_file)
    all_programs = list(ratings.keys())
    hours = list(time_slots)

    def fitness(schedule):
        return sum([ratings[program][i] for i, program in enumerate(schedule)])

    def init_population(size):
        return [random.sample(all_programs, len(all_programs)) for _ in range(size)]

    def crossover(p1, p2):
        point = random.randint(1, len(p1)-2)
        return p1[:point]+p2[point:], p2[:point]+p1[point:]

    def mutate(schedule):
        s = schedule.copy()
        i = random.randint(0, len(s)-1)
        s[i] = random.choice(all_programs)
        return s

    def genetic_algorithm():
        pop = init_population(POP)
        for _ in range(GEN):
            pop = sorted(pop, key=fitness, reverse=True)
            new_pop = pop[:EL_S]
            while len(new_pop) < POP:
                p1, p2 = random.choices(pop[:10], k=2)
                c1, c2 = (p1.copy(), p2.copy())
                if random.random() < CO_R:
                    c1, c2 = crossover(p1, p2)
                if random.random() < MUT_R:
                    c1 = mutate(c1)
                    c2 = mutate(c2)
                new_pop.extend([c1, c2])
            pop = new_pop
        top_schedules = sorted(pop, key=fitness, reverse=True)[:3]
        return top_schedules

    # --- RUN BUTTON ---
    st.markdown("### 🎬 Generate Optimal Schedule")
    if st.button("🚀 Run Genetic Algorithm"):
        top_schedules = genetic_algorithm()
        for idx, sched in enumerate(top_schedules, start=1):
            total = fitness(sched)
            st.markdown(f"### 🏆 Top {idx} Schedule | Total Rating: {total:.2f}")
            df = pd.DataFrame({
                "Hour": hours[:len(sched)],
                "Program": sched[:len(hours)]
            })
            st.dataframe(df, use_container_width=True)
            # Bar chart of ratings
            ratings_list = [ratings[prog][i] for i, prog in enumerate(sched)]
            st.bar_chart(pd.DataFrame({"Ratings": ratings_list}, index=df["Hour"]))
else:
    st.warning("👆 Please upload a valid CSV file to continue.")
