import itertools
import json

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import pandas as pd
from dash.dependencies import Input, Output
import os
import flask
from random import shuffle
import numpy as np

####
from utils import excel_cols

server = flask.Flask(__name__)
server.secret_key = os.environ.get('secret_key', str(np.random.randint(0, 1000000)))
app = dash.Dash(__name__, server=server)
####

DF_SIMPLE = pd.DataFrame({
    'x': ['A', 'B', 'C', 'D', 'E', 'F'],
    'y': [4, 3, 1, 2, 3, 6],
    'z': ['a', 'b', 'c', 'a', 'b', 'c']
})

n_rows = 1000
df_rows = pd.DataFrame({
    'x': list(itertools.islice(excel_cols(), n_rows)),
    'y':np.random.randint(0,n_rows*10, n_rows),
    'z': shuffle(list(itertools.islice(excel_cols(), n_rows)))
})

app.layout = html.Div([
    html.H4('Editable DataTable'),
    dt.DataTable(
        rows=df_rows.to_dict('records'),

        # optional - sets the order of columns
        columns=sorted(df_rows.columns),

        editable=True,

        id='editable-table'
    ),

    html.Div([
        html.Pre(id='output', className='two columns'),
    '''
        html.Div(
            dcc.Graph(
                id='graph',
                style={
                    'overflow-x': 'wordwrap'
                }
            ),
            className='ten columns'
        )
    '''
    ], className='row')
], className='container')


@app.callback(
    Output('output', 'children'),
    [Input('editable-table', 'rows')])
def update_selected_row_indices(rows):
    return json.dumps(rows, indent=2)

'''
@app.callback(
    Output('graph', 'figure'),
    [Input('editable-table', 'rows')])
def update_figure(rows):
    dff = pd.DataFrame(rows)
    return {
        'data': [{
            'x': dff['x'],
            'y': dff['y'],
        }],
        'layout': {
            'margin': {'l': 10, 'r': 0, 't': 10, 'b': 20}
        }
    }

'''

app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

if __name__ == '__main__':
    # Run the Dash app
    app.server.run(debug=True, threaded=True)