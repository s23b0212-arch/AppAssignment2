import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="TV Scheduler Pro", layout="wide")

st.markdown(
"""
<style>
.main-title {
    text-align: center;
    color: #4CAF50;
    font-size: 42px;
    font-weight: bold;
}
.subtext {
    text-align: center;
    font-size: 18px;
    color: #555;
    margin-bottom: 20px;
}
</style>
<h1 class="main-title">🎯 TV Scheduler Pro</h1>
<p class="subtext">Maximize viewer ratings with Genetic Algorithm</p>
""", unsafe_allow_html=True
)

# -------------------- CSV UPLOAD --------------------
uploaded_file = st.file_uploader("📂 Upload your program ratings CSV", type=["csv"])

@st.cache_data
def read_csv(file):
    df = pd.read_csv(file)
    ratings = {row[0]: [float(x) for x in row[1:]] for i, row in df.iterrows()}
    return ratings, df.columns[1:]

# -------------------- GA PARAMETERS --------------------
if uploaded_file:
    ratings, time_slots = read_csv(uploaded_file)
    all_programs = list(ratings.keys())
    all_time_slots = list(time_slots)

    st.markdown("## ⚙️ Genetic Algorithm Parameters")
    cols = st.columns(4)
    CO_R = cols[0].slider("Crossover Rate", 0.0, 0.95, 0.8, 0.01)
    MUT_R = cols[1].slider("Mutation Rate", 0.01, 0.05, 0.02, 0.01)
    POP = cols[2].number_input("Population Size", min_value=10, max_value=200, value=50)
    GEN = cols[3].number_input("Generations", min_value=50, max_value=500, value=100)
    EL_S = 2

    # -------------------- GA FUNCTIONS --------------------
    def fitness(schedule):
        return sum([ratings[program][i] for i, program in enumerate(schedule)])

    def init_pop(programs, size):
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
        population = init_pop(all_programs, POP)
        for _ in range(GEN):
            population = sorted(population, key=fitness, reverse=True)
            new_pop = population[:EL_S]
            while len(new_pop) < POP:
                p1, p2 = random.choices(population[:10], k=2)
                c1, c2 = (crossover(p1, p2) if random.random() < CO_R else (p1.copy(), p2.copy()))
                if random.random() < MUT_R: c1 = mutate(c1)
                if random.random() < MUT_R: c2 = mutate(c2)
                new_pop.extend([c1, c2])
            population = new_pop
        return max(population, key=fitness)

    # -------------------- RUN TRIALS --------------------
    if st.button("🚀 Generate Optimal Schedules (3 Trials)"):
        trial_summary = []
        all_schedules = []
        for t in range(1, 4):
            sched = genetic_algorithm()
            total = fitness(sched)
            df = pd.DataFrame({"Hour": all_time_slots, "Program": sched})
            trial_summary.append({"Trial": t, "Total Rating": total})
            all_schedules.append(df)
        
        st.markdown("## 📊 Trial Comparison")
        summary_df = pd.DataFrame(trial_summary)
        st.dataframe(summary_df)

        # Show schedules
        for idx, df in enumerate(all_schedules):
            st.markdown(f"### 📝 Trial {idx+1} Schedule")
            # color high ratings
            def highlight_program(x):
                val = ratings[x][df.index[df['Program']==x][0]]
                color = f'background-color: rgba(255, {255-int(val*255)}, {255-int(val*255)}, 0.3)'
                return [color]*len(x)
            st.dataframe(df, use_container_width=True)

else:
    st.warning("👆 Upload a CSV file to continue.")
