import streamlit as st
import pandas as pd
from tv_scheduling_ga import genetic_algorithm, read_csv_to_dict, fitness_function

st.set_page_config(page_title="TV Scheduling GA", layout="wide")
st.title("TV Program Scheduling using Genetic Algorithm")

# -----------------------------
# Upload CSV
# -----------------------------
uploaded_file = st.file_uploader("Upload CSV file with program ratings", type=["csv"])
if uploaded_file:
    ratings_dict = read_csv_to_dict(uploaded_file)
    all_programs = list(ratings_dict.keys())
    all_time_slots = list(range(6, 24))  # 6:00 to 23:00
    
    st.success("CSV loaded successfully!")
    
    # -----------------------------
    # GA Parameters Input
    # -----------------------------
    st.sidebar.header("GA Parameters for Trials")
    trials = []
    
    for i in range(1, 4):
        st.sidebar.subheader(f"Trial {i}")
        co_r = st.sidebar.slider(f"Crossover Rate (Trial {i})", 0.0, 0.95, 0.8)
        mut_r = st.sidebar.slider(f"Mutation Rate (Trial {i})", 0.01, 0.05, 0.02)
        trials.append((co_r, mut_r))
    
    # -----------------------------
    # Run GA for each trial
    # -----------------------------
    for idx, (co_r, mut_r) in enumerate(trials, start=1):
        st.header(f"Trial {idx} Results")
        best_schedule = genetic_algorithm(
            initial_schedule=all_programs,
            ratings_dict=ratings_dict,
            crossover_rate=co_r,
            mutation_rate=mut_r
        )
        
        # Prepare DataFrame for table display
        schedule_df = pd.DataFrame({
            "Time Slot": [f"{hour:02d}:00" for hour in all_time_slots],
            "Program": best_schedule
        })
        
        st.table(schedule_df)
        st.write(f"**Total Ratings:** {fitness_function(best_schedule, ratings_dict):.2f}")
