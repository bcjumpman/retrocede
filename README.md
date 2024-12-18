# Retrocede

Retrocede is a fun and educational stock trading simulation app designed to teach users—especially beginners and students—about buying, selling, and managing stocks. With pretend money, users can explore the world of trading in a risk-free environment while learning the basics of the stock market.

## 🛠 Features
- **Simple Signup & Login**: Start trading quickly with secure user authentication.
- **Real-Time Stock Data**: View up-to-date stock prices and trends.
- **Buy & Sell Stocks**: Learn how to manage your portfolio through easy-to-use buy and sell options.
- **Portfolio Management**: Track your holdings and performance at a glance.
- **Budget Management**: See how much pretend money you have left to spend.
- **Search by Company Name**: Don’t know the ticker symbol? Search for stocks by company name.
- **Learn Mode**: A beginner-friendly guide to understanding stock trading.
- **Educational Predictions**: The ability to explore potential stock trends with performance predictions (powered by machine learning) is coming soon.

## 🖥️ Tech Stack
- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python (Flask framework)
- **Database:** SQLite
- **APIs:** Alpha Vantage, and Yahoo Finance
- **Machine Learning:** Prophet for stock performance prediction
- **Authentication**: Google Authentication integration

## 🚀 Get Started
1. Prerequisites
- Python 3.8+
- A free Alpha Vantage API Key for stock data
- Google Cloud Console credentials for authentication (if needed)

## 2. Installation
1. Clone the repository:

```
bash
Copy code
git clone https://github.com/bcjumpman/retrocede.git
cd retrocede
```

2. Set up a virtual environment: 
```
bash
Copy code
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install dependencies:
```
bash
Copy code
pip install -r requirements.txt
```
Add a .env file:
```
plaintext
Copy code
FLASK_SECRET_KEY=your_secret_key_here
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```
Initialize the database:
```
bash
Copy code
python reset_db.py
```
Start the app:
```
bash
Copy code
flask run
```

## 3. Usage
Visit the app in your browser at http://127.0.0.1:5000/.
Create an account or log in using Google authentication.
Use your pretend money to buy and sell stocks.
Track your portfolio, check your performance, and learn about the stock market.
Explore stock trends and predictions.
## 📘 Learn Mode
Navigate to the Learn section in the app for a beginner-friendly guide on stock trading basics, including:
What are stocks?
How does buying and selling work?
Understanding risk and rewards.
Tips for smart trading.

## 🤝 Contributing
We welcome contributions to improve the app. Please fork the repository, make your changes, and submit a pull request.

## 📨 Contact
For any questions, suggestions, or feedback, feel free to reach out:

Author: [Brian Carmichael](https://www.linkedin.com/in/bcarmichael31/)
GitHub: [bcjumpman](https://github.com/bcjumpman)
