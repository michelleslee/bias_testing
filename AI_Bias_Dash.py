import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import base64
import io
from sklearn.metrics import confusion_matrix
from html_block import generate_html
from helper_functions import get_classes, generate_class_fairness

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__ ,external_stylesheets=external_stylesheets)
app.config.include_asset_files = True 
app.config.suppress_callback_exceptions = True

df = pd.DataFrame()

def get_page_stats(df,ao,pc,prob,po,pf,bg,error): 
    #Fill in final page stats here
    children_start =  [
                html.Div( children=[html.Img(
                    src=app.get_asset_url('deloitte_logo.png'),
                    style={
                        'height' : '15%',
                        'width' : '15%',
                        'float' : 'left',
                        'position' : 'left',
                        'padding-top' : 0,
                        'padding-right' : 0

                    })]),
                    html.Br(),
                    html.Br(),
                    html.Br(),
                    html.Br()]
    children_end = [html.Div([
                        dcc.Link('Choose new columns', href='/selectcolumns'),
                        html.Br(),
                        dcc.Link('Upload new data', href='/')
                        ])]
    classes = get_classes(df, pf)
    fairness_classes = generate_class_fairness(df, pf, bg, 
                            classes, ao, po, pc, prob)
    children = children_start + generate_html(bg, fairness_classes, error) + children_end

    page_layout = html.Div(children =children)
    
    
    return page_layout


def get_bar_chart(classes, bg_index, eop_values, fperb_values, ppp_values, pcb_values, ncb_values):
    data_list = []
    index = 0 
    for i, class_name in enumerate(classes):
        if i == bg_index:
            pass
        else:
            data_item = {'x': ['EOP', 'FPERB', 'PPP', 'PCB', 'NCB'], 
            'y': [eop_values[index], fperb_values[index], ppp_values[index], pcb_values[index], ncb_values[index]], 
            'type': 'bar', 'name': class_name}
            data_list.append(data_item)
            index += 1

    return dcc.Graph(
        id='example-graph',
        figure={
            'data':data_list,
            'layout': {
                'title': f'Comparison for {classes[bg_index]}'
            }
        }
    )

def get_error_delta(value, error):
    if value % error == value:
        return 0
    else:
        return value % error

def get_stack_bar(bg_class, class_name, value, error):
    trace1 = go.Bar(
    x=[class_name],
    y=[value-get_error_delta(value, error)],
    name='Value'
    )
    trace2 = go.Bar(
        x=[class_name],
        y=[get_error_delta(value, error)],
        name='Error'
    )

    return html.Div([
        dcc.Graph(id=f'bar_plot_{class_name}',
                figure=go.Figure(data=[trace1, trace2],
                                layout=go.Layout(barmode='stack'))
                )
        ])
    
def replace_empty_string_with_passed(string_):
    if string_ == '':
        return 'Passed'
    else:
        return string_


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
   
    html.Div(id='page-content'),
    dcc.Dropdown(id='ao-dropdown',style={'display':'none'}),
    dcc.Dropdown(id='pc-dropdown',style={'display':'none'}),
    dcc.Dropdown(id='prob-dropdown',style={'display':'none'}),
    dcc.Dropdown(id='po-dropdown',style={'display':'none'}),
    dcc.Dropdown(id='pf-dropdown',style={'display':'none'}),
    dcc.Dropdown(id='bg-dropdown',style={'display':'none'}),
    dcc.Input(id='error-input',style={'display':'none'}),
])

page_upload = html.Div([
    html.Div( children=[html.Img(
                    src=app.get_asset_url('deloitte_logo.png'),
                    style={
                        'height' : '15%',
                        'width' : '15%',
                        'float' : 'left',
                        'position' : 'left',
                        'padding-top' : 0,
                        'padding-right' : 0

                    }),
                    html.H1('AI Bias Detection', style={'display': 'inlineBlock','textAlign':'center','width':'85%'}),
                    
                    
                    ]),
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '97%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px',
            'paddingRight': '5px'
        },
        # Don't allow multiple files to be uploaded
        multiple=False
    ),
    html.Br(),
    html.Div(id='upload-button-container',children=html.Div(['Upload a CSV or Excel file.'])),

])

@app.callback(dash.dependencies.Output('upload-button-container', 'children'),
              [dash.dependencies.Input('upload-data', 'contents')],
              [dash.dependencies.State('upload-data', 'filename'),
               dash.dependencies.State('upload-data', 'last_modified')])
def show_upload_button(contents,filename,last_modified):
    global df
    if contents != None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)

    try:
        if '.xls' in str(filename):
            df = pd.read_excel(io.BytesIO(decoded))
            df = df.applymap(lambda s:s.capitalize().strip() if type(s) == str else s)

            return dcc.Link('Upload', href='/selectcolumns') 

        elif '.csv' in str(filename):
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            df = df.applymap(lambda s:s.capitalize().strip() if type(s) == str else s)
            
            return dcc.Link('Upload', href='/selectcolumns')  
            
        else:
            return html.Div([
            'Please Upload a CSV or Excel file.'
            ])

    except Exception as e:
        print(str(e))
        return html.Div([
            'There was an error processing this file.'
        ])
           
# Update the index
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname'),
              dash.dependencies.Input('ao-dropdown', 'value'),
              dash.dependencies.Input('pc-dropdown', 'value'),
              dash.dependencies.Input('prob-dropdown', 'value'),
              dash.dependencies.Input('po-dropdown', 'value'),
              dash.dependencies.Input('pf-dropdown', 'value'),
              dash.dependencies.Input('bg-dropdown', 'value'),
              dash.dependencies.Input('error-input', 'value'),])
def display_page(pathname,ao_value,pc_value,prob_value,po_value,pf_value,bg_value,error_value):

    if pathname == '/':
        return page_upload

    elif pathname == '/selectcolumns':
        if ao_value == None:
            disabled_pc = True
            options_pc = []
        else:
            disabled_pc = False
            options_pc = df[ao_value].unique()

        if pf_value == None:
            disabled_bg = True
            options_bg = []
        else:
            disabled_bg = False
            options_bg = df[pf_value].unique()

        if ao_value != None and pc_value != None and po_value != None and pf_value != None and bg_value != None and error_value != None:
            link = dcc.Link('Analyse', href='/stats')
        else:
            link = html.Div('Please fill in all required details')

        page_select_columns = html.Div([

                html.Div( children=[html.Img(
                    src=app.get_asset_url('deloitte_logo.png'),
                    style={
                        'height' : '15%',
                        'width' : '15%',
                        'float' : 'left',
                        'position' : 'left',
                        'padding-top' : 0,
                        'padding-right' : 0

                    }),
                    html.H1('Customise data analysis', style={'display': 'inlineBlock','textAlign':'center','width':'85%'}),
                    
                    
                    ]),

                html.Br(),
                html.Div(dcc.Dropdown(
                                        id='ao-dropdown',
                                        options=[{'label': i, 'value': i} for i in df.columns.values],
                                        value=ao_value,
                                        placeholder="Actual Outcome",
                                        style={'width':'50%'})),

                html.Div(dcc.Dropdown(
                                        id='pc-dropdown',
                                        options=[{'label': i, 'value': i} for i in options_pc],
                                        value=pc_value,
                                        placeholder="Positive Class",
                                        disabled = disabled_pc,
                                        style={'width':'50%'})),

                html.Div(dcc.Dropdown(
                                        id='prob-dropdown',
                                        options=[{'label': i, 'value': i} for i in df.columns.values],
                                        value=prob_value,
                                        placeholder="Probability (optional)",
                                        style={'width':'50%'})),
                html.Div(dcc.Dropdown(
                                        id='po-dropdown',
                                        options=[{'label': i, 'value': i} for i in df.columns.values],
                                        value=po_value,
                                        placeholder="Predicted outcome",
                                        style={'width':'50%'})),

                html.Div(dcc.Dropdown(
                                        id='pf-dropdown',
                                        options=[{'label': i, 'value': i} for i in df.columns.values],
                                        value=pf_value,
                                        placeholder="Protected feature",
                                        style={'width':'50%'})),

                html.Div(dcc.Dropdown(
                                        id='bg-dropdown',
                                        options=[{'label': i, 'value': i} for i in options_bg],
                                        value=bg_value,
                                        placeholder="Baseline group",
                                        disabled = disabled_bg,
                                        style={'width':'50%'})),

                html.Div(dcc.Input(     
                                        id='error-input', 
                                        type='number', 
                                        value=error_value,
                                        placeholder="Acceptable level of error (%)",
                                        style={'width':'50%'})),

                link
                ])
        return page_select_columns

    elif pathname == '/stats':
        return get_page_stats(df,ao_value,pc_value,prob_value,po_value,pf_value,bg_value,error_value)

    else:
        return 'Error 404 URL Not Found'

if __name__ == '__main__':
    app.run_server(debug=True)