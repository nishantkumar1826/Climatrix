import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ---------------------------
# CONFIG
# ---------------------------
DATA_CSV = "data/predictions.csv"
app = dash.Dash(__name__)
app.title = "Interactive Weather Dashboard"

# ---------------------------
# LOAD DATA
# ---------------------------
df = pd.read_csv(DATA_CSV)

# Ensure date column exists
if 'date' in df.columns:
    df['date'] = pd.to_datetime(df['date'])
else:
    df['date'] = pd.date_range(start="2000-01-01", periods=len(df))

# Available features for dropdown
available_features = [col for col in ['Temperature (C)', 'Predicted_Temperature',
                                       'Humidity', 'Wind Speed (km/h)', 'Apparent Temperature (C)']
                      if col in df.columns]

# ---------------------------
# DASH LAYOUT
# ---------------------------
app.layout = html.Div(
    style={'backgroundColor': '#111111', 'color': 'white', 'font-family': 'Arial'},
    children=[
        html.H1("Interactive Weather Dashboard", style={'textAlign': 'center', 'marginBottom': 30}),
        
        html.Div([
            html.Div([
                html.Label("Select Features:", style={'marginRight': '10px'}),
                dcc.Dropdown(
                    id='feature-dropdown',
                    options=[{'label': f, 'value': f} for f in available_features],
                    value=['Temperature (C)', 'Predicted_Temperature'],
                    multi=True,
                    style={'color': '#000000'}
                )
            ], style={'width': '48%', 'display': 'inline-block'}),
            
            html.Div([
                html.Label("Select Date Range:", style={'marginRight': '10px'}),
                dcc.DatePickerRange(
                    id='date-picker',
                    start_date=df['date'].min(),
                    end_date=df['date'].max(),
                    display_format='YYYY-MM-DD'
                )
            ], style={'width': '48%', 'display': 'inline-block', 'float': 'right'})
        ], style={'marginBottom': 20}),
        
        dcc.Graph(id='weather-graph')
    ]
)

# ---------------------------
# CALLBACK
# ---------------------------
@app.callback(
    Output('weather-graph', 'figure'),
    Input('feature-dropdown', 'value'),
    Input('date-picker', 'start_date'),
    Input('date-picker', 'end_date')
)
def update_graph(selected_features, start_date, end_date):
    filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    
    # Create subplots for selected features
    fig = make_subplots(rows=len(selected_features), cols=1, shared_xaxes=True,
                        vertical_spacing=0.05,
                        subplot_titles=selected_features)
    
    for i, feature in enumerate(selected_features, start=1):
        fig.add_trace(go.Scatter(
            x=filtered_df['date'],
            y=filtered_df[feature],
            mode='lines+markers',
            name=feature,
            marker=dict(size=6),
            line=dict(width=2),
            hovertemplate=f"%{{x|%Y-%m-%d}}<br>{feature}: %{{y:.2f}}<extra></extra>"
        ), row=i, col=1)
    
    fig.update_layout(
        height=300*len(selected_features),  # dynamic height
        template='plotly_dark',
        margin=dict(l=50, r=50, t=80, b=50),
        hovermode='x unified'
    )
    
    # Add range slider for x-axis
    fig.update_xaxes(rangeslider_visible=True)
    
    return fig

# ---------------------------
# RUN APP
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)
