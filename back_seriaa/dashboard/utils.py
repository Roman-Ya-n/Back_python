# dashboard/utils.py
import plotly.graph_objects as go
import plotly.express as px
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.transform import factor_cmap
from bokeh.palettes import Category20
import pandas as pd
from .queries import DashboardQueries


class PlotlyCharts:
    """Клас для створення графіків Plotly"""
    
    @staticmethod
    def create_teams_bar_chart():
        """Стовпчикова діаграма: команди з найкращою різницею голів"""
        queryset = DashboardQueries.teams_best_goal_difference(min_points=30)
        df = DashboardQueries.to_dataframe(queryset)
        
        fig = px.bar(
            df, 
            x='team_name', 
            y='goal_difference',
            title='Команди з найкращою різницею голів (очки ≥ 30)',
            labels={'team_name': 'Команда', 'goal_difference': 'Різниця голів'},
            color='goal_difference',
            color_continuous_scale='Viridis'
        )
        
        fig.update_layout(
            xaxis_tickangle=-45,
            height=500
        )
        
        return fig.to_html(full_html=False)
    
    @staticmethod
    def create_age_pie_chart():
        """Кругова діаграма: середній вік по командах"""
        queryset = DashboardQueries.avg_player_age_by_team()
        df = DashboardQueries.to_dataframe(queryset)
        
        # Обмежуємо для кращого відображення
        df = df.head(10)
        
        fig = px.pie(
            df,
            names='player_team__team_name',
            values='avg_age',
            title='Середній вік гравців по командах (Топ-10)',
            hole=0.3
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        
        return fig.to_html(full_html=False)
    
    @staticmethod
    def create_wins_line_chart():
        """Лінійний графік: перемоги по роках"""
        queryset = DashboardQueries.team_wins_by_year()
        df = DashboardQueries.to_dataframe(queryset)
        
        # Pivot для лінійного графіка
        pivot_df = df.pivot(index='year', columns='win_team__team_name', 
                           values='win_count').fillna(0)
        
        fig = px.line(
            pivot_df,
            title='Кількість перемог команд по роках',
            labels={'value': 'Кількість перемог', 'year': 'Рік'},
            markers=True
        )
        
        fig.update_layout(
            height=500,
            xaxis_title='Рік',
            yaxis_title='Перемоги'
        )
        
        return fig.to_html(full_html=False)
    
    @staticmethod
    def create_players_scatter():
        """Scatter plot: гравці (голи vs асисти)"""
        queryset = DashboardQueries.top_players_by_contributions(20)
        df = DashboardQueries.to_dataframe(queryset)
        
        fig = px.scatter(
            df,
            x='goal_scored',
            y='assist_scored',
            size='total_contributions',
            color='player_team__team_name',
            hover_name='player_name',
            title='Гравці: Голи vs Асисти (розмір = гол+асист)',
            labels={'goal_scored': 'Голи', 'assist_scored': 'Асисти'},
            size_max=30
        )
        
        fig.update_layout(height=600)
        
        return fig.to_html(full_html=False)
    
    @staticmethod
    def create_matches_area_chart():
        """Area chart: матчі по місяцях"""
        queryset = DashboardQueries.matches_by_month()
        df = DashboardQueries.to_dataframe(queryset)
        
        fig = px.area(
            df,
            x='month',
            y='match_count',
            title='Кількість матчів по місяцях',
            labels={'month': 'Місяць', 'match_count': 'Кількість матчів'}
        )
        
        fig.update_layout(height=400)
        
        return fig.to_html(full_html=False)
    
    @staticmethod
    def create_coaches_heatmap():
        """Heatmap: тренери по країнах"""
        queryset = DashboardQueries.coaches_by_country()
        df = DashboardQueries.to_dataframe(queryset)
        
        # Створюємо матрицю для heatmap
        df['exp_level'] = pd.cut(df['avg_experience'], 
                                bins=3, 
                                labels=['Низький', 'Середній', 'Високий'])
        
        pivot_df = df.pivot_table(index='coach_country', 
                                 columns='exp_level', 
                                 values='coach_count', 
                                 aggfunc='sum').fillna(0)
        
        fig = px.imshow(
            pivot_df,
            title='Тренери по країнах та рівню досвіду',
            labels=dict(x="Рівень досвіду", y="Країна", color="Кількість"),
            aspect="auto"
        )
        
        fig.update_layout(height=400)
        
        return fig.to_html(full_html=False)


class BokehCharts:
    """Клас для створення графіків Bokeh"""
    
    @staticmethod
    def create_teams_bar_chart():
        """Стовпчикова діаграма Bokeh"""
        queryset = DashboardQueries.teams_best_goal_difference(min_points=30)
        df = DashboardQueries.to_dataframe(queryset)
        
        source = ColumnDataSource(df)
        
        p = figure(
            x_range=df['team_name'].tolist(),
            height=400,
            title="Команди з найкращою різницею голів",
            toolbar_location="above"
        )
        
        p.vbar(
            x='team_name', 
            top='goal_difference', 
            width=0.9,
            source=source,
            line_color='white',
            fill_color=factor_cmap(
                'team_name', 
                palette=Category20[20], 
                factors=df['team_name'].tolist()
            )
        )
        
        p.xgrid.grid_line_color = None
        p.y_range.start = 0
        p.xaxis.major_label_orientation = 45
        p.add_tools(HoverTool(
            tooltips=[
                ("Команда", "@team_name"),
                ("Різниця голів", "@goal_difference"),
                ("Очки", "@points")
            ]
        ))
        
        return p
    
    # ... аналогічно решта 5 графіків для Bokeh