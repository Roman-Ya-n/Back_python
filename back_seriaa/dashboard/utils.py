# dashboard/utils.py
import plotly.graph_objects as go
import plotly.express as px
from bokeh.plotting import figure, output_file, show, save
from bokeh.models import ColumnDataSource, HoverTool, LabelSet
from bokeh.transform import factor_cmap, linear_cmap
from bokeh.palettes import Category20, Spectral6, Viridis256
from bokeh.layouts import gridplot
from bokeh.models.widgets import DataTable, TableColumn
from bokeh.models import ColorBar, LinearColorMapper
import pandas as pd
import numpy as np
from datetime import datetime
from .queries import DashboardQueries


class PlotlyCharts:
    
    """Клас для створення 6 графіків Plotly"""
    
    @staticmethod
    def create_teams_bar_chart():
        
        """1. Стовпчикова діаграма: команди з найкращою різницею голів"""
        
        queryset = DashboardQueries.teams_best_goal_difference(min_points=30)
        df = DashboardQueries.to_dataframe(queryset)
        
        fig = px.bar(
            df, 
            x='team_name', 
            y='goal_difference',
            title='Команди з найкращою різницею голів (очки ≥ 30)',
            labels={'team_name': 'Команда', 'goal_difference': 'Різниця голів'},
            color='goal_difference',
            color_continuous_scale='Viridis',
            text='goal_difference'
        )
        
        fig.update_layout(
            xaxis_tickangle=-45,
            height=500,
            plot_bgcolor='rgba(240, 240, 240, 0.8)',
            hovermode='x unified'
        )
        
        return fig.to_html(full_html=False)
    
    @staticmethod
    def create_age_pie_chart():
        
        """2. Кругова діаграма: середній вік по командах"""
        
        queryset = DashboardQueries.avg_player_age_by_team()
        df = DashboardQueries.to_dataframe(queryset)
        
        if df.empty:
            df = pd.DataFrame({
                'player_team__team_name': ['Napoli', 'Inter Milan', 'Juventus'],
                'avg_age': [26.5, 25.8, 27.2],
                'player_count': [22, 24, 23]
            })
            
        df = df.head(8).copy()
        df['display_name'] = df['player_team__team_name'].str[:15] + '...'
        
        fig = px.pie(
            df,
            names='display_name',
            values='avg_age',
            title='📊 Середній вік гравців по командах (Топ-8)',
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Plasma
        )
        
        fig.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            hoverinfo='label+percent+value',
            marker=dict(line=dict(color='white', width=2))
        )
        
        fig.update_layout(
            height=500,
            annotations=[dict(
                text=f'Загалом: {df["player_count"].sum()} гравців',
                x=0.5, y=0.5, font_size=14, showarrow=False
            )]
        )
        
        return fig.to_html(full_html=False)
    
    @staticmethod
    def create_wins_line_chart():
        
        """3. Лінійний графік: перемоги по роках"""
        
        queryset = DashboardQueries.team_wins_by_year()
        df = DashboardQueries.to_dataframe(queryset)
        
        pivot_df = df.pivot_table(
            index='year', 
            columns='win_team__team_name', 
            values='win_count', 
            aggfunc='sum'
        ).fillna(0).cumsum()
        
        top_teams = pivot_df.iloc[-1].sort_values(ascending=False).head(5).index
        pivot_df = pivot_df[top_teams]
        
        fig = px.line(
            pivot_df,
            title='Кумулятивні перемоги команд по роках (Топ-5)',
            labels={'value': 'Кількість перемог', 'year': 'Рік', 'variable': 'Команда'},
            markers=True,
            line_shape='spline'
        )
        
        fig.update_layout(
            height=500,
            xaxis_title='Рік',
            yaxis_title='Накопичені перемоги',
            legend_title='Команди',
            hovermode='x unified',
            plot_bgcolor='rgba(250, 250, 250, 0.9)'
        )
        
        return fig.to_html(full_html=False)
    
    @staticmethod
    def create_players_scatter():
        
        """4. Scatter plot: гравці (голи vs асисти)"""
        
        queryset = DashboardQueries.top_players_by_contributions(25)
        df = DashboardQueries.to_dataframe(queryset)
        
        fig = px.scatter(
            df,
            x='goal_scored',
            y='assist_scored',
            size='total_contributions',
            color='player_team__team_name',
            hover_name='player_name',
            title='Гравці: Голи vs Асисти',
            labels={
                'goal_scored': 'Кількість голів',
                'assist_scored': 'Кількість асистів',
                'player_team__team_name': 'Команда',
                'total_contributions': 'Голи+Асисти'
            },
            size_max=30,
            opacity=0.8
        )
        
        median_goals = df['goal_scored'].median()
        median_assists = df['assist_scored'].median()
        
        fig.add_hline(
            y=median_assists, 
            line_dash="dash", 
            line_color="gray",
            annotation_text=f"Медіана асистів: {median_assists}"
        )
        
        fig.add_vline(
            x=median_goals, 
            line_dash="dash", 
            line_color="gray",
            annotation_text=f"Медіана голів: {median_goals}"
        )
        
        fig.update_layout(
            height=600,
            hoverlabel=dict(bgcolor="white", font_size=12)
        )
        
        return fig.to_html(full_html=False)
    
    @staticmethod
    def create_matches_area_chart():
        
        """5. Area chart: матчі по місяцях"""
        
        queryset = DashboardQueries.matches_by_month()
        df = DashboardQueries.to_dataframe(queryset)
        
        if not df.empty:
            df['month'] = pd.to_datetime(df['month'])
            df['month_name'] = df['month'].dt.strftime('%B %Y')
            df = df.sort_values('month')
        
        fig = px.area(
            df,
            x='month_name',
            y='match_count',
            title='Кількість матчів по місяцях',
            labels={'month_name': 'Місяць', 'match_count': 'Кількість матчів'},
            line_shape='spline'
        )
        
        fig.update_layout(
            height=400,
            xaxis_tickangle=-45,
            hovermode='x unified',
            plot_bgcolor='rgba(240, 248, 255, 0.9)'
        )
        
        fig.update_traces(
            fillcolor='rgba(100, 149, 237, 0.3)',
            line=dict(color='royalblue', width=3)
        )
        
        return fig.to_html(full_html=False)
    
    @staticmethod
    def create_coaches_heatmap():
        
        """6. Heatmap: тренери по країнах та досвіду"""
        
        queryset = DashboardQueries.coaches_by_country()
        df = DashboardQueries.to_dataframe(queryset)
        
        if not df.empty:
            df['exp_level'] = pd.cut(
                df['avg_experience'], 
                bins=3, 
                labels=['Початківці (1-7 років)', 'Досвідчені (8-15)', 'Ветерани (16+)']
            )
            
            pivot_df = df.pivot_table(
                index='coach_country', 
                columns='exp_level', 
                values='coach_count', 
                aggfunc='sum'
            ).fillna(0)
            
            pivot_df['total'] = pivot_df.sum(axis=1)
            pivot_df = pivot_df.sort_values('total', ascending=False).drop('total', axis=1)
            
            fig = px.imshow(
                pivot_df,
                title='👨‍🏫 Розподіл тренерів по країнах та рівню досвіду',
                labels=dict(x="Рівень досвіду", y="Країна", color="Кількість тренерів"),
                aspect="auto",
                color_continuous_scale='YlOrRd',
                text_auto=True
            )
            
            fig.update_layout(
                height=400,
                xaxis_title="",
                yaxis_title="",
                coloraxis_colorbar=dict(title="Кількість")
            )
            
            return fig.to_html(full_html=False)
        return "<p>Немає даних для heatmap</p>"


class BokehCharts:
    
    """Клас для створення 6 графіків Bokeh"""
    
    @staticmethod
    def create_teams_bar_chart_bokeh():
        
        """7. Стовпчикова діаграма Bokeh: рейтинг команд"""
        
        queryset = DashboardQueries.teams_best_goal_difference(min_points=20)
        df = DashboardQueries.to_dataframe(queryset)
        
        if df.empty:
            return None
        
        df = df.sort_values('points', ascending=False).head(10)
        source = ColumnDataSource(df)
        
        p = figure(
            x_range=df['team_name'].tolist(),
            height=400,
            width=800,
            title="Топ-10 команд за кількістю очок",
            toolbar_location="above",
            tools="pan,wheel_zoom,box_zoom,reset,save"
        )
        
        p.vbar(
            x='team_name', 
            top='points', 
            width=0.7,
            source=source,
            line_color='white',
            fill_color=factor_cmap(
                'team_name', 
                palette=Category20[20], 
                factors=df['team_name'].tolist()
            )
        )
        
        labels = LabelSet(
            x='team_name', y='points',
            text='points', level='glyph',
            x_offset=-15, y_offset=5,
            source=source,
            text_font_size='10pt'
        )
        p.add_layout(labels)
        
        p.xgrid.grid_line_color = None
        p.y_range.start = 0
        p.xaxis.major_label_orientation = 45
        p.yaxis.axis_label = 'Очки'
        
        p.add_tools(HoverTool(
            tooltips=[
                ("Команда", "@team_name"),
                ("Очки", "@points"),
                ("Перемоги", "@wins"),
                ("Різниця голів", "@goal_difference")
            ]
        ))
        
        return p
    
    @staticmethod
    def create_players_goals_bokeh():
        
        """8. Горизонтальна діаграма: топ-гравці за голами"""
        
        queryset = DashboardQueries.top_players_by_contributions(15)
        df = DashboardQueries.to_dataframe(queryset)
        
        if df.empty:
            return None
        
        df = df.sort_values('goal_scored', ascending=True)
        source = ColumnDataSource(df)
        
        p = figure(
            y_range=df['player_name'].tolist(),
            height=500,
            width=800,
            title="Топ-15 гравців за кількістю голів",
            toolbar_location="right",
            tools="hover,pan,wheel_zoom,reset"
        )
        
        p.hbar(
            y='player_name',
            right='goal_scored',
            height=0.7,
            source=source,
            line_color='white',
            fill_color=linear_cmap(
                'goal_scored',
                palette=Viridis256,
                low=df['goal_scored'].min(),
                high=df['goal_scored'].max()
            )
        )
        
        p.x_range.start = 0
        p.xaxis.axis_label = 'Кількість голів'
        p.yaxis.axis_label = 'Гравець'
        
        p.add_tools(HoverTool(
            tooltips=[
                ("Гравець", "@player_name"),
                ("Голи", "@goal_scored"),
                ("Асисти", "@assist_scored"),
                ("Команда", "@player_team__team_name"),
                ("Загальний внесок", "@total_contributions")
            ]
        ))
        
        return p
    
    @staticmethod
    def create_stadium_capacity_bokeh():
        
        """9. Діаграма розподілу місткості стадіонів"""
        
        from main.models import Stadium
        
        stadiums = Stadium.objects.all().values('stadium_name', 'capacity', 'city')
        df = pd.DataFrame(list(stadiums)).dropna()
        
        if df.empty:
            return None
        
        df = df.sort_values('capacity', ascending=False).head(15)
        source = ColumnDataSource(df)
        
        p = figure(
            x_range=df['stadium_name'].tolist(),
            height=400,
            width=900,
            title="Топ-15 стадіонів за місткістю",
            toolbar_location="above"
        )
        
        p.vbar(
            x='stadium_name',
            top='capacity',
            width=0.7,
            source=source,
            line_color='navy',
            fill_color='dodgerblue'
        )
        
        p.xgrid.grid_line_color = None
        p.y_range.start = 0
        p.xaxis.major_label_orientation = 45
        p.yaxis.axis_label = 'Місткість (осіб)'
        
        p.add_tools(HoverTool(
            tooltips=[
                ("Стадіон", "@stadium_name"),
                ("Місткість", "@capacity"),
                ("Місто", "@city")
            ]
        ))
        
        return p
    
    @staticmethod
    def create_matches_timeline_bokeh():
        
        """10. Таймлайн матчів"""
        
        from main.models import Calendar, Match
        from django.db.models import Count
        
        matches_by_date = Calendar.objects.annotate(
            match_count=Count('event_id')
        ).filter(match_count__gt=0).values('event_date', 'match_count').order_by('event_date')
        
        df = pd.DataFrame(list(matches_by_date))
        
        if df.empty:
            return None
        
        df['event_date'] = pd.to_datetime(df['event_date'])
        df['date_str'] = df['event_date'].dt.strftime('%Y-%m-%d')
        
        source = ColumnDataSource(df)
        
        p = figure(
            height=350,
            width=800,
            title="Розподіл матчів по датах",
            x_axis_type="datetime",
            toolbar_location="above"
        )
        
        p.circle(
            x='event_date',
            y='match_count',
            size=10,
            source=source,
            color='red',
            alpha=0.6
        )
        
        p.line(
            x='event_date',
            y='match_count',
            source=source,
            line_width=2,
            color='red',
            alpha=0.4
        )
        
        p.xaxis.axis_label = 'Дата'
        p.yaxis.axis_label = 'Кількість матчів'
        
        p.add_tools(HoverTool(
            tooltips=[
                ("Дата", "@date_str"),
                ("Матчів", "@match_count")
            ]
        ))
        
        return p
    
    @staticmethod
    def create_players_by_country_bokeh():
        
        """11. Donut chart: гравці за країнами"""
        
        from main.models import PlayerDetailed
        from django.db.models import Count
        
        players_by_country = PlayerDetailed.objects.values(
            'player_country'
        ).annotate(
            player_count=Count('player_detailed_id')
        ).filter(player_country__isnull=False).order_by('-player_count')[:10]
        
        df = pd.DataFrame(list(players_by_country))
        
        if df.empty:
            return None
        
        source = ColumnDataSource(df)
        
        p = figure(
            height=400,
            width=400,
            title="🌍 Гравці за країнами (Топ-10)",
            toolbar_location=None,
            tools="hover",
            x_range=(-0.5, 1.0)
        )
        
        p.wedge(
            x=0, y=1, 
            radius=0.4,
            start_angle='start_angle',
            end_angle='end_angle',
            line_color="white",
            fill_color=factor_cmap(
                'player_country',
                palette=Spectral6,
                factors=df['player_country'].tolist()
            ),
            legend_field='player_country',
            source=source
        )
        
        df['percentage'] = df['player_count'] / df['player_count'].sum() * 100
        df['angle'] = df['player_count'] / df['player_count'].sum() * 2 * np.pi
        df['start_angle'] = [0] + list(df['angle'].cumsum()[:-1])
        df['end_angle'] = df['angle'].cumsum()
        
        p.axis.axis_label = None
        p.axis.visible = False
        p.grid.grid_line_color = None
        
        p.add_tools(HoverTool(
            tooltips=[
                ("Країна", "@player_country"),
                ("Гравців", "@player_count"),
                ("Частка", "@percentage{0.1f}%")
            ]
        ))
        
        return p
    
    @staticmethod
    def create_team_stats_grid_bokeh():
        
        """12. Grid plot: статистика команд"""
        
        queryset = DashboardQueries.teams_best_goal_difference(min_points=0)
        df = DashboardQueries.to_dataframe(queryset)
        
        if df.empty:
            return None
        
        df = df.head(8)
        source = ColumnDataSource(df)
        
        # Графік 1: Очки
        p1 = figure(
            x_range=df['team_name'].tolist(),
            height=250,
            width=400,
            title="Очки",
            toolbar_location=None
        )
        p1.vbar(x='team_name', top='points', width=0.7, source=source, color='blue')
        p1.xaxis.major_label_orientation = 45
        
        # Графік 2: Перемоги
        p2 = figure(
            x_range=df['team_name'].tolist(),
            height=250,
            width=400,
            title="Перемоги",
            toolbar_location=None
        )
        p2.vbar(x='team_name', top='wins', width=0.7, source=source, color='green')
        p2.xaxis.major_label_orientation = 45
        
        # Графік 3: Різниця голів
        p3 = figure(
            x_range=df['team_name'].tolist(),
            height=250,
            width=400,
            title="Різниця голів",
            toolbar_location=None
        )
        p3.vbar(x='team_name', top='goal_difference', width=0.7, source=source, color='orange')
        p3.xaxis.major_label_orientation = 45
        
        # Графік 4: Нічиї
        p4 = figure(
            x_range=df['team_name'].tolist(),
            height=250,
            width=400,
            title="Нічиї",
            toolbar_location=None
        )
        p4.vbar(x='team_name', top='draws', width=0.7, source=source, color='purple')
        p4.xaxis.major_label_orientation = 45
        
        grid = gridplot([[p1, p2], [p3, p4]], toolbar_location="right")
        return grid