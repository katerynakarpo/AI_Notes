from dash import html, dcc
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify
from layouts_methods import get_note_table
from db.db_methods import get_notes_limited, get_notes_number

create_note_btn = dbc.Button([html.Img(src=f'./assets/icons/add_note.png', alt='image',
                                       height='30', width='30', style={'margin-right': '7px'}),
                              "Create Note"], id=f"add-note-btn",
                             color="success", outline=True, style={'height': '45px'})

search_input = dbc.InputGroup(
    [dbc.Input(
        type="text",
        id='search-notes-input',
        placeholder="Search in your notes",
        persistence=False,
        autocomplete="off",
        style={'height': '45px'}
    ),
        dbc.Button(children=DashIconify(icon="line-md:search-twotone"),
                   id="search-btn", color="success"), ])

create_note_modal_window = dbc.Modal(
    [
        dbc.ModalHeader(close_button=True, style={'border': 'none', 'margin-bottom': '0', 'padding-bottom': '0'}),
        dbc.ModalBody([
            dcc.Textarea(
                id='note-textarea',
                placeholder='Write here your note...',
                style={'width': '100%', 'height': 200, 'border': 'none', 'outline': 'none', 'resize': 'none'},
            ),
            dbc.Button("Submit", id="create-note-submit-btn", n_clicks=0)
        ])],
    id="create-note-modal",
    is_open=False, )

cancel_btn = dbc.Button(
    DashIconify(icon="hugeicons:cancel-circle"),
    id='search-cancel-btn',
    n_clicks=0,
    color='danger', style={'display': 'none', 'height': '45px'})


def get_layout():
    notes_per_page = 5
    total_notes = get_notes_number()
    get_existing_notes = get_notes_limited(notes_per_page, 0)
    note_cards_table = get_note_table(notes_per_page=5, total_notes=total_notes, notes_list=get_existing_notes)

    return html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Row([dbc.Col(search_input),
                         dbc.Col(cancel_btn), ])], width=8),
            dbc.Col([create_note_btn,
                     create_note_modal_window], width=4),
        ]),
        dbc.Row([note_cards_table], style={"margin-top": "15px"})
    ], style={'width': '100%', 'margin': '20px auto 0', })
