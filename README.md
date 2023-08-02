# Powerball Number Prediction using LSTM

![Powerball](https://github.com/idanshimon/powerball_ai/blob/main/Powerball-Circle.png?raw=true)

## Overview

This project aims to predict the next set of winning Powerball numbers using Long Short-Term Memory (LSTM), a type of recurrent neural network. It fetches the latest Powerball winning numbers from New York State's open data API, preprocesses the data, and trains an LSTM model to make predictions. Please note that predicting lottery numbers is highly challenging and not guaranteed to be successful.

## Features

- Fetches the latest Powerball winning numbers from a public API
- Sorts the winning numbers by date to train the LSTM model
- Trains an LSTM model on the historical winning numbers to make predictions
- Generates a new set of Powerball numbers based on the predictions
- Replaces any duplicate numbers in the predictions to ensure a valid number set

## Usage

1. Clone the repository to your local machine:

```bash
git clone https://github.com/your-username/powerball-prediction.git
cd powerball-prediction
