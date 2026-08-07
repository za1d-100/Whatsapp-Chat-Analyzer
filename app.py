import matplotlib.pyplot as plt
import streamlit as st
import preprocessor
import helper
import seaborn as sns
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(409deg, #ffd6e7, #fff9c4);
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffccbc, #ffab91);
    }

</style>
""", unsafe_allow_html=True)
st.sidebar.title("Whatsapp Chat Analyzer")
uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)
    users_list=df['user'].unique().tolist()
    if 'group_notification' in users_list:
        users_list.remove('group_notification')
    users_list.sort()
    users_list.insert(0,'Overall')

    selected_user=st.sidebar.selectbox('Show Analysis',users_list)
    if st.sidebar.button('Show Analysis:'):
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user,df)

        col1,col2,col3,col4=st.columns(4)

        with col1:
            st.header('Total number of messages:')
            st.title(num_messages)
        with col2:
            st.header('Total number of words:')
            st.title(words)
        with col3:
            st.header('Media messages:')
            st.title(num_media_messages)
        with col4:
            st.header('Links:')
            st.title(num_links)
        if selected_user=='Overall':
            st.title('Most busy users')
            x,new_df=helper.most_busy_users(df)
            fig,ax=plt.subplots()
            col1,col2=st.columns(2)
            with col1:
                 ax.bar(x.index,x.values,color='red')
                 plt.xticks(rotation='vertical')
                 st.pyplot(fig)
            with col2:
                 plt.xticks(rotation='vertical')
                 st.dataframe(new_df)

        st.title('Word cloud')
        df_wc=helper.word_cloud(selected_user,df)
        fig,ax=plt.subplots()
        ax.imshow(df_wc)
        st.pyplot(fig)
        st.title('Most Common words')
        mcw=helper.most_common_words(selected_user,df)
        st.dataframe(mcw)

        st.title('Emojis analysis')
        emoji_df = helper.emoji_counter(selected_user, df)

        col1, col2 = st.columns(2)

        with col1:
            st.dataframe(emoji_df)

        with col2:
            if emoji_df.empty:
                st.info("No emojis found in this chat.")
            else:
                fig, ax = plt.subplots()
                ax.pie(
                    emoji_df["count"].head(),
                    labels=emoji_df["emoji"].head(),
                    autopct="%0.2f"
                )
                st.pyplot(fig)

        st.title("Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        st.title("Weekly Activity Map")
        user_heatmap = helper.activity_heatmap(selected_user,df)
        fig,ax = plt.subplots()
        ax = sns.heatmap(user_heatmap)
        st.pyplot(fig)


        st.title('Activity Map')
        col1,col2 = st.columns(2)

        with col1:
            st.header("Most busy day")
            busy_day = helper.week_activity_map(selected_user,df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index,busy_day.values,color='purple')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        with col2:
            st.header("Most busy month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values,color='orange')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
        # ==========================================
        # AI Mood Monitor
        # ==========================================

        st.title("🧠 AI Mood Monitor")

        days = st.selectbox(
            "Select Time Range",
            [7, 30, 90],
            index=1
        )

        result = helper.mood_analysis(selected_user, df, days)

        if result is None:

            st.info("Not enough meaningful messages available for analysis.")

        else:

            current = result["current"]

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "😊 Positive",
                    f"{current['positive']}%"
                )

            with col2:
                st.metric(
                    "😐 Neutral",
                    f"{current['neutral']}%"
                )

            with col3:
                st.metric(
                    "😔 Negative",
                    f"{current['negative']}%"
                )

            st.divider()

            # Overall Mood

            if current["negative"] < 20:
                mood = "😊 Positive"

            elif current["negative"] < 40:
                mood = "😐 Neutral"

            else:
                mood = "😔 Negative"

            st.subheader(f"Current Mood : {mood}")

            st.divider()

            # Trend

            if result["trend"] == "Improved":

                st.success(
                    f"📈 Mood Improved\n\nNegative sentiment decreased by {result['change']}% compared to the previous period."
                )

            elif result["trend"] == "Declined":

                st.error(
                    f"📉 Mood Declined\n\nNegative sentiment increased by {result['change']}% compared to the previous period."
                )

            else:

                st.info(
                    "➖ Mood Stable\n\nNo significant change detected compared to the previous period."
                )

            st.divider()

            # AI Insight

            st.subheader("🤖 AI Insight")

            if result["trend"] == "Improved":

                st.success(
                    """
        Recent conversations appear more positive than the previous period.

        The overall mood has improved and no major emotional risk is detected.
                    """
                )

            elif result["trend"] == "Declined":

                if current["negative"] >= 40:

                    st.error(
                        """
        Recent conversations show a noticeable increase in negative sentiment.

        The conversation may require attention as emotional tone has declined.
                        """
                    )

                else:

                    st.warning(
                        """
        Negative sentiment has increased compared to the previous period.

        However, the overall conversation is still reasonably balanced.
                        """
                    )

            else:

                st.info(
                    """
        Conversation sentiment remained relatively stable during the selected period.

        No major emotional changes were detected.
                    """
                )







