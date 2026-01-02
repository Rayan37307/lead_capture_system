import gspread
import asyncio
from google.oauth2.service_account import Credentials
from app.config.settings import settings
from typing import Dict, Any


class GoogleSheetsService:
    def __init__(self):
        if settings.GOOGLE_SHEETS_SYNC:
            # Define the scope
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive"
            ]
            
            # Authenticate using the service account file
            creds = Credentials.from_service_account_file(
                settings.GOOGLE_SHEETS_CREDENTIALS_FILE,
                scopes=scope
            )
            
            # Authorize the client
            self.client = gspread.authorize(creds)
            self.spreadsheet = self.client.open_by_key(settings.GOOGLE_SHEETS_SPREADSHEET_ID)
            self.worksheet = self.spreadsheet.sheet1  # Default to first sheet
        else:
            self.client = None
            self.spreadsheet = None
            self.worksheet = None

    async def add_lead_to_sheet(self, lead_data: Dict[str, Any]):
        """Add a lead to the Google Sheet"""
        if not settings.GOOGLE_SHEETS_SYNC or not self.worksheet:
            return

        def append_row():
            try:
                # Prepare the row data
                row = [
                    lead_data.get("name", ""),
                    lead_data.get("email", ""),
                    lead_data.get("phone", ""),
                    lead_data.get("source", ""),
                    lead_data.get("intent", ""),
                    lead_data.get("created_at", ""),
                ]
                
                # Append the row to the worksheet
                self.worksheet.append_row(row)
            except Exception as e:
                print(f"Error adding lead to Google Sheets: {e}")
        
        await asyncio.to_thread(append_row)

    async def update_lead_in_sheet(self, lead_id: str, lead_data: Dict[str, Any]):
        """Update a lead in the Google Sheet"""
        if not settings.GOOGLE_SHEETS_SYNC or not self.worksheet:
            return

        def update_row():
            try:
                # Find the row corresponding to the lead_id
                # This is a simplified implementation - in practice, you'd need a more robust way to identify rows
                pass
            except Exception as e:
                print(f"Error updating lead in Google Sheets: {e}")
        
        await asyncio.to_thread(update_row)

    async def get_all_leads_from_sheet(self):
        """Get all leads from the Google Sheet"""
        if not settings.GOOGLE_SHEETS_SYNC or not self.worksheet:
            return []

        def get_all_records():
            try:
                # Get all records from the sheet
                records = self.worksheet.get_all_records()
                return records
            except Exception as e:
                print(f"Error getting leads from Google Sheets: {e}")
                return []
        
        return await asyncio.to_thread(get_all_records)