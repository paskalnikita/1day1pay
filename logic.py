#PKO BANK. use it once a day during Elixir sessions
'''
Splits your future salary for small, daily credits in total equals to your salary
'''
import fintech
import datetime
import calendar as cal
fintech.register()
from fintech.sepa import Account, SEPACreditTransfer, SEPADirectDebit

debtor = Account('DE89370400440532013000', 'IBAN OWNER') #PKO BANK.mock #Create the debtor account from an IBAN
creditor = Account(('AT611904300234573201', 'BKAUATWW'), 'BANK') #PKO BANK.mock # Create the creditor account from a tuple (IBAN, BIC)


class UserData():
    def __init__(self):
        self.name = "Bank user"
        self.salary = 6000
        self.salary_credit = 6000
        self.fridays_extra_pay = 50 # can be passed as argument, provides by User in application

    def get_salary(self):
        return self.salary
    
    def get_full_credit(self):
        return self.salary_credit

    def get_fridays_extra_pay(self):
        return self.fridays_extra_pay
    

class PayCalendar():
    def get_today():
        day=datetime.datetime.today().now().day
        month=datetime.datetime.today().now().month
        year=datetime.datetime.today().now().year
        return datetime.date(year, month, day)

    def get_year():
        return datetime.datetime.today().now().year

    def get_month():
        return datetime.datetime.today().now().month

    def get_last_pay_day(days):
        last_pay_day = days[-1]

        if days[-1].weekday() == 5:
            last_pay_day=days[-2]
        
        if days[-1].weekday() == 6:
            last_pay_day=days[-3]

        return last_pay_day

    def calc_days(year, month):
        working_days=0
        fridays=0
        def date_iter(year, month):
            for i in range(1, cal.monthrange(year, month)[1] + 1):
                yield datetime.date(year, month, i)

        for day in date_iter(year, month):
            weekday=day.weekday()
            if weekday < 5:
                working_days += 1 # Weekday
            
            if int(weekday) == 4:
                fridays += 1  # 5 Sat, 6 Sun: Weekends

        return working_days, fridays


def split_sum(num_of_working_days, num_of_fridays, salary, fridays_extra_pay):
    salary = salary - fridays_extra_pay * num_of_fridays
    daily_payment, left_for_last_pay = divmod(salary, num_of_working_days)

    return daily_payment, left_for_last_pay

#main logic
def paymentsGenerator():
    user_data = UserData()
    salary, full_credit_left=user_data.get_salary(), user_data.get_full_credit()
    num_of_working_days, num_of_fridays = PayCalendar.calc_days(PayCalendar.get_year(), PayCalendar.get_month())
    daily_payment, left_for_last_pay = split_sum(num_of_working_days, num_of_fridays, salary, user_data.get_fridays_extra_pay())
    num_days = cal.monthrange(PayCalendar.get_year(), PayCalendar.get_month())[1]
    days = [datetime.date(PayCalendar.get_year(), PayCalendar.get_month(), day) for day in range(1, num_days+1)]

    payments = []
    fridays_counted=0
    incoming_salary = False
    for day in days: #PKO BANK. for logic validations only, normally you can get day by day
        if incoming_salary: 
            # #PKO BANK. In Elixir you can do anuthing with credit
            pass
        if day == PayCalendar.get_today():
            # do not pay forward
            break

        last_pay_day=PayCalendar.get_last_pay_day(days)
        day_name = day.strftime("%A")
        if day != last_pay_day:
            if day.weekday() < 4: # mon - thu
                payments.append(f"{day_name} {day}, paying: {daily_payment}")
                sct = SEPACreditTransfer(debtor) # Create a SEPACreditTransfer instance
                sct.add_transaction(creditor, daily_payment, f'Pay for {day}') # Add the transaction

                full_credit_left -= daily_payment

            if day.weekday() == 4: #friday
                if fridays_counted == int(num_of_fridays)-1: #last friday
                    today_payment=daily_payment+user_data.get_fridays_extra_pay()+left_for_last_pay
                    payments.append(f"Last {day_name} {day}, paying: {today_payment}")
                    sct = SEPACreditTransfer(debtor) # Create a SEPACreditTransfer instance
                    sct.add_transaction(creditor, today_payment, f'Pay for {day}') # Add the transaction
                    
                    full_credit_left -= today_payment
                    fridays_counted += 1
                    continue

                today_payment=daily_payment+user_data.get_fridays_extra_pay()
                payments.append(f"{day_name} {day}, paying: {today_payment}")
                fridays_counted += 1
                sct = SEPACreditTransfer(debtor) # Create a SEPACreditTransfer instance
                sct.add_transaction(creditor, today_payment, f'Pay for {day}') # Add the transaction

                full_credit_left -= today_payment

        if day == last_pay_day: # if last day pay all money left
            if int(full_credit_left) != 0:
                payments.append(f"{day} is last day, paying: {full_credit_left}")
                sct = SEPACreditTransfer(debtor) # Create a SEPACreditTransfer instance
                sct.add_transaction(creditor, full_credit_left, f'Pay for {day}') # Add the transaction

                full_credit_left -= full_credit_left


    SEPA_doc=sct.render() #PKO BANK. Render the SEPA document
    return payments, salary, full_credit_left, SEPA_doc
