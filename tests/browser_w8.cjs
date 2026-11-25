const {chromium}=require('playwright-core');
const fs=require('node:fs');
const path=require('node:path');
const assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const output=path.join(root,'runs/w8');
(async()=>{
  const server=JSON.parse(fs.readFileSync(path.join(output,'fixture-server.json'),'utf8'));
  const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
  const context=await browser.newContext({viewport:{width:1440,height:1000}});
  const page=await context.newPage();
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  const checks=[];
  try{
    // Never run delete tests against the real app or a private history database.
    const fixtureStatus=await (await page.request.get(server.url+'/api/status')).json();
    assert.equal(fixtureStatus.fixture_execution,true);
    // Use an isolated browser session and remove only this fixture server's data.
    const sessions=await (await page.request.get(server.url+'/api/session/get-sessions')).json();
    for(const session of sessions.sessions)await page.request.delete(server.url+'/api/session/delete-session/'+session.id);
    await page.goto(server.url);
    await page.locator('#send').waitFor();
    await page.waitForFunction(()=>!document.querySelector('#send').disabled);
    assert.match(await page.locator('#runtime-status').textContent(),/FIXTURE/);
    await page.locator('#question').fill('Synthetic W8: đi xe máy không đội mũ bảo hiểm?');
    await page.locator('#send').click();
    await page.waitForFunction(()=>document.querySelectorAll('.message.bot').length===1&&!document.querySelector('#send').disabled);
    assert.ok(await page.locator('.progress-list li').count()>3);
    assert.equal(await page.locator('.source-card').count(),1);
    checks.push('stage_sse_and_source_cards');
    await page.screenshot({path:path.join(output,'integrated-app-fixture.png'),fullPage:true});
    await page.getByRole('button',{name:'Đọc nội dung nguồn'}).click();
    await page.locator('#source-dialog[open]').waitFor();
    assert.match(await page.locator('#dialog-text').textContent(),/synthetic/);
    await page.screenshot({path:path.join(output,'source-dialog-fixture.png'),fullPage:true});
    await page.locator('#close-source').click();checks.push('source_snapshot_dialog');
    await page.reload();
    await page.waitForFunction(()=>document.querySelectorAll('.message.bot').length===1&&!document.querySelector('#send').disabled);
    assert.match(await page.locator('.message.user').textContent(),/Synthetic W8/);
    assert.equal(await page.locator('.source-card').count(),1);checks.push('reload_history_and_citations');
    await page.locator('#new-chat').click();
    await page.waitForFunction(()=>document.querySelectorAll('.message').length===0&&document.querySelectorAll('.history-row').length===2);
    await page.locator('#question').fill('Synthetic W8: tiền lương thử việc?');await page.locator('#send').click();
    await page.waitForFunction(()=>document.querySelectorAll('.message.bot').length===1&&!document.querySelector('#send').disabled);
    await page.getByRole('button',{name:'Synthetic W8: đi xe máy không đội mũ bảo hiểm?',exact:true}).click();
    await page.waitForFunction(()=>document.querySelectorAll('.message.user').length===1&&document.querySelector('.message.user').textContent.includes('mũ bảo hiểm'));
    checks.push('session_switch_isolation');
    const row=page.locator('.history-row').filter({has:page.getByRole('button',{name:'Synthetic W8: tiền lương thử việc?',exact:true})});
    page.once('dialog',dialog=>dialog.accept());await row.locator('.history-delete').click();
    await page.waitForFunction(()=>document.querySelectorAll('.history-row').length===1);checks.push('delete_session');
    await page.setViewportSize({width:390,height:844});
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
    await page.screenshot({path:path.join(output,'mobile-history-fixture.png'),fullPage:true});checks.push('mobile_history_no_horizontal_overflow');
    await page.getByRole('button',{name:'Xem nguồn của câu trả lời này'}).click();
    await page.locator('#sources-panel.mobile-open').waitFor();
    await page.getByRole('button',{name:'Đọc nội dung nguồn'}).click();
    await page.locator('#source-dialog[open]').waitFor();
    await page.locator('#close-source').click();await page.locator('#close-sources-panel').click();
    checks.push('mobile_source_snapshot_access');
    await page.setViewportSize({width:1440,height:1000});await page.locator('#new-chat').click();
    await page.waitForFunction(()=>document.querySelectorAll('.message').length===0&&!document.querySelector('#send').disabled);
    await page.locator('#question').fill('W8_PROVIDER_ERROR');await page.locator('#send').click();
    await page.waitForFunction(()=>document.querySelectorAll('.message.bot').length===1&&!document.querySelector('#send').disabled);
    assert.match(await page.locator('.message.bot').textContent(),/Chưa hoàn tất/);
    await page.locator('#refresh-history').click();
    await page.waitForFunction(()=>document.querySelector('.message.bot')?.textContent.includes('Lượt trước chưa hoàn tất'));
    assert.equal(await page.locator('.source-card').count(),0);checks.push('provider_failure_persisted_without_fake_answer');
    await page.screenshot({path:path.join(output,'failure-history-fixture.png'),fullPage:true});
    assert.deepEqual(errors,[]);
    const report={status:'passed',run_at:new Date().toISOString(),checks,checks_passed:checks.length,
      browser:'installed Chrome via playwright-core 1.56.1',fixture_execution:true,aws_calls:0,real_model_inference:false,
      screenshots:['integrated-app-fixture.png','source-dialog-fixture.png','mobile-history-fixture.png','failure-history-fixture.png'],javascript_errors:errors};
    fs.writeFileSync(path.join(output,'browser-results.json'),JSON.stringify(report,null,2)+'\n');
    console.log(JSON.stringify(report));
  }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
