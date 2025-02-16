from django.shortcuts import render
import pandas as pd
import joblib
df=pd.read_csv("data/comple_n1.csv")
model=joblib.load("model_r.pkl")
def home(request):
    if request.method == 'POST':
        college = request.POST.get('college')
        branch = request.POST.get('branch')
        category = request.POST.get('category')
    
        past_cutoffs_row = df.loc[
            (df['COLLEGE'] == college) & 
            (df['BRANCH'] == branch) & 
            (df['CATEGORIES'] == category)
        ]

        if not past_cutoffs_row.empty:
            # Get past cutoffs as a list
            past_cutoffs = past_cutoffs_row.iloc[0][['Cutoff_2019', 'Cutoff_2020', 'Cutoff_2021', 'Cutoff_2022', 'Cutoff_2023','Cutoff_2024']].tolist()
        else:
            # Handle the case where there is no matching record
            past_cutoffs = [0, 0, 0, 0, 0,0]  # Default values

        # Prepare the input for prediction
        input_data = pd.DataFrame({
            'COLLEGE': [college],
            'BRANCH': [branch],
            'CATEGORIES': [category],
            'Cutoff_2019': [past_cutoffs[0] if len(past_cutoffs) > 0 else None],
            'Cutoff_2020': [past_cutoffs[1] if len(past_cutoffs) > 1 else None],
            'Cutoff_2021': [past_cutoffs[2] if len(past_cutoffs) > 2 else None],
            'Cutoff_2022': [past_cutoffs[3] if len(past_cutoffs) > 3 else None],
            'Cutoff_2023': [past_cutoffs[4] if len(past_cutoffs) > 4 else None],
            'Cutoff_2024': [past_cutoffs[5] if len(past_cutoffs) > 5 else None],
        })


        
        # Make prediction
        predicted_cutoff = model.predict(input_data)[0]

        # Format the prediction to an integer
        formatted_cutoff = int(round(predicted_cutoff))

        # Calculate differences from previous cutoffs
        differences = [cutoff - formatted_cutoff for cutoff in past_cutoffs]

        # Redirect to the result page with previous cutoffs, predicted cutoff, and differences
        return render(request,'result.html', 
                               {"college":college, 
                               "branch":branch, 
                               "category":category, 
                               "past_cutoffs":past_cutoffs, 
                               "predicted_cutoff":formatted_cutoff, 
                               "differences":differences})

    # Prepare dropdown lists for the form
    return render(request,'index.html', {"colleges":df['COLLEGE'].unique(), "branches":df['BRANCH'].unique(), "categories":df['CATEGORIES'].unique()})
