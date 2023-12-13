#from flask import Flask, render_template

import dash
from dash import dcc, html, Dash
from sqlalchemy import create_engine
import pandas as pd
import psycopg2
import os
from dash.dependencies import Input, Output


app = dash.Dash(__name__)

db_uri_chan = 'postgresql://postgres:testpassword@postgres:5432/chan_crawler'
db_uri_reddit = 'postgresql://postgres:testpassword@postgres:5432/reddit_crawler'

chan_engine = create_engine(db_uri_chan)
reddit_engine = create_engine(db_uri_reddit)

def refresh_everything() :
    chan_data = pd.read_sql_query("SELECT COUNT(*) FROM posts", chan_engine)
    reddit_data_posts = pd.read_sql_query("SELECT COUNT(*) FROM posts where subreddit != 'gundeals' and subreddit != 'politics'", reddit_engine)
    reddit_data_comments = pd.read_sql_query("SELECT COUNT(*) FROM comments where subreddit != 'gundeals' and subreddit != 'politics'", reddit_engine)

    chan_count = chan_data.iloc[0, 0]
    reddit_count = reddit_data_posts.iloc[0, 0] + reddit_data_comments.iloc[0, 0]

    # get the chan toxicity and gunpride statistics
    chan_toxicity = pd.read_sql_query("SELECT COUNT(*) FROM posts where is_toxic = 1", chan_engine)
    chan_gunpride_toxicity = pd.read_sql_query("SELECT COUNT(*) FROM posts where is_toxic = 1 and is_gunpride = 1", chan_engine)
    chan_gunpride = pd.read_sql_query("SELECT COUNT(*) FROM posts where is_gunpride = 1", chan_engine)

    chan_toxicity_count = chan_toxicity.iloc[0, 0]
    chan_gunpride_toxicity_count = chan_gunpride_toxicity.iloc[0, 0]
    chan_gunpride_count = chan_gunpride.iloc[0, 0]

    chan_gunpride_percentage = (chan_gunpride_count / chan_count) * 100
    chan_toxic_percentage = (chan_toxicity_count / chan_count) * 100
    chan_toxic_gunpride_percentage = (chan_gunpride_toxicity_count / chan_gunpride_count) * 100

    # get the reddit toxicity and gunpride statistics
    reddit_toxicity_posts = pd.read_sql_query("SELECT COUNT(*) FROM posts where is_toxic = 1 and subreddit != 'gundeals' and subreddit != 'politics'", reddit_engine)
    reddit_toxicity_comments = pd.read_sql_query("SELECT COUNT(*) FROM comments where is_toxic = 1 and subreddit != 'gundeals' and subreddit != 'politics'", reddit_engine)
    reddit_gunpride_toxicity_posts = pd.read_sql_query("SELECT COUNT(*) FROM posts where is_toxic = 1 and is_gunpride = 1 and subreddit != 'gundeals' and subreddit != 'politics'", reddit_engine)
    reddit_gunpride_toxicity_comments = pd.read_sql_query("SELECT COUNT(*) FROM comments where is_toxic = 1 and is_gunpride = 1 and subreddit != 'gundeals' and subreddit != 'politics'", reddit_engine)
    reddit_gunpride_posts = pd.read_sql_query("SELECT COUNT(*) FROM posts where is_gunpride = 1 and subreddit != 'gundeals' and subreddit != 'politics'", reddit_engine)
    reddit_gunpride_comments = pd.read_sql_query("SELECT COUNT(*) FROM comments where is_gunpride = 1 and subreddit != 'gundeals' and subreddit != 'politics'", reddit_engine)

    reddit_toxicity_count = reddit_toxicity_posts.iloc[0, 0] + reddit_toxicity_comments.iloc[0, 0] 
    reddit_gunpride_toxicity_count = reddit_gunpride_toxicity_posts.iloc[0, 0] + reddit_gunpride_toxicity_comments.iloc[0, 0]
    reddit_gunpride_count = reddit_gunpride_posts.iloc[0, 0] + reddit_gunpride_comments.iloc[0, 0]

    reddit_gunpride_percentage = (reddit_gunpride_count / reddit_count) * 100
    reddit_toxic_percentage = (reddit_toxicity_count / reddit_count) * 100
    reddit_toxic_gunpride_percentage = (reddit_gunpride_toxicity_count / reddit_gunpride_count) * 100

    return [reddit_gunpride_percentage, reddit_toxic_percentage, reddit_toxic_gunpride_percentage, 
            chan_gunpride_percentage, chan_toxic_percentage, chan_toxic_gunpride_percentage]

subreddit_list = []
board_list = []

subreddit_options = [
    {'label': 'guns', 'value': 'guns'},
    {'label': 'progun', 'value': 'progun'},
    {'label': 'gunpolitics', 'value': 'gunpolitics'},
    {'label': 'gundeals', 'value': 'gundeals'}
]

board_options = [
    {'label': 'k', 'value': 'k'},
    {'label': 'pol', 'value': 'pol'},
    {'label': 'news', 'value': 'news'}
]

app.layout = html.Div([
    html.Button('Switch Graph', id='switch-button', n_clicks=0),
    html.Button('Refresh', id='refresh-button', n_clicks=0),
    dcc.Checklist(
        id='subreddit-checklist',
        options=subreddit_options,
        value=[],
        inline=True
    ),

    dcc.Checklist(
        id='board-checklist',
        options=board_options,
        value=[],
        inline=True
    ),
    dcc.Graph(id='totals_graph'),
    dcc.Graph(id='individuals_graph'),
    html.Div(id='hidden-div1', style={'display': 'none'}),
    html.Div(id='hidden-div2', style={'display': 'none'})
])

@app.callback(
    [Output('subreddit-checklist', 'style'), Output('board-checklist', 'style'), 
    Output('totals_graph', 'style'), Output('individuals_graph', 'style')],
    [Input('switch-button', 'n_clicks')]
)
def toggle_checkboxes(n):
    if n % 2 == 0:
        return {'display': 'none'}, {'display': 'none'}, {'display': 'block'}, {'display': 'none'}
    else:
        return {'display': 'block'}, {'display': 'block'}, {'display': 'none'}, {'display': 'block'}

@app.callback(
    Output('hidden-div1', 'children'), 
    [Input('subreddit-checklist', 'value'), Input('board-checklist', 'value')]
)
def update_lists(subreddits_selected, boards_selected):
    global subreddit_list
    global boards_list
    subreddit_list = subreddits_selected
    boards_list = boards_selected
    return None

@app.callback(
    [Output('totals_graph', 'figure'), Output('individuals_graph', 'figure')],
    [Input('refresh-button', 'n_clicks')]
)
def button_clicked(n_clicks):
    totals_list = refresh_everything()

    data_totals = pd.DataFrame({
        'Category': ['Gunpride', 'Toxic', 'Toxic Gunpride'] * 2,
        'Percentage': totals_list,
        'Group': ['Reddit'] * 3 + ['4chan'] * 3
    })
    
    pivot_data_totals = data_totals.pivot(index='Group', columns='Category', values='Percentage').reset_index()

    figure_totals = {
        'data': [
            {'x': pivot_data_totals['Group'], 'y': pivot_data_totals['Gunpride'], 'type': 'bar', 'name': 'Gunpride', 'marker': {'color': '#00c0c0'}},
            {'x': pivot_data_totals['Group'], 'y': pivot_data_totals['Toxic'], 'type': 'bar', 'name': 'Toxic', 'marker': {'color': '#000080'}},
            {'x': pivot_data_totals['Group'], 'y': pivot_data_totals['Toxic Gunpride'], 'type': 'bar', 'name': 'Toxic Gunpride', 'marker': {'color': 'coral'}}
        ],
        'layout': {
            'title': 'Reddit and 4chan Totals by Category',
            'barmode': 'group',
            'xaxis': {'showgrid': True, 'gridcolor': '#bdbdbd'},
            'yaxis': {'showgrid': True, 'gridcolor': '#bdbdbd', 'title': 'Percentage'}
        }
    }

    if n_clicks > 0:
        numbers_items = []
        for subreddit in subreddit_list :
            numbers_items.append(get_percentages_reddit(subreddit))
        for board in boards_list :
            numbers_items.append(get_percentages_chan(board))

        if len(numbers_items) > 0 :
            figure_individuals = {
                'data': [
                    {'x': [item[0] for item in numbers_items], 'y': [item[1] for item in numbers_items], 'type': 'bar', 'name': 'Gunpride', 'marker': {'color': '#00c0c0'}},
                    {'x': [item[0] for item in numbers_items], 'y': [item[2] for item in numbers_items], 'type': 'bar', 'name': 'Toxic', 'marker': {'color': '#000080'}},
                    {'x': [item[0] for item in numbers_items], 'y': [item[3] for item in numbers_items], 'type': 'bar', 'name': 'Toxic Gunpride', 'marker': {'color': 'coral'}},
                ],
                'layout': {
                    'title': 'Individual Subreddit and Board Analysis',
                    'barmode': 'group',
                    'xaxis': {'showgrid': True, 'gridcolor': '#bdbdbd'},
                    'yaxis': {'showgrid': True, 'gridcolor': '#bdbdbd', 'title': 'Percentage'}

                }
            }
        else:
            figure_individuals = {'data': [], 'layout': {'title': 'Individual Subreddit and Board Analysis'}}
        return figure_totals, figure_individuals
    else:
        return figure_totals, {'data': [], 'layout': {'title': 'Individual Subreddit and Board Analysis'}}

def get_percentages_reddit(subreddit) :
    total_posts = pd.read_sql_query(f"SELECT COUNT(*) FROM posts where subreddit = '{subreddit}'", reddit_engine)
    toxicity_posts = pd.read_sql_query(f"SELECT COUNT(*) FROM posts where is_toxic = 1 and subreddit = '{subreddit}'", reddit_engine)
    gunpride_toxicity_posts = pd.read_sql_query(f"SELECT COUNT(*) FROM posts where is_toxic = 1 and is_gunpride = 1 and subreddit = '{subreddit}'", reddit_engine)
    gunpride_posts = pd.read_sql_query(f"SELECT COUNT(*) FROM posts where is_gunpride = 1 and subreddit = '{subreddit}'", reddit_engine)

    total_comments = pd.read_sql_query(f"SELECT COUNT(*) FROM comments where subreddit = '{subreddit}'", reddit_engine)
    toxicity_comments = pd.read_sql_query(f"SELECT COUNT(*) FROM comments where is_toxic = 1 and subreddit = '{subreddit}'", reddit_engine)
    gunpride_toxicity_comments = pd.read_sql_query(f"SELECT COUNT(*) FROM comments where is_toxic = 1 and is_gunpride = 1 and subreddit = '{subreddit}'", reddit_engine)
    gunpride_comments = pd.read_sql_query(f"SELECT COUNT(*) FROM comments where is_gunpride = 1 and subreddit = '{subreddit}'", reddit_engine)

    total_count = total_posts.iloc[0, 0] + total_comments.iloc[0, 0]
    toxicity_count = toxicity_posts.iloc[0, 0] + toxicity_comments.iloc[0, 0]
    gunpride_toxicity_count = gunpride_toxicity_posts.iloc[0, 0] + gunpride_toxicity_comments.iloc[0, 0]
    gunpride_count = gunpride_posts.iloc[0, 0] + gunpride_comments.iloc[0, 0]

    gunpride_percentage = (gunpride_count / total_count) * 100
    toxic_percentage = (toxicity_count / total_count) * 100
    toxic_gunpride_percentage = (gunpride_toxicity_count / gunpride_count) * 100

    value = [subreddit, gunpride_percentage, toxic_percentage, toxic_gunpride_percentage]

    return value


def get_percentages_chan(board) :
    total = pd.read_sql_query(f"SELECT COUNT(*) FROM posts where board = '{board}'", chan_engine)
    toxicity = pd.read_sql_query(f"SELECT COUNT(*) FROM posts where is_toxic = 1 and board = '{board}'", chan_engine)
    gunpride_toxicity = pd.read_sql_query(f"SELECT COUNT(*) FROM posts where is_toxic = 1 and is_gunpride = 1 and board = '{board}'", chan_engine)
    gunpride = pd.read_sql_query(f"SELECT COUNT(*) FROM posts where is_gunpride = 1 and board = '{board}'", chan_engine)

    total_count = total.iloc[0, 0]
    toxicity_count = toxicity.iloc[0, 0]
    gunpride_toxicity_count = gunpride_toxicity.iloc[0, 0]
    gunpride_count = gunpride.iloc[0, 0]

    gunpride_percentage = (gunpride_count / total_count) * 100
    toxic_percentage = (toxicity_count / total_count) * 100
    toxic_gunpride_percentage = (gunpride_toxicity_count / gunpride_count) * 100

    value = [board, gunpride_percentage, toxic_percentage, toxic_gunpride_percentage]

    return value

# run the app
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=80)
    


