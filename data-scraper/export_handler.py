import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils.dataframe import dataframe_to_rows
import os
from typing import Dict, List

class ExportHandler:
    def __init__(self, data_collector):
        self.data_collector = data_collector
    
    def export_to_csv(self, df: pd.DataFrame, filename: str = 'fifa26_teams_data.csv') -> str:
        """Export all data to a single CSV file"""
        
        os.makedirs('exports', exist_ok=True)
        filepath = os.path.join('exports', filename)
        
        df.to_csv(filepath, index=False, encoding='utf-8')
        
        return filepath
    
    def export_to_excel(self, df: pd.DataFrame, filename: str = 'fifa26_teams_data.xlsx', player_rosters: pd.DataFrame = None) -> str:
        """Export data to Excel with multiple sheets organized by category"""
        
        os.makedirs('exports', exist_ok=True)
        filepath = os.path.join('exports', filename)
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            
            df.to_excel(writer, sheet_name='All Teams Overview', index=False)
            
            overview_ws = writer.sheets['All Teams Overview']
            self._style_worksheet(overview_ws)
            
            categories = self.data_collector.get_feature_categories()
            
            for category_name, features in categories.items():
                available_features = ['team'] + [f for f in features if f in df.columns]
                
                category_df = df[available_features]
                
                # Sanitize sheet name: remove invalid characters and limit length
                sheet_name = category_name.replace('/', '-').replace('\\', '-')
                sheet_name = sheet_name.replace('?', '').replace('*', '').replace('[', '').replace(']', '').replace(':', '')
                sheet_name = sheet_name[:31]
                
                category_df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                category_ws = writer.sheets[sheet_name]
                self._style_worksheet(category_ws)
            
            stats_data = {
                'Metric': [
                    'Total Teams',
                    'Total Features',
                    'Average FIFA Rank',
                    'Total World Cup Titles',
                    'Average Squad Value (€M)',
                    'Average Team Age',
                    'Teams from UEFA',
                    'Teams from CONMEBOL',
                    'Teams from CONCACAF',
                    'Teams from CAF',
                    'Teams from AFC'
                ],
                'Value': [
                    len(df),
                    len(df.columns) - 1,
                    round(df['fifa_rank'].mean(), 1),
                    int(df['titles_won'].sum()),
                    round(df['total_squad_value'].mean(), 1),
                    round(df['avg_player_age'].mean(), 1),
                    len(df[df['continent'] == 'UEFA']),
                    len(df[df['continent'] == 'CONMEBOL']),
                    len(df[df['continent'] == 'CONCACAF']),
                    len(df[df['continent'] == 'CAF']),
                    len(df[df['continent'] == 'AFC'])
                ]
            }
            
            stats_df = pd.DataFrame(stats_data)
            stats_df.to_excel(writer, sheet_name='Summary Statistics', index=False)
            
            stats_ws = writer.sheets['Summary Statistics']
            self._style_worksheet(stats_ws, is_summary=True)
            
            # Add player rosters if provided
            if player_rosters is not None and not player_rosters.empty:
                player_rosters.to_excel(writer, sheet_name='Player Rosters', index=False)
                player_ws = writer.sheets['Player Rosters']
                self._style_worksheet(player_ws)
        
        return filepath
    
    def _style_worksheet(self, worksheet, is_summary: bool = False):
        """Apply styling to Excel worksheet"""
        
        header_fill = PatternFill(start_color='366092', end_color='366092', fill_type='solid')
        header_font = Font(color='FFFFFF', bold=True, size=11)
        
        for cell in worksheet[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')
        
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
        
        worksheet.freeze_panes = 'A2'
