import re
from dataclasses import dataclass, asdict
from typing import Optional

@dataclass
class Proposal:
    intent: str
    confidence: float
    contact_name: Optional[str] = None
    case_title: Optional[str] = None
    revenue: Optional[float] = None
    expense: Optional[float] = None
    expense_category: Optional[str] = None
    due_date: Optional[str] = None
    notes: Optional[str] = None

MONEY_RE = re.compile(r"(?:R\$\s*)?([0-9]{1,3}(?:\.[0-9]{3})*(?:,[0-9]{1,2})?|[0-9]+(?:,[0-9]{1,2})?)")

def money_values(text: str):
    out=[]
    for m in MONEY_RE.findall(text):
        s=m.replace('.','').replace(',','.')
        try: out.append(float(s))
        except ValueError: pass
    return out

def first_name_after(text, patterns):
    for p in patterns:
        m=re.search(p,text,re.I)
        if m: return m.group(1).strip(" .,!?:;")
    return None

def interpret_ptbr(text: str) -> dict:
    t=text.strip()
    low=t.lower()
    vals=money_values(t)
    revenue=None; expense=None; category=None
    if any(x in low for x in ['recebi','recebemos','recebimento','vendi','venda','faturei','pagou','pagamento de','fechei um serviço','fechei um servico','fechei serviço','fechei servico']):
        revenue=vals[0] if vals else None
    if any(x in low for x in ['gastei','paguei','comprei','despesa','custo','material','combustível','combustivel']):
        expense=vals[-1] if vals else None
        if 'combust' in low: category='COMBUSTÍVEL'
        elif 'material' in low or 'comprei' in low: category='MATERIAL'
        else: category='OUTROS'
    contact=first_name_after(t,[r'\bcom\s+([A-ZÁÀÃÂÉÊÍÓÔÕÚÇ][\wÁÀÃÂÉÊÍÓÔÕÚÇ-]*)',r'\bdo\s+([A-ZÁÀÃÂÉÊÍÓÔÕÚÇ][\wÁÀÃÂÉÊÍÓÔÕÚÇ-]*)',r'\bda\s+([A-ZÁÀÃÂÉÊÍÓÔÕÚÇ][\wÁÀÃÂÉÊÍÓÔÕÚÇ-]*)'])
    if not contact:
        contact=first_name_after(t,[r'\bcliente\s+([A-ZÁÀÃÂÉÊÍÓÔÕÚÇ][\wÁÀÃÂÉÊÍÓÔÕÚÇ-]*)'])
    title=None
    if any(x in low for x in ['serviço','servico','instala','orçamento','orcamento','projeto','manutenção','manutencao']):
        title=t[:90]
    if revenue is not None and expense is not None: intent='MOVIMENTO_MISTO'
    elif revenue is not None: intent='RECEITA'
    elif expense is not None: intent='DESPESA'
    elif title: intent='NOVO_CASO'
    else: intent='INDETERMINADO'
    score=0.55
    if vals: score+=0.2
    if contact: score+=0.1
    if title: score+=0.1
    return asdict(Proposal(intent=intent,confidence=min(score,0.95),contact_name=contact,case_title=title,revenue=revenue,expense=expense,expense_category=category,notes=t))
