import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout="wide")
st.sidebar.title("WhatsApp Chat Analyzer")

# ---------------- Upload File ----------------
uploaded_file = st.sidebar.file_uploader("Choose a WhatsApp chat file")
if uploaded_file is not None:
    bytes_data = uploaded_file.read()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)

    # ---------------- Select User ----------------
    user_list = df['user'].unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show analysis wrt", user_list)

    if st.sidebar.button("Show Analysis"):

        # ---------------- Top Stats ----------------
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
        st.title("Top Statistics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.header("Total Messages"); st.title(num_messages)
        with col2:
            st.header("Total Words"); st.title(words)
        with col3:
            st.header("Media Shared"); st.title(num_media_messages)
        with col4:
            st.header("Links Shared"); st.title(num_links)

        # ---------------- Monthly Timeline ----------------
        st.title("Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)
        if not timeline.empty:
            fig, ax = plt.subplots(figsize=(10,4))
            ax.plot(timeline['time'], timeline['message'], color='green', marker='o')
            ax.set_xticks(timeline['time'][::max(1,len(timeline)//10)])
            plt.xticks(rotation='vertical')
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.warning("No data available for monthly timeline.")

        # ---------------- Daily Timeline ----------------
        st.title("Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        if not daily_timeline.empty:
            fig, ax = plt.subplots(figsize=(10,4))
            ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='purple', marker='o')
            ax.set_xticks(daily_timeline['only_date'][::max(1,len(daily_timeline)//10)])
            plt.xticks(rotation='vertical')
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.warning("No data available for daily timeline.")

        # ---------------- Activity Map ----------------
        st.title("Activity Map")
        col1, col2 = st.columns(2)
        with col1:
            st.header("Most Busy Day")
            busy_day = helper.week_activity_map(selected_user, df)
            if not busy_day.empty:
                fig, ax = plt.subplots()
                ax.bar(busy_day.index, busy_day.values, color='orange')
                plt.xticks(rotation='vertical')
                plt.tight_layout()
                st.pyplot(fig)
            else:
                st.warning("No data available for busy day.")
        with col2:
            st.header("Most Busy Month")
            busy_month = helper.month_activity_map(selected_user, df)
            if not busy_month.empty:
                fig, ax = plt.subplots()
                ax.bar(busy_month.index, busy_month.values, color='blue')
                plt.xticks(rotation='vertical')
                plt.tight_layout()
                st.pyplot(fig)
            else:
                st.warning("No data available for busy month.")

        # ---------------- Weekly Heatmap ----------------
        st.subheader("Weekly Activity Heatmap")
        heatmap = helper.activity_heatmap(selected_user, df)
        if not heatmap.empty:
            fig, ax = plt.subplots(figsize=(10,4))
            sns.heatmap(heatmap, cmap='YlGnBu', ax=ax)
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.warning("No data available for heatmap.")

        # ---------------- Most Busy Users ----------------
        if selected_user == 'Overall':
            st.title("Most Busy Users")
            x, new_df = helper.most_busy_users(df)
            col1, col2 = st.columns(2)
            with col1:
                if not x.empty:
                    fig, ax = plt.subplots()
                    ax.bar(x.index, x.values, color='red')
                    plt.xticks(rotation='vertical')
                    plt.tight_layout()
                    st.pyplot(fig)
                else:
                    st.warning("No user data available.")
            with col2:
                st.dataframe(new_df)

        # ---------------- WordCloud ----------------
        st.title("WordCloud")
        df_wc = helper.create_wordcloud(selected_user, df)
        if df_wc is not None:
            fig, ax = plt.subplots(figsize=(6,6))
            ax.imshow(df_wc, interpolation='bilinear')
            ax.axis('off')
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.warning("No data available for WordCloud.")

        # ---------------- Most Common Words ----------------
        st.title("Most Common Words")
        most_common_df = helper.most_common_words(selected_user, df)
        if not most_common_df.empty:
            fig, ax = plt.subplots(figsize=(8,6))
            ax.barh(most_common_df[0], most_common_df[1], color='green')
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.warning("No common words data.")

        # ---------------- Emoji Analysis ----------------
        st.title("Emoji Analysis")
        emoji_df = helper.emoji_helper(selected_user, df)
        col1, col2 = st.columns(2)
        with col1:
            if not emoji_df.empty:
                st.dataframe(emoji_df)
            else:
                st.warning("No emoji data available.")
        with col2:
            if not emoji_df.empty:
                fig, ax = plt.subplots()
                ax.pie(emoji_df['count'].head(), labels=emoji_df['emoji'].head(), autopct="%0.2f")
                plt.tight_layout()
                st.pyplot(fig)
