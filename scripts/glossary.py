#!/usr/bin/env python3
"""Validador, renderizador y reporte determinista del glosario."""
from __future__ import annotations
import argparse, datetime as dt, json, re, sys
from pathlib import Path

EXIT_OK, EXIT_INVALID, EXIT_USAGE, EXIT_MISSING = 0, 1, 2, 3
CATEGORIES = {'proceso','producto','técnico','operación','gobernanza','seguridad','otro'}
STATUSES = {'active','draft','deprecated','superseded'}
ID_RE = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')
OWNER_RE = re.compile(r'^[A-Za-zÀ-ÿ0-9][A-Za-zÀ-ÿ0-9 _./-]{1,79}$')
EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')

def norm(value): return ' '.join(str(value).casefold().replace('-', ' ').split())
def error(message, warnings=None): return {'errors':[message], 'warnings':warnings or []}
def load_registry(root):
    path = root / 'docs/glossary/terms.yaml'
    if not path.is_file(): raise FileNotFoundError(path)
    try: data = json.loads(path.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc: raise ValueError(f'{path}: registro inválido: {exc}')
    if not isinstance(data, dict) or not isinstance(data.get('terms'), list): raise ValueError(f'{path}: se requiere schema y lista terms')
    return data
def parse_date(value):
    if not isinstance(value, str) or not DATE_RE.fullmatch(value): return None
    try: return dt.date.fromisoformat(value)
    except ValueError: return None
def source_anchor_exists(path, anchor):
    if not anchor: return True
    text = path.read_text(encoding='utf-8')
    return f'id="{anchor}"' in text or f"id='{anchor}'" in text or re.search(rf'^#{1,6} .*{re.escape(anchor.replace("-", " "))}', text, re.M) is not None

def validate(root, strict=False):
    try: data = load_registry(root)
    except FileNotFoundError as exc: return error(f'archivo faltante: {exc}'), EXIT_MISSING
    except ValueError as exc: return error(str(exc)), EXIT_INVALID
    errors, warnings, ids, labels, anchors = [], [], {}, {}, set(); terms = data['terms']
    if data.get('schema') != 'glossary.v1': errors.append('schema no soportado (se esperaba glossary.v1)')
    required = ['id','label','aliases','acronym','anchor','category','definition','context','source','related','owner','status','reviewed_on','review_due','introduced_in','deprecated_by']
    for i, term in enumerate(terms):
        where=f'terms[{i}]'
        if not isinstance(term, dict): errors.append(f'{where}: debe ser objeto'); continue
        for key in required:
            if key not in term: errors.append(f'{where}: falta {key}')
        ident=term.get('id')
        if not isinstance(ident,str) or not ID_RE.fullmatch(ident or ''): errors.append(f'{where}.id: kebab-case inválido')
        if ident in ids: errors.append(f'{where}.id: duplicado de terms[{ids[ident]}]')
        else: ids[ident]=i
        label=term.get('label')
        if not isinstance(label,str) or not label.strip(): errors.append(f'{where}.label: requerido')
        aliases=term.get('aliases')
        if not isinstance(aliases,list) or any(not isinstance(x,str) or not x.strip() for x in (aliases if isinstance(aliases,list) else [])): errors.append(f'{where}.aliases: textos no vacíos requeridos')
        acronym=term.get('acronym')
        if acronym is not None and (not isinstance(acronym,str) or acronym != acronym.upper()): errors.append(f'{where}.acronym: debe ser mayúscula o null')
        anchor=term.get('anchor')
        if not isinstance(anchor,str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',anchor or ''): errors.append(f'{where}.anchor: inválida')
        elif anchor in anchors: errors.append(f'{where}.anchor: duplicada')
        else: anchors.add(anchor)
        if term.get('category') not in CATEGORIES: errors.append(f'{where}.category: inválida')
        for field, minimum in [('definition',10),('context',1)]:
            if not isinstance(term.get(field),str) or len(term.get(field,'').strip()) < minimum: errors.append(f'{where}.{field}: no puede estar vacío')
        owner=term.get('owner')
        if not isinstance(owner,str) or not OWNER_RE.fullmatch(owner) or EMAIL_RE.fullmatch(owner): errors.append(f'{where}.owner: debe ser rol/equipo, no correo')
        if term.get('status') not in STATUSES: errors.append(f'{where}.status: inválido')
        reviewed=parse_date(term.get('reviewed_on')); due=parse_date(term.get('review_due'))
        if not reviewed: errors.append(f'{where}.reviewed_on: fecha ISO inválida')
        if not due: errors.append(f'{where}.review_due: fecha ISO inválida')
        if reviewed and due and term.get('status')=='active' and (due-reviewed).days>90: errors.append(f'{where}.review_due: excede 90 días para active')
        if term.get('status') in {'deprecated','superseded'} and not isinstance(term.get('deprecated_by'),str): errors.append(f'{where}: {term.get("status")} requiere deprecated_by')
        sources=term.get('source')
        if not isinstance(sources,list) or not sources: errors.append(f'{where}.source: requiere al menos una fuente')
        else:
            for source in sources:
                if not isinstance(source,dict) or not isinstance(source.get('path'),str) or not source['path']: errors.append(f'{where}.source: entrada inválida'); continue
                source_path=(root/source['path']).resolve()
                if not source_path.is_file(): errors.append(f'{where}.source: archivo inexistente {source["path"]}')
                elif source.get('anchor') and not source_anchor_exists(source_path,source['anchor']): errors.append(f'{where}.source: ancla rota {source["path"]}#{source["anchor"]}')
        if not isinstance(term.get('related'),list): errors.append(f'{where}.related: debe ser lista')
    idset=set(ids)
    for i,t in enumerate(terms):
        where=f'terms[{i}]'
        deprecated_by=t.get('deprecated_by')
        if deprecated_by is not None:
            if not isinstance(deprecated_by,str) or not deprecated_by.strip():
                errors.append(f'{where}.deprecated_by: debe ser un ID no vacío o null')
            elif deprecated_by not in idset:
                errors.append(f'{where}.deprecated_by: ID inexistente {deprecated_by}')
        if t.get('status') in {'deprecated','superseded'}:
            if not isinstance(deprecated_by,str) or not deprecated_by.strip():
                errors.append(f'{where}: {t.get("status")} requiere deprecated_by no vacío')
            elif deprecated_by not in idset:
                errors.append(f'{where}: {t.get("status")} apunta a deprecated_by inexistente {deprecated_by}')
    entries=root/'docs/glossary/entries'
    if entries.is_dir():
        expected={f'{t.get("id")}.md' for t in terms if t.get('status')!='draft' and isinstance(t.get('id'),str)}
        for entry in sorted(entries.glob('*.md')):
            if entry.name not in expected:
                errors.append(f'entrada huérfana: {entry.relative_to(root)} no corresponde a un término publicado del registro')
    for i,t in enumerate(terms):
        where=f'terms[{i}]'; values=[t.get('label')] + (t.get('aliases') if isinstance(t.get('aliases'),list) else [])
        for value in values:
            key=norm(value)
            if key and key in labels: errors.append(f'{where}: label/alias colisiona con {labels[key]}')
            elif key: labels[key]=where
        for rel in t.get('related',[]) if isinstance(t.get('related'),list) else []:
            if rel not in idset: errors.append(f'{where}.related: ID inexistente {rel}')
    entries=root/'docs/glossary/entries'; index=root/'docs/glossary/README.md'; published=[t for t in terms if t.get('status')!='draft']
    for t in published:
        entry=entries/f'{t.get("id","")}.md'
        if not entry.is_file(): errors.append(f'entrada faltante: {entry.relative_to(root)}'); continue
        text=entry.read_text(encoding='utf-8')
        for field in ('id','label','anchor','status'):
            if not re.search(rf'^{field}: {re.escape(str(t.get(field)))}$',text,re.M): errors.append(f'{entry.relative_to(root)}: front matter {field} no coincide')
        if f'<a id="{t.get("anchor")}"></a>' not in text: errors.append(f'{entry.relative_to(root)}: ancla faltante')
        if entry_body(t) not in text: errors.append(f'{entry.relative_to(root)}: cuerpo no coincide con registro')
    if not index.is_file(): errors.append('índice README.md faltante')
    else:
        text=index.read_text(encoding='utf-8')
        for t in published:
            if f'entries/{t["id"]}.md' not in text: errors.append(f'índice: falta entries/{t["id"]}.md')
    errors.extend(check_links(root))
    for t in terms:
        for rel in t.get('related',[]):
            other=next((x for x in terms if x.get('id')==rel),None)
            if other and t['id'] not in other.get('related',[]): warnings.append(f'related no simétrico: {t["id"]} -> {rel}')
    if strict and warnings: errors.extend('strict: '+w for w in warnings)
    return {'errors':errors,'warnings':warnings}, EXIT_INVALID if errors else EXIT_OK

def check_links(root):
    errors=[]; excluded={'.git','node_modules','dist','build','coverage','playwright-report','test-results','.cache','__pycache__'}; fixtures=root/'tests/fixtures'
    for path in root.rglob('*.md'):
        if excluded.intersection(path.parts) or fixtures in path.parents: continue
        try: text=path.read_text(encoding='utf-8')
        except UnicodeDecodeError: continue
        scrub=re.sub(r'```.*?```','',text,flags=re.S)
        for target in re.findall(r'!?\[[^]]*\]\(([^)\s]+)(?:\s+"[^"]*")?\)',scrub):
            if target.startswith(('http://','https://','mailto:','#')): continue
            bits=target.split('#',1); dest=(path.parent/bits[0]).resolve()
            if not dest.is_file(): errors.append(f'enlace roto: {path.relative_to(root)} -> {bits[0]}')
            elif len(bits)>1:
                body=dest.read_text(encoding='utf-8')
                if f'id="{bits[1]}"' not in body and not re.search(rf'^#{1,6} .*{re.escape(bits[1].replace("-"," "))}',body,re.M): errors.append(f'ancla rota: {path.relative_to(root)} -> {bits[0]}#{bits[1]}')
    return errors

def entry_body(t):
    aliases='; '.join(t.get('aliases',[])) or '—'; sources=[]
    for s in t.get('source',[]):
        href='../../../'+s.get('path','') + (('#'+s['anchor']) if s.get('anchor') else '')
        sources.append(f'[{s.get("path","fuente")}]({href})')
    related=', '.join(f'[{x}]({x}.md)' for x in t.get('related',[])) or '—'
    return f'\n<a id="{t["anchor"]}"></a>\n\n# {t["label"]}\n\n**Aliases:** {aliases}\n**Categoría:** {t["category"]}\n**Propietario:** {t["owner"]}\n**Revisión:** {t["reviewed_on"]} (próxima: {t["review_due"]})\n\n{t["definition"]}\n\n**Contexto:** {t["context"]}\n\n**Fuente:** {", ".join(sources)}\n\n**Relacionado:** {related}\n'
def entry_text(t): return f'---\nid: {t["id"]}\nlabel: {t["label"]}\nanchor: {t["anchor"]}\nstatus: {t["status"]}\n---'+entry_body(t)

def render(root, check=False):
    data=load_registry(root); terms=sorted(data['terms'],key=lambda x:(x['label'].casefold(),x['id'])); out=['# Glosario enlazable','','Registro canónico: [`terms.yaml`](terms.yaml). Las anclas HTML son estables.','','## Índice','']; current=None
    for t in terms:
        if t.get('status')=='draft': continue
        letter=t['label'][0].upper()
        if letter!=current: out += [f'### {letter}','']; current=letter
        out.append(f'- [{t["label"]}](entries/{t["id"]}.md#{t["anchor"]}) — {t["category"]} ({t["status"]})')
    out += ['','## Tabla de términos','','| Término | Categoría | Estado |','| --- | --- | --- |']
    for t in terms:
        if t.get('status')!='draft': out.append(f'| [{t["label"]}](entries/{t["id"]}.md#{t["anchor"]}) | {t["category"]} | {t["status"]} |')
    out += ['','## Esquema y uso','','`terms.yaml` es la fuente canónica (JSON válido como YAML 1.2). Cada término requiere `id`, `label`, `aliases`, `acronym`, `anchor`, `category`, `definition`, `context`, `source`, `related`, `owner`, `status`, `reviewed_on`, `review_due`, `introduced_in` y `deprecated_by`. IDs y anclas son estables; `owner` siempre es un rol o equipo.','','Enlaza solo la primera aparición significativa por documento o sección autónoma. No enlaces encabezados, tablas ni bloques de código. Ejecuta `make glossary-check`, `make docs-check` y `python scripts/glossary.py render --check` antes de abrir una PR.']
    content='\n'.join(out)+'\n'; path=root/'docs/glossary/README.md'
    if check: return path.is_file() and content==path.read_text(encoding='utf-8'),content
    path.write_text(content,encoding='utf-8')
    for t in terms:
        if t.get('status')!='draft': (root/'docs/glossary/entries'/f'{t["id"]}.md').write_text(entry_text(t),encoding='utf-8')
    return True,content

def report(root):
    data=load_registry(root); result,code=validate(root); terms=data['terms']; today=dt.date.today(); active=[t for t in terms if t.get('status')=='active']; stale=sum(1 for t in active if (parse_date(t.get('review_due')) or today)<today); broken=[x for x in result['errors'] if x.startswith(('enlace roto:','ancla rota:'))]; referenced={r for t in terms for r in t.get('related',[])}
    metrics={'terms':len(terms),'active':len(active),'coverage':{'published_entries':sum((root/'docs/glossary/entries'/f'{t.get("id","")}.md').is_file() for t in terms if t.get('status')!='draft'),'published_terms':len([t for t in terms if t.get('status')!='draft'])},'source_freshness':{'active':len(active)-stale,'stale':stale},'review_age_days':max([(today-(parse_date(t.get('reviewed_on')) or today)).days for t in terms] or [0]),'broken_links':sum(x.startswith('enlace roto:') for x in broken),'broken_anchors':sum(x.startswith('ancla rota:') for x in broken),'collisions':sum('colisiona' in x or 'duplicado' in x for x in result['errors']),'orphans':sum(1 for t in terms if t.get('status')!='draft' and t.get('id') not in referenced),'unused_aliases':sum(len(t.get('aliases',[])) for t in terms),'deprecated_linked':sum(1 for t in terms if t.get('status') in {'deprecated','superseded'} and t.get('id') in referenced),'warnings':{'count':len(result['warnings']),'ratio':len(result['warnings'])/len(terms) if terms else 0}}
    result['metrics']=metrics; return result,code

def add(args,root):
    try: data=load_registry(root)
    except FileNotFoundError: return error('registro faltante'),EXIT_MISSING
    label=args.label.strip(); ident=re.sub(r'[^a-z0-9]+','-',label.casefold()).strip('-')
    if any(norm(label)==norm(x.get('label')) or ident==x.get('id') for x in data['terms']): return error('colisión: el término ya existe'),EXIT_USAGE
    if not args.non_interactive or any(not x for x in [args.definition,args.context,args.source,args.owner,args.review_due]): return error('faltan campos obligatorios para --non-interactive'),EXIT_USAGE
    t={'id':ident,'label':label,'aliases':args.alias or [],'acronym':args.acronym,'anchor':'glossary-'+ident,'category':args.category,'definition':args.definition,'context':args.context,'source':[{'path':args.source}],'related':[],'owner':args.owner,'status':'active','reviewed_on':args.reviewed_on,'review_due':args.review_due,'introduced_in':None,'deprecated_by':None}; data['terms'].append(t); data['terms'].sort(key=lambda x:x['id']); (root/'docs/glossary/terms.yaml').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); render(root); return {'errors':[],'warnings':[]},EXIT_OK

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument('--root',default='.',type=Path); p.add_argument('--format',choices=['human','json'],default='human'); sub=p.add_subparsers(dest='command',required=True)
    c=sub.add_parser('check'); c.add_argument('--strict',action='store_true'); c.add_argument('--format',choices=['human','json'],default='human')
    r=sub.add_parser('render'); r.add_argument('--check',action='store_true'); r.add_argument('--format',choices=['human','json'],default='human')
    q=sub.add_parser('report'); q.add_argument('--format',choices=['human','json'],default='human')
    a=sub.add_parser('add'); a.add_argument('--label',required=True); a.add_argument('--alias',action='append'); a.add_argument('--acronym'); a.add_argument('--category',required=True,choices=sorted(CATEGORIES)); a.add_argument('--owner',required=True); a.add_argument('--definition'); a.add_argument('--context'); a.add_argument('--source'); a.add_argument('--reviewed-on',default=dt.date.today().isoformat()); a.add_argument('--review-due'); a.add_argument('--non-interactive',action='store_true'); a.add_argument('--format',choices=['human','json'],default='human')
    args=p.parse_args(argv); root=args.root.resolve()
    try:
        if args.command=='check': result,code=validate(root,args.strict)
        elif args.command=='render': ok,_=render(root,args.check); result={'errors':[] if ok else ['render drift: README.md no coincide con registry'],'warnings':[]}; code=EXIT_OK if ok else EXIT_INVALID
        elif args.command=='add': result,code=add(args,root)
        else: result,code=report(root)
    except (FileNotFoundError,OSError,ValueError) as exc: result=error(f'archivo faltante o entorno incompatible: {exc}'); code=EXIT_MISSING
    if args.format=='json': print(json.dumps(result,ensure_ascii=False,sort_keys=True))
    else:
        for key in ('errors','warnings'):
            for item in result.get(key,[]): print(f'{key[:-1].upper()}: {item}')
        if not result.get('errors'): print('glossary: OK' + (f' ({len(result.get("warnings",[]))} advertencias)' if result.get('warnings') else ''))
    return code
if __name__=='__main__': sys.exit(main())
