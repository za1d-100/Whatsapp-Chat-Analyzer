from urlextract import URLExtract
import pandas as pd
from wordcloud import WordCloud
from collections import Counter
import emoji

extract = URLExtract()


def fetch_stats(selected_user, df):

    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    num_of_messages = df.shape[0]

    words = []
    for msg in df["message"].fillna("").astype(str):
        words.extend(msg.split())

    num_of_media_messages = df[df["message"].astype(str).str.contains("Media omitted", na=False)].shape[0]

    links = []
    for message in df["message"].fillna("").astype(str):
        links.extend(extract.find_urls(message))

    return num_of_messages, len(words), num_of_media_messages, len(links)


def most_busy_users(df):
    x = df["user"].value_counts().head()

    percentage = round((df["user"].value_counts() / df.shape[0]) * 100, 2).reset_index()
    percentage.columns = ["name", "percent"]

    return x, percentage


def word_cloud(selected_user, df):

    with open("stop_hinglish.txt", "r", encoding="utf-8") as f:
        stop_words = set(f.read().split())

    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    temp = df.copy()

    temp = temp[temp["user"] != "group_notification"]

    temp = temp.dropna(subset=["message"])

    temp["message"] = temp["message"].astype(str)

    temp = temp[~temp["message"].str.contains("Media omitted", na=False)]

    def remove_stopwords(message):

        words = []

        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)

        return " ".join(words)

    temp["message"] = temp["message"].apply(remove_stopwords)

    temp = temp[temp["message"].str.strip() != ""]

    if temp.empty:
        wc = WordCloud(
            width=500,
            height=500,
            background_color="white"
        )
        return wc.generate("No Data")

    text = " ".join(temp["message"])

    wc = WordCloud(
        width=500,
        height=500,
        background_color="white",
        min_font_size=10
    )

    return wc.generate(text)


def most_common_words(selected_user, df):

    with open("stop_hinglish.txt", "r", encoding="utf-8") as f:
        stop_words = set(f.read().split())

    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    temp = df.copy()

    temp = temp[temp["user"] != "group_notification"]

    temp = temp.dropna(subset=["message"])

    temp["message"] = temp["message"].astype(str)

    temp = temp[~temp["message"].str.contains("Media omitted", na=False)]

    words = []

    for message in temp["message"]:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)

    return pd.DataFrame(Counter(words).most_common(20))


def emoji_counter(selected_user, df):

    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    emojis = []

    for msg in df["message"].fillna("").astype(str):
        emojis.extend([c for c in msg if c in emoji.EMOJI_DATA])

    return pd.DataFrame(Counter(emojis).most_common())


def monthly_timeline(selected_user, df):

    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    timeline = df.groupby(["year", "month_num", "month"]).count()["message"].reset_index()

    time = []

    for i in range(timeline.shape[0]):
        time.append(f"{timeline['month'][i]}-{timeline['year'][i]}")

    timeline["time"] = time

    return timeline


def daily_timeline(selected_user, df):

    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    return df.groupby("only_date").count()["message"].reset_index()


def week_activity_map(selected_user, df):

    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    return df["day_name"].value_counts()


def month_activity_map(selected_user, df):

    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    return df["month"].value_counts()


def activity_heatmap(selected_user, df):

    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    return df.pivot_table(
        index="day_name",
        columns="period",
        values="message",
        aggfunc="count"
    ).fillna(0)
