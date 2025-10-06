"""
Business logic for calculations and reporting.
"""
from typing import Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class EvaluationEngine:
    """Handles evaluation calculations and analysis."""
    
    def __init__(self, criteria_store, evaluations_store):
        self.criteria_store = criteria_store
        self.evaluations_store = evaluations_store
    
    def get_criteria_map(self) -> Dict[str, Dict]:
        """Get criteria as a dictionary keyed by ID."""
        criteria = self.criteria_store.load()
        return {c['id']: c for c in criteria}
    
    def compute_weighted_score(self, scores: Dict[str, int],
                              criteria_map: Dict[str, Dict]) -> float:
        """Calculate weighted average score."""
        if not scores:
            return 0.0
        
        total_weighted = 0.0
        total_weight = 0.0
        
        for criterion_id, score in scores.items():
            if criterion_id in criteria_map:
                weight = criteria_map[criterion_id].get('weight', 1.0)
                total_weighted += score * weight
                total_weight += weight
        
        return total_weighted / total_weight if total_weight > 0 else 0.0
    
    def get_employee_evaluations(self, employee_id: str) -> List[Dict]:
        """Get all evaluations for an employee."""
        return self.evaluations_store.find_by(employee_id=employee_id)
    
    def get_employee_summary(self, employee_id: str) -> Dict:
        """Get summary statistics for an employee."""
        evaluations = self.get_employee_evaluations(employee_id)
        criteria_map = self.get_criteria_map()
        
        if not evaluations:
            return {
                'employee_id': employee_id,
                'total_evaluations': 0,
                'average_score': 0.0,
                'latest_evaluation': None
            }
        
        scores = []
        for ev in evaluations:
            if ev.get('status') == 'final':
                score = self.compute_weighted_score(ev['scores'], criteria_map)
                scores.append(score)
        
        # Sort by date
        evaluations_sorted = sorted(
            evaluations,
            key=lambda x: x.get('date', ''),
            reverse=True
        )
        
        return {
            'employee_id': employee_id,
            'total_evaluations': len(evaluations),
            'final_evaluations': len(scores),
            'average_score': sum(scores) / len(scores) if scores else 0.0,
            'latest_score': scores[0] if scores else 0.0,
            'latest_evaluation': evaluations_sorted[0] if evaluations_sorted else None
        }
    
    def get_all_employee_summaries(self, user_store) -> List[Dict]:
        """Get summaries for all employees."""
        employees = user_store.find_by(role='employee')
        summaries = []
        
        for emp in employees:
            summary = self.get_employee_summary(emp['id'])
            summary['employee_name'] = emp.get('full_name', emp.get('username'))
            summary['email'] = emp.get('email', '')
            summaries.append(summary)
        
        return summaries
