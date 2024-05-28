from dash import Dash, Output, Input, State, ALL, ctx, html, Patch, MATCH, dcc
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify
import numpy as np


def create_empty_modal(note_index: int):
    return dbc.Modal([dbc.ModalHeader(close_button=True,
                                      style={'border': 'none', 'margin-bottom': '0', 'padding-bottom': '0'}),
                      dbc.ModalBody([
                          dcc.Textarea(
                              id={'type': 'preview-textarea', 'index': note_index},
                              style={'width': '100%', 'height': 200, 'border': 'none', 'outline': 'none',
                                     'resize': 'none'}, ),

                          dbc.Button("Submit",
                                     id={'type': 'update-note-submit-btn',
                                         'index': note_index},
                                     n_clicks=0)
                      ])],
                     id={'type': 'modal-preview', 'index': note_index},
                     is_open=False
                     )


def get_new_note_card(note: str, note_index: int):
    note_card = html.Tr([
        html.Td(html.B(note, id={'type': 'note-text', 'index': note_index}), ),
        html.Td(dbc.Container([
            dbc.Button(DashIconify(icon="mi:delete"),
                       id={'type': 'delete-note-btn', 'index': note_index},
                       n_clicks=0,
                       color='danger', ),
            dbc.Button(DashIconify(icon="bx:edit"),
                       id={'type': 'update-note-btn', 'index': note_index},
                       n_clicks=0,
                       color='secondary', ),
            create_empty_modal(note_index)]), style={'text-align': 'right'}),
    ], id={'type': 'tr-notes-table', 'index': note_index})
    return note_card


def get_note_table(notes_per_page: int, total_notes: str, notes_list: list = None):
    display = 'block'
    if notes_list is None:
        notes_list = []
        display = 'none'
    notes_list_html = [get_new_note_card(note, note_id) for note_id, note in notes_list]
    note_cards_table = html.Div([
        dbc.Table(id='notes-datatable', children=notes_list_html),

        html.Div(dbc.Row([
            dbc.Col(dbc.Input(id="page-size-input", type="number", value=notes_per_page,
                              placeholder="Enter number of notes per page",
                              min=1, max=40
                              ), width=3, style={'maxWidth': 300}),
            dbc.Col(dbc.Pagination(id="notes-pagination", max_value=np.ceil(total_notes / notes_per_page),
                                   fully_expanded=False, active_page=1),
                    width=8,)],
            ), id='pages-control-container', style={'display': display,})

    ], id='notes-container', style={'display': display})
    return note_cards_table


def search_cansel_btn():
    cansel_button = dbc.Button(
        DashIconify(icon="hugeicons:cancel-circle"),
        id='search-cancel-btn',
        n_clicks=0,
        color='danger', style={'display': 'none'}),
    return cansel_button
