import plotly.express as px
import plotly.graph_objects as go
from utils import COLORS

def plot_anxiety_trend(df):
    """Line chart untuk rata-rata tingkat kebingungan/kecemasan"""
    fig = px.line(df, y='Avg_C', title='Average Anxiety (Confusion) Over Time',
                  labels={'index': 'Time Step', 'Avg_C': 'Average Anxiety'})
    fig.update_traces(line=dict(width=3, color='#8E44AD'))
    
    # Tambahkan garis batas aman dan bahaya
    fig.add_hline(y=0.3, line_dash="dash", line_color="green", annotation_text="Safe Zone")
    fig.add_hline(y=0.7, line_dash="dash", line_color="red", annotation_text="Danger Zone")
    fig.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20))
    return fig

def plot_score_trend(df):
    """Line chart untuk rata-rata skor kecocokan"""
    fig = px.line(df, y='Avg_Score', title='Average Match Score Over Time',
                  labels={'index': 'Time Step', 'Avg_Score': 'Average Score'})
    fig.update_traces(line=dict(width=3, color='#3498DB'))
    fig.add_hline(y=0.7, line_dash="dot", line_color="lightgreen", annotation_text="Threshold Score Yakin")
    fig.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20))
    return fig

def plot_state_distribution(df):
    """Stacked area chart untuk komposisi status agen"""
    fig = go.Figure()
    for state in ['N_Yakin', 'N_Ragu', 'N_Salah']:
        clean_state = state.split('_')[1]
        fig.add_trace(go.Scatter(
            x=df.index, y=df[state],
            mode='lines',
            stackgroup='one',
            name=clean_state,
            line=dict(color=COLORS.get(clean_state, 'gray'))
        ))
    fig.update_layout(title='Agent State Distribution Over Time',
                      xaxis_title='Time Step', yaxis_title='Number of Agents',
                      template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20))
    return fig

def plot_final_state_pie(dist):
    """Pie chart untuk status akhir agen"""
    labels = list(dist.keys())
    values = list(dist.values())
    fig = px.pie(names=labels, values=values, title='Final State Distribution',
                 color=labels, color_discrete_map=COLORS, hole=0.4)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20))
    return fig

def plot_state_bar(dist):
    """Bar chart untuk jumlah status akhir"""
    labels = list(dist.keys())
    values = list(dist.values())
    df_bar = {'State': labels, 'Count': values}
    fig = px.bar(df_bar, x='State', y='Count', color='State', 
                 color_discrete_map=COLORS, title='Agent Count per State')
    fig.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20))
    return fig
