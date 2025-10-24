import streamlit as st
import preprocessor , helper
import matplotlib.pyplot as plt
import seaborn as sns

st.sidebar.title("Whatsapp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.read()
    data = bytes_data.decode("utf-8")
    # st.text(data)
    df = preprocessor.preprocess(data)

    # st.dataframe(df)

    # fetch unique users
    user_list = df['user'].unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0 , "Overall")

    selected_user = st.sidebar.selectbox("Show analysis wrt",user_list)

    if st.sidebar.button("Show Analysis"):

       # ------------------ Stats Area ------------------
       num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)

       st.title("Top Statistics")
       col1, col2, col3, col4 = st.columns(4)

       with col1:
           st.header("Total Messages")
           st.title(num_messages)

       with col2:
           st.header("Total Words")
           st.title(words)

       with col3:
           st.header("Media Shared")
           st.title(num_media_messages)

       with col4:
           st.header("Links Shared")
           st.title(num_links)

       # ------------------ Monthly Timeline ------------------
       st.title("Monthly Timeline")
       timeline = helper.monthly_timeline(selected_user, df)
       if timeline.empty:
           st.warning("No data for monthly timeline.")
       else:
           fig, ax = plt.subplots()
           ax.plot(timeline['time'], timeline['message'], color='green')
           ax.set_xticks(timeline['time'][::max(1, len(timeline)//10)])
           plt.xticks(rotation='vertical')
           plt.tight_layout()
           st.pyplot(fig)

       # ------------------ Daily Timeline ------------------
       st.title("Daily Timeline")
       daily_timeline = helper.daily_timeline(selected_user, df)
       if daily_timeline.empty:
           st.warning("No data for daily timeline.")
       else:
           fig, ax = plt.subplots()
           ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='purple')
           ax.set_xticks(daily_timeline['only_date'][::max(1, len(daily_timeline)//10)])
           plt.xticks(rotation='vertical')
           plt.tight_layout()
           st.pyplot(fig)

       # ------------------ Activity Map ------------------
       st.title("Activity Map")
       col1, col2 = st.columns(2)

       with col1:
           st.header("Most Busy Day")
           busy_day = helper.week_activity_map(selected_user, df)
           if busy_day.empty:
               st.warning("No data for busy day.")
           else:
               fig, ax = plt.subplots()
               ax.bar(busy_day.index, busy_day.values, color='orange')
               plt.xticks(rotation='vertical')
               plt.tight_layout()
               st.pyplot(fig)

       with col2:
           st.header("Most Busy Month")
           busy_month = helper.month_activity_map(selected_user, df)
           if busy_month.empty:
               st.warning("No data for busy month.")
           else:
               fig, ax = plt.subplots()
               ax.bar(busy_month.index, busy_month.values, color='blue')
               plt.xticks(rotation='vertical')
               plt.tight_layout()
               st.pyplot(fig)

       # ------------------ Weekly Activity Heatmap ------------------
       st.subheader("Weekly Activity Heatmap")
       required_cols = ['day_name', 'period', 'message']
       if all(col in df.columns for col in required_cols):
           user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)
           if user_heatmap.empty:
               st.warning("No data available for heatmap.")
           else:
               fig, ax = plt.subplots(figsize=(10,4))
               sns.heatmap(user_heatmap, cmap='YlGnBu', ax=ax)
               st.pyplot(fig)
       else:
           st.warning("Heatmap cannot be generated (missing columns).")

       # ------------------ Most Busy Users ------------------
       if selected_user == 'Overall':
           st.title("Most Busy Users")
           x, new_df = helper.most_busy_users(df)
           if x.empty:
               st.warning("No user data available.")
           else:
               fig, ax = plt.subplots()
               ax.bar(x.index, x.values, color='red')
               plt.xticks(rotation='vertical')
               plt.tight_layout()
               col1, col2 = st.columns(2)
               with col1:
                   st.pyplot(fig)
               with col2:
                   st.dataframe(new_df)

       # ------------------ Wordcloud ------------------
       st.title("WordCloud")
       df_wc = helper.create_wordcloud(selected_user, df)
       if df_wc is None:
           st.warning("No data for WordCloud.")
       else:
           fig, ax = plt.subplots()
           ax.imshow(df_wc, interpolation='bilinear')
           ax.axis('off')
           plt.tight_layout()
           st.pyplot(fig)

       # ------------------ Most Common Words ------------------
       st.title("Most Common Words")
       most_common_df = helper.most_common_words(selected_user, df)
       if most_common_df.empty:
           st.warning("No common words data.")
       else:
           fig, ax = plt.subplots()
           ax.barh(most_common_df[0], most_common_df[1], color='green')
           plt.tight_layout()
           st.pyplot(fig)

       # ------------------ Emoji Analysis ------------------
       st.title("Emoji Analysis")
       emoji_df = helper.emoji_helper(selected_user, df)
       col1, col2 = st.columns(2)
       with col1:
           if emoji_df.empty:
               st.warning("No emoji data.")
           else:
               st.dataframe(emoji_df)
       with col2:
           if not emoji_df.empty:
               fig, ax = plt.subplots()
               ax.pie(emoji_df['count'].head(), labels=emoji_df['emoji'].head(), autopct="%0.2f")
               plt.tight_layout()
               st.pyplot(fig)
