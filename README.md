# BillSplitter Application

This is a BillSplitter application built using Streamlit. The application allows users to manage bills by adding participants, items, and calculating totals for each participant. It also provides functionality to save the resulting data in JSON format.

## Project Structure

```
streamlit-billsplitter
├── app.py               # Main entry point for the Streamlit application
├── core
│   ├── __init__.py     # Initializes the core module
│   ├── logic.py        # Contains business logic for the application
│   └── models.py       # Defines data models for participants and bills
├── requirements.txt     # Lists project dependencies
└── README.md            # Documentation for the project
```

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd streamlit-billsplitter
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   streamlit run app.py
   ```

## Usage

- Open the application in your web browser.
- Add participants by entering their names.
- For each bill, add items with their respective prices and select the participants involved.
- Calculate the total amount for each participant.
- Save the results in JSON format for future reference.

## Contributing

Feel free to submit issues or pull requests for any improvements or features you would like to see in the application.