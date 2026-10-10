(function(){let e=document.createElement(`link`).relList;if(e&&e.supports&&e.supports(`modulepreload`))return;for(let e of document.querySelectorAll(`link[rel="modulepreload"]`))n(e);new MutationObserver(e=>{for(let t of e)if(t.type===`childList`)for(let e of t.addedNodes)e.tagName===`LINK`&&e.rel===`modulepreload`&&n(e)}).observe(document,{childList:!0,subtree:!0});function t(e){let t={};return e.integrity&&(t.integrity=e.integrity),e.referrerPolicy&&(t.referrerPolicy=e.referrerPolicy),t.credentials=e.crossOrigin===`use-credentials`?`include`:e.crossOrigin===`anonymous`?`omit`:`same-origin`,t}function n(e){if(e.ep)return;e.ep=!0;let n=t(e);fetch(e.href,n)}})();function e(e,t){return Math.max(0,Math.ceil((e-t)/1e3))}function t(e){let t=Math.max(0,Math.floor(e)),n=Math.floor(t/60),r=t%60;return`${String(n).padStart(2,`0`)}:${String(r).padStart(2,`0`)}`}function n(e,t){if(e<=0)return 0;let n=e-Math.max(0,t);return Math.min(100,Math.max(0,n/e*100))}var r=[{id:`session-1`,title:`Shape the next idea`,durationMinutes:25,remainingSeconds:1500,completed:!1},{id:`session-2`,title:`Sort the working notes`,durationMinutes:15,remainingSeconds:900,completed:!1},{id:`session-3`,title:`Read with intention`,durationMinutes:45,remainingSeconds:2700,completed:!1}],i=document.querySelector(`#app`);if(!i)throw Error(`Tempo Board needs an #app element.`);var a=i;i.innerHTML=`
  <div class="app-shell">
    <header class="site-header">
      <a class="brand" href="/" aria-label="Tempo Board home">
        <span class="brand-mark" aria-hidden="true"><span></span><span></span><span></span></span>
        <span>tempo <span class="brand-light">board</span></span>
      </a>
      <p class="header-note">A little structure for your next stretch of focus.</p>
    </header>

    <main class="workspace" id="workspace">
      <section class="focus-section" aria-labelledby="page-title">
        <header class="page-intro">
          <p class="date-line" id="today-label"></p>
          <h1 id="page-title">Make room for focus.</h1>
          <p>Choose a session, then settle into one thing at a time.</p>
        </header>

        <article class="timer-card" aria-labelledby="session-title">
          <div class="timer-topline">
            <p id="timer-status" class="timer-status" role="status">Ready to begin</p>
            <p id="timer-length" class="timer-length">25 minute session</p>
          </div>
          <div class="timer-copy">
            <h2 id="session-title">Shape the next idea</h2>
            <p id="timer-hint">Take a breath. Then begin.</p>
          </div>
          <time
            class="timer-display"
            id="timer-display"
            role="timer"
            aria-live="off"
            datetime="PT1500S"
            aria-label="25 minutes remaining"
          >25:00</time>
          <div
            class="progress-track"
            id="progress-track"
            role="progressbar"
            aria-label="Session progress"
            aria-valuemin="0"
            aria-valuemax="100"
            aria-valuenow="0"
            aria-valuetext="0% complete"
          >
            <span class="progress-fill" id="progress-fill" aria-hidden="true"></span>
          </div>
          <div class="timer-footer">
            <p class="timer-footnote">One thing at a time.</p>
            <div class="timer-actions">
              <button class="button-primary" id="start-button" type="button">Start session</button>
              <button class="button-quiet" id="reset-button" type="button" disabled>Reset</button>
            </div>
          </div>
        </article>

        <p class="privacy-note"><span aria-hidden="true"></span> No account or sync; your plan stays in this tab.</p>
      </section>

      <aside class="plan-panel" aria-labelledby="plan-title">
        <header class="plan-heading">
          <div>
            <h2 id="plan-title">Your sessions</h2>
            <p>Keep the next step small.</p>
          </div>
          <span class="queue-count" id="queue-count">3 sessions left</span>
        </header>

        <ol class="session-list" id="session-list" aria-label="Focus session queue"></ol>
        <div class="empty-queue" id="empty-queue" hidden>
          <p class="empty-title">Nothing on the plan yet.</p>
          <p>Add one small session to get started.</p>
        </div>

        <form class="session-form" id="session-form" action="/" method="get">
          <h3>Add to your plan</h3>
          <div class="field-group">
            <label for="session-name">Session name</label>
            <input
              id="session-name"
              name="session-name"
              type="text"
              required
              minlength="1"
              maxlength="48"
              autocomplete="off"
              aria-describedby="session-name-help session-name-error"
              aria-errormessage="session-name-error"
              placeholder="What will you focus on?"
            />
            <p class="field-help" id="session-name-help">A few words is plenty.</p>
            <p class="field-error" id="session-name-error" hidden></p>
          </div>
          <fieldset class="duration-fieldset">
            <legend>Choose a length</legend>
            <div class="duration-options">
              <label class="duration-choice">
                <input type="radio" name="duration" value="15" required />
                <span>15 <small>min</small></span>
              </label>
              <label class="duration-choice">
                <input type="radio" name="duration" value="25" checked required />
                <span>25 <small>min</small></span>
              </label>
              <label class="duration-choice">
                <input type="radio" name="duration" value="45" required />
                <span>45 <small>min</small></span>
              </label>
            </div>
          </fieldset>
          <button class="button-add" type="submit">Add session</button>
        </form>

      </aside>
    </main>
    <p class="sr-only" id="live-announcement" role="status" aria-live="polite"></p>
  </div>
`;function o(e){let t=a.querySelector(e);if(!t)throw Error(`Missing Tempo Board element: ${e}`);return t}var s=o(`#session-list`),c=o(`#empty-queue`),l=o(`#queue-count`),u=o(`#timer-status`),d=o(`#timer-length`),f=o(`#session-title`),p=o(`#timer-hint`),m=o(`#timer-display`),h=o(`#progress-track`),g=o(`#progress-fill`),_=o(`#start-button`),v=o(`#reset-button`),y=o(`#session-form`),b=o(`#session-name`),x=o(`#session-name-error`),S=o(`#live-announcement`),C=o(`#today-label`),w=r[0]?.id??null,T=!1,E=null,D,O=r.length,k;C.textContent=new Intl.DateTimeFormat(void 0,{weekday:`long`,month:`long`,day:`numeric`}).format(new Date);function A(){return r.find(e=>e.id===w)}function j(e){return e.replace(/[&<>"']/g,e=>({"&":`&amp;`,"<":`&lt;`,">":`&gt;`,'"':`&quot;`,"'":`&#39;`})[e]??e)}function M(e){return e.completed?`Complete`:e.id===w&&T?`In focus`:e.id===w&&e.remainingSeconds<e.durationMinutes*60?`Paused`:`Up next`}function N(){let e=r.filter(e=>!e.completed).length;l.textContent=e===0?`All done`:`${e} ${e===1?`session`:`sessions`} left`,c.hidden=r.length!==0,s.hidden=r.length===0,s.innerHTML=r.map(e=>{let t=e.id===w,n=j(e.title),r=M(e);return`
        <li class="session-item${t?` is-selected`:``}${e.completed?` is-complete`:``}">
          <button
            class="session-select"
            type="button"
            data-session-id="${e.id}"
            aria-pressed="${t}"
            aria-label="Select ${n}, ${e.durationMinutes} minutes"
          >
            <span class="session-marker" aria-hidden="true"></span>
            <span class="session-details">
              <span class="session-name">${n}</span>
              <span class="session-meta">${e.durationMinutes} min <span aria-hidden="true">·</span> ${r}</span>
            </span>
          </button>
          <button
            class="remove-session"
            type="button"
            data-remove-id="${e.id}"
            aria-label="Remove ${n}"
          >Remove</button>
        </li>
      `}).join(``)}function P(){k?.cancel();let e=window.matchMedia(`(prefers-reduced-motion: reduce)`).matches;k=f.animate(e?[{opacity:.78},{opacity:1}]:[{opacity:.78,transform:`translateY(3px)`},{opacity:1,transform:`translateY(0)`}],{duration:e?140:180,easing:`cubic-bezier(0.23, 1, 0.32, 1)`})}function F(){let e=A();if(_.disabled=!e,!e){u.textContent=`No session selected`,d.textContent=`Add a session to begin`,f.textContent=`Your next session will land here.`,p.textContent=`Add one small step to get started.`,m.textContent=`00:00`,m.dateTime=`PT0S`,m.setAttribute(`aria-label`,`No session selected`),h.setAttribute(`aria-valuenow`,`0`),h.setAttribute(`aria-valuetext`,`No session selected`),g.style.transform=`scaleX(0)`,_.textContent=`Start session`,v.disabled=!0;return}let r=e.durationMinutes*60,i=n(r,e.remainingSeconds),a=Math.ceil(e.remainingSeconds/60),o=T?`In focus`:e.completed?`Session complete`:e.remainingSeconds<r?`Paused`:`Ready to begin`;u.textContent!==o&&(u.textContent=o),d.textContent=`${e.durationMinutes} minute${e.durationMinutes===1?``:`s`} session`,f.textContent=e.title,p.textContent=T?`Stay with this one small step.`:e.completed?`You gave this one your time. Well done.`:e.remainingSeconds<r?`Paused. Continue when you’re ready.`:`Take a breath. Then begin.`,m.textContent=t(e.remainingSeconds),m.dateTime=`PT${e.remainingSeconds}S`,m.setAttribute(`aria-label`,`${a} ${a===1?`minute`:`minutes`} remaining`),h.setAttribute(`aria-valuenow`,String(Math.round(i))),h.setAttribute(`aria-valuetext`,`${Math.round(i)}% complete`),g.style.transform=`scaleX(${i/100})`,_.textContent=T?`Pause session`:e.completed?`Start again`:e.remainingSeconds<r?`Continue session`:`Start session`,v.disabled=!T&&!e.completed&&e.remainingSeconds===r}function I(){N(),F()}function L(){D!==void 0&&window.clearInterval(D),D=void 0}function R(){let t=A();t&&T&&E!==null&&(t.remainingSeconds=e(E,Date.now()),T=!1,E=null,L())}function z(){let t=A();if(!t||!T||E===null)return;let n=e(E,Date.now());n!==t.remainingSeconds&&(t.remainingSeconds=n,F()),n===0&&(t.completed=!0,T=!1,E=null,L(),S.textContent=`${t.title} is complete.`,I())}function B(){let e=A();e&&(e.completed&&(e.completed=!1,e.remainingSeconds=e.durationMinutes*60),!(e.remainingSeconds<=0)&&(T=!0,E=Date.now()+e.remainingSeconds*1e3,L(),D=window.setInterval(z,250),S.textContent=`Started ${e.title}.`,I()))}function V(){let e=b.value.trim().length===0;b.setCustomValidity(e?`Enter a short name for this session.`:``)}b.addEventListener(`invalid`,()=>{b.setAttribute(`aria-invalid`,`true`),x.textContent=b.validationMessage,x.hidden=!1}),b.addEventListener(`input`,()=>{V(),b.validity.valid&&(b.removeAttribute(`aria-invalid`),x.hidden=!0)}),y.addEventListener(`submit`,e=>{if(e.preventDefault(),V(),!y.reportValidity())return;let t=b.value.trim(),n=Number(new FormData(y).get(`duration`)),i={id:`session-${++O}`,title:t,durationMinutes:n,remainingSeconds:n*60,completed:!1};r.push(i),w===null&&(w=i.id,f.textContent=i.title,P()),b.value=``,b.removeAttribute(`aria-invalid`),x.hidden=!0,S.textContent=`Added ${i.title} to your plan.`,I(),b.focus()}),s.addEventListener(`click`,e=>{let t=e.target;if(!(t instanceof HTMLElement))return;let n=t.closest(`[data-remove-id]`);if(n){let e=r.findIndex(e=>e.id===n.dataset.removeId);if(e<0)return;let t=r[e]?.id===w;t&&T&&(z(),R());let[i]=r.splice(e,1);if(!i)return;if(t&&(w=r[e]?.id??r[e-1]?.id??null,w)){let e=A();e&&(f.textContent=e.title),P()}S.textContent=`Removed ${i.title} from your plan.`,I();return}let i=t.closest(`[data-session-id]`)?.dataset.sessionId;if(!i||i===w)return;z(),R(),w=i;let a=A();a&&(f.textContent=a.title),P(),S.textContent=a?`Selected ${a.title}.`:`Session selected.`,I()}),_.addEventListener(`click`,()=>{if(T){z(),R();let e=A();e&&(S.textContent=`Paused ${e.title}.`),I()}else B()}),v.addEventListener(`click`,()=>{let e=A();e&&(L(),T=!1,E=null,e.completed=!1,e.remainingSeconds=e.durationMinutes*60,S.textContent=`Reset ${e.title}.`,I())}),I();