// Enhanced Unit Converter with modern UX
let isLoading = false;

async function loadUnits() {
  try {
    showLoading('Loading units...');
    const res = await fetch('/units');
    const data = await res.json();
    const units = data.available_units || {};
    
    const category = document.getElementById('uc-category');
    const fromSel = document.getElementById('uc-from');
    const toSel = document.getElementById('uc-to');
    
    const categories = Object.keys(units);
    category.innerHTML = '<option value="">Select Category</option>' + 
      categories.map(c => `<option value="${c}">${c}</option>`).join('');
    
    function populateFor(cat) {
      const options = units[cat] || [];
      fromSel.innerHTML = '<option value="">From Unit</option>' + 
        options.map(u => `<option value="${u}">${u}</option>`).join('');
      toSel.innerHTML = '<option value="">To Unit</option>' + 
        options.map(u => `<option value="${u}">${u}</option>`).join('');
      
      if (options.length > 1) { 
        toSel.selectedIndex = 1; 
      }
      
      // Clear result when category changes
      document.getElementById('uc-result').value = '';
      hideResult();
    }
    
    populateFor(category.value);
    category.addEventListener('change', () => populateFor(category.value));
    
    hideLoading();
    showSuccess('Units loaded successfully!');
  } catch (e) {
    hideLoading();
    showError('Failed to load units: ' + e.message);
    console.error('Error loading units:', e);
  }
}

async function convertUnits() {
  if (isLoading) return;
  
  const value = Number(document.getElementById('uc-value').value);
  const fromUnit = document.getElementById('uc-from').value;
  const toUnit = document.getElementById('uc-to').value;
  const resultInput = document.getElementById('uc-result');
  
  // Validation
  if (!value || value <= 0) {
    showError('Please enter a valid positive number');
    return;
  }
  
  if (!fromUnit || !toUnit) {
    showError('Please select both from and to units');
    return;
  }
  
  if (fromUnit === toUnit) {
    showError('From and to units cannot be the same');
    return;
  }
  
  try {
    isLoading = true;
    setButtonLoading(true);
    resultInput.value = 'Converting...';
    hideResult();
    
    const res = await fetch('/convert', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        value: value, 
        from_unit: fromUnit, 
        to_unit: toUnit 
      })
    });
    
    const data = await res.json();
    
    if (res.ok && data && data.response && data.response.success) {
      const result = data.response.result;
      resultInput.value = formatNumber(result);
      showSuccess(`${value} ${fromUnit} = ${formatNumber(result)} ${toUnit}`);
      
      // Add animation to result
      resultInput.style.transform = 'scale(1.05)';
      setTimeout(() => {
        resultInput.style.transform = 'scale(1)';
      }, 200);
      
    } else if (data && data.response && data.response.error) {
      showError(data.response.error);
      resultInput.value = '';
    } else if (data && data.error) {
      showError(data.error);
      resultInput.value = '';
    } else {
      showError('Conversion failed - please try again');
      resultInput.value = '';
    }
  } catch (e) {
    showError('Network error: ' + e.message);
    resultInput.value = '';
    console.error('Conversion error:', e);
  } finally {
    isLoading = false;
    setButtonLoading(false);
  }
}

function formatNumber(num) {
  if (num === null || num === undefined) return '0';
  
  // Handle very large or very small numbers
  if (Math.abs(num) >= 1e6 || (Math.abs(num) < 1e-3 && num !== 0)) {
    return num.toExponential(3);
  }
  
  // Round to reasonable precision
  const rounded = Math.round(num * 1e6) / 1e6;
  
  // Format with commas for large numbers
  return rounded.toLocaleString('en-US', {
    maximumFractionDigits: 6,
    minimumFractionDigits: 0
  });
}

function setButtonLoading(loading) {
  const btn = document.getElementById('convert-btn');
  const btnText = btn.querySelector('.btn-text');
  
  if (loading) {
    btn.disabled = true;
    btnText.innerHTML = '<span class="spinner"></span> Converting...';
    btn.classList.add('loading');
  } else {
    btn.disabled = false;
    btnText.textContent = 'Convert Units';
    btn.classList.remove('loading');
  }
}

function showResult(message, type = 'success') {
  const resultDiv = document.getElementById('result');
  resultDiv.textContent = message;
  resultDiv.className = type;
  resultDiv.style.display = 'block';
  
  // Auto-hide after 5 seconds
  setTimeout(() => {
    hideResult();
  }, 5000);
}

function hideResult() {
  const resultDiv = document.getElementById('result');
  resultDiv.style.display = 'none';
}

function showSuccess(message) {
  showResult(message, 'success');
}

function showError(message) {
  showResult(message, 'error');
}

function showWarning(message) {
  showResult(message, 'warning');
}

function showLoading(message) {
  showResult(message, 'warning');
}

function hideLoading() {
  hideResult();
}

// Enhanced event listeners
document.addEventListener('DOMContentLoaded', () => {
  // Load units on page load
  loadUnits();
  
  // Add enter key support
  document.getElementById('uc-value').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      convertUnits();
    }
  });
  
  // Add input validation
  document.getElementById('uc-value').addEventListener('input', (e) => {
    const value = e.target.value;
    if (value && (isNaN(value) || value < 0)) {
      e.target.style.borderColor = 'var(--error)';
      showWarning('Please enter a valid positive number');
    } else {
      e.target.style.borderColor = 'var(--border)';
      hideResult();
    }
  });
  
  // Clear result when inputs change
  document.getElementById('uc-from').addEventListener('change', () => {
    document.getElementById('uc-result').value = '';
    hideResult();
  });
  
  document.getElementById('uc-to').addEventListener('change', () => {
    document.getElementById('uc-result').value = '';
    hideResult();
  });
  
  // Add keyboard shortcuts
  document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'Enter') {
      convertUnits();
    }
  });
  
  // Add tooltips and help text
  const helpText = document.createElement('div');
  helpText.innerHTML = `
    <small style="color: var(--text-muted); margin-top: 1rem; display: block; text-align: center;">
      💡 Tip: Press Enter or Ctrl+Enter to convert quickly
    </small>
  `;
  document.querySelector('.converter-form').appendChild(helpText);
});

// Add some fun animations
function addFloatingElements() {
  const body = document.body;
  
  for (let i = 0; i < 5; i++) {
    const element = document.createElement('div');
    element.style.cssText = `
      position: fixed;
      width: 4px;
      height: 4px;
      background: rgba(255, 255, 255, 0.3);
      border-radius: 50%;
      pointer-events: none;
      animation: float ${3 + Math.random() * 4}s linear infinite;
      left: ${Math.random() * 100}%;
      top: 100%;
    `;
    body.appendChild(element);
  }
}

// Add floating animation CSS
const style = document.createElement('style');
style.textContent = `
  @keyframes float {
    0% {
      transform: translateY(0) rotate(0deg);
      opacity: 0;
    }
    10% {
      opacity: 1;
    }
    90% {
      opacity: 1;
    }
    100% {
      transform: translateY(-100vh) rotate(360deg);
      opacity: 0;
    }
  }
`;
document.head.appendChild(style);

// Start floating elements after page load
setTimeout(addFloatingElements, 1000);