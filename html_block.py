import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from fairness_metrics import fairness_metrics, introduction_text
import pandas as pd


def generate_html(baseline_group, fairness_class, error):
    out_html = []
    out_html += [html.Div(children=introduction_text)]
    out_html += generate_summary(baseline_group, fairness_class, error)
    print(fairness_class['confusion_metrics'])
    out_html += generate_confusion_metrics(baseline_group, 
                                            fairness_class['confusion_metrics'][baseline_group]['true_negative'],
                                            fairness_class['confusion_metrics'][baseline_group]['false_positive'],
                                            fairness_class['confusion_metrics'][baseline_group]['false_negative'],
                                            fairness_class['confusion_metrics'][baseline_group]['true_positive'])
    for c in fairness_class.keys():
        if c == 'confusion_metrics':
            continue
        out_html += generate_confusion_metrics(c, 
                                               fairness_class['confusion_metrics'][c]['true_negative'],
                                               fairness_class['confusion_metrics'][c]['false_positive'],
                                               fairness_class['confusion_metrics'][c]['false_negative'],
                                               fairness_class['confusion_metrics'][c]['true_positive'])
    for metric in fairness_metrics:
        out_html += generate_html_block(baseline_group, metric, fairness_class, error)
        if metric['tag'] == 'equalised_odds':
            out_html += get_eodd_results(baseline_group, fairness_class, metric, error)
        else:
            out_html += get_bar_chart(baseline_group, fairness_class, metric, error)
        out_html += [html.Hr()]
    return out_html

def generate_confusion_metrics(group, tn, fp, fn, tp):
    data_item = [{
            "x": ['Predicted <br> negative', 'Predicted <br> positive'], 
            "y": ['Actual <br> positive', 'Actual <br> negative'], 
            "z": [[tn, fp], [fn, tp]], 
            "colorscale": "RdBu", 
            "showscale": True, 
            "type": "heatmap"
            }]
    return [html.Div(dcc.Graph(
        id=f'{group}-confusion',
        figure={
            'data':data_item,
              "annotations": [
                        {
                        "x": 0, 
                        "y": 1, 
                        "font": {"color": "#FFFFFF"}, 
                        "showarrow": False, 
                        "text": "9", 
                        "xref": "x1", 
                        "yref": "y1"
                        }, 
                        {
                        "x": 1, 
                        "y": 1, 
                        "font": {"color": "#FFFFFF"}, 
                        "showarrow": False, 
                        "text": "36", 
                        "xref": "x1", 
                        "yref": "y1"
                        }, 
                        {
                        "x": 0, 
                        "y": 0, 
                        "font": {"color": "#FFFFFF"}, 
                        "showarrow": False, 
                        "text": "401", 
                        "xref": "x1", 
                        "yref": "y1"
                        }, 
                        {
                        "x": 1, 
                        "y": 0, 
                        "font": {"color": "#FFFFFF"}, 
                        "showarrow": False, 
                        "text": "4", 
                        "xref": "x1", 
                        "yref": "y1"
                        }
                    ],
            'layout': {
                'title': f'{group} confusion matrix '
            },'showlegend':False
        })
    ,style={'width': '30%','display': 'inline-block', 'marginLeft':'100px', 'paddingLeft':'50px'})]


def generate_summary(baseline_group, fairness_class, error):
    results_dict = generate_results_dict(baseline_group, fairness_class, error)
    data = {'Fairness metric': [], 'Pass or Fail?': []}
    for metric in fairness_metrics:
        data['Fairness metric'].append(metric['name'])
        pass_fail = 'Pass'
        for c in results_dict[metric['tag']].keys():
            if not results_dict[metric['tag']][c]:
                pass_fail = 'Fail'
        data['Pass or Fail?'].append(pass_fail)
    df = pd.DataFrame(data)
    out_html = [html.Div(html.H3(html.B('Executive Summary', style={'width':'50%'}))),
                html.Br(),
                html.Div("""The below shows each of the fairness metrics considered, and whether or not they passed or failed for one or more
                             of the groups in the protected class.""")]
    out_html += generate_table('summary-table', df)
    out_html += [html.Hr()]
    return out_html

def generate_results_dict(baseline_group, fairness_class, error):
    results_dict = {}
    for metric in fairness_metrics:
        results_dict[metric['tag']] = {}
        for c in fairness_class.keys():
            if c == 'confusion_metrics':
                continue
            if metric['tag'] == 'equalised_odds':
                if results_dict['equal_opp'][c] and results_dict['predictive_equality'][c]:
                    results_dict[metric['tag']][c] = True
                else:
                    results_dict[metric['tag']][c] = False
            elif fairness_class[c][metric['tag']] > error/100:
                results_dict[metric['tag']][c] = False
            elif fairness_class[c][metric['tag']] < -1*error/100:
                results_dict[metric['tag']][c] = False
            else:
                results_dict[metric['tag']][c] = True
    return results_dict


def get_eodd_results(baseline_group, fairness_class, metric, error):
    result_block = []
    data = {'Comparison Group' : [], 'Pass or Fail?' : [], 'Rationale': []}
    for c in fairness_class.keys():
        if c == 'confusion_metrics':
            continue
        if abs(fairness_class[c]['equal_opp']) > error/100 and abs(fairness_class[c]['predictive_equality']) > error/100:
            data['Comparison Group'].append(c)
            data['Pass or Fail?'].append(html.B(html.B('Fail')))
            data['Rationale'].append(f"""Both Equal Opportunity and Predictive Equality failed""")
        elif abs(fairness_class[c]['equal_opp']) > error/100:
            data['Comparison Group'].append(c)
            data['Pass or Fail?'].append(html.B(html.B('Fail')))
            data['Rationale'].append(f"""Equal Opportunity failed""")
        elif abs(fairness_class[c]['predictive_equality']) > error/100:
            data['Comparison Group'].append(c)
            data['Pass or Fail?'].append(html.B(html.B('Fail')))
            data['Rationale'].append(f"""Predictive Equality failed""")
        else:
            data['Comparison Group'].append(c)
            data['Pass or Fail?'].append('Passed')
            data['Rationale'].append(f"""Both Equal Opportunity and Predictive Equality passed""")
    df = pd.DataFrame(data)     
    result_block += generate_table(f"{metric['name']}-table", df)
    return [html.Div(result_block)]

def generate_html_block(baseline_group, metric, fairness_class, error):
    return [html.Div(html.H4(html.B(metric['name'], style={'width':'50%'}))),
            html.Div(html.H5('Description')),
            html.Div(metric['description'], style={'width':'50%'}), 
            html.Br(),
            html.Div(metric['link'], style={'width':'50%'}),
            html.Br(),
            html.Div(html.H5('Results')),
            html.Div(generate_results(baseline_group, metric, fairness_class, error), style={'width':'50%'})]

def generate_table(div_name, dataframe, max_rows=26):
    return [html.Div(id = div_name, 
        children = [html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns]) ] +
        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )])]

def generate_results(baseline_group, metric, fairness_class, error):
    result_block = []
    data = {'Comparison Group' : [], 'Pass or Fail?' : [], 'Rationale': []}
    
    result_block.append(html.Div(f"""For the {metric["name"]} metric, we have the following results comparing with the baseline group {baseline_group}:"""))
    
    result_block.append(html.Br())
    for c in fairness_class.keys():
        if c == 'confusion_metrics':
            continue
        if metric['tag'] == 'equalised_odds':
            continue
        elif fairness_class[c][metric['tag']] > error/100:
            data['Comparison Group'].append(c)
            data['Pass or Fail?'].append(html.B('Fail'))
            data['Rationale'].append(f"""The value, {round(fairness_class[c][metric['tag']], 2)} is greater than 
                                 the specified error {error/100}""")
        elif fairness_class[c][metric['tag']] < -1*error/100:
            data['Comparison Group'].append(c)
            data['Pass or Fail?'].append(html.B('Fail'))
            data['Rationale'].append(f"""The value, {round(fairness_class[c][metric['tag']], 2)} is less than 
                                 the specified error {-1*error/100}""")
        else:
            data['Comparison Group'].append(c)
            data['Pass or Fail?'].append('Pass')
            data['Rationale'].append(f"""The value, {round(fairness_class[c][metric['tag']], 2)} is within the specified tolerance""")
    df = pd.DataFrame(data)
    if metric['tag'] != 'equalised_odds':
        result_block += generate_table(f"{metric['name']}-table", df)
    return html.Div(result_block)

def get_bar_chart(baseline_group, fairness_class, metric, error):
    x = []
    y = []
    y_line_pos = []
    y_line_neg = []

    for c in fairness_class.keys():
        if c == 'confusion_metrics':
            continue
        if fairness_class[c][metric['tag']] > error/100 or fairness_class[c][metric['tag']] < -1*error/100:
            x.append(f'<b>{c}</b>')
        else:
            x.append(c)
        y.append(fairness_class[c][metric['tag']])
        y_line_pos.append(error/100)
        y_line_neg.append(-1*error/100)

    data_item = [{'x': x, 'y': y, 'type': 'bar', 'name':'Value'}, 
    {'x': x, 'y': y_line_pos, 'type': 'line', 'name':'Threshold', 'line': {
                'color': 'rgb(0, 0, 0)',
                'dash': 'dot'
            }}, 
    {'x': x, 'y': y_line_neg, 'type': 'line', 'name':'Threshold', 'line': {
                'color': 'rgb(0, 0, 0)',
                'dash': 'dot'
            }}]
    return [html.Div(dcc.Graph(
        id=f'{metric["name"]}-graph',
        figure={
            'data':data_item,
            'layout': {
                'title': f'{metric["name"]}:<br> {baseline_group} compared with '
            },'showlegend':False
        })
    ,style={'width': '30%','display': 'inline-block'})]