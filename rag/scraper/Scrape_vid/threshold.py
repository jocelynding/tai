import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV file
df = pd.read_csv('189.csv')

# Assuming the CSV has columns named 'content_val' and 'frame_rate'
content_val = df['content_val']
frame_rate = df['Frame Number']
print(df['content_val'].mean())
# Create a plot
plt.plot(frame_rate, content_val, marker='o')  # 'o' is for circle markers

# Adding title and labels
plt.title('Content Value vs Frame Number')
plt.xlabel('Frame Number')
plt.ylabel('Content Value')

# Define the threshold for content value
threshold = 2 # You can adjust this value as needed

# Print out Timecode where content_val exceeds the threshold
for index, row in df.iterrows():
    if row['content_val'] > threshold:
        print(f'Timecode for high content value: {row["Timecode"]} with content value: {row["content_val"]}')

# Show the plot
plt.show()
