import os
import re
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Directory to search
directory = 'results/baseline/'

# Pattern for lines we're interested in
pattern = re.compile(r'^>>\s*\[(.*?)\]\s*(\d+\.\d+)')

# Hold the parsed data
separation_cohesion_ratios = []
scores = []

# Iterate over all files in directory
for filename in os.listdir(directory):
    if filename == 'overview.txt':
        continue  # Skip this file
    if "400f" not in filename:
        continue  # Only do 400 fish setting

    # Open each file
    with open(os.path.join(directory, filename), 'r') as file:
        # Read lines from the file
        for line in file.readlines():
            # If the line matches our pattern
            match = pattern.match(line)
            if match:
                # Extract data
                numbers_string = match.group(1).split(',')
                numbers_in_brackets = list(map(float, filter(None, (n.strip() for n in numbers_string))))

                separation_cohesion_ratio = numbers_in_brackets[3] / numbers_in_brackets[2]

                number_outside = float(match.group(2))

                # Append to our data list
                separation_cohesion_ratios.append(separation_cohesion_ratio)
                scores.append(number_outside)

# Create a pandas DataFrame
df = pd.DataFrame({
    'separation_cohesion_ratio': separation_cohesion_ratios,
    'score': scores
})

# Create the plot
plt.figure(figsize=(10, 5))
sns.scatterplot(data=df, x='separation_cohesion_ratio', y='score')

# Set the x-axis to log scale
plt.xscale('log')

plt.title('Scatter plot of separation-cohesion ratio and score', fontsize=15)
plt.xlabel('Separation-cohesion ratio (log scale)', fontsize=14)
plt.ylabel('N. dead fish', fontsize=14)

plt.savefig('separation-cohesion-score-plot.png', dpi=300)
plt.show()
