from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

def build_pdf(title, summary, transactions, cases):
    buf=BytesIO(); doc=SimpleDocTemplate(buf,pagesize=A4,rightMargin=36,leftMargin=36,topMargin=36,bottomMargin=36)
    styles=getSampleStyleSheet(); story=[Paragraph(title,styles['Title']),Spacer(1,12)]
    data=[['Indicador','Valor'],['Receitas',f"R$ {summary['receitas']:,.2f}"],['Despesas',f"R$ {summary['despesas']:,.2f}"],['Saldo registrado',f"R$ {summary['saldo_registrado']:,.2f}"],['A receber',f"R$ {summary['a_receber']:,.2f}"],['A pagar',f"R$ {summary['a_pagar']:,.2f}"]]
    t=Table(data,colWidths=[260,180]); t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.lightgrey),('GRID',(0,0),(-1,-1),0.5,colors.grey),('ALIGN',(1,1),(-1,-1),'RIGHT')]))
    story += [Paragraph('Resumo financeiro',styles['Heading2']),t,Spacer(1,16),Paragraph('Movimentações',styles['Heading2'])]
    rows=[['Tipo','Categoria','Descrição','Valor']]+[[x['kind'],x['category'],x['description'],f"R$ {x['amount']:,.2f}"] for x in transactions[:100]]
    tt=Table(rows,colWidths=[65,90,260,75],repeatRows=1); tt.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.lightgrey),('GRID',(0,0),(-1,-1),0.35,colors.grey),('FONTSIZE',(0,0),(-1,-1),8)])); story += [tt,Spacer(1,16),Paragraph(f"Casos registrados: {len(cases)}",styles['Normal'])]
    doc.build(story); return buf.getvalue()
