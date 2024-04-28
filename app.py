import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import dash
from dash import dcc
from dash import html
from dash import dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

gss = pd.read_csv("https://github.com/jkropko/DS-6001/raw/master/localdata/gss2018.csv",
                 encoding='cp1252', na_values=['IAP','IAP,DK,NA,uncodeable', 'NOT SURE',
                                               'DK', 'IAP, DK, NA, uncodeable', '.a', "CAN'T CHOOSE"])

mycols = ['id', 'wtss', 'sex', 'educ', 'region', 'age', 'coninc',
          'prestg10', 'mapres10', 'papres10', 'sei10', 'satjob',
          'fechld', 'fefam', 'fepol', 'fepresch', 'meovrwrk'] 
gss_clean = gss[mycols]
gss_clean = gss_clean.rename({'wtss':'weight', 
                              'educ':'education', 
                              'coninc':'income', 
                              'prestg10':'job_prestige',
                              'mapres10':'mother_job_prestige', 
                              'papres10':'father_job_prestige', 
                              'sei10':'socioeconomic_index', 
                              'fechld':'relationship', 
                              'fefam':'male_breadwinner', 
                              'fehire':'hire_women', 
                              'fejobaff':'preference_hire_women', 
                              'fepol':'men_bettersuited', 
                              'fepresch':'child_suffer',
                              'meovrwrk':'men_overwork'},axis=1)
gss_clean.age = gss_clean.age.replace({'89 or older':'89'})
gss_clean.age = gss_clean.age.astype('float')


markdown_text = '''
The ratio of women's to men's earned income has remained steady at 80% to 85% over the past roughly 15 years even though women are graduating college at higher rates than men.

There is no clear single cause for this dicrepancy. Rather, it is likely caused by a combination of factors. These factors may include discrimination, job selection, and wowmen taking more time off for family or pregnancy, among others. This gap tends to widen as men and women get farther into their careers.

The General Social Survey (GSS) is a survey that has been going on since 1977. It collects data on attitude and behavioral trends in the United States. It does this by asking respondents feelings on political and cultural topics relevant at the time of the survey, along with core topics which have been consistent across surveys.
'''

gss_grouped = gss_clean.groupby('sex').agg({'income':'mean', 'job_prestige':'mean','socioeconomic_index':'mean', 'education':'mean'}).reset_index()
gss_grouped.income = round(gss_grouped.income,2)
gss_grouped.job_prestige = round(gss_grouped.job_prestige,2)
gss_grouped.socioeconomic_index = round(gss_grouped.socioeconomic_index,2)
gss_grouped.education = round(gss_grouped.education,2)

gss_grouped = gss_grouped.rename({'sex':'Sex', 
                    'income':'Income (dollars)', 
                    'job_prestige':'Job Prestige Index',
                    'socioeconomic_index':'Socioeconomic Index',
                    'education':'Education (years)'}, axis=1)


table = ff.create_table(gss_grouped)


gss_bar = pd.DataFrame(gss_clean[['sex','male_breadwinner']].groupby(['sex','male_breadwinner']).size()).reset_index().rename({0:'count'},axis=1)

gss_bar.male_breadwinner = gss_bar.male_breadwinner.astype('category')
gss_bar.male_breadwinner = gss_bar.male_breadwinner.cat.reorder_categories(["strongly agree", "agree", "disagree", "strongly disagree"], ordered=True)
gss_bar = gss_bar.sort_values(by='male_breadwinner')


gss_scatter = gss_clean[['sex','income','job_prestige','education','socioeconomic_index']]

fig_scatter = px.scatter(gss_scatter, x='job_prestige', y='income',
                 trendline = 'ols',
                 color = 'sex',
                 color_discrete_map = {'male':'#369b94','female':'#dd7423'},
                 height=700, width=700,
                 labels={'job_prestige':'Job Prestige Rating', 
                        'income':'Income'},
                 hover_data=['education','socioeconomic_index'])


gss_boxplot = gss_clean[['sex','income','job_prestige']]

fig_box_inc = px.box(gss_scatter, x='sex', y='income',
                 color = 'sex',
                 color_discrete_map = {'male':'#369b94','female':'#dd7423'},
                 height=700, width=700,
                 labels={'income':'Income', 'sex':''})
fig_box_inc.update_layout(showlegend=False)

fig_box_pres = px.box(gss_scatter, x='sex', y='job_prestige',
                 color = 'sex',
                 color_discrete_map = {'male':'#369b94','female':'#dd7423'},
                 height=700, width=700,
                 labels={'job_prestige':'Job Prestige Rating', 'sex':''})
fig_box_pres.update_layout(showlegend=False)


gss_facet = gss_clean[['income','sex','job_prestige']]
gss_facet['prestige_bracket'] = pd.cut(gss_facet.job_prestige, 6)

gss_facet = gss_facet.dropna()

fig_box_facet = px.box(gss_facet, x='sex', y='income', color='sex', 
             facet_col='prestige_bracket', facet_col_wrap=3,
            labels={'sex':'Sex', 'income':'Income'},
            width=1000, height=600,
            color_discrete_map = {'male':'#369b94','female':'#dd7423'})
fig_box_facet.update(layout=dict(title=dict(x=0.5)))
fig_box_facet.update_layout(showlegend=False)


#Defining relevant variables
questions = list(gss_clean.columns)[11:]

groups = list(gss_clean.columns)[2:5]





app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SANDSTONE])

app.layout = html.Div(
    [
        #Title and description text
        html.H1("Economic and Opinion Differences Between Males and Females in the GSS"),
        dcc.Markdown(children = markdown_text),
        
        #Summary table of important metrics
        html.H2("Summary Table"),
        dcc.Graph(figure=table),
        
        #Dropdown bar chart
        html.Div([
            
        html.H3("Question of Interest"),
        dcc.Dropdown(id='question',
            options=[{'label': i, 'value': i} for i in questions],
            value='male_breadwinner'),

        html.H3("Bar Grouping Category"),
        dcc.Dropdown(id='grouping',
            options=[{'label': i, 'value': i} for i in groups],
            value='sex'),
        
        ]),
        
        html.Div([
            
            dcc.Graph(id="graph")
        
        ]),
        
        #html.H2("Views on if Men Should be Breadwinner"),
        #dcc.Graph(figure=fig_bar),
        
        #Scatter plot of Income and Job Prestige
        html.H2("Income vs. Job Prestige by Sex"),
        dcc.Graph(figure=fig_scatter),
        
        #Side by Side Boxplots
        html.Div([
            
            html.H2("Income by Sex"),
            
            dcc.Graph(figure=fig_box_inc)
            
        ], style = {'width':'48%', 'float':'left'}),
        
        html.Div([
            
            html.H2("Job Prestige by Sex"),
            
            dcc.Graph(figure=fig_box_pres)
            
        ], style = {'width':'48%', 'float':'right'}),
        
        html.H2("Income by Sex and Job Prestige Bracket"),
        dcc.Graph(figure=fig_box_facet), 
    ]
)

#Callback and figure function
@app.callback(Output(component_id="graph",component_property="figure"), 
             [Input(component_id='question',component_property="value"),
              Input(component_id='grouping',component_property="value")])

def make_figure(question, grouping):
    gss_dropdown = pd.DataFrame(gss_clean[[question, grouping]].groupby([question, grouping]).size()).reset_index().rename({0:'count'},axis=1)       
    return px.bar(gss_dropdown, x=question, y='count', color=question,
            color_discrete_sequence=px.colors.qualitative.T10,
            #height = 600, width = 800,
            facet_col = grouping)
                

if __name__ == '__main__':
    app.run_server(mode='inline', debug=True)
