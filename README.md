# Powerball Number Prediction using LSTM

![Powerball](https://github.com/idanshimon/powerball_ai/blob/main/Powerball-Circle.png?raw=true)

## Overview

This project aims to predict the next set of winning Powerball numbers using Long Short-Term Memory (LSTM), a type of recurrent neural network. It fetches the latest Powerball winning numbers from New York State's open data API, preprocesses the data, and trains an LSTM model to make predictions. Please note that predicting lottery numbers is highly challenging and not guaranteed to be successful.

The reason LSTM was used is for demonstration purposes, to showcase the application of machine learning models on sequential data. However, when it comes to lotteries, the best strategy is to treat them as games of chance and enjoy them responsibly for entertainment purposes rather than relying on any model for predicting winning numbers.

## Features

- Fetches the latest Powerball winning numbers from a public API (goes back to 2010) or uses local database if not available
- Sorts the winning numbers by date to train the LSTM model
- Trains an LSTM model on the historical winning numbers to make predictions
- Generates a new set of Powerball numbers based on the predictions
- Replaces any duplicate numbers in the predictions to ensure a valid number set

## Requirements

- Python 3.9.5

## Usage

1. Clone the repository to your local machine:

```bash
git clone https://github.com/idanshimon/powerball_ai.git
cd powerball_ai
pip install -r requirements.txt
python powerball_ai.py

> python powerball_ai.py
Epoch 1/10
47/47 [==============================] - 2s 11ms/step - loss: 1051.7180
Epoch 2/10
47/47 [==============================] - 0s 10ms/step - loss: 638.7297
Epoch 3/10
47/47 [==============================] - 1s 11ms/step - loss: 429.2337
Epoch 4/10
47/47 [==============================] - 1s 11ms/step - loss: 312.5386
Epoch 5/10
47/47 [==============================] - 0s 11ms/step - loss: 238.4485
Epoch 6/10
47/47 [==============================] - 0s 10ms/step - loss: 191.6049
Epoch 7/10
47/47 [==============================] - 0s 10ms/step - loss: 162.0938
Epoch 8/10
47/47 [==============================] - 0s 10ms/step - loss: 143.5754
Epoch 9/10
47/47 [==============================] - 0s 10ms/step - loss: 132.3892
Epoch 10/10
47/47 [==============================] - 0s 10ms/step - loss: 125.7005
1/1 [==============================] - 0s 472ms/step
[ 7 62 18 49 66  1]
```


## Disclaimer
This project is purely for educational and entertainment purposes. Predicting lottery numbers is improbable and not recommended as a reliable strategy for winning the lottery. The predictions made by the model are not guaranteed to be accurate, and using them to play the lottery involves risks.

## Dataset Source
The Powerball winning numbers are obtained from New York State's open data API. Please refer to the data source for terms of use and licensing information.

## Author Notes
Feel free to contribute, open issues, and provide feedback to help improve the project!

By Idan Shimon

## Roadmap (Future Developments)
- Probability map with html bar-chart output
- Analyzed data with Ball Number | Times Drawn | % of Drawings | % of Draws | Last Drawn results.
- Add perdict model to the bonus ball (10 epoch)

Teaser

