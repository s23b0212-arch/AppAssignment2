import streamlit as st
import pandas as pd
import random

# Set page configuration
st.set_page_config(page_title="TV Program Scheduler", layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
    /* Style for Title: Centered with blurred font */
    h1 {
        text-align: center;
        color: #1E88E5;
        font-size: 40px;
        font-weight: bold;
        text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.3); /* Adding blur effect */
    }

    /* Sidebar background */
    [data-testid="stSidebar"] {
        background-color: #d4edda;  /* Light green */
        padding-left: 2rem;  /* push content to the right */
    }

    /* Main content background */
    .main .block-container {
        background-color: #e6ffe6;  /* lighter green */
        padding: 2rem;
        border-radius: 10px;
    }

    /* Genetic Algorithm Parameters Header: Uppercase & Bold */
    st.sidebar .css-1v0mbd3 {
        font-weight: bold;
        text-transform: uppercase;
    }

    /* Bold all headings */
    h2, h3, h4, h5, h6 {
        font-weight: bold;
    }

    /* Bold other texts in main content */
    p, label {
        font-weight: bold;
    }

    /* Push sliders to the right */
    div[data-baseweb="slider"] {
        margin-left: auto;
        margin-right: 0;
    }

    /* Style sliders in sidebar */
    .stSlider {
        font-size: 16px;
        color: #1E88E5;  /* Blue color for sliders */
    }

    /* Add color to buttons */
    .stButton button {
        background-color: #1E88E5;
        color: white;
        font-weight: bold;
    }

    .stButton button:hover {
        background-color: #1565C0;
        color: white;
    }

    </style>
""", unsafe_allow_html=True)

# Title
st.markdown("<h1>TV Program Scheduler - Genetic Algorithm</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#555;'>Optimize your daily broadcast schedule for maximum viewer ratings</p>", unsafe_allow_html=True)

# Upload CSV
uploaded_file = st.file_uploader("Upload your CSV file with program ratings", type=["csv"])

# Sidebar for GA parameters
st.sidebar.header("GENETIC ALGORITHM PARAMETERS")
CO_R = st.sidebar.slider("Crossover Rate", 0.0, 0.95, 0.8, 0.01)
MUT_R = st.sidebar.slider("Mutation Rate", 0.01, 0.05, 0.02, 0.01)
GEN = st.sidebar.number_input("Generations", 50, 500, 100, 10)
POP = st.sidebar.number_input("Population Size", 10, 200, 50, 10)
EL_S = 2

# Function to read CSV
@st.cache_data
def read_csv(file):
    df = pd.read_csv(file)
    ratings = {row[0]: [float(x) for x in row[1:]] for _, row in df.iterrows()}
    time_slots = df.columns[1:]
    return ratings, list(time_slots)

# GA functions
def fitness(schedule, ratings):
    return sum(ratings[prog][i] for i, prog in enumerate(schedule))

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

# Run GA
if uploaded_file:
    ratings, time_slots = read_csv(uploaded_file)
    all_programs = list(ratings.keys())
    if st.button("Generate Optimal Schedule"):
        schedule = genetic_algorithm(all_programs, ratings)
        total_rating = fitness(schedule, ratings)
        min_len = min(len(schedule), len(time_slots))
        schedule = schedule[:min_len]
        time_slots_trim = time_slots[:min_len]
        df_result = pd.DataFrame({"Hour": time_slots_trim, "Program": schedule})
        st.success(f"Optimal schedule generated! Total Rating: {total_rating:.2f}")
        st.dataframe(df_result, use_container_width=True)
else:
    st.info("Upload your CSV file to start scheduling.")
