// ========== القوائم الجاهزة ==========
const presetDevices = {
    "منزلي": [
        { name: "إضاءة LED كاملة", amp: 2, hours: 8, icon: "💡", surgeFactor: 1.2 },
        { name: "برّاد (ثلاجة)", amp: 5, hours: 24, icon: "❄️", surgeFactor: 3.5 },
        { name: "فريزر (مجمدة)", amp: 6, hours: 24, icon: "🧊", surgeFactor: 3.5 },
        { name: "شاشة LED 50\"", amp: 3, hours: 6, icon: "📺", surgeFactor: 1.2 },
        { name: "رسيفر + راوتر", amp: 1.5, hours: 24, icon: "🌐", surgeFactor: 1.2 },
        { name: "مروحة سقف", amp: 1.5, hours: 8, icon: "🌀", surgeFactor: 3.5 },
        { name: "مروحة استاند", amp: 2, hours: 8, icon: "💨", surgeFactor: 3.5 },
        { name: "غسالة أوتوماتيك", amp: 10, hours: 2, icon: "👕", surgeFactor: 3.5 },
        { name: "مكيف 1 طن", amp: 15, hours: 8, icon: "❄️", surgeFactor: 3.5 },
        { name: "مكيف 2 طن", amp: 25, hours: 8, icon: "❄️", surgeFactor: 3.5 },
        { name: "مكيف 3 طن", amp: 35, hours: 8, icon: "❄️", surgeFactor: 3.5 },
        { name: "سخان ماء كهربائي", amp: 20, hours: 3, icon: "🔥", surgeFactor: 1.0 },
        { name: "مدفأة كهربائية", amp: 15, hours: 6, icon: "♨️", surgeFactor: 1.0 },
        { name: "مضخة ماء منزلية", amp: 12, hours: 3, icon: "💧", surgeFactor: 3.5 },
        { name: "جاكوزي / مساج", amp: 8, hours: 1, icon: "🛁", surgeFactor: 3.5 }
    ],
    "صناعي": [
        { name: "محرك 5 حصان", amp: 25, hours: 8, icon: "⚙️", surgeFactor: 3.5 },
        { name: "محرك 10 حصان", amp: 50, hours: 6, icon: "⚙️", surgeFactor: 3.5 },
        { name: "كومبريسور 100لتر", amp: 30, hours: 6, icon: "💨", surgeFactor: 3.5 },
        { name: "ماكينة لحام 300A", amp: 40, hours: 4, icon: "🔧", surgeFactor: 3.5 },
        { name: "ماكينة لحام CO2", amp: 25, hours: 4, icon: "🔧", surgeFactor: 3.5 },
        { name: "مخرطة حديد", amp: 20, hours: 6, icon: "🔩", surgeFactor: 3.5 },
        { name: "ماكينة تفريز", amp: 18, hours: 5, icon: "⚙️", surgeFactor: 3.5 },
        { name: "منشار حديد", amp: 20, hours: 4, icon: "🪚", surgeFactor: 3.5 },
        { name: "مثقاب مغناطيسي", amp: 8, hours: 3, icon: "🔩", surgeFactor: 1.2 },
        { name: "فرن صهر معادن", amp: 45, hours: 6, icon: "🔥", surgeFactor: 1.0 },
        { name: "إضاءة ورشة LED", amp: 10, hours: 12, icon: "💡", surgeFactor: 1.2 },
        { name: "نظام تهوية", amp: 12, hours: 10, icon: "🌀", surgeFactor: 3.5 },
        { name: "مضخة مياه 3 حصان", amp: 15, hours: 6, icon: "💧", surgeFactor: 3.5 },
        { name: "ماكينة غسيل ضغط", amp: 18, hours: 3, icon: "💦", surgeFactor: 3.5 },
        { name: "شاحن بطاريات", amp: 8, hours: 12, icon: "🔋", surgeFactor: 1.2 }
    ],
    "زراعي": [
        { name: "مضخة غاطسة 5 حصان", amp: 25, hours: 6, icon: "💧", surgeFactor: 3.5 },
        { name: "مضخة سطحية 3 حصان", amp: 15, hours: 8, icon: "💧", surgeFactor: 3.5 },
        { name: "مضخة 10 حصان (ري)", amp: 50, hours: 8, icon: "💧", surgeFactor: 3.5 },
        { name: "خلاط أعلاف 2طن", amp: 18, hours: 4, icon: "🌾", surgeFactor: 3.5 },
        { name: "ماكينة حلب", amp: 10, hours: 3, icon: "🐄", surgeFactor: 1.2 },
        { name: "مدفأة صيصان", amp: 5, hours: 12, icon: "🐤", surgeFactor: 1.0 },
        { name: "مروحة دواجن كبيرة", amp: 8, hours: 10, icon: "🐔", surgeFactor: 3.5 },
        { name: "إضاءة حظائر", amp: 4, hours: 10, icon: "💡", surgeFactor: 1.2 },
        { name: "رشاش مبيدات", amp: 12, hours: 2, icon: "🌿", surgeFactor: 3.5 },
        { name: "حصّادة قمح", amp: 30, hours: 6, icon: "🚜", surgeFactor: 3.5 },
        { name: "ضاغط هواء زراعي", amp: 22, hours: 5, icon: "💨", surgeFactor: 3.5 },
        { name: "ماكينة فرم", amp: 25, hours: 4, icon: "🔪", surgeFactor: 3.5 },
        { name: "مكبس علف", amp: 20, hours: 5, icon: "🌾", surgeFactor: 3.5 },
        { name: "مضخة رش سماد", amp: 8, hours: 3, icon: "🌱", surgeFactor: 3.5 },
        { name: "جهاز تفقيس بيض", amp: 6, hours: 24, icon: "🥚", surgeFactor: 1.2 }
    ]
};

let devices = window.backendDevices || [];
let currentCategory = "منزلي";

// ========== دوال المودال (لم تتغير) ==========
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

// ========== إضافة جهاز مخصص (لم تتغير) ==========
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

// ========== إضافة جهاز جاهز ==========
function addPresetDevice(preset) {
    // نضيف الجهاز مع بياناته الجاهزة
    devices.push({
        id: Date.now(),
        name: preset.name,
        amp: preset.amp,
        qty: 1,           // العدد الافتراضي 1
        hours: preset.hours,
        surgeFactor: preset.surgeFactor
    });
    renderDevices();
    calculateLive();
    
    // تمرير بسيط للأسفل ليرى المستخدم جهازه المضاف
    document.getElementById('deviceList').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ========== مسح جهاز (لم تتغير) ==========
function removeDevice(id) {
    devices = devices.filter(d => d.id !== id);
    renderDevices();
    calculateLive();
}

// ========== تحديث قيم العدد والساعات (لم تتغير) ==========
function updateDeviceValue(id, field, value) {
    let device = devices.find(d => d.id === id);
    if(device) {
        device[field] = parseInt(value) || 0;
        calculateLive();
    }
}

// ========== عرض القوائم الجاهزة ==========
function renderPresetDevices(category) {
    const container = document.getElementById('presetDevicesContainer');
    const list = presetDevices[category] || [];
    
    if (list.length === 0) {
        container.innerHTML = '<p style="color:var(--muted); text-align:center; width:100%;">لا توجد أجهزة مقترحة حالياً.</p>';
        return;
    }

    let html = '';
    list.forEach(device => {
        html += 
            `<div class="preset-card">
                <div class="preset-card-icon">${device.icon}</div>
                <div class="preset-card-name">${device.name}</div>
                <div class="preset-card-amp">${device.amp} أمبير</div>
                <button class="preset-card-add" onclick="addPresetDevice(${JSON.stringify(device).replace(/"/g, '&quot;')})">+ إضافة</button>
            </div>`
        ;
    });
    container.innerHTML = html;
}

// ========== تبديل الفئة ==========
function switchCategory(category) {
    currentCategory = category;
    // تحديث الأزرار النشطة
    document.querySelectorAll('.preset-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.category === category);
    });
    renderPresetDevices(category);
}

// تهيئة أزرار الفئات
document.querySelectorAll('.preset-btn').forEach(btn => {
    btn.addEventListener('click', () => switchCategory(btn.dataset.category));
});

// ========== رسم الأجهزة في الشاشة (معدلة) ==========
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

// ========== الحساب المباشر (لم يتغير) ==========
function calculateLive() {
    let totalKwh = 0;
    let maxSurge = 0;
    let voltage = parseInt(document.getElementById('voltageSelect').value) || 220;
    
    devices.forEach(d => {
        if(d.qty > 0 && d.hours > 0) {
            let watts = d.amp * voltage;
            let dailyKwh = (watts * d.qty * d.hours) / 1000;
            totalKwh += dailyKwh;
            
            let deviceSurge = watts * d.qty * d.surgeFactor;
            if (deviceSurge > maxSurge) {
                maxSurge = deviceSurge;
            }
        }
    });

    document.getElementById('dailyTotal').textContent = totalKwh.toFixed(2);
    document.getElementById('monthlyTotal').textContent = (totalKwh * 30).toFixed(2);
    document.getElementById('maxSurge').textContent = Math.round(maxSurge).toLocaleString();
    
    const aiCard = document.getElementById('aiCard');
    if (totalKwh > 0) {
        aiCard.style.display = 'flex';
        sendDataToBackend(totalKwh, maxSurge, voltage);
    } else {
        aiCard.style.display = 'none';
    }
}

// ========== حفظ البيانات (لم يتغير) ==========
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

// ========== بدء التشغيل ==========
window.onload = function() {
    renderPresetDevices(currentCategory);
    renderDevices();
    calculateLive();
};