from dash import Dash, html, Input, Output, dcc
import dash_bootstrap_components as dbc
from layouts import get_layout
from callbacks import register_callbacks

app = Dash(external_stylesheets=[
    "https://cdn.datatables.net/1.13.4/css/jquery.dataTables.min.css",
    "https://cdn.datatables.net/1.13.4/css/dataTables.bootstrap5.min.css",
    "https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/5.2.0/css/bootstrap.min.css",
    dbc.themes.BOOTSTRAP,
    dbc.icons.FONT_AWESOME
],
    external_scripts=[
        "https://code.jquery.com/jquery-3.5.1.js",
        "https://cdn.datatables.net/1.13.4/js/jquery.dataTables.min.js",
        "https://cdn.datatables.net/1.13.4/js/dataTables.bootstrap5.min.js",
    ],
    include_assets_files=True,
    suppress_callback_exceptions=True,
    update_title=None, )

app.title = 'AINotes'
app.layout = html.Div([
    dcc.Location(id="dashboard_url"),
    html.Div([
        html.Div(get_layout(), id="dashboard_container")
    ], style={'width': '95%', 'margin': '0 auto 0'})])
register_callbacks(app)

if __name__ == '__main__':
    @app.callback(
        Output("dashboard_container", "children"),
        [Input("dashboard_url", "pathname")],
        prevent_initial_call=True
    )
    def refresh_table(pathname):
        layout = get_layout()
        return layout


    app.run_server(host="0.0.0.0", port="9000", debug=True)
