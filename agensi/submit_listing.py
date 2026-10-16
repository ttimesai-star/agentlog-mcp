"""Fill (and with --submit, send) the Agensi listing for agentlog-audit as a FREE skill.
Usage: python submit_listing.py <screenshot_dir> [--submit]
Profile: ~/.claude/browser_profiles/agensi_ttimesai (logged in as ttimesai@gmail.com)."""
import os, sys
from playwright.sync_api import sync_playwright
import listing_content as C

HERE = os.path.dirname(os.path.abspath(__file__))
SC = sys.argv[1]
SUBMIT = '--submit' in sys.argv
prof = os.path.expanduser('~/.claude/browser_profiles/agensi_ttimesai')
SHOTS = [os.path.join(HERE, '..', 'video', 'work', 'p1_clean.png'), os.path.join(HERE, '..', 'video', 'work', 'p_edit.png')]
TAGS = ['mcp', 'audit-log', 'tamper-evident', 'agent-logging', 'security', 'compliance', 'observability']
USECASES = ['Prove to a client what an AI agent did and that the log was not edited',
            'Answer "what did my agent do yesterday?" with a verified daily audit',
            'Settle a dispute between an operator and a client over an agent run',
            'Keep a signed action log for agent runs that change records or money']


def P(*a):
    print(*a, flush=True)


def shot(pg, name):
    pg.screenshot(path=os.path.join(SC, name), full_page=True)


def set_text(loc, text):
    loc.click()
    loc.fill(text)


with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(prof, headless=True, viewport={'width': 1280, 'height': 2400}, locale='en-US')
    ctx.set_default_timeout(25000)
    pg = ctx.pages[0]
    pg.goto('https://www.agensi.io/dashboard/submit', wait_until='domcontentloaded')
    pg.wait_for_timeout(4000)
    pg.query_selector_all('input[type=file]')[0].set_input_files(os.path.join(HERE, 'agentlog-audit.zip'))
    pg.wait_for_timeout(4000)
    for _ in range(40):
        if 'Generating listing metadata' not in pg.inner_text('body'):
            break
        pg.wait_for_timeout(2000)
    pg.wait_for_timeout(2000)
    # drop everything the site's AI drafted: every sentence on the listing must be ours
    pg.get_by_role('button', name='Clear all autofill').click()
    pg.wait_for_timeout(1000)
    pg.get_by_role('button', name='Clear fields').click()
    pg.wait_for_timeout(2500)
    P('autofill cleared')

    shot(pg,'cleared.png'); P(pg.inner_text('body')[:600])
    # logo
    pg.query_selector_all('input[type=file]')[1].set_input_files(os.path.join(HERE, 'agentlog_logo_512.png'))
    pg.wait_for_timeout(2500)
    shot(pg,'afterlogo.png'); P([ (e.get_attribute('name') or e.get_attribute('placeholder') or '')[:30] for e in pg.query_selector_all('input,textarea')][:12])
    set_text(pg.locator('input[placeholder^="e.g., Code Reviewer"]'), C.NAME)
    set_text(pg.locator('input[placeholder^="e.g., Deep code review"]'), C.SUMMARY)
    set_text(pg.locator('textarea[placeholder^="Describe what your skill"]'), C.DESCRIPTION)
    set_text(pg.locator('textarea[placeholder^="e.g., Review this React"]'), C.SAMPLE_INPUT)
    set_text(pg.locator('textarea[placeholder^="## Summary"]'), C.SAMPLE_OUTPUT)
    set_text(pg.locator('textarea[placeholder^="e.g., Requires Node.js 18"]'), C.COMPAT)
    shot(pg,'prepricing.png')
    pg.get_by_text('No charge').first.click()
    P('basics filled')
    shot(pg, 'fill1.png')

    for label in ['Tags, Categories, Usecases', 'Extra Details', 'FAQ']:
        try:
            pg.get_by_role('button', name=label).first.click(timeout=5000)
            pg.wait_for_timeout(800)
        except Exception as e:
            P('open fail', label)
    # tags
    tag_in = pg.locator('input[placeholder="Add a tag"]')
    for t in TAGS:
        tag_in.fill(t)
        tag_in.press('Enter')
        pg.wait_for_timeout(200)
    # use cases
    uc = pg.locator('input[placeholder="e.g., Pre-commit code reviews"]')
    for u in USECASES:
        uc.fill(u)
        uc.press('Enter')
        pg.wait_for_timeout(300)
    P('tags + use cases')
    shot(pg, 'fill2.png')

    # categories
    cat = pg.locator('input[placeholder="Search categories"]')
    cat.click()
    pg.wait_for_timeout(500)
    for c in ['LLM Ops', 'Security', 'Agents & Orchestration']:
        cat.fill(c)
        pg.wait_for_timeout(500)
        pg.get_by_text(c, exact=True).last.click()
        pg.wait_for_timeout(500)
    P('categories')
    shot(pg, 'fill3.png')

    # requirements, permission notes, limitations
    if not pg.locator('textarea[placeholder^="apple-music-mcp"]').is_visible():
        pg.get_by_role('button', name='Permissions').first.click()
        pg.wait_for_timeout(1000)
    set_text(pg.locator('textarea[placeholder^="apple-music-mcp"]'), C.REQUIREMENTS)
    set_text(pg.locator('textarea[placeholder^="Explain why these permissions"]'), C.PERM_NOTES)
    set_text(pg.locator('textarea[placeholder^="e.g., Does not support TypeScript"]'),
             "Needs the agentlog MCP server running; the skill alone logs nothing.\n"
             "Anyone holding both the agent's key and the log file can rewrite a whole run consistently (optional Arkiv mode closes this).\n"
             "Proves that a step changed, not who changed it, and not that the agent told the truth when it wrote.\n"
             "Verified with the official MCP TypeScript SDK client; not yet tried in every listed agent.")
    # FAQ
    for q, a in C.FAQ:
        pg.locator('input[placeholder="New question"]').fill(q)
        pg.locator('textarea[placeholder="Answer"]').last.fill(a)
        pg.get_by_role('button', name='Add FAQ').click()
        pg.wait_for_timeout(500)
    P('requirements, FAQ')
    # screenshots + demo video + docs link
    if '--noshots' not in sys.argv:
        pg.query_selector_all('input[type=file]')[-1].set_input_files([os.path.abspath(s) for s in SHOTS])
    pg.wait_for_timeout(1000)
    set_text(pg.locator('input[placeholder^="https://youtube.com"]'), C.DEMO_VIDEO)
    try:
        pg.get_by_text('Documentation Link').first.click()
        pg.wait_for_timeout(800)
        dl = pg.locator('input[placeholder*="docs" i], input[placeholder*="http" i]').last
        P('doc input placeholder:', dl.get_attribute('placeholder'))
        dl.fill(C.DOC_LINK)
    except Exception as e:
        P('doc link fail', str(e)[:100])
    pg.wait_for_timeout(2000)
    shot(pg, 'fill4.png')
    t = pg.inner_text('body')
    P('error words:', [w for w in ('required', 'invalid', 'error') if w in t.lower()])
    if SUBMIT:
        pg.get_by_role('button', name='Submit for Review').first.click()
        pg.wait_for_timeout(8000)
        P('after submit url', pg.url)
        P(pg.inner_text('body')[:1500])
        shot(pg, 'after_submit.png')
    ctx.close()
