"""
Excel export functionality.
"""
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class ExcelExporter:
    """Handles Excel report generation."""
    
    def __init__(self, exports_dir: Path):
        self.exports_dir = Path(exports_dir)
        self.exports_dir.mkdir(exist_ok=True)
    
    def export_evaluations_detail(self, evaluations: List[Dict],
                                  criteria: List[Dict],
                                  users: List[Dict],
                                  filename: str = None) -> str:
        """Export detailed evaluation data to Excel."""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"evaluations_detail_{timestamp}.xlsx"
        
        filepath = self.exports_dir / filename
        
        # Create user lookup
        user_map = {u['id']: u.get('full_name', u.get('username')) for u in users}
        criteria_map = {c['id']: c['name'] for c in criteria}
        
        # Build rows
        rows = []
        for ev in evaluations:
            row = {
                'Evaluation ID': ev['id'],
                'Date': ev.get('date', ''),
                'Employee': user_map.get(ev['employee_id'], ev['employee_id']),
                'Evaluator': user_map.get(ev['evaluator_id'], ev['evaluator_id']),
                'Status': ev.get('status', ''),
                'Comments': ev.get('comments', '')
            }
            
            # Add scores
            for crit_id, score in ev.get('scores', {}).items():
                crit_name = criteria_map.get(crit_id, crit_id)
                row[crit_name] = score
            
            rows.append(row)
        
        # Create DataFrame and export
        df = pd.DataFrame(rows)
        df.to_excel(filepath, index=False, engine='openpyxl')
        logger.info(f"Exported evaluations detail to {filepath}")
        return str(filepath)
    
    def export_employee_summary(self, summaries: List[Dict],
                               filename: str = None) -> str:
        """Export employee summary report to Excel."""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"employee_summary_{timestamp}.xlsx"
        
        filepath = self.exports_dir / filename
        
        rows = []
        for summary in summaries:
            rows.append({
                'Employee Name': summary.get('employee_name', ''),
                'Email': summary.get('email', ''),
                'Total Evaluations': summary.get('total_evaluations', 0),
                'Final Evaluations': summary.get('final_evaluations', 0),
                'Average Score': round(summary.get('average_score', 0), 2),
                'Latest Score': round(summary.get('latest_score', 0), 2)
            })
        
        df = pd.DataFrame(rows)
        df.to_excel(filepath, index=False, engine='openpyxl')
        logger.info(f"Exported employee summary to {filepath}")
        return str(filepath)