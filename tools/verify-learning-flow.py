"""WebView2 UI regression probe; requires Python websockets.

Create target/navigation-course.json from the current KPC course, with a
unique course id and the first two units. Launch the debug app with that
MOLIP_COURSE_PATH and remote-debugging-port=9227. This clears the first unit;
do not run against student progress. Tests Markdown colors, correct-answer
popups, CodeMirror, mission navigation and navigation between units.
"""
import asyncio,json,urllib.request
from pathlib import Path
import websockets

async def main():
 course=json.loads(Path('target/navigation-course.json').read_text(encoding='utf-8'))
 solutions=json.loads(Path('courses/kpc-solutions.json').read_text(encoding='utf-8'))
 target=json.load(urllib.request.urlopen('http://localhost:9227/json/list'))[0]
 async with websockets.connect(target['webSocketDebuggerUrl']) as ws:
  sequence=0
  async def js(expression):
   nonlocal sequence
   sequence+=1
   await ws.send(json.dumps({'id':sequence,'method':'Runtime.evaluate','params':{'expression':expression,'returnByValue':True}}))
   while True:
    response=json.loads(await ws.recv())
    if response.get('id')==sequence:
     result=response['result']
     if 'exceptionDetails' in result:raise RuntimeError(result['exceptionDetails'])
     return result['result'].get('value')
  async def click(text):
   await js('Array.from(document.querySelectorAll("button")).find(b=>b.textContent.trim()=='+json.dumps(text)+')?.click()')
   await asyncio.sleep(.2)
  async def expect(expression,label):
   assert await js(expression),label
   print('PASS',label)
  async def wait_popup():
   for _ in range(100):
    if await js("!!document.querySelector('[aria-label=\"정답 확인\"]')"):return
    await asyncio.sleep(.1)
   raise AssertionError('correct-answer popup missing')
  await click('학습 시작 · 이어하기')
  await expect("Array.from(document.querySelectorAll('button')).find(b=>b.textContent.trim()==='다음 →').disabled",'next locked before correct answer')
  await expect("!!document.querySelector('.markdown code.language-python .tok-string')",'Markdown Python syntax colors')
  await expect("!!document.querySelector('.markdown blockquote strong')",'Markdown emphasis and callout')
  activities=course['chapters'][0]['units'][0]['activities']
  for index,activity in enumerate(activities):
   kind=activity['kind']
   if kind in ['concept','quiz']:
    questions=[activity['check']] if kind=='concept' else activity['questions']
    for q in questions:
     if q['type']=='short_answer':
      answer=q['accepted'][0]
      await js('(()=>{const input=Array.from(document.querySelectorAll("input")).find(e=>e.getAttribute("aria-label")=='+json.dumps(q['prompt'])+');input.value='+json.dumps(answer)+';input.dispatchEvent(new InputEvent("input",{bubbles:true,data:'+json.dumps(answer)+'}));})()')
     else:
      await js('document.querySelector("input[name=\\"'+q['id']+'\\"][value=\\"'+str(q['correct'])+'\\"]").click()')
     await asyncio.sleep(.1)
    await click('채점 · 클리어 확인')
   else:
    await expect("!!document.querySelector('.cm-editor .cm-content')",'CodeMirror content mounted')
    source=solutions[activity['problem']['id']]
    await js('(()=>{const textarea=document.querySelector("textarea[data-code-editor]");textarea.value='+json.dumps(source)+';textarea.dispatchEvent(new Event("input",{bubbles:true}));})()')
    await asyncio.sleep(.2)
    await expect('document.querySelector(".cm-content").textContent.includes('+json.dumps(source.splitlines()[0])+')','CodeMirror synchronized with code')
    await click('테스트 · 완료')
   await wait_popup()
   await expect("document.querySelector('[aria-label=\"정답 확인\"]').textContent.includes('정답입니다!')",'correct-answer popup')
   await click('확인')
   await expect('document.querySelectorAll(".mission-tabs button")['+str(index)+'].classList.contains("selected")','stays on cleared mission')
   if index==0:
    await click('다음 →')
    await expect("!!document.querySelector('.cm-editor .cm-content')",'next opens coding editor')
    await click('← 이전')
    await expect("!!document.querySelector('.concept-flow')",'previous returns to concept')
    await click('다음 →')
   else:await click('다음 →')
  await expect('document.querySelector(".mission-heading strong").textContent.includes('+json.dumps(course['chapters'][0]['units'][1]['title'])+')','next crosses unit boundary')
  await click('← 이전')
  await expect('document.querySelector(".mission-heading strong").textContent.includes('+json.dumps(course['chapters'][0]['units'][0]['title'])+')','previous crosses unit boundary')
  print('ALL UI FLOW CHECKS PASSED')

asyncio.run(main())
