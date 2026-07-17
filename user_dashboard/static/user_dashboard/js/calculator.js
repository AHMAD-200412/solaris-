let devices = window.backendDevices || []; // مصفوفة لحفظ الأجهزة اللي يضيفها المستخدم

const overlay = document.getElementById('customModal');

function openModal() {
    overlay.classList.add("show");
}

function closeModal() {
    overlay.classList.remove("show");
    document.getElementById('m_name').value = '';
    document.getElementById('m_amp').value = '';
    document.getElementById('m_qty').value = '1';
    document.getElementById('m_hours').value = '5';
    document.getElementById('m_type').value = '1.2';
}

overlay.addEventListener("click", (e) => {
    if(e.target === overlay){ closeModal(); }
});

// دالة إضافة الجهاز إلى القائمة
function addCustomDevice() {
    let name = document.getElementById('m_name').value.trim();
    let amp = parseFloat(document.getElementById('m_amp').value);
    let qty = parseInt(document.getElementById('m_qty').value) || 1;
    let hours = parseInt(document.getElementById('m_hours').value) || 1;
    let surgeFactor = parseFloat(document.getElementById('m_type').value) || 1.2;

    if (!name || isNaN(amp) || amp <= 0) {
        alert('يرجى إدخال اسم الجهاز وسحب الأمبير بشكل صحيح.');
        return;
    }

    // إضافة الجهاز للمصفوفة
    devices.push({
        id: Date.now(),
        name: name,
        amp: amp,
        qty: qty,
        hours: hours,
        surgeFactor: surgeFactor
    });

    closeModal();
    renderDevices();
    calculateLive();
}

// دالة مسح جهاز من القائمة
function removeDevice(id) {
    devices = devices.filter(d => d.id !== id);
    renderDevices();
    calculateLive();
}

// دالة تحديث قيم العدد والساعات عند تغييرها من الكارت المباشر
function updateDeviceValue(id, field, value) {
    let device = devices.find(d => d.id === id);
    if(device) {
        device[field] = parseInt(value) || 0;
        calculateLive();
    }
}

// دالة رسم الأجهزة في الشاشة
function renderDevices() {
    const list = document.getElementById('deviceList');
    const emptyMsg = document.getElementById('emptyStateMsg');
    list.innerHTML = '';

    if(devices.length === 0) {
        emptyMsg.style.display = 'block';
    } else {
        emptyMsg.style.display = 'none';
        
        devices.forEach(d => {
            let card = document.createElement('div');
            card.className = 'device-app-card';
            card.innerHTML = 
                `<div class="d-info-side">
                    <div class="d-icon">✨</div>
                    <div class="d-text">
                        <h4>${d.name}</h4>
                        <span class="d-amp">${d.amp} أمبير</span>
                    </div>
                </div>
                <div class="d-inputs-side">
                    <div class="input-col">
                        <label>العدد</label>
                        <input type="number" value="${d.qty}" min="0" class="app-input" oninput="updateDeviceValue(${d.id}, 'qty', this.value)">
                    </div>
                    <div class="input-col">
                        <label>ساعات</label>
                        <input type="number" value="${d.hours}" min="0" max="24" class="app-input" oninput="updateDeviceValue(${d.id}, 'hours', this.value)">
                    </div>
                    <button type="button" class="btn-delete-device" onclick="removeDevice(${d.id})">🗑</button>
                </div>`
            ;
            list.appendChild(card);
        });
    }
}

// دالة الحساب المباشر للاستهلاك
function calculateLive() {
    let totalKwh = 0;
    let maxSurge = 0;
    
    // سحب الفولتية المحددة من القائمة المنسدلة
    let voltage = parseInt(document.getElementById('voltageSelect').value) || 220;
    
    devices.forEach(d => {
        if(d.qty > 0 && d.hours > 0) {
            // معادلة تحويل الأمبير إلى واط: الواط = الأمبير × الفولتية المحددة
            let watts = d.amp * voltage;
            // حساب الاستهلاك بالـ كيلوواط
            let dailyKwh = (watts * d.qty * d.hours) / 1000;
            totalKwh += dailyKwh;
            
            // حساب النهضة (Surge)
            let deviceSurge = watts * d.qty * d.surgeFactor;
            if (deviceSurge > maxSurge) {
                maxSurge = deviceSurge;
            }
        }
    });

    // تحديث الواجهة
    document.getElementById('dailyTotal').textContent = totalKwh.toFixed(2);
    document.getElementById('monthlyTotal').textContent = (totalKwh * 30).toFixed(2);
    document.getElementById('maxSurge').textContent = Math.round(maxSurge).toLocaleString();
    
    // إظهار بوكس المساعد الذكي إذا كان هناك استهلاك
    const aiCard = document.getElementById('aiCard');
    if (totalKwh > 0) {
        aiCard.style.display = 'flex';
        sendDataToBackend(totalKwh, maxSurge, voltage); // حفظ البيانات بالخلفية
    } else {
        aiCard.style.display = 'none';
    }
}

// دالة حفظ البيانات بالباك-أند بصمت
function sendDataToBackend(kwh, surge, voltage) {
    const csrfToken = document.getElementById('csrf_token').value;
    
    fetch(window.location.pathname, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            total_kwh_day: kwh,
            max_surge_watts: surge,
            voltage: voltage,
            devices: devices
        })
    }).catch(err => console.log('Saving error:', err));
}

// تشغيل الواجهة أول مرة
window.onload = function() {
    renderDevices();
    calculateLive();
};