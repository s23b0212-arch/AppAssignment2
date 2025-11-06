import streamlit as st
import pandas as pd
import random

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="TV Program Scheduler using GA", layout="wide")

# ------------------ CUSTOM PAGE STYLE ------------------
st.markdown("""
<style>
/* General font and background */
html, body, [class*="css"]  {
    font-family: 'Poppins', sans-serif;
    background-color: #F4F7FB;
    color: #222;
}

/* Title */
h1 {
    text-align: center;
    color: #1E88E5;
    font-weight: 800;
    font-size: 40px;
    text-shadow: 1px 1px 2px #90CAF9;
    margin-bottom: 30px;
}

/* Section headers */
h2, h3, h4 {
    color: #1565C0;
    font-weight: 700;
}

/* Info boxes and success boxes */
div.stAlert > div {
    font-size: 16px;
}

/* Buttons */
div.stButton > button {
    background-color: #1E88E5;
    color: white;
    border-radius: 10px;
    font-weight: 600;
    transition: 0.3s;
}
div.stButton > button:hover {
    background-color: #1565C0;
    transform: scale(1.02);
}

/* Table style */
thead tr th {
    background-color: #1E88E5 !important;
    color: white !important;
    font-weight: 700 !important;
    text-align: center !important;
}
tbody tr:nth-child(even) {
    background-color: #E3F2FD !important;
}
tbody tr:nth-child(odd) {
    background-color: #FFFFFF !important;
}
td {
    text-align: center !important;
    font-weight: 500;
}
</style>
""", unsafe_allow_html=True)

# ------------------ PAGE HEADER ------------------
st.markdown("<h1>📺 TV Program Scheduling using Genetic Algorithm</h1>", unsafe_allow_html=True)

# ------------------ 1. UPLOAD CSV ------------------
st.markdown("### 📂 **Upload Program Ratings CSV File**")

uploaded_file = st.file_uploader("Upload your CSV file below:", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.markdown("### 🧾 **Original Rating Data**")
    st.dataframe(df, use_container_width=True)

    # ------------------ 2. MODIFY RATING DATA ------------------
    st.markdown("### ✏️ **Modify Program Ratings (Optional)**")
    st.info("You can edit the ratings directly below to test different scenarios.")
    edited_df = st.data_editor(df, num_rows="dynamic")
    st.markdown("### ✅ **Modified Rating Data**")
    st.dataframe(edited_df, use_container_width=True)

    # Convert DataFrame to dictionary
    program_ratings = {}
    for i, row in edited_df.iterrows():
        program = row[0]
        ratings = [float(x) for x in row[1:]]
        program_ratings[program] = ratings

    # ------------------ 3. PARAMETER INPUT ------------------
    st.markdown("### ⚙️ **Genetic Algorithm Parameters**")
    col1, col2 = st.columns(2)

    with col1:
        CO_R = st.slider(
            "Crossover Rate (CO_R)",
            0.0, 0.95, 0.8, 0.01,
            help="Controls how much parent genes combine during crossover."
        )

    with col2:
        MUT_R = st.slider(
            "Mutation Rate (MUT_R)",
            0.01, 0.05, 0.02, 0.01,
            help="Determines how often random mutations occur in the population."
        )

    st.success(f"**Crossover Rate (CO_R):** {CO_R}  **Mutation Rate (MUT_R):** {MUT_R}")

    # ------------------ 4. RUN GENETIC ALGORITHM ------------------
    st.markdown("### 🚀 **Run the Genetic Algorithm**")

    if st.button("🧩 Run Scheduler"):
        programs = list(program_ratings.keys())
        num_slots = len(programs)
        population_size = 10
        generations = 20

        # Create population
        def create_population():
            return [random.sample(programs, num_slots) for _ in range(population_size)]

        # Fitness function (sum of ratings per schedule)
        def fitness(schedule):
            total = 0
            for i, prog in enumerate(schedule):
                total += program_ratings[prog][i % len(program_ratings[prog])]
            return total

        # Selection (Tournament)
        def selection(population):
            return max(random.sample(population, 2), key=fitness)

        # Crossover (single point)
        def crossover(p1, p2):
            if random.random() < CO_R:
                point = random.randint(1, num_slots - 2)
                child = p1[:point] + [p for p in p2 if p not in p1[:point]]
                return child
            else:
                return p1

        # Mutation (swap two positions)
        def mutate(schedule):
            if random.random() < MUT_R:
                i, j = random.sample(range(num_slots), 2)
                schedule[i], schedule[j] = schedule[j], schedule[i]
            return schedule

        # GA loop
        population = create_population()
        for _ in range(generations):
            new_pop = []
            for _ in range(population_size):
                parent1 = selection(population)
                parent2 = selection(population)
                child = crossover(parent1, parent2)
                child = mutate(child)
                new_pop.append(child)
            population = new_pop

        best_schedule = max(population, key=fitness)

        # ------------------ 5. DISPLAY RESULTS ------------------
        st.markdown("### 🗓️ **Generated TV Schedule**")

        schedule_df = pd.DataFrame({
            "🕒 Time Slot": [f"Slot {i+1}" for i in range(num_slots)],
            "🎬 Program": best_schedule
        })

        st.table(schedule_df)

        st.success("🎉 The Genetic Algorithm has successfully generated an optimal schedule!")
else:
    st.warning("⚠️ Please upload a CSV file to begin.")

