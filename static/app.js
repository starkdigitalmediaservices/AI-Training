const $ = (s) => document.querySelector(s);

// Beautiful UI Helper Functions
function showToast(message, type = 'info') {
  const toast = document.createElement('div');
  toast.className = `fixed top-4 right-4 z-50 px-6 py-3 rounded-lg text-white font-medium transform translate-x-full transition-transform duration-300 ${
    type === 'success' ? 'bg-green-500' : 
    type === 'error' ? 'bg-red-500' : 
    type === 'warning' ? 'bg-yellow-500' : 'bg-blue-500'
  }`;
  toast.textContent = message;
  document.body.appendChild(toast);
  
  setTimeout(() => toast.style.transform = 'translateX(0)', 100);
  setTimeout(() => {
    toast.style.transform = 'translateX(100%)';
    setTimeout(() => document.body.removeChild(toast), 300);
  }, 3000);
}

function setStatus(element, message, type = 'info') {
  const icon = element.querySelector('i');
  const text = element.querySelector('span');
  
  if (icon && text) {
    icon.className = type === 'success' ? 'fas fa-check-circle mr-1' :
                    type === 'error' ? 'fas fa-times-circle mr-1' :
                    type === 'warning' ? 'fas fa-exclamation-triangle mr-1' :
                    'fas fa-info-circle mr-1';
    
    text.textContent = message;
    element.className = `text-sm flex items-center ${
      type === 'success' ? 'text-green-400' :
      type === 'error' ? 'text-red-400' :
      type === 'warning' ? 'text-yellow-400' :
      'text-gray-300'
    }`;
  }
}

async function saveURLs() {
  const btn = $('#btnSave');
  const originalText = btn.innerHTML;
  btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Saving...';
  btn.disabled = true;
  
  try {
    const payload = {
      calculator_url: $('#calculator_url').value.trim(),
      unit_url: $('#unit_url').value.trim(),
      statistics_url: $('#statistics_url').value.trim(),
    };
    const r = await fetch('/config/agents', { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
    const b = await r.json();
    
    if (b.ok) {
      setStatus($('#urlsStatus'), 'URLs saved successfully!', 'success');
      showToast('Agent URLs saved successfully!', 'success');
    } else {
      setStatus($('#urlsStatus'), 'Error: ' + (b.error || 'unknown'), 'error');
      showToast('Failed to save URLs', 'error');
    }
  } catch (error) {
    setStatus($('#urlsStatus'), 'Connection error', 'error');
    showToast('Connection error', 'error');
  } finally {
    btn.innerHTML = originalText;
    btn.disabled = false;
  }
}

async function testURLs() {
  const btn = $('#btnTest');
  const originalText = btn.innerHTML;
  btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Testing...';
  btn.disabled = true;
  
  try {
    const r = await fetch('/config/test', { method: 'POST' });
    const b = await r.json();
    
    const allOk = Object.values(b).every(result => result.ok);
    if (allOk) {
      setStatus($('#urlsStatus'), 'All agents connected successfully!', 'success');
      showToast('All agents are online!', 'success');
    } else {
      const failed = Object.entries(b).filter(([k, v]) => !v.ok).map(([k]) => k);
      setStatus($('#urlsStatus'), `Failed: ${failed.join(', ')}`, 'error');
      showToast(`Some agents are offline: ${failed.join(', ')}`, 'warning');
    }
  } catch (error) {
    setStatus($('#urlsStatus'), 'Connection test failed', 'error');
    showToast('Connection test failed', 'error');
  } finally {
    btn.innerHTML = originalText;
    btn.disabled = false;
  }
}

function parseCSVFloats(s) {
  return s.split(',').map(x => x.trim()).filter(Boolean).map(parseFloat);
}

function getCalculatorData(operation, numbers) {
  switch(operation) {
    case 'add':
    case 'subtract':
    case 'multiply':
    case 'divide':
      return { numbers };
    case 'power':
      return { base: numbers[0] || 0, exponent: numbers[1] || 2 };
    case 'square_root':
      return { number: numbers[0] || 0 };
    default:
      return { numbers };
  }
}

function updateNumberInputPlaceholder() {
  const operation = $('#calc_op').value;
  const input = $('#numbers');
  switch(operation) {
    case 'add':
    case 'subtract':
    case 'multiply':
    case 'divide':
      input.placeholder = '10,20,30 (multiple numbers)';
      break;
    case 'power':
      input.placeholder = '2,3 (base,exponent)';
      break;
    case 'square_root':
      input.placeholder = '16 (single number)';
      break;
    default:
      input.placeholder = '10,20,30';
  }
}

async function runPipeline() {
  const btn = $('#btnRun');
  const originalText = btn.innerHTML;
  btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Running Pipeline...';
  btn.disabled = true;
  
  // Clear previous results
  $('#stepsBox').innerHTML = '<div class="text-center text-gray-400 py-8"><i class="fas fa-spinner fa-spin text-2xl mb-2"></i><p>Processing pipeline...</p></div>';
  $('#resultBox').innerHTML = '<div class="text-center text-gray-400 py-8"><i class="fas fa-spinner fa-spin text-2xl mb-2"></i><p>Calculating result...</p></div>';
  
  try {
    const calc_op = $('#calc_op').value;
    const numbers = parseCSVFloats($('#numbers').value || '');
    const from_unit = $('#from_unit').value;
    const to_unit = $('#to_unit').value;
    const stats_op = $('#stats_op').value;
    const stats_numbers = parseCSVFloats($('#stats_numbers').value || '');

    const calc_data = getCalculatorData(calc_op, numbers);

    const cfg = await (await fetch('/config/agents')).json();
    const chain = {
      sender: 'ui',
      correlation_id: String(Date.now()),
      trace: [],
      message: { operation: calc_op, data: calc_data },
      next: {
        url: cfg.unit_url + '/convert',
        handoff: { from_unit, to_unit },
        next: {
          url: cfg.statistics_url + '/message',
          handoff: { operation: stats_op, data: { numbers: stats_numbers } }
        }
      }
    };

    const r = await fetch('/route', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ target: 'calculator', endpoint: '/message', payload: chain }) });
    const b = await r.json();
    
    if (r.ok) {
      // Beautiful result display
      const resultHtml = `
        <div class="space-y-4">
          <div class="bg-gradient-to-r from-green-500/20 to-blue-500/20 p-4 rounded-lg border border-green-500/30">
            <h3 class="text-lg font-bold text-green-400 mb-2">🎯 Final Result</h3>
            <p class="text-2xl font-bold text-white">${b.final}</p>
          </div>
          <div class="text-sm text-gray-300">
            <p><strong>Correlation ID:</strong> ${b.correlation_id}</p>
            <p><strong>Trace:</strong> ${b.trace.join(' → ')}</p>
          </div>
        </div>
      `;
      $('#resultBox').innerHTML = resultHtml;
      
      // Beautiful steps display
      const steps = Array.isArray(b.steps) ? b.steps : [];
      const stepsHtml = steps.map((s, i) => `
        <div class="flex items-center p-3 bg-gradient-to-r from-purple-500/10 to-pink-500/10 rounded-lg border border-purple-500/20 mb-2">
          <div class="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-white font-bold mr-3">
            ${i + 1}
          </div>
          <div class="flex-1">
            <p class="font-semibold text-white">${s.agent}</p>
            <p class="text-sm text-gray-300">${s.operation}</p>
          </div>
          <div class="text-right">
            <p class="font-bold text-green-400">${s.result}</p>
          </div>
        </div>
      `).join('');
      
      $('#stepsBox').innerHTML = stepsHtml || '<div class="text-center text-gray-400 py-8"><i class="fas fa-info-circle text-2xl mb-2"></i><p>No steps recorded</p></div>';
      
      setStatus($('#runStatus'), 'Pipeline completed successfully!', 'success');
      showToast('Pipeline executed successfully!', 'success');
      
      // Add success animation
      $('#resultBox').classList.add('success-animation');
      setTimeout(() => $('#resultBox').classList.remove('success-animation'), 600);
    } else {
      throw new Error('Pipeline execution failed');
    }
  } catch (e) {
    $('#resultBox').innerHTML = `
      <div class="text-center text-red-400 py-8">
        <i class="fas fa-exclamation-triangle text-2xl mb-2"></i>
        <p class="font-semibold">Pipeline Error</p>
        <p class="text-sm mt-2">${e.message}</p>
      </div>
    `;
    $('#stepsBox').innerHTML = '<div class="text-center text-gray-400 py-8"><i class="fas fa-times-circle text-2xl mb-2"></i><p>No steps completed</p></div>';
    setStatus($('#runStatus'), 'Pipeline failed', 'error');
    showToast('Pipeline execution failed', 'error');
    
    // Add error animation
    $('#resultBox').classList.add('error-animation');
    setTimeout(() => $('#resultBox').classList.remove('error-animation'), 500);
  } finally {
    btn.innerHTML = originalText;
    btn.disabled = false;
  }
}

async function loadURLs() {
  const cfg = await (await fetch('/config/agents')).json();
  $('#calculator_url').value = cfg.calculator_url || '';
  $('#unit_url').value = cfg.unit_url || '';
  $('#statistics_url').value = cfg.statistics_url || '';
}

window.addEventListener('DOMContentLoaded', () => {
  $('#btnSave').addEventListener('click', saveURLs);
  $('#btnTest').addEventListener('click', testURLs);
  $('#btnRun').addEventListener('click', runPipeline);
  $('#calc_op').addEventListener('change', updateNumberInputPlaceholder);
  loadURLs();
  updateNumberInputPlaceholder(); // Set initial placeholder
});
