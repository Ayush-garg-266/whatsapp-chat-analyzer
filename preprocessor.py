import pandas as pd
import re

def preprocess(data):
    # Split messages and extract dates
    pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}(?:\s?[apAP][mM])?\s-\s'
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    # Robust date parsing
    df['message_date'] = pd.to_datetime(df['message_date'], errors='coerce', dayfirst=True)
    df.rename(columns={'message_date': 'date'}, inplace=True)

    users = []
    msgs = []
    for message in df['user_message']:
        if ": " in message:
            user, msg = message.split(": ", 1)
            users.append(user)
            msgs.append(msg)
        else:
            users.append('group_notification')
            msgs.append(message)

    df['user'] = users
    df['message'] = msgs
    df.drop(columns=['user_message'], inplace=True)

    # Check empty dataframe
    if df.empty:
        return pd.DataFrame(columns=['date','only_date','year','month_num','month','day','day_name','hour','minute','period','user','message'])

    # Date-time features
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute
    df['period'] = df['hour'].apply(lambda x: f"{x}-{(x+1)%24:02d}")

    return df
