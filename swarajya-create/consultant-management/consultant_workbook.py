import openpyxl
import os

class ConsultantWorkbook:
    def __init__(self, file_path):
        self.file_path = file_path

    def get_test_cases(self):
        """Extracts positive test cases from the Excel sheet."""
        cases = []
        if not os.path.exists(self.file_path):
            return cases
        
        wb = openpyxl.load_workbook(self.file_path, data_only=True)
        ws = wb.active
        
        # Start reading from row 2
        for row in ws.iter_rows(min_row=2, values_only=True):
            tc_id = row[0]
            if not tc_id or not tc_id.startswith("TC_CONSULTANT"):
                continue
                
            cases.append({
                "id": tc_id,
                "scenario": row[1] or "",
                "test_data_raw": row[4] or "",
                "expected": row[5] or ""
            })
            
        return cases
