import re,sys,xml.etree.ElementTree as ET
ns='{http://cnx.rice.edu/cnxml}'
r=ET.parse(sys.argv[1]).getroot()
def text(e): return re.sub(r'\s+',' ',''.join(e.itertext())).strip()
def walk(el,d=0):
  for ch in el:
    tag=ch.tag.replace(ns,'')
    if tag=='section':
      t=ch.find(ns+'title'); print('\n'+'#'*(d+2)+' '+(text(t) if t is not None else '')); walk(ch,d+1)
    elif tag=='para': print('P['+ch.get('id','')+']: '+text(ch))
    elif tag in ('figure','note','table'): 
      cap=ch.find('.//'+ns+'caption'); 
      if tag=='figure' and cap is not None: print('FIG['+ch.get('id','')+']: '+text(cap))
      if tag=='note': walk(ch,d)
    else: walk(ch,d)
walk(r.find(ns+'content'))
