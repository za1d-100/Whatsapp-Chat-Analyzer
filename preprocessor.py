import re
import pandas as pd


def preprocess(data):

    # Split messages (supports WhatsApp exports like: 12/06/22, 8:44 pm - )
    pattern = r'(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2})\s*([AaPp][Mm])\s-\s'

    parts = re.split(pattern, data)[1:]

    messages = []
    dates = []

    for i in range(0, len(parts), 4):
        date = parts[i]
        time = parts[i + 1]
        ampm = parts[i + 2].upper()
        message = parts[i + 3]

        dates.append(f"{date} {time} {ampm}")
        messages.append(message.strip())

    df = pd.DataFrame({
        "user_message": messages,
        "date": dates
    })

    # Automatically detect date format
    df["date"] = pd.to_datetime(
        df["date"],
        dayfirst=True,
        errors="coerce"
    )

    df = df.dropna(subset=["date"])

    users = []
    msg = []

    for message in df["user_message"]:

        entry = re.split(r"([^:]+):\s", message, maxsplit=1)

        if len(entry) >= 3:
            users.append(entry[1].strip())
            msg.append(entry[2].strip())
        else:
            users.append("group_notification")
            msg.append(message.strip())

    df["user"] = users
    df["message"] = msg

    df.drop(columns=["user_message"], inplace=True)

    df["only_date"] = df["date"].dt.date
    df["year"] = df["date"].dt.year
    df["month_num"] = df["date"].dt.month
    df["month"] = df["date"].dt.month_name()
    df["day"] = df["date"].dt.day
    df["day_name"] = df["date"].dt.day_name()
    df["hour"] = df["date"].dt.hour
    df["minute"] = df["date"].dt.minute

    period = []

    for hour in df["hour"]:

        if hour == 23:
            period.append("23-00")
        elif hour == 0:
            period.append("00-01")
        else:
            period.append(f"{hour}-{hour+1}")

    df["period"] = period

    return df
