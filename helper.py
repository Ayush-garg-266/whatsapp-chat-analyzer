from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji

extract = URLExtract()

# ------------------ Stats Functions ------------------

def fetch_stats(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user].copy()
    if df.empty:
        return 0, 0, 0, 0

    # 1. number of messages
    num_messages = df.shape[0]

    # 2. number of words
    words = []
    for message in df['message']:
        words.extend(message.split())

    # 3. number of media messages
    num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]

    # 4. number of links
    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))

    return num_messages, len(words), num_media_messages, len(links)


def most_busy_users(df):
    if df.empty:
        return pd.Series(), pd.DataFrame(columns=['name','percent'])
    x = df['user'].value_counts().head()
    new_df = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index()
    new_df.columns = ['name', 'percent']
    return x, new_df

# ------------------ Wordcloud & Words ------------------

def create_wordcloud(selected_user, df):
    f = open('stop_hinglish.txt', 'r')
    stop_words = set(f.read().split())
    f.close()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user].copy()
    temp = df[(df['user'] != 'group_notification') & (df['message'] != '<Media omitted>\n')].copy()
    if temp.empty:
        return None

    def remove_stop_words(message):
        return " ".join([word for word in message.lower().split() if word not in stop_words])

    temp['message'] = temp['message'].apply(remove_stop_words)
    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
    df_wc = wc.generate(temp['message'].str.cat(sep=" "))
    return df_wc


def most_common_words(selected_user, df):
    f = open('stop_hinglish.txt','r')
    stop_words = set(f.read().split())
    f.close()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user].copy()

    temp = df[(df['user'] != 'group_notification') & (df['message'] != '<Media omitted>\n')].copy()
    if temp.empty:
        return pd.DataFrame(columns=[0,1])

    words = []
    for message in temp['message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)

    most_common_df = pd.DataFrame(Counter(words).most_common(20))
    return most_common_df

# ------------------ Emoji ------------------

def emoji_helper(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user].copy()
    if df.empty:
        return pd.DataFrame(columns=['emoji','count'])

    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if emoji.is_emoji(c)])
    if not emojis:
        return pd.DataFrame(columns=['emoji','count'])

    emoji_df = pd.DataFrame(Counter(emojis).most_common(), columns=['emoji','count'])
    return emoji_df

# ------------------ Timelines ------------------

def monthly_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user].copy()
    if df.empty:
        return pd.DataFrame(columns=['time','message'])

    timeline = df.groupby(['year','month_num','month']).count()['message'].reset_index()
    timeline['time'] = timeline['month'] + "-" + timeline['year'].astype(str)
    return timeline


def daily_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user].copy()
    if df.empty:
        return pd.DataFrame(columns=['only_date','message'])
    timeline = df.groupby('only_date').count()['message'].reset_index()
    return timeline

# ------------------ Activity Maps ------------------

def week_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user].copy()
    if 'day_name' not in df.columns or df.empty:
        return pd.Series()
    return df['day_name'].value_counts()


def month_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user].copy()
    if 'month' not in df.columns or df.empty:
        return pd.Series()
    return df['month'].value_counts()


def activity_heatmap(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user].copy()
    if df.empty or 'day_name' not in df.columns or 'period' not in df.columns:
        return pd.DataFrame()
    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)
    return user_heatmap
