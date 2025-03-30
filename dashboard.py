import dash
from dash import dcc, html, Input, Output
import dash_draggable
import plotly.express as px

df = px.data.gapminder()

available_countries = df['country'].unique()
available_years = sorted(df['year'].unique())
numeric_measures = ['lifeExp', 'pop', 'gdpPercap']

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

application = dash.Dash(__name__, external_stylesheets=external_stylesheets)

style_dashboard={
          "height":'100%',
          "width":'100%',
          "display":"flex",
          "flex-direction":"column",
          "flex-grow":"0"
}

default_country = ['Costa Rica']

application.layout = html.Div([
    html.Div([
        html.H4("Выбор стран и меры для оси Y (Линейный график)"),
        dcc.Dropdown(
            id='line-country-dropdown',
            options=[{'label': c, 'value': c} for c in available_countries],
            multi=True,
            placeholder="Выберите страны",
            value=default_country
        ),
        dcc.Dropdown(
            id='line-yaxis-dropdown',
            options=[{'label': m, 'value': m} for m in numeric_measures],
            value='lifeExp',
            placeholder="Выберите меру для оси Y"
        )
    ], style=style_dashboard),

    html.Div([
        html.H4("Выбор года (Пузырьковая, топ-15, круговая)"),
        dcc.Slider(
            id='year-slider',
            min=min(available_years),
            max=max(available_years),
            step=5,
            marks={str(year): str(year) for year in available_years},
            value=min(available_years)
        )
    ], style=style_dashboard),

    html.Hr(),

    html.Div([
        html.H4("Выбор осей и радиуса (Пузырьковая диаграмма)"),
        html.Div([
            html.Label("Ось X:"),
            dcc.Dropdown(
                id='bubble-x-dropdown',
                options=[{'label': m, 'value': m} for m in numeric_measures],
                value='gdpPercap'
            )
        ], style=style_dashboard),
        html.Div([
            html.Label("Ось Y:"),
            dcc.Dropdown(
                id='bubble-y-dropdown',
                options=[{'label': m, 'value': m} for m in numeric_measures],
                value='lifeExp'
            )
        ], style=style_dashboard),
        html.Div([
            html.Label("Размер пузырька:"),
            dcc.Dropdown(
                id='bubble-size-dropdown',
                options=[{'label': m, 'value': m} for m in numeric_measures],
                value='pop'
            )
        ], style=style_dashboard)
    ], style=style_dashboard),

    dash_draggable.ResponsiveGridLayout(
        id='draggable-container',
        children=[
                dcc.Graph(id='bubble-chart', style=style_dashboard),
                dcc.Graph(id='line-chart', style=style_dashboard),
                dcc.Graph(id='top15-chart', style=style_dashboard),
                dcc.Graph(id='pie-chart', style=style_dashboard),
        ],
        style=style_dashboard
    )
])

@application.callback(
    Output('line-chart', 'figure'),
    Input('line-country-dropdown', 'value'),
    Input('line-yaxis-dropdown', 'value'),
)
def update_line_chart(selected_countries, y_measure):
    if not selected_countries or len(selected_countries) == 0:
        return {}
    filtered_df = df[df['country'].isin(selected_countries)]
    fig = px.line(filtered_df, x='year', y=y_measure, color='country',
                  title=f"Линейный график: {y_measure} по годам")
    return fig

@application.callback(
    Output('bubble-chart', 'figure'),
    Input('bubble-x-dropdown', 'value'),
    Input('bubble-y-dropdown', 'value'),
    Input('bubble-size-dropdown', 'value'),
    Input('year-slider', 'value'),
)
def update_bubble_chart(x_measure, y_measure, size_measure, year):
    filtered_df = df[df['year'] == year]
    fig = px.scatter(filtered_df, x=x_measure, y=y_measure, size=size_measure, color='continent',
                     hover_name='country',
                     title=f"Пузырьковая диаграмма ({year})")
    return fig

@application.callback(
    Output('top15-chart', 'figure'),
    Input('year-slider', 'value'),
)
def update_top15_chart(year):
    filtered_df = df[df['year'] == year].sort_values(by='pop', ascending=False).head(15)
    fig = px.bar(filtered_df, x='country', y='pop', color='continent',
                 title=f"Топ-15 стран по популяции ({year})")
    return fig

@application.callback(
    Output('pie-chart', 'figure'),
    Input('year-slider', 'value'),
)
def update_pie_chart(year):
    filtered_df = df[df['year'] == year]
    pop_by_continent = filtered_df.groupby('continent', as_index=False)['pop'].sum()
    fig = px.pie(pop_by_continent, names='continent', values='pop',
                 title=f"Распределение популяции по континентам ({year})")
    return fig
