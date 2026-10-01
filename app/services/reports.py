from app.services.finance import summary, list_transactions
from app.services.cases import list_cases
from app.reports.pdf import build_pdf
from app.reports.excel import build_excel

def data_for_report(user_id):
    return summary(user_id), list_transactions(user_id), list_cases(user_id)

def pdf_report(user_id):
    s,t,c=data_for_report(user_id); return build_pdf('RESOLVE — Relatório Financeiro',s,t,c)

def excel_report(user_id):
    s,t,c=data_for_report(user_id); return build_excel(s,t,c)
