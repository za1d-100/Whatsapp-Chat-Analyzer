from urlextract import URLExtract
import pandas as pd
from wordcloud import WordCloud
from collections import Counter
import emoji
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import timedelta

analyzer = SentimentIntensityAnalyzer()
extract=URLExtract()
def fetch_stats(selected_user,df):
    if selected_user!='Overall':
        df=df[df['user']==selected_user]

    num_of_message=df.shape[0]

    words=[]
    for msg in df["message"].fillna("").astype(str):
        words.extend(msg.split())

    num_of_media_message = df[df['message'] == '<Media omitted>'].shape[0]

    links=[]
    for message in df["message"].fillna("").astype(str):
        links.extend(extract.find_urls(message))

    return num_of_message,len(words),num_of_media_message,len(links)
def most_busy_users(df):
    x=df['user'].value_counts().head()
    df=round((df['user'].value_counts()/df.shape[0])*100,2).reset_index().rename(columns={'index':'name','user':'percent'})
    return x,df

def word_cloud(selected_user, df):

    with open("stop_hinglish.txt", "r", encoding="utf-8") as f:
        stop_words = set(f.read().split())

    temp = df.copy()

    if selected_user != "Overall":
        temp = temp[temp["user"] == selected_user]

    temp = temp[temp["user"] != "group_notification"]

    temp = temp[temp["message"] != "<Media omitted>"]

    temp["message"] = temp["message"].fillna("").astype(str)

    def remove_stopwords(message):
        words = []

        for word in message.lower().split():

            if word not in stop_words:
                words.append(word)

        return " ".join(words)

    temp["message"] = temp["message"].apply(remove_stopwords)

    wc = WordCloud(
        width=500,
        height=500,
        min_font_size=10,
        background_color="white"
    )

    return wc.generate(" ".join(temp["message"]))
def most_common_words(selected_user, df):

    with open("stop_hinglish.txt", "r", encoding="utf-8") as f:
        stop_words = set(f.read().split())

    temp = df.copy()

    if selected_user != "Overall":
        temp = temp[temp["user"] == selected_user]

    temp = temp[temp["user"] != "group_notification"]

    temp = temp[temp["message"] != "<Media omitted>"]

    temp["message"] = temp["message"].fillna("").astype(str)

    words = []

    for message in temp["message"]:

        for word in message.lower().split():

            if word not in stop_words:
                words.append(word)

    return pd.DataFrame(Counter(words).most_common(20))
def emoji_counter(selected_user,df):
    if selected_user!='Overall':
        df=df[df['user']==selected_user]
    emojis=[]
    for msg in df["message"].fillna("").astype(str):
        emojis.extend([i for i in msg if i in emoji.EMOJI_DATA])
    emoji_df = pd.DataFrame(
        Counter(emojis).most_common(),
        columns=["emoji", "count"]
    )
    return emoji_df
def monthly_timeline(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))

    timeline['time'] = time

    return timeline

def daily_timeline(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby('only_date').count()['message'].reset_index()

    return daily_timeline

def week_activity_map(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()

def month_activity_map(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()

def activity_heatmap(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

    return user_heatmap
def mood_analysis(selected_user, df, days=30):

    temp = df.copy()

    if selected_user != "Overall":
        temp = temp[temp["user"] == selected_user]

    latest_date = temp["date"].max()

    temp = temp[temp["date"] >= latest_date - timedelta(days=days)]

    temp = temp[
        ~temp["message"].str.contains(
            "Media omitted|This message was deleted",
            case=False,
            na=False
        )
    ]

    temp = temp[
        ~temp["message"].str.contains(
            "http",
            case=False,
            na=False
        )
    ]

    temp = temp[
        temp["message"].astype(str).str.split().str.len() >= 5
    ]

    if len(temp) < 10:
        return None

    midpoint = latest_date - timedelta(days=days/2)

    previous = temp[temp["date"] < midpoint]

    current = temp[temp["date"] >= midpoint]

    def calculate(df_part):

        pos = neg = neu = 0

        for msg in df_part["message"]:

            score = analyzer.polarity_scores(str(msg))["compound"]

            if score >= 0.05:
                pos += 1

            elif score <= -0.05:
                neg += 1

            else:
                neu += 1

        total = pos + neg + neu

        if total == 0:
            return None

        return {
            "positive": round(pos/total*100,2),
            "neutral": round(neu/total*100,2),
            "negative": round(neg/total*100,2)
        }

    previous_result = calculate(previous)
    current_result = calculate(current)

    if current_result is None:
        return None

    if previous_result is None:

        trend = "Stable"

        change = 0

    else:

        change = round(
            current_result["negative"] -
            previous_result["negative"],2
        )

        if change > 5:
            trend = "Declined"

        elif change < -5:
            trend = "Improved"

        else:
            trend = "Stable"

    return {

        "current": current_result,

        "previous": previous_result,

        "trend": trend,

        "change": abs(change)

    }


