import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="TV Program Scheduler", layout="wide")

st.markdown(
    """
    <style>
    .main-title {
        text-align: center;
        color: #1E88E5;
        font-size: 40px;
        font-weight: 800;
    }
    .subtext {
        text-align: center;
        font-size: 18px;
        color: #555;
        margin-bottom: 20px;
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
    }
    </style>
    <h1 class="main-title">Smart TV Scheduler</h1>
    <p class="subtext">Generate your optimal broadcast schedule</p>
    """,
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

st.sidebar.markdown("## Algorithm Parameters")
CO_R = st.sidebar.slider("Crossover Rate", 0.0, 0.95, 0.8, 0.01)
MUT_R = st.sidebar.slider("Mutation Rate", 0.01, 0.05, 0.02, 0.01)
GEN = st.sidebar.number_input("Generations", 50, 500, 100, 10)
POP = st.sidebar.number_input("Population Size", 10, 200, 50, 10)
EL_S = 2

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    ratings = {row[0]: [float(x) for x in row[1:]] for row in df.values}
    time_slots = list(df.columns[1:])
    all_programs = list(ratings.keys())

    def fitness(schedule):
        return sum(ratings[prog][i] for i, prog in enumerate(schedule))

    def init_population():
        return [random.sample(all_programs, len(all_programs)) for _ in range(POP)]

    def crossover(s1, s2):
        point = random.randint(1, len(s1) - 2)
        return s1[:point] + s2[point:], s2[:point] + s1[point:]

    def mutate(schedule):
        new = schedule.copy()
        new[random.randint(0, len(new)-1)] = random.choice(all_programs)
        return new

    def run_ga():
        pop = init_population()
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

    if st.button("Generate Optimal Schedule"):
        best = run_ga()
        best = best[:len(time_slots)]  # match length with CSV columns
        total = fitness(best)

        st.subheader("Optimal Schedule")
        result_df = pd.DataFrame({"Hour": time_slots, "Program": best})
        st.dataframe(result_df, use_container_width=True)

        st.markdown(f"**Total Viewer Rating:** {total:.2f}")
        st.progress(min(total / 10, 1.0))

else:
    st.warning("Please upload a CSV file to start.")
