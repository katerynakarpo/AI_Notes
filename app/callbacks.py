import dash
import numpy as np
from dash import Dash, Output, Input, State, ALL, ctx, MATCH
from layouts_methods import get_new_note_card
import db.db_methods as db
from search import get_embeddings, search_by_embeddings_emb


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
            "notes-container": Output('notes-container', 'style'),
            "pagination": Output('notes-pagination', 'max_value'),
            "active_page": Output('notes-pagination', 'active_page'),
            "search_cancel_btn": Output('search-cancel-btn', 'style'),
            "search_btn": Output('search-btn', 'children'),
            "pagination_search": Output('pages-control-container', 'style'),
            "search_text": Output('search-notes-input', 'value'),
        },

        [Input('create-note-submit-btn', 'n_clicks'),
         Input({'type': 'delete-note-btn', 'index': ALL}, 'n_clicks'),
         Input('page-size-input', 'value'),
         Input('notes-pagination', 'active_page'),
         Input('search-notes-input', 'value'),
         Input('search-btn', 'n_clicks'),
         Input('search-cancel-btn', 'n_clicks')
         ],
        [State('note-textarea', 'value'),
         State('notes-datatable', 'children'),
         State('notes-container', 'style'),
         State('search-cancel-btn', 'style'),
         State('page-size-input', 'value'),
         State('notes-pagination', 'active_page'),
         State('pages-control-container', 'style')],
        prevent_initial_call=True
    )
    def update_notes_datatable(submit_n_clicks, delete_n_clicks, notes_per_page, active_page, search_text,
                               search_btn_click, cancel_search_bnt_click,
                               note, all_notes, style_table, style_search_btn, note_page_size_state, active_page_state,
                               pagination_style):
        outputs = {
            "note_cards": dash.no_update,
            "modal_is_open": False,
            "modal-text": "",
            "notes-container": dash.no_update,
            "pagination": dash.no_update,
            "active_page": dash.no_update,
            "search_cancel_btn": style_search_btn,
            "search_btn": dash.no_update,
            "pagination_search": dash.no_update,
            "search_text": dash.no_update,
        }

        trigger = ctx.triggered_id
        if trigger == 'create-note-submit-btn':
            note_id = db.add_note(note, get_embeddings(text=note))
            all_notes.insert(0, get_new_note_card(note, note_id))
            style_table['display'] = "block"
            outputs['note_cards'] = all_notes[:note_page_size_state]
            outputs['notes-container'] = style_table
        elif trigger and type(trigger) != str and trigger.get('type', '') == 'delete-note-btn':
            index_to_delete = trigger['index']
            db.delete_note(note_id=index_to_delete)  # delete note from DB

            note_cards = list(filter(lambda x: x['props']['id']['index'] != index_to_delete, all_notes))
            style_table['display'] = 'block' if note_cards else 'none'

            outputs['note_cards'] = note_cards
            outputs['notes-container'] = style_table
        elif trigger == 'notes-pagination':
            notes = db.get_notes_limited(notes_per_page, active_page * notes_per_page - notes_per_page)
            outputs['note_cards'] = [get_new_note_card(note, note_id) for note_id, note in notes]
        elif trigger == 'page-size-input':
            active_page = 1
            notes = db.get_notes_limited(notes_per_page, 0)

            outputs['note_cards'] = [get_new_note_card(note, note_id) for note_id, note in notes]
            outputs['pagination'] = np.ceil(db.get_notes_number() / notes_per_page)
            outputs['active_page'] = active_page
        elif trigger == 'search-btn':
            if search_text:
                search_embedding = get_embeddings(search_text)
                db.add_search_prompt(prompt=search_text, prompt_embedding=search_embedding)
                emb_list_from_db = db.get_all_notes_embeddings()
                search_result_df = search_by_embeddings_emb(search_embedding=search_embedding,
                                                            note_embeddings=emb_list_from_db)
                notes = db.get_notes_by_ids(search_result_df['note_id'])
                searched_notes_table = [get_new_note_card(note, note_id) for note_id, note in notes]
                style_search_btn['display'] = "block"
                pagination_style['display'] = "none"

                outputs['note_cards'] = searched_notes_table
                outputs['search_cancel_btn'] = style_search_btn
                outputs['pagination_search'] = pagination_style
        elif trigger == 'search-cancel-btn':
            style_search_btn['display'] = "none"
            pagination_style['display'] = "block"

            notes = db.get_notes_limited(note_page_size_state, (active_page_state - 1) * note_page_size_state)
            outputs['search_cancel_btn'] = style_search_btn
            outputs['pagination_search'] = pagination_style
            outputs['note_cards'] = [get_new_note_card(note, note_id) for note_id, note in notes]
            outputs['search_text'] = ''

        return outputs

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
        outputs = {
            'is_open': False,
            'text_modal': "",
            'text_note': dash.no_update
        }
        trigger = ctx.triggered_id
        trigger_type, ind_id = trigger.get('type', None), trigger.get('index', None)

        if trigger_type == 'update-note-btn':
            outputs['is_open'] = True
            outputs['text_modal'] = note

        elif trigger_type == 'update-note-submit-btn':
            db.update_note(note_id=ind_id, new_text=modal_text)  # Update text in DB
            outputs['text_note'] = modal_text
        return outputs
