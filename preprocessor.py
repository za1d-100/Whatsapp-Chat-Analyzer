import re
import pandas as pd
def preprocess(data):
    pattern = r'(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2})\u202f(AM|PM)\s-\s'
    allmessage = re.split(pattern, data)[1:]
    messages = []

    for i in range(3, len(allmessage), 4):
        if i < len(allmessage):
            messages.append(allmessage[i].strip())
    dates = re.findall(pattern, data)
    datetime_strings = []
    for date_tuple in dates:
        date_str, time_str, am_pm = date_tuple
        # Combine into format: "5/26/22 11:53 PM"
        datetime_str = f"{date_str} {time_str} {am_pm}"
        datetime_strings.append(datetime_str)

    # Now create DataFrame with proper datetime strings
    df = pd.DataFrame({'user_message': messages, 'date': datetime_strings})

    # Convert to datetime with correct format (US format: MM/DD/YY)
    df['date'] = pd.to_datetime(df['date'], format='%m/%d/%y %I:%M %p')
    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split('([\w\W]+?):\s', message)
        if entry[1:]:  # user name
            users.append(entry[1])
            messages.append(" ".join(entry[2:]))
        else:
            users.append('group_notification')
            messages.append(entry[0])
    df['user'] = users
    df['message'] = messages
    df.drop('user_message', axis=1, inplace=True)
    df['only_date'] = pd.to_datetime(df['date'].dt.date)
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute
    period = []
    for hour in df[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df['period'] = period

    return df