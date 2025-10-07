# ui.py
from shiny import ui
from shinywidgets import output_widget

# Set to True to greatly enlarge chat UI (for presenting to a larger audience)
DEMO_MODE = False # Or True, depending on your default preference

app_ui = ui.page_fluid(
    ui.panel_title("Shiny Python Demo"),
    ui.output_text("txt")
)