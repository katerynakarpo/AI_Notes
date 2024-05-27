import dash
from dash import Dash, Output, Input, State, ALL, ctx, Patch, MATCH
from layouts_methods import get_new_note_card
from db.db_methods import add_note, update_note, delete_note, add_search_prompt, get_notes_number


def register_callbacks(app: Dash) -> None:

    @app.callback(
        [Output("create-note-modal", "is_open", allow_duplicate=True),
         Output('note-textarea', 'value', allow_duplicate=True), ],
        [Input("add-note-btn", "n_clicks")],
        prevent_initial_call=True
    )
    def toggle_modal(n1):
        if n1:
            return True, ''

    @app.callback(
        {
            "note_cards": Output('notes-datatable', 'children'),
            "modal_is_open": Output("create-note-modal", "is_open"),
            "modal-text": Output('note-textarea', 'value'),
            "notes-container": Output('notes-container', 'style')
        },
        [Input('create-note-submit-btn', 'n_clicks'),
         Input({'type': 'delete-note-btn', 'index': ALL}, 'n_clicks')],
        [State('note-textarea', 'value'),
         State('notes-datatable', 'children'),
         State('notes-container', 'style')],
        prevent_initial_call=True
    )
    def create_delete_notes(submit_n_clicks, delete_n_clicks, note, all_notes, style_table):
        trigger = ctx.triggered_id
        if trigger == 'create-note-submit-btn':
            note_id = add_note(note_text=note)  # insert note into DB
            new_note = get_new_note_card(note, note_id)
            all_notes.insert(0, new_note)
            style_table['display'] = "block"
            return {
                "note_cards": all_notes,
                "modal_is_open": False,
                "modal-text": "",
                "notes-container": style_table
            }

        if trigger and type(trigger) != str and trigger.get('type', '') == 'delete-note-btn':
            index_to_delete = trigger['index']
            delete_note(note_id=index_to_delete)  # delete note from DB
            note_cards = list(filter(lambda x: x['props']['id']['index'] != index_to_delete, all_notes))
            style_table['display'] = 'block' if note_cards else 'none'
            return {
                "note_cards": note_cards,
                "modal_is_open": False,
                "modal-text": "",
                "notes-container": style_table
            }

    @app.callback(
        {
            'is_open': Output({'type': 'modal-preview', 'index': MATCH}, 'is_open'),
            'text_modal': Output({'type': 'preview-textarea', 'index': MATCH}, 'value'),
            'text_note': Output({'type': 'note-text', 'index': MATCH}, 'children'),
        },
        [Input({'type': 'update-note-btn', 'index': MATCH}, 'n_clicks'),
         Input({'type': 'update-note-submit-btn', 'index': MATCH}, 'n_clicks')],
        [State({'type': 'note-text', 'index': MATCH}, 'children'),
         State({'type': 'preview-textarea', 'index': MATCH}, 'value')],
        prevent_initial_call=True
    )
    def edit_notes(update_n_clicks, update_submit_btn, note, modal_text):
        trigger = ctx.triggered_id
        trigger_type, ind_id = trigger.get('type', None), trigger.get('index', None)
        if trigger_type is None or ind_id is None:
            return {
                'is_open': False,
                'text_modal': "",
                'text_note': dash.no_update
            }
        if trigger_type == 'update-note-btn':
            return {
                'is_open': True,
                'text_modal': note,
                'text_note': dash.no_update
            }
        if trigger_type == 'update-note-submit-btn':
            update_note(note_id=ind_id, new_text=modal_text)  # Update text in DB
            return {
                'is_open': False,
                'text_modal': "",
                'text_note': modal_text
            }

    @app.callback(
        [Output('search-cancel-btn', 'style'),
         Output('search-btn', 'children'),
         Output('search-btn', 'color'),
         ],
        [Input('search-notes-input', 'value'),
         Input('search-btn', 'n_clicks')],
        State('search-cancel-btn', 'style')
    )
    def search_notes(search_text, search_n_clicks, style_search_btn):
        if search_text and search_n_clicks:
            style_search_btn['display'] = "block"
            return style_search_btn, dash.no_update, dash.no_update
        else:
            return dash.no_update, dash.no_update, dash.no_update
