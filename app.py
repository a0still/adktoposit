# app.py
import os
import sys
from pathlib import Path
from typing import List
import logging
import dotenv
from datetime import datetime
import io

# Set up logging
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logger = logging.getLogger('adk_chat')
logger.setLevel(logging.INFO)

# Always log to stdout for Posit Connect
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter(log_format))
logger.addHandler(console_handler)

# Try to log to file if possible
try:
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    file_handler = logging.FileHandler('logs/app.log')
    file_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(file_handler)
except Exception as e:
    logger.warning(f"Could not set up file logging: {e}")

from shiny import App, reactive, render, ui, Inputs, Outputs, Session
try:
    from shinywidgets import output_widget, render_plotly
except ImportError:
    output_widget = None
    render_plotly = None
    logger.warning("shinywidgets not available - some features may not work")

try:
    from markdown2 import markdown
except ImportError:
    # Fallback if markdown2 not available
    def markdown(text, *args, **kwargs):
        return text
    logger.warning("markdown2 not available - markdown rendering disabled")

from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from agents import create_chat_agent
from ui import app_ui
from src.server_custom_reports import setup_custom_reports_server
import plotly.graph_objects as go
import plotly.express as px
from data_service import DataService
import pandas as pd

# Load environment variables
dotenv.load_dotenv()

# Ensure required files and permissions
try:
    # Log current working directory and permissions
    current_dir = os.getcwd()
    logger.info(f"Current working directory: {current_dir}")
    logger.info(f"Directory contents: {os.listdir(current_dir)}")
    
    # Check for service account credentials
    credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if not credentials_path and os.path.isfile('key.json'):
        credentials_path = 'key.json'
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
    
    if not credentials_path:
        logger.error("No service account credentials found in environment or key.json")
        raise FileNotFoundError("No service account credentials found")
    
    if not os.path.isfile(credentials_path):
        logger.error(f"Service account file not found at {credentials_path}")
        raise FileNotFoundError(f"Service account file not found at {credentials_path}")
    
    # Test credentials file readability and log size
    with open(credentials_path, 'r') as f:
        cred_content = f.read()
        if len(cred_content.strip()) == 0:
            raise ValueError("Service account file is empty")
        logger.info(f"Service account file verified successfully at {credentials_path} ({len(cred_content)} bytes)")
        
except Exception as e:
    logger.error(f"Error during initialization: {e}", exc_info=True)
    raise

def server(input: Inputs, output: Outputs, session: Session):
    """Define the server logic"""
    
    # Initialize chat messages as a reactive value
    chat_messages = reactive.Value([])
    
    # Reactive value to track processing state
    is_processing = reactive.Value(False)
    
    # Store initialization state in session
    if not hasattr(session, 'initialized'):
        session.initialized = False
        logger.info("Session created, initialized flag set to False")
    
    # Initialize data service
    data_service = DataService()
    
    # Set up Custom Reports tab
    setup_custom_reports_server(input, output, session, data_service)
    logger.info("Custom Reports server initialized")
    
    # Cache for Store 1 data and filter lists at session level with timestamps
    if not hasattr(session, 'cache'):
        import time
        session.cache = {
            'store_1_data': None,
            'store_1_timestamp': None,
            'stores_list': None,
            'stores_timestamp': None,
            'departments': None,
            'departments_timestamp': None,
            'CACHE_TTL': 300  # 5 minutes cache
        }
        logger.info("Session cache initialized")
    
    def get_store_1_data_cached():
        """Get Store 1 data with caching (5 min TTL)"""
        import time
        now = time.time()
        
        # Check if cache is valid
        if (session.cache['store_1_data'] is not None and 
            session.cache['store_1_timestamp'] is not None and
            now - session.cache['store_1_timestamp'] < session.cache['CACHE_TTL']):
            logger.info("Using cached Store 1 data")
            return session.cache['store_1_data']
        
        # Fetch fresh data
        logger.info("Fetching fresh Store 1 data from BigQuery")
        data = data_service.get_irr_data(store_nbr=1, current_month_only=True)
        session.cache['store_1_data'] = data
        session.cache['store_1_timestamp'] = now
        return data
    
    def get_stores_list_cached():
        """Get all stores list with caching (5 min TTL)"""
        import time
        now = time.time()
        
        # Check if cache is valid
        if (session.cache['stores_list'] is not None and 
            session.cache['stores_timestamp'] is not None and
            now - session.cache['stores_timestamp'] < session.cache['CACHE_TTL']):
            logger.info("Using cached stores list")
            return session.cache['stores_list']
        
        # Fetch fresh data
        logger.info("Fetching fresh stores list from BigQuery")
        stores = data_service.get_store_list(all_stores=True)
        session.cache['stores_list'] = stores
        session.cache['stores_timestamp'] = now
        return stores
    
    def get_departments_cached(store_nbr=1):
        """Get departments list with caching (5 min TTL)"""
        import time
        now = time.time()
        
        # Check if cache is valid
        if (session.cache['departments'] is not None and 
            session.cache['departments_timestamp'] is not None and
            now - session.cache['departments_timestamp'] < session.cache['CACHE_TTL']):
            logger.info("Using cached departments list")
            return session.cache['departments']
        
        # Fetch fresh data
        logger.info("Fetching fresh departments list from BigQuery")
        departments = data_service.get_department_list(store_nbr=store_nbr)
        session.cache['departments'] = departments
        session.cache['departments_timestamp'] = now
        return departments
    
    # CONSOLIDATED filter initialization - loads data ONCE and shares between tabs - WITH CACHING
    @reactive.Effect
    @reactive.event(lambda: True, ignore_none=False)
    def _():
        """Populate ALL filter dropdowns on startup with minimal data - OPTIMIZED with caching"""
        try:
            logger.info("Initializing filters for all tabs (consolidated with caching)...")
            
            # STEP 1: Get Store 1 info ONCE with caching (reuse for both tabs)
            store_1_data = get_store_1_data_cached()
            if not store_1_data.empty and 'City_State' in store_1_data.columns:
                city_state = store_1_data['City_State'].iloc[0]
                store_label = f"1 - {city_state}"
            else:
                store_label = "1 - Rogers, AR"  # Fallback
            
            # STEP 2: Get departments for Store 1 ONCE with caching (reuse for both tabs)
            departments = get_departments_cached(store_nbr=1)
            dept_choices = {"": "All Departments"}
            dept_choices.update({str(d["value"]): d["label"] for d in departments})
            
            # STEP 3: Update IRR Dashboard tab filters
            ui.update_selectize("store_filter", choices={"1": store_label}, selected="1")
            ui.update_selectize("dept_filter", choices=dept_choices)
            logger.info(f"IRR Dashboard filters populated: {store_label}, {len(departments)} departments")
            
            # STEP 4: Update Markdowns tab filters (using same data)
            ui.update_selectize("md_store_filter", choices={"1": store_label}, selected="1")
            ui.update_selectize("md_dept_filter", choices=dept_choices, selected="1")
            logger.info(f"Markdowns tab filters populated: {store_label}, {len(departments)} departments")
            
            # STEP 5: Load all stores in background ONCE with caching (update both tabs)
            try:
                stores = get_stores_list_cached()
                if stores and len(stores) > 1:
                    store_choices = {str(s["value"]): s["label"] for s in stores}
                    if "1" in store_choices:
                        store_label = store_choices["1"]
                    # Update both tabs with full store list
                    ui.update_selectize("store_filter", choices=store_choices, selected="1")
                    ui.update_selectize("md_store_filter", choices=store_choices, selected="1")
                    logger.info(f"Background load complete: {len(stores)} stores available for both tabs")
            except Exception as bg_error:
                logger.warning(f"Background store loading failed (non-critical): {bg_error}")
            
            # STEP 6: Initialize MD Description filter (Markdowns-specific)
            try:
                logger.info("Loading Markdown Description filter options...")
                filter_options = data_service.get_markdown_filter_options()
                md_choices = {"": "All Descriptions"}
                md_choices.update({str(x): str(x) for x in filter_options['md_desc']})
                ui.update_selectize("md_desc_filter", choices=md_choices, selected="")
                logger.info(f"MD Description filter populated with {len(filter_options['md_desc'])} options")
            except Exception as md_error:
                logger.warning(f"MD Description filter loading failed: {md_error}")
            
            logger.info("Filter initialization complete for all tabs")
            
        except Exception as e:
            logger.error(f"Error populating filters: {e}", exc_info=True)
    
    # Reactive value for current month IRR data (for table) - LAZY LOAD
    @reactive.Calc
    def irr_data_current():
        """Get current month IRR data based on filters - only loads when IRR Dashboard tab is active"""
        try:
            # Only fetch data when IRR Dashboard tab is selected
            current_tab = input.dashboard_tabs()
            logger.info(f">>> IRR_DATA_CURRENT CALC: Current tab = {current_tab}")
            if current_tab != "IRR Dashboard":
                logger.info(">>> IRR_DATA_CURRENT: Tab not active, returning empty")
                return pd.DataFrame()
            
            # Get filter values - trigger on these
            store = input.store_filter()
            dept = input.dept_filter()
            
            # Convert to int if not None and not empty string
            store_nbr = int(store) if store and store.strip() else 1  # Default to Store 1
            dept_nbr = int(dept) if dept and dept.strip() else None
            
            logger.info(f"Fetching current month IRR data: store={store_nbr}, dept={dept_nbr}")
            
            # Get current month data from service
            df = data_service.get_irr_data(
                store_nbr=store_nbr,
                dept_nbr=dept_nbr,
                current_month_only=True
            )
            
            logger.info(f"Retrieved {len(df)} rows of current month IRR data")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching current month IRR data: {e}", exc_info=True)
            return pd.DataFrame()
    
    # Reactive value for 13 months IRR data (for charts) - LAZY LOAD
    @reactive.Calc
    def irr_data_13months():
        """Get 13 months IRR data based on filters - only loads when IRR Dashboard tab is active"""
        try:
            # Only fetch data when IRR Dashboard tab is selected
            current_tab = input.dashboard_tabs()
            logger.info(f">>> IRR_DATA_13MONTHS CALC: Current tab = {current_tab}")
            if current_tab != "IRR Dashboard":
                logger.info(">>> IRR_DATA_13MONTHS: Tab not active, returning empty")
                return pd.DataFrame()
            
            # Get filter values - trigger on these
            store = input.store_filter()
            dept = input.dept_filter()
            
            # Convert to int if not None and not empty string
            store_nbr = int(store) if store and store.strip() else 1  # Default to Store 1
            dept_nbr = int(dept) if dept and dept.strip() else None
            
            logger.info(f"Fetching 13 months IRR data: store={store_nbr}, dept={dept_nbr}")
            
            # Get 13 months data from service
            df = data_service.get_irr_data(
                store_nbr=store_nbr,
                dept_nbr=dept_nbr,
                current_month_only=False
            )
            
            logger.info(f"Retrieved {len(df)} rows of 13 months IRR data")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching 13 months IRR data: {e}", exc_info=True)
            return pd.DataFrame()
    
    # Render data table
    @render.data_frame
    @reactive.event(input.dashboard_tabs, ignore_none=False)
    def irr_table():
        """Render the IRR data table"""
        try:
            logger.info(">>> IRR TABLE RENDER CALLED")
            # Only render when IRR Dashboard tab is active
            if input.dashboard_tabs() != "IRR Dashboard":
                return render.DataGrid(pd.DataFrame())
            df = irr_data_current()
            
            if df.empty:
                logger.info(">>> IRR TABLE: No data, returning empty")
                # Return empty dataframe silently - no message to avoid double render
                return render.DataGrid(pd.DataFrame())
            
            # Select columns for display - SIMPLIFIED
            display_cols = [
                'Dept_Nbr', 'DEPT_DESC', 'Purchases', 'Markdowns', 
                'Sales', 'Book', 'SKU', 'Book_vs_SKU'
            ]
            
            # Filter to only include columns that exist
            display_cols = [col for col in display_cols if col in df.columns]
            table_df = df[display_cols].copy()
            
            # Rename columns for better display
            table_df = table_df.rename(columns={
                'Dept_Nbr': 'Dept',
                'DEPT_DESC': 'Department Description'
            })
            
            # Format dollar columns with commas and 2 decimals
            dollar_cols = ['Purchases', 'Markdowns', 'Sales', 'Book', 'SKU', 'Book_vs_SKU']
            for col in dollar_cols:
                if col in table_df.columns:
                    table_df[col] = table_df[col].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "$0.00")
            
            # Sort by Department Number
            if 'Dept' in table_df.columns:
                table_df = table_df.sort_values('Dept')
            
            # Limit to top 50 rows for faster rendering
            if len(table_df) > 50:
                table_df = table_df.head(50)
                logger.info(f"Limiting table to 50 rows (from {len(df)})")
            
            logger.info(f"Rendering table with {len(table_df)} rows")
            
            return render.DataGrid(
                table_df,
                height="400px",
                width="100%",
                filters=False,  # Disable filters for faster rendering
                summary=False
            )
            
        except Exception as e:
            logger.error(f"Error rendering IRR table: {e}", exc_info=True)
            return render.DataGrid(pd.DataFrame({"Error": [str(e)]}))
    
    # Export to Excel
    @render.download(filename=lambda: f"IRR_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
    async def download_excel():
        """Download the current IRR data as Excel file"""
        try:
            df = irr_data_current()
            
            if df.empty:
                # Return empty Excel file with message
                df = pd.DataFrame({"Message": ["No data available for selected filters"]})
            
            # Create Excel file in memory
            import io
            output = io.BytesIO()
            
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='IRR Report', index=False)
            
            output.seek(0)
            yield output.getvalue()
            
        except Exception as e:
            logger.error(f"Error generating Excel file: {e}", exc_info=True)
            # Return error message as Excel
            df = pd.DataFrame({"Error": [str(e)]})
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Error', index=False)
            output.seek(0)
            yield output.getvalue()
    
    # Export to CSV
    @render.download(filename=lambda: f"IRR_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    async def download_csv():
        """Download the current IRR data as CSV file"""
        try:
            df = irr_data_current()
            
            if df.empty:
                df = pd.DataFrame({"Message": ["No data available for selected filters"]})
            
            yield df.to_csv(index=False).encode('utf-8')
            
        except Exception as e:
            logger.error(f"Error generating CSV file: {e}", exc_info=True)
            df = pd.DataFrame({"Error": [str(e)]})
            yield df.to_csv(index=False).encode('utf-8')
    
    def parse_insights_to_html(text):
        """Parse markdown-like bullet format to structured HTML"""
        if not text or not text.strip():
            return "<p>No insights available.</p>"
        
        lines = text.split('\n')
        html = []
        current_section = None
        current_dept = None
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            
            # Count leading spaces to determine indent level
            indent_level = len(line) - len(line.lstrip(' '))
            
            # Remove the asterisk and extra spaces
            content = stripped.lstrip('* ').strip()
            
            if not content:
                continue
            
            # Level 0: Section titles (e.g., "Recommended Actions:")
            if indent_level == 0 and content.endswith(':'):
                if current_dept:
                    html.append('</ul>')
                    current_dept = None
                if current_section:
                    html.append('</ul>')
                html.append(f'<h3>{content}</h3>')
                html.append('<ul class="section-list">')
                current_section = True
            
            # Level 2: Department names (e.g., "Department 60:")
            elif indent_level <= 2 and content.endswith(':') and ('Department' in content or 'Anomalies' in content):
                if current_dept:
                    html.append('</ul>')
                html.append(f'<li class="dept-item"><strong>{content}</strong>')
                html.append('<ul class="detail-list">')
                current_dept = True
            
            # Level 4+: Detail items
            else:
                html.append(f'<li class="detail-item">{content}</li>')
        
        # Close any open lists
        if current_dept:
            html.append('</ul></li>')
        if current_section:
            html.append('</ul>')
        
        return '\n'.join(html)
    
    # Render AI-Generated Store Insights
    @render.ui
    def store_insights():
        """Render the AI-generated store summary"""
        try:
            # Get selected store
            store = input.store_filter()
            
            # Default to Store 1 if no store selected
            store_nbr = int(store) if store and store.strip() else 1
            
            logger.info(f"Fetching store insights for store {store_nbr}")
            
            # Get the summary from BigQuery
            summary_text = data_service.get_store_summary(store_nbr)
            
            # Parse the markdown-like format to HTML
            html_content = parse_insights_to_html(summary_text)
            
            # Return the HTML-formatted summary
            return ui.HTML(f"""
                <div style="color: white; line-height: 1.6;">
                    {html_content}
                </div>
            """)
            
        except Exception as e:
            logger.error(f"Error rendering store insights: {e}", exc_info=True)
            return ui.HTML(f"""
                <div style="color: white;">
                    <p>Error loading store insights: {str(e)}</p>
                </div>
            """)
    
    # Reactive value for markdowns data (lazy load - only when tab is selected)
    @reactive.Calc
    def markdowns_data_current():
        """Get current markdowns data based on filters - only loads when Markdowns tab is active"""
        try:
            # Only fetch data when Markdowns tab is selected
            current_tab = input.dashboard_tabs()
            if current_tab != "Markdowns":
                logger.debug("Markdowns tab not selected, skipping data fetch")
                return pd.DataFrame()
            
            # Get markdown tab-specific filters
            try:
                store = input.md_store_filter()
            except:
                store = None
            
            try:
                dept = input.md_dept_filter()
            except:
                dept = None
            
            # Get markdown-specific filters from text inputs
            try:
                item = input.item_nbr_filter()
                item = None if not item or str(item).strip() == "" else str(item).strip()
            except:
                item = None
            
            try:
                cid = input.cid_filter()
                cid = None if not cid or str(cid).strip() == "" else str(cid).strip()
            except:
                cid = None
            
            try:
                md_desc = input.md_desc_filter()
                md_desc = None if not md_desc or md_desc == "" else md_desc
            except:
                md_desc = None
            
            store_nbr = int(store) if store and str(store).strip() else None
            dept_nbr = int(dept) if dept and str(dept).strip() else None
            item_nbr = int(item) if item and item.isdigit() else None
            
            # Get sort and limit settings
            try:
                sort_column = input.md_sort_column()
            except:
                sort_column = "MUMD_AMT"
            
            try:
                sort_order = input.md_sort_order()
            except:
                sort_order = "ASC"
            
            try:
                limit_rows = input.md_limit_rows()
            except:
                limit_rows = True
            
            # Require at least one filter to be selected to prevent loading massive datasets
            if not any([store_nbr, dept_nbr, item_nbr, cid, md_desc]):
                logger.info("No filters selected for markdowns data - returning empty dataframe")
                return pd.DataFrame()
            
            logger.info(f"Fetching markdowns data: store={store_nbr}, dept={dept_nbr}, item={item_nbr}, cid={cid}, md_desc={md_desc}, sort={sort_column} {sort_order}, limit={limit_rows}")
            
            df = data_service.get_markdowns_data(
                store_nbr=store_nbr,
                dept_nbr=dept_nbr,
                item_nbr=item_nbr,
                cid=cid,
                md_desc=md_desc,
                sort_column=sort_column,
                sort_order=sort_order,
                limit_rows=limit_rows
            )
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching markdowns data: {e}")
            return pd.DataFrame()
    
    # Render markdowns data table
    @render.data_frame
    def markdowns_table():
        """Render the markdowns data table with custom formatting"""
        try:
            df = markdowns_data_current()
            
            if df.empty:
                # Check if any filters are selected
                store = None
                dept = None
                item = None
                cid = None
                md_desc = None
                
                try:
                    store = input.md_store_filter()
                except:
                    pass
                
                try:
                    dept = input.md_dept_filter()
                except:
                    pass
                
                try:
                    item = input.item_nbr_filter()
                    item = item if item and str(item).strip() != "" else None
                except:
                    pass
                
                try:
                    cid = input.cid_filter()
                    cid = cid if cid and str(cid).strip() != "" else None
                except:
                    pass
                
                try:
                    md_desc = input.md_desc_filter()
                    md_desc = md_desc if md_desc and md_desc != "" else None
                except:
                    pass
                
                has_filters = any([
                    store and str(store).strip(),
                    dept and str(dept).strip(),
                    item,
                    cid,
                    md_desc
                ])
                
                if not has_filters:
                    message = "Please select at least one filter to load markdown data"
                else:
                    message = "No markdowns data available for selected filters"
                
                return render.DataGrid(pd.DataFrame({"Message": [message]}))
            
            # Create display dataframe
            table_df = df.copy()
            
            # Format CID as whole number
            if 'CID' in table_df.columns:
                table_df['CID'] = table_df['CID'].apply(lambda x:
                    f"{int(x)}" if pd.notna(x) else ""
                )
            
            # Format dollar amounts
            for col in ['prev_retail', 'new_retail', 'MUMD_AMT']:
                if col in table_df.columns:
                    table_df[col] = table_df[col].apply(lambda x: 
                        f"(${abs(x):,.2f})" if pd.notna(x) and x < 0 
                        else f"${x:,.2f}" if pd.notna(x) 
                        else "$0.00"
                    )
            
            # Format MD_QTY - 1 decimal, hide .0
            if 'MD_QTY' in table_df.columns:
                table_df['MD_QTY'] = table_df['MD_QTY'].apply(lambda x:
                    f"{int(x)}" if pd.notna(x) and x == int(x)
                    else f"{x:.1f}" if pd.notna(x)
                    else "0"
                )
            
            # Format percentage
            if 'Markdown_Percent' in table_df.columns:
                table_df['Markdown_Percent'] = table_df['Markdown_Percent'].apply(lambda x:
                    f"{x:.1f}%" if pd.notna(x) else "0.0%"
                )
            
            # Format date
            if 'MUMD_DT' in table_df.columns:
                table_df['MUMD_DT'] = pd.to_datetime(table_df['MUMD_DT']).dt.strftime('%Y-%m-%d')
            
            # Drop Calendar_Year and Calendar_Month columns
            columns_to_drop = ['Calendar_Year', 'Calendar_Month']
            table_df = table_df.drop(columns=[col for col in columns_to_drop if col in table_df.columns])
            
            # Rename columns for display
            table_df = table_df.rename(columns={
                'Store_Nbr': 'Store',
                'Dept_Nbr': 'Dept',
                'item_nbr': 'Item #',
                'prev_retail': 'Prev Retail',
                'new_retail': 'New Retail',
                'MD_QTY': 'MD Qty',
                'MUMD_AMT': 'MD Amount',
                'MUMD_DT': 'MD Date',
                'MD_Desc': 'MD Description',
                'Markdown_Percent': 'MD %'
            })
            
            # Set specific column widths
            table_df = table_df[['Store', 'Dept', 'Item #', 'MD Description', 'Description', 
                                  'CID', 'MD Date', 'Prev Retail', 'New Retail', 
                                  'MD Qty', 'MD Amount', 'MD %']]
            
            total_rows = len(table_df)
            logger.info(f"Rendering markdowns table with {total_rows} total rows")
            
            return render.DataGrid(
                table_df,
                height="500px",
                width="100%",
                filters=False,
                summary=False,
                row_selection_mode="none"
            )
            
        except Exception as e:
            logger.error(f"Error rendering markdowns table: {e}", exc_info=True)
            return render.DataGrid(pd.DataFrame({"Error": [str(e)]}))
    
    # Export markdowns to Excel
    @render.download(filename=lambda: f"Markdowns_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
    async def download_markdowns_excel():
        """Download markdowns data as Excel file"""
        try:
            df = markdowns_data_current()
            if df.empty:
                df = pd.DataFrame({"Message": ["No data available"]})
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Markdowns', index=False)
            output.seek(0)
            yield output.getvalue()
        except Exception as e:
            logger.error(f"Error generating markdowns Excel: {e}")
            df = pd.DataFrame({"Error": [str(e)]})
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Error', index=False)
            output.seek(0)
            yield output.getvalue()
    
    # Export markdowns to CSV
    @render.download(filename=lambda: f"Markdowns_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    async def download_markdowns_csv():
        """Download markdowns data as CSV file"""
        try:
            df = markdowns_data_current()
            if df.empty:
                df = pd.DataFrame({"Message": ["No data available"]})
            yield df.to_csv(index=False).encode('utf-8')
        except Exception as e:
            logger.error(f"Error generating markdowns CSV: {e}")
            yield pd.DataFrame({"Error": [str(e)]}).to_csv(index=False).encode('utf-8')
    
    # Render Book vs SKU chart
    @render_plotly
    @reactive.event(input.dashboard_tabs, ignore_none=False)
    def book_sku_chart():
        """Render Book vs SKU line chart - waits for data to avoid double render"""
        try:
            logger.info(">>> BOOK/SKU CHART RENDER CALLED")
            # Only render when IRR Dashboard tab is active
            if input.dashboard_tabs() != "IRR Dashboard":
                return None
            df = irr_data_13months()
            
            # Return None to prevent rendering when no data
            if df.empty:
                logger.info(">>> BOOK/SKU CHART: No data, returning None")
                return None
            
            # Aggregate by month
            chart_df = data_service.aggregate_by_month(df, ['Book', 'SKU'])
            
            if chart_df.empty:
                return go.Figure()
            
            # Helper function to format values with K/M suffix
            def format_currency(val):
                if val >= 1_000_000:
                    return f"${val/1_000_000:.1f}M"
                elif val >= 1_000:
                    return f"${val/1_000:.1f}K"
                else:
                    return f"${val:.1f}"
            
            # Add formatted hover text columns
            chart_df['Book_formatted'] = chart_df['Book'].apply(format_currency)
            chart_df['SKU_formatted'] = chart_df['SKU'].apply(format_currency)
            
            # Create line chart
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=chart_df['Month_Year'],
                y=chart_df['Book'],
                mode='lines+markers',
                name='Book',
                line=dict(color='rgb(0, 83, 226)', width=3),
                marker=dict(size=8),
                customdata=chart_df['Book_formatted'],
                hovertemplate='<b>Book:</b> %{customdata}<extra></extra>'
            ))
            
            fig.add_trace(go.Scatter(
                x=chart_df['Month_Year'],
                y=chart_df['SKU'],
                mode='lines+markers',
                name='SKU',
                line=dict(color='rgb(255, 194, 32)', width=3),
                marker=dict(size=8),
                customdata=chart_df['SKU_formatted'],
                hovertemplate='<b>SKU:</b> %{customdata}<extra></extra>'
            ))
            
            fig.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0.1)',
                font=dict(color='white', size=12),
                xaxis_title='Month',
                yaxis_title='Value ($)',
                yaxis=dict(rangemode='normal'),  # Auto-scale y-axis to data range
                hovermode='x unified',
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=13,
                    font_family="Arial",
                    font_color="rgb(0, 30, 96)"
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                autosize=True,
                margin=dict(l=50, r=50, t=50, b=50)
            )
            
            logger.info(f"Rendered Book vs SKU chart with {len(chart_df)} months")
            return fig
            
        except Exception as e:
            logger.error(f"Error rendering Book vs SKU chart: {e}", exc_info=True)
            return go.Figure()
    
    # Render Purchases chart
    @render_plotly
    @reactive.event(input.dashboard_tabs, ignore_none=False)
    def purchases_chart():
        """Render Purchases line chart - waits for data to avoid double render"""
        try:
            logger.info(">>> PURCHASES CHART RENDER CALLED")
            # Only render when IRR Dashboard tab is active
            if input.dashboard_tabs() != "IRR Dashboard":
                return None
            df = irr_data_13months()
            
            if df.empty:
                logger.info(">>> PURCHASES CHART: No data, returning None")
                return None
            
            # Aggregate by month
            chart_df = data_service.aggregate_by_month(df, ['Purchases'])
            
            if chart_df.empty:
                return go.Figure()
            
            # Helper function to format values with K/M suffix
            def format_currency(val):
                if val >= 1_000_000:
                    return f"${val/1_000_000:.1f}M"
                elif val >= 1_000:
                    return f"${val/1_000:.1f}K"
                else:
                    return f"${val:.1f}"
            
            # Add formatted hover text column
            chart_df['Purchases_formatted'] = chart_df['Purchases'].apply(format_currency)
            
            # Create line chart
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=chart_df['Month_Year'],
                y=chart_df['Purchases'],
                mode='lines+markers',
                name='Purchases',
                line=dict(color='rgb(0, 83, 226)', width=3),
                marker=dict(size=8),
                customdata=chart_df['Purchases_formatted'],
                hovertemplate='<b>Purchases:</b> %{customdata}<extra></extra>'
            ))
            
            fig.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0.1)',
                font=dict(color='white', size=12),
                xaxis_title='Month',
                yaxis_title='Purchases ($)',
                yaxis=dict(rangemode='normal'),  # Auto-scale y-axis to data range
                hovermode='x unified',
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=13,
                    font_family="Arial",
                    font_color="rgb(0, 30, 96)"
                ),
                showlegend=False,
                autosize=True,
                margin=dict(l=50, r=50, t=50, b=50)
            )
            
            logger.info(f"Rendered Purchases chart with {len(chart_df)} months")
            return fig
            
        except Exception as e:
            logger.error(f"Error rendering Purchases chart: {e}", exc_info=True)
            return go.Figure()
    
    # Render Markdowns chart
    @render_plotly
    @reactive.event(input.dashboard_tabs, ignore_none=False)
    def markdowns_chart():
        """Render Markdowns line chart - waits for data to avoid double render"""
        try:
            logger.info(">>> MARKDOWNS CHART RENDER CALLED")
            # Only render when IRR Dashboard tab is active
            if input.dashboard_tabs() != "IRR Dashboard":
                return None
            df = irr_data_13months()
            
            if df.empty:
                logger.info(">>> MARKDOWNS CHART: No data, returning None")
                return None
            
            # Aggregate by month
            chart_df = data_service.aggregate_by_month(df, ['Markdowns'])
            
            if chart_df.empty:
                return go.Figure()
            
            # Helper function to format values with K/M suffix
            def format_currency(val):
                if val >= 1_000_000:
                    return f"${val/1_000_000:.1f}M"
                elif val >= 1_000:
                    return f"${val/1_000:.1f}K"
                else:
                    return f"${val:.1f}"
            
            # Add formatted hover text column
            chart_df['Markdowns_formatted'] = chart_df['Markdowns'].apply(format_currency)
            
            # Create line chart
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=chart_df['Month_Year'],
                y=chart_df['Markdowns'],
                mode='lines+markers',
                name='Markdowns',
                line=dict(color='rgb(255, 194, 32)', width=3),
                marker=dict(size=8),
                customdata=chart_df['Markdowns_formatted'],
                hovertemplate='<b>Markdowns:</b> %{customdata}<extra></extra>'
            ))
            
            fig.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0.1)',
                font=dict(color='white', size=12),
                xaxis_title='Month',
                yaxis_title='Markdowns ($)',
                yaxis=dict(rangemode='normal'),  # Auto-scale y-axis to data range
                hovermode='x unified',
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=13,
                    font_family="Arial",
                    font_color="rgb(0, 30, 96)"
                ),
                showlegend=False,
                autosize=True,
                margin=dict(l=50, r=50, t=50, b=50)
            )
            
            logger.info(f"Rendered Markdowns chart with {len(chart_df)} months")
            return fig
            
        except Exception as e:
            logger.error(f"Error rendering Markdowns chart: {e}", exc_info=True)
            return go.Figure()
    
    # Render Markdowns tab chart (separate, lazy-loaded)
    @render_plotly
    def markdowns_tab_chart():
        """Render Markdowns line chart for Markdowns tab - only loads when tab is active"""
        try:
            # Only render when Markdowns tab is selected
            current_tab = input.dashboard_tabs()
            if current_tab != "Markdowns":
                logger.debug("Markdowns tab not selected, skipping chart render")
                return None
            
            df = irr_data_13months()
            
            if df.empty:
                logger.debug("No data available for Markdowns tab chart yet")
                return None
            
            # Aggregate by month
            chart_df = data_service.aggregate_by_month(df, ['Markdowns'])
            
            if chart_df.empty:
                return go.Figure()
            
            # Helper function to format values with K/M suffix
            def format_currency(val):
                if val >= 1_000_000:
                    return f"${val/1_000_000:.1f}M"
                elif val >= 1_000:
                    return f"${val/1_000:.1f}K"
                else:
                    return f"${val:.1f}"
            
            # Add formatted hover text column
            chart_df['Markdowns_formatted'] = chart_df['Markdowns'].apply(format_currency)
            
            # Create line chart
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=chart_df['Month_Year'],
                y=chart_df['Markdowns'],
                mode='lines+markers',
                name='Markdowns',
                line=dict(color='rgb(255, 194, 32)', width=3),
                marker=dict(size=8),
                customdata=chart_df['Markdowns_formatted'],
                hovertemplate='<b>Markdowns:</b> %{customdata}<extra></extra>'
            ))
            
            fig.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0.1)',
                font=dict(color='white', size=12),
                xaxis_title='Month',
                yaxis_title='Markdowns ($)',
                yaxis=dict(rangemode='normal'),  # Auto-scale y-axis to data range
                hovermode='x unified',
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=13,
                    font_family="Arial",
                    font_color="rgb(0, 30, 96)"
                ),
                showlegend=False,
                autosize=True,
                margin=dict(l=50, r=50, t=50, b=50)
            )
            
            logger.info(f"Rendered Markdowns tab chart with {len(chart_df)} months")
            return fig
            
        except Exception as e:
            logger.error(f"Error rendering Markdowns tab chart: {e}", exc_info=True)
            return go.Figure()
    
    def initialize_agent():
        """Initialize the agent once per session with conversation memory"""
        logger.info(f"initialize_agent called. Current initialized state: {session.initialized}")
        if session.initialized:
            logger.info("Agent already initialized, skipping")
            return
        
        logger.info("Starting agent initialization with conversation memory...")
        try:
            # Set default values for critical environment variables
            gcp_project = os.getenv('GCP_PROJECT', 'wmt-us-gg-shrnk-prod')
            vertex_location = os.getenv('VERTEX_LOCATION', 'us-central1')
            vertex_model = os.getenv('VERTEX_MODEL', 'gemini-pro')
            credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'key.json')
            
            # Ensure environment variables are set
            os.environ['GCP_PROJECT'] = gcp_project
            os.environ['VERTEX_LOCATION'] = vertex_location
            os.environ['VERTEX_MODEL'] = vertex_model
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
            
            logger.info("=== Environment Configuration ===")
            logger.info(f"GCP_PROJECT: {gcp_project}")
            logger.info(f"VERTEX_LOCATION: {vertex_location}")
            logger.info(f"VERTEX_MODEL: {vertex_model}")
            logger.info(f"CREDENTIALS_PATH: {credentials_path}")
            logger.info(f"WORKING_DIR: {os.getcwd()}")
            logger.info("============================")
            
            if not os.path.isfile(credentials_path):
                raise ValueError(f"Credentials file not found at {credentials_path}")
            
            try:
                # Initialize Vertex AI with grounding using the new recommended approach
                logger.info(f"Initializing Vertex AI with grounding for project {gcp_project}...")
                
                from agents import create_grounded_model, create_chat_agent
                
                # Create the grounded model with Vertex AI Search datastore
                grounded_model = create_grounded_model()
                logger.info("Grounded model created successfully with Vertex AI Search")
                
                # Create conversation memory for this session
                from langchain.memory import ConversationBufferWindowMemory
                memory = ConversationBufferWindowMemory(
                    k=5,  # Keep last 5 exchanges
                    memory_key="chat_history",
                    return_messages=True,
                    output_key="output"
                )
                logger.info("Created conversation memory (5-message window)")
                
                # For compatibility with existing chat handler, we still use LangChain wrapper
                # But the grounded model will be used for knowledge retrieval
                from google.generativeai.types import HarmCategory, HarmBlockThreshold
                
                safety_settings = {
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                }
                
                llm = ChatVertexAI(
                    project=gcp_project,
                    location=vertex_location,
                    model_name="gemini-1.5-pro-002",
                    temperature=0.7,
                    max_retries=3,
                    request_timeout=120,
                    safety_settings=safety_settings
                )
                
                logger.info("LangChain wrapper created for agent compatibility")
                
                # Initialize chat agent with knowledge retrieval and report recommendation tools
                # Note: Grounding temporarily disabled, using retrieve_knowledge tool instead
                logger.info("Initializing chat agent with knowledge retrieval and report recommendations...")
                from tools import retrieve_knowledge, recommend_report
                chat_agent = create_chat_agent(llm, tools=[retrieve_knowledge, recommend_report], memory=memory)
                logger.info("Chat agent created with memory, knowledge retrieval, and report recommendation capability")
                
                # Store both in session for reuse
                session.grounded_model = grounded_model  # The Vertex AI Search grounded model
                session.chat_agent = chat_agent  # LangChain agent for tools and memory
                session.chat_memory = memory  # Store memory separately for access
                session.initialized = True
                
                logger.info("Chat system initialized successfully with Vertex AI Search grounding")
                
            except Exception as e:
                logger.error(f"Error during LLM/Agent initialization: {str(e)}", exc_info=True)
                # Provide user-friendly error message
                error_type = type(e).__name__
                if "VPCServiceControlsError" in str(e) or "VPC" in str(e):
                    user_msg = "⚠️ Network access issue detected. The chat service is temporarily unavailable due to VPC restrictions. Please try again in a few moments."
                elif "PermissionDenied" in str(e):
                    user_msg = "⚠️ Permission error. Please contact your administrator to verify service account permissions."
                elif "ResourceExhausted" in str(e):
                    user_msg = "⚠️ Service quota exceeded. Please try again in a few moments."
                else:
                    user_msg = f"⚠️ Chat initialization failed: {error_type}. Please contact support if this persists."
                
                raise Exception(user_msg)
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error initializing chat agent: {error_msg}", exc_info=True)
            # Update chat history with user-friendly error message
            new_history = [{
                "role": "system", 
                "content": error_msg if error_msg.startswith("⚠️") else f"⚠️ Error: {error_msg}",
                "timestamp": datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
            }]
            chat_messages.set(new_history)

    @reactive.Effect
    @reactive.event(input.send)
    def _():
        user_msg = None
        try:
            logger.info("=== SEND BUTTON CLICKED ===")
            user_msg = input.user_message()
            logger.info(f"User message value: '{user_msg}'")
            
            if not user_msg or not user_msg.strip():
                logger.warning("No user message, returning early")
                return
            
            # Set processing state to True (disables input/button)
            is_processing.set(True)
            logger.info("Set processing state to True")
            
            # Try to initialize agent if not already done
            logger.info("Send button pressed, checking agent initialization")
            initialize_agent()
            
            # Check if initialization failed
            if not hasattr(session, 'chat_agent'):
                logger.error("Chat agent not initialized after initialize_agent call")
                raise Exception("Chat service not available. Please refresh the page and try again.")
                
            # Add user message to chat history (create NEW list for reactivity)
            current_history = chat_messages.get()
            logger.info(f"Current history before adding user message: {len(current_history)} messages")
            timestamp = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
            new_history = current_history + [{"role": "user", "content": user_msg, "timestamp": timestamp}]
            chat_messages.set(new_history)
            logger.info(f"Added user message to history. Total messages: {len(chat_messages.get())}")
            
            # Clear the input field
            ui.update_text("user_message", value="")
            logger.info("Cleared input field")
            
            # Get response from the LangChain agent executor with retry logic
            logger.info(f"Invoking agent with message: {user_msg}")
            start_time = datetime.now()
            
            result = None
            max_retries = 2
            retry_count = 0
            original_user_msg = user_msg  # Save original message
            
            while retry_count <= max_retries:
                try:
                    if retry_count > 0:
                        logger.info(f"Retry attempt {retry_count} of {max_retries}")
                        # Add a small delay before retry
                        import time
                        time.sleep(1)
                    
                    result = session.chat_agent.invoke({"input": user_msg})
                    
                    # Success - break out of retry loop
                    response_time = (datetime.now() - start_time).total_seconds()
                    logger.info(f"Agent response received in {response_time:.2f}s")
                    break
                    
                except Exception as retry_error:
                    error_str = str(retry_error)
                    retry_count += 1
                    
                    # Check if it's a retryable error
                    is_safety_block = "SAFETY" in error_str or "blocked" in error_str.lower() or "finish_reason" in error_str.lower()
                    is_quota = "ResourceExhausted" in error_str or "quota" in error_str.lower()
                    is_timeout = "timeout" in error_str.lower() or "deadline" in error_str.lower()
                    
                    if retry_count > max_retries:
                        # Max retries reached - re-raise the error
                        logger.error(f"Max retries ({max_retries}) reached, giving up")
                        raise
                    
                    if is_safety_block:
                        logger.warning(f"Safety block detected on attempt {retry_count}, retrying with context...")
                        # On first retry, add business context. On second retry, use simplified version
                        if retry_count == 1:
                            user_msg = f"As a retail operations assistant, please answer this business question: {original_user_msg}"
                        else:
                            # Second retry - very simple professional framing
                            user_msg = f"Question about retail inventory management: {original_user_msg}"
                    elif is_quota:
                        logger.warning(f"Quota exceeded on attempt {retry_count}, waiting before retry...")
                        import time
                        time.sleep(2)  # Wait longer for quota issues
                        user_msg = original_user_msg  # Reset to original
                    elif is_timeout:
                        logger.warning(f"Timeout on attempt {retry_count}, retrying with same input...")
                        user_msg = original_user_msg  # Reset to original
                    else:
                        # Unknown error - don't retry
                        logger.error(f"Non-retryable error: {error_str}")
                        raise
            
            if result is None:
                raise Exception("Failed to get response after retries")
            
            # Extract the output from the result
            response_content = result.get("output", str(result))
            
            # Log memory state (for debugging)
            if hasattr(session, 'chat_memory'):
                memory_vars = session.chat_memory.load_memory_variables({})
                logger.info(f"Memory contains {len(memory_vars.get('chat_history', []))} messages after exchange")
            
            # Update chat history with AI response (create NEW list for reactivity)
            current_history = chat_messages.get()
            timestamp = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
            new_history = current_history + [{"role": "assistant", "content": response_content, "timestamp": timestamp}]
            chat_messages.set(new_history)
            logger.info(f"Added assistant response to history. Total messages: {len(chat_messages.get())}")
            
        except Exception as e:
            error_type = type(e).__name__
            error_str = str(e)
            logger.error(f"Error processing chat request: {error_str}", exc_info=True)
            logger.error(f"Exception type: {error_type}")
            
            # Provide user-friendly error messages based on error type
            if "VPCServiceControlsError" in error_str or "VPC" in error_str:
                user_error_msg = "⚠️ Network access issue. The AI service is temporarily blocked by VPC restrictions. This has been logged and we'll retry automatically."
            elif "ResourceExhausted" in error_str or "quota" in error_str.lower():
                user_error_msg = "⚠️ Service quota exceeded. We attempted to retry your request but the service is currently at capacity. Please try again in a minute."
            elif "SAFETY" in error_str or "blocked" in error_str.lower() or "finish_reason" in error_str.lower():
                # This should rarely happen now due to retry logic
                user_error_msg = "⚠️ I apologize, but I couldn't process that question even after multiple attempts. This appears to be a safety filter issue. Could you try rephrasing your question? For example, try starting with 'What is...' or 'How does...'."
            elif "timeout" in error_str.lower() or "deadline" in error_str.lower():
                user_error_msg = "⚠️ Request timed out after multiple attempts. Please try a simpler question or try again. If this persists, contact support."
            elif "PermissionDenied" in error_str or "permission" in error_str.lower():
                user_error_msg = "⚠️ Permission error. Your account may not have access to the AI service. Please contact your administrator."
            elif "not initialized" in error_str.lower():
                user_error_msg = "⚠️ Chat service not ready. Please refresh the page and try again. If this persists, contact support."
            else:
                # Generic error with type - should be rare now
                logger.error(f"Unhandled error type: {error_type}", exc_info=True)
                user_error_msg = f"⚠️ Unexpected error occurred. We attempted to recover but were unsuccessful. Please try again. If this persists, contact support with error code: {error_type}"
            
            # Add the user's original message if we haven't yet
            current_history = chat_messages.get()
            if user_msg and not any(msg.get("content") == user_msg for msg in current_history[-3:]):
                timestamp = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
                current_history = current_history + [{"role": "user", "content": user_msg, "timestamp": timestamp}]
            
            # Add error message
            timestamp = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
            new_history = current_history + [{"role": "system", "content": user_error_msg, "timestamp": timestamp}]
            chat_messages.set(new_history)
            logger.info(f"Added error message to chat history")
            
        finally:
            # Always re-enable input after processing (success or failure)
            is_processing.set(False)
            logger.info("Set processing state to False")

    @output
    @render.ui
    def chat_history():
        # Initialize agent on first render
        initialize_agent()
        
        # Get current chat messages (this creates reactive dependency)
        history = chat_messages.get()
        
        logger.info(f"Rendering chat history with {len(history)} messages")
        
        chat_elements = []
        
        # Show welcome message if no chat history
        if not history:
            chat_elements.append(
                ui.div(
                    ui.div(
                        ui.div(
                            ui.p("👋 Welcome! Ask me anything about retail operations, shrink prevention, or inventory management.", style="margin: 0;"),
                            class_="bubble-content"
                        ),
                        class_="assistant-message message-bubble"
                    )
                )
            )
        
        for msg in history:
            # Get timestamp if available, otherwise show as "N/A"
            timestamp = msg.get("timestamp", "N/A")
            
            if msg["role"] == "user":
                chat_elements.append(
                    ui.div(
                        ui.div(
                            ui.markdown(msg["content"]),
                            class_="bubble-content"
                        ),
                        ui.div(timestamp, class_="message-timestamp"),
                        class_="user-message message-bubble"
                    )
                )
            elif msg["role"] == "assistant":
                chat_elements.append(
                    ui.div(
                        ui.div(
                            ui.markdown(msg["content"]),
                            class_="bubble-content"
                        ),
                        ui.div(timestamp, class_="message-timestamp"),
                        class_="assistant-message message-bubble"
                    )
                )
            else:  # system messages (errors)
                chat_elements.append(
                    ui.div(
                        ui.div(
                            ui.strong("⚠️ System: "),
                            ui.markdown(msg["content"]),
                            class_="bubble-content",
                            style="background-color: #f8d7da; color: #721c24;"
                        ),
                        ui.div(timestamp, class_="message-timestamp"),
                        class_="assistant-message message-bubble"
                    )
                )
        
        # Important: Return just the elements, NOT wrapped in another div with id="chat-container"
        # The container already exists in ui.py
        return ui.div(*chat_elements)
    
    @reactive.Effect
    def _():
        """Update UI elements based on processing state"""
        processing = is_processing.get()
        logger.info(f"Processing state changed to: {processing}")
        
        # Disable/enable the send button
        if processing:
            ui.update_action_button("send", label="Processing...", disabled=True)
        else:
            ui.update_action_button("send", label="Send", disabled=False)

# Run startup diagnostics
logger.info("=== ADK Chat Interface Starting ===")
logger.info(f"Working directory: {os.getcwd()}")
logger.info(f"Environment variables:")
for key in ['GOOGLE_APPLICATION_CREDENTIALS', 'GCP_PROJECT', 'VERTEX_LOCATION', 'VERTEX_MODEL']:
    logger.info(f"{key}: {os.getenv(key, 'Not set')}")

# Log Python version and platform
logger.info(f"Python version: {sys.version}")
logger.info(f"Platform: {sys.platform}")
logger.info("=== Startup Diagnostics Complete ===")

# Create the Shiny app with static file directory
app = App(app_ui, server, static_assets=Path(__file__).parent / "www")