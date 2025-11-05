import streamlit as st
import pandas as pd
import random

# ------------------- PAGE CONFIG -------------------
st.set_page_config(page_title="Charu TV Scheduler", layout="wide")
st.markdown(
"""
<h1 style='text-align:center; color:#e63946; font-size:44px;'>📺 Charu TV Scheduler</h1>
<p style='text-align:center; color:#555; font-size:18px;'>Optimize broadcast schedule with Genetic Algorithm</p>
""", unsafe_allow_html=True
)

# ------------------- CSV UPLOAD -------------------
uploaded_file = st.file_uploader("Upload your program ratings CSV", type=["csv"])

@st.cache_data
def load_ratings(file):
    df = pd.read_csv(file)
    ratings = {row[0]: [float(x) for x in row[1:]] for _, row in df.iterrows()}
    return ratings, df.columns[1:]

# ------------------- GA PARAMETERS -------------------
if uploaded_file:
    ratings, time_slots = load_ratings(uploaded_file)
    programs = list(ratings.keys())
    hours = list(time_slots)

    with st.expander("⚙️ Adjust Genetic Algorithm Parameters"):
        CO_R = st.slider("Crossover Rate", 0.0, 0.95, 0.75, 0.01)
        MUT_R = st.slider("Mutation Rate", 0.01, 0.05, 0.02, 0.01)
        POP = st.number_input("Population Size", min_value=10, max_value=200, value=50)
        GEN = st.number_input("Generations", min_value=50, max_value=500, value=120)
        EL_S = 2

    # ------------------- GA FUNCTIONS -------------------
    def fitness(sched):
        return sum([ratings[prog][i] for i, prog in enumerate(sched)])

    def init_pop(progs, size):
        return [random.sample(progs, len(progs)) for _ in range(size)]

    def crossover(s1, s2):
        point = random.randint(1, len(s1) - 2)
        return s1[:point] + s2[point:], s2[:point] + s1[point:]

    def mutate(sched):
        new = sched.copy()
        idx = random.randint(0, len(sched)-1)
        new[idx] = random.choice(programs)
        return new

    def run_ga():
        pop = init_pop(programs, POP)
        for _ in range(GEN):
            pop = sorted(pop, key=fitness, reverse=True)
            new_pop = pop[:EL_S]
            while len(new_pop) < POP:
                p1, p2 = random.choices(pop[:10], k=2)
                c1, c2 = (crossover(p1, p2) if random.random() < CO_R else (p1.copy(), p2.copy()))
                if random.random() < MUT_R: c1 = mutate(c1)
                if random.random() < MUT_R: c2 = mutate(c2)
                new_pop.extend([c1, c2])
            pop = new_pop
        return max(pop, key=fitness)

    # ------------------- RUN TRIALS -------------------
    if st.button("🚀 Generate Optimal Schedules"):
        st.markdown("### Results of 3 Trials")
        trial_data = []
        schedules = []
        for i in range(1,4):
            sched = run_ga()
            total = fitness(sched)
            schedules.append(sched)
            trial_data.append({"Trial": i, "Total Rating": total})
        # Show comparison chart
        trial_df = pd.DataFrame(trial_data)
        st.bar_chart(trial_df.set_index("Trial"))

        # Show schedules as colored heatmaps
        for i, sched in enumerate(schedules):
            st.markdown(f"#### Trial {i+1} Schedule")
            df = pd.DataFrame({"Hour": hours, "Program": sched})
            df["Rating"] = [ratings[prog][idx] for idx, prog in enumerate(sched)]
            styled = df.style.background_gradient(cmap='YlGnBu', subset=["Rating"])
            st.dataframe(styled, use_container_width=True)

else:
    st.warning("Please upload your CSV file to continue.")
