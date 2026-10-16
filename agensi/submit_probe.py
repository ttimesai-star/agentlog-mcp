"""Probe the Agensi submit form: upload the zip, open the collapsed sections, dump their fields. No submission."""
import os, sys
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
SC = sys.argv[1]
prof = os.path.expanduser('~/.claude/browser_profiles/agensi_ttimesai')


def P(*a):
    print(*a, flush=True)


with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(prof, headless=True, viewport={'width': 1280, 'height': 2400}, locale='en-US')
    ctx.set_default_timeout(20000)
    pg = ctx.pages[0]
    pg.goto('https://www.agensi.io/dashboard/submit', wait_until='domcontentloaded')
    pg.wait_for_timeout(4000)
    files = pg.query_selector_all('input[type=file]')
    P('file inputs', len(files))
    files[0].set_input_files(os.path.join(HERE, 'agentlog-audit.zip'))
    pg.wait_for_timeout(4000)
    for _ in range(30):
        if 'Generating listing metadata' not in pg.inner_text('body'): break
        pg.wait_for_timeout(2000)
    pg.wait_for_timeout(1500)
    pg.screenshot(path=os.path.join(SC,'probe_after_upload.png'))
    P(pg.inner_text('body')[:1500])
    for el in pg.query_selector_all('input,select,textarea'):
        try:
            P('EL0', el.evaluate('e=>[e.tagName,e.type,e.name,e.id,e.placeholder,e.value.slice(0,30)].join("|")'))
        except Exception:
            pass
    for label in ['Tags, Categories, Usecases', 'Permissions', 'Extra Details', 'FAQ', 'Documentation Link']:
        try:
            pg.get_by_role('button', name=label).first.click()
            pg.wait_for_timeout(800)
        except Exception as e:
            P('open fail', label, str(e)[:80])
    pg.wait_for_timeout(1000)
    t = pg.inner_text('body')
    i = t.find('Pricing Model')
    j = t.find('LIVE PREVIEW')
    P(t[i:j])
    for el in pg.query_selector_all('input,select,textarea'):
        try:
            P('EL', el.evaluate('e=>[e.tagName,e.type,e.name,e.id,e.placeholder,e.value.slice(0,40)].join("|")'))
        except Exception:
            pass
    pg.screenshot(path=os.path.join(SC, 'probe_form.png'), full_page=True)
    ctx.close()
