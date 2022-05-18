import os, pandas as pd

PAY = 140

df = pd.read_csv (r"data.csv")
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

def getYear():
    flag = False
    while(flag == False):
        year = input("\033[1;34mPlease enter the year\033[0m: ")
        try:
            year = int(year)
            if year < 2022:
                raise Exception
            else:
                flag = True
        except Exception:
            print("\n\033[1;31mInvalid year! Please enter a valid year.\033[0m\n")
    
    return str(year)

def getMonth():
    flag = False
    while(flag == False):
        month = input("\033[1;34mPlease enter the month in numeric terms (eg. August = 8)\033[0m: ")
        try:
            month = int(month)
            if month not in range(1,13):
                raise Exception
            else:
                flag = True
        except Exception:
            print("\n\033[1;31mInvalid month! Please enter a valid month (1-12).\033[0m\n")
    
    month = str(month)
    if len(month.strip()) == 1:
        month = f"0{month}"

    return month

def getDay():
    flag = False
    while(flag == False):
        day = input("\033[1;34mPlease enter the day (number)\033[0m: ")
        try:
            day = int(day)
            if day not in range(1,32):
                raise Exception
            else:
                flag = True
        except Exception:
            print("\n\033[1;31mInvalid Day! Please enter a valid day (1-31).\033[0m\n")
    
    day = str(day)
    if len(day.strip()) == 1:
        day = f"0{day}"

    return day

def getDate():
    year = getYear()
    month = getMonth()
    day = getDay()
    
    return f"{year}/{month}/{day}"

def addLog():
    global df
    os.system('cls')
    date = getDate()
    os.system('cls')

    flag = False
    while(flag == False):
        hours = input("\033[1;34mPlease enter the hours worked on this day (positive float)\033[0m: ")
        try:
            hours = float(hours)
            if hours < 0 or hours > 24:
                raise Exception
            elif hours == 0:
                hours = 0.5
            
            flag = True
        except Exception:
            print("\n\033[1;31mInvalid number of hours! Please enter a float from 0 - 24 (inclusive).\033[0m\n")
    
    df = df.append({'Date':date, 'Amount':PAY, 'Hours':hours, 'Hourly Pay':round(PAY/hours, 2)}, ignore_index=True)
    os.system('cls')
    print("\n\033[1;32mNew Log Added\033[0m\n")


def getAverage():
    global df
    total = df['Hourly Pay'].sum()
    average = total / len(df['Date'])
    
    return round(average, 2)

def select(choice):
    global df
    try:
        choice = int(choice)
        if choice not in range(1,5):
            raise Exception
        os.system('cls')

        if choice == 4:
            os.system('cls')
            print("\n\033[1;32mExited\033[0m\n")
            return False
        elif choice == 3:
            df.to_csv('data.csv')
            os.system('cls')
            print("\n\033[1;32mStats have been saved\033[0m\n")
        elif choice == 2:
            addLog()
        else:
            print(f"{df}\n")
            print(f"\033[1;34m{getAverage()}\033[0m\n")
            input("\033[1;32mPress enter to continue\033[0m\n")
            os.system('cls')
        return True
    except Exception:
        os.system('cls')
        print("\n\033[1;31mInvalid Prompt!\033[0m\n")
        return True
        
def main():
    flag = True
    while(flag):
        param = input(menu_msg)
        flag = select(param)

os.system('cls')
print("Welcome to your 'Average Hourly Pay Calculator'")
menu_msg = """
\033[1;31mPlease only select from one of the following options:\033[0m\n
\033[1;32m1 - View current stats\n
2 - Enter a new log\n
3 - Save Stats\n
4 - Exit\033[0m\n
"""

main()