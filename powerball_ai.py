import numpy as np
from keras.models import Sequential
from keras.layers import LSTM, Dense
import csv
from pprint import pprint
import requests
from io import StringIO
from datetime import datetime
import os
import time


def download_powerball_numbers(url):
    """
    Downloads Powerball winning numbers from the given URL.

    Parameters:
        url (str): The URL to download the CSV file containing Powerball winning numbers.

    Returns:
        str: The content of the downloaded CSV file as a string.
    """
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception("Failed to download the file.")

def parse_powerball_numbers(csv_content):
    """
    Parses the CSV content containing Powerball winning numbers.

    Parameters:
        csv_content (str): The CSV content as a string.

    Returns:
        list: A list of winning numbers sequence (list of int). i.e. [[1,2,3,4,5,6], ...]
    """
    powerball_numbers = []
    reader = csv.reader(StringIO(csv_content))
    next(reader)  # Skip the header row

    for row in reader:
        # Convert the date to a datetime object
        draw_date = datetime.strptime(row[0], "%m/%d/%Y")
        # Convert the numbers to integers and add to the list
        winning_numbers = [int(num) for num in row[1].split()]
        powerball_numbers.append((draw_date, winning_numbers))

    # Sort the list by date
    powerball_numbers.sort(key=lambda x: x[0])

    # Extract sorted winning numbers
    sorted_winning_numbers = [numbers for _, numbers in powerball_numbers]

    return sorted_winning_numbers

# Usage example
csv_url = "https://data.ny.gov/api/views/d6yy-54nr/rows.csv?accessType=DOWNLOAD"
data_source = "online"
try:
    csv_content = download_powerball_numbers(csv_url)
except Exception as e:
    print(f"Failed to download from the URL: {e}")
    # Use the local file if online fetch fails
    local_file_path = "./powerball_db.csv"
    if os.path.exists(local_file_path):
        with open(local_file_path, 'r') as file:
            csv_content = file.read()
        data_source = "local CSV"
    else:
        raise Exception("Local file not found. Please ensure the file './powerball_db.csv' exists.")
winning_numbers = parse_powerball_numbers(csv_content)

lottery_numbers_data = winning_numbers
print(f"Training data source: {data_source}")

# Create a sequential model
model = Sequential()
model.add(LSTM(128, input_shape=(6, 1)))
model.add(Dense(6))

# Compile the model
model.compile(loss='mse', optimizer='adam')

# Transform data into the correct format
x = np.array(lottery_numbers_data)
y = np.roll(x, -1, axis=0)

# Train the model with shuffled data before each epoch
epochs = 10
for epoch in range(epochs):
    print(f"Epoch {epoch + 1}/{epochs}")
    # Shuffle the training data before each epoch
    indices = np.arange(len(x))
    np.random.shuffle(indices)
    x_shuffled = x[indices]
    y_shuffled = y[indices]
    model.fit(x_shuffled, y_shuffled, batch_size=32, epochs=1, verbose=1)

# Use a fresh RNG each run for variability
rng = np.random.default_rng()

# Generate a random valid ticket (5 unique mains, 1 powerball)
main_numbers = rng.choice(np.arange(1, 70), size=5, replace=False)
main_numbers = np.sort(main_numbers)
powerball_number = rng.integers(1, 27)

predicted_sequence = np.append(main_numbers, powerball_number)

print(predicted_sequence)
