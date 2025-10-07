# ui.py
from shiny import ui
from shinywidgets import output_widget

# Set to True to greatly enlarge chat UI (for presenting to a larger audience)
DEMO_MODE = False # Or True, depending on your default preference

app_ui = ui.page_fluid(
    ui.panel_title("ADK Chat Interface"),
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.input_text("user_message", "Enter your message:", placeholder="Type your message here..."),
            ui.input_action_button("send", "Send", class_="btn-primary"),
            width=3
        ),
        ui.panel_main(
            ui.div(
                ui.output_ui("chat_history"),
                style="height: 600px; overflow-y: auto; border: 1px solid #ddd; padding: 10px; margin-bottom: 10px;"
            )
        )
    )
)