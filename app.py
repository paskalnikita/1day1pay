from flask import Flask, render_template
from logic import paymentsGenerator
app = Flask(__name__)

@app.route('/')
def home():
    payments, salary, full_credit_left, transactions_doc = paymentsGenerator()
    return render_template('index.html', payments=payments, salary=salary,full_credit_left=full_credit_left, transactions_doc=transactions_doc)

if __name__ == '__main__':
    app.run()