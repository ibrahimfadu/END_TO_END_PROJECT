from django.shortcuts import render
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import io
import urllib
import base64
from django.http import JsonResponse

# Load dataset and model
df = pd.read_csv("data/comple_n1.csv")
model = joblib.load("model_r.pkl")

def generate_graph(fig):
    """Converts a Matplotlib figure to a Base64-encoded string."""
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    buffer.close()
    return f"data:image/png;base64,{image_base64}"

def plot_cutoff_trend(df, colleges, branch, category):
    """Generates a line chart for cutoff trends."""
    cutoff_years = ["Cutoff_2019", "Cutoff_2020", "Cutoff_2021", "Cutoff_2022", "Cutoff_2023", "Cutoff_2024"]
    filtered_df = df[(df["BRANCH"] == branch) & (df["CATEGORIES"] == category) & (df["COLLEGE"].isin(colleges))]
    
    if filtered_df.empty:
        return None
    
    fig, ax = plt.subplots(figsize=(10, 6))
    for _, row in filtered_df.iterrows():
        ax.plot(cutoff_years, row[cutoff_years], marker="o", linestyle="-", label=row["COLLEGE"])

    ax.set_xlabel("Year")
    ax.set_ylabel("Cutoff Score")
    ax.set_title(f"Cutoff Trend (2019-2024) for {branch}, {category}")
    ax.legend(title="Colleges")
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    
    return generate_graph(fig)

def plot_cutoff_bar(df, colleges, branch, category):
    """Generates a bar chart for cutoff trends."""
    cutoff_years = ["Cutoff_2019", "Cutoff_2020", "Cutoff_2021", "Cutoff_2022", "Cutoff_2023", "Cutoff_2024"]
    filtered_df = df[(df["BRANCH"] == branch) & (df["CATEGORIES"] == category) & (df["COLLEGE"].isin(colleges))]
    
    if filtered_df.empty:
        return None
    
    import numpy as np
    bar_width = 0.15  
    x = np.arange(len(cutoff_years))
    
    fig, ax = plt.subplots(figsize=(12, 6))
    for i, (_, row) in enumerate(filtered_df.iterrows()):
        ax.bar(x + i * bar_width, row[cutoff_years], width=bar_width, label=row["COLLEGE"])

    ax.set_xlabel("Year")
    ax.set_ylabel("Cutoff Score")
    ax.set_title(f"Cutoff Comparison (2019-2024) for {branch}, {category}")
    ax.set_xticks(x + (bar_width * (len(filtered_df) - 1)) / 2)
    ax.set_xticklabels(cutoff_years, rotation=45)
    ax.legend(title="Colleges")
    ax.grid(axis="y", linestyle="--", alpha=0.7)

    return generate_graph(fig)

def home(request):
    if request.method == 'POST':
        college = request.POST.get('college')
        branch = request.POST.get('branch')
        category = request.POST.get('category')

        past_cutoffs_row = df.loc[(df['COLLEGE'] == college) & (df['BRANCH'] == branch) & (df['CATEGORIES'] == category)]
        past_cutoffs = past_cutoffs_row.iloc[0][['Cutoff_2019', 'Cutoff_2020', 'Cutoff_2021', 'Cutoff_2022', 'Cutoff_2023','Cutoff_2024']].tolist() if not past_cutoffs_row.empty else [0, 0, 0, 0, 0, 0]

        input_data = pd.DataFrame({
            'COLLEGE': [college],
            'BRANCH': [branch],
            'CATEGORIES': [category],
            'Cutoff_2019': [past_cutoffs[0]],
            'Cutoff_2020': [past_cutoffs[1]],
            'Cutoff_2021': [past_cutoffs[2]],
            'Cutoff_2022': [past_cutoffs[3]],
            'Cutoff_2023': [past_cutoffs[4]],
            'Cutoff_2024': [past_cutoffs[5]],
        })

        predicted_cutoff = int(round(model.predict(input_data)[0]))
        differences = [cutoff - predicted_cutoff for cutoff in past_cutoffs]

        # Generate graphs
        line_chart = plot_cutoff_trend(df, [college], branch, category)
        bar_chart = plot_cutoff_bar(df, [college], branch, category)

        return render(request, 'result.html', {
            "college": college, 
            "branch": branch, 
            "category": category, 
            "past_cutoffs": past_cutoffs, 
            "predicted_cutoff": predicted_cutoff, 
            "differences": differences
        })

    return render(request, 'index.html', {
        "colleges": df['COLLEGE'].unique(), 
        "branches": df['BRANCH'].unique(), 
        "categories": df['CATEGORIES'].unique()
    })

def graph(request):
    return render(request, 'graph.html', {
        "colleges": df['COLLEGE'].unique(), 
        "branches": df['BRANCH'].unique(), 
        "categories": df['CATEGORIES'].unique()
    })

def graph_result(request):
    if request.method == 'POST':
        selected_colleges = request.POST.getlist('college')
        selected_branch = request.POST.get('branch')
        selected_category = request.POST.get('category')
        graph_type = request.POST.get('graph_type')

        # Generate graphs
        line_chart = plot_cutoff_trend(df, selected_colleges, selected_branch, selected_category)
        bar_chart = plot_cutoff_bar(df, selected_colleges, selected_branch, selected_category)

        return render(request, 'graph_result.html', {
            'selected_colleges': selected_colleges,
            'selected_branch': selected_branch,
            'selected_category': selected_category,
            'graph_type': graph_type,
            'line_chart': line_chart,
            'bar_chart': bar_chart
        })

    return render(request, 'graph.html')  # Redirect if accessed via GET