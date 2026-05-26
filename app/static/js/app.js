// 冒險者金庫 - 守護靈裝備系統 通用與 AJAX 互動腳本

// 全域通知 Toast 函式
function showToast(title, message, type = 'success') {
    const toast = document.getElementById('global-toast');
    const toastTitle = document.getElementById('toast-title');
    const toastMessage = document.getElementById('toast-message');
    const toastIcon = document.getElementById('toast-icon');
    
    // 設定樣式類別
    toast.className = 'custom-alert d-flex align-items-start gap-3 show ' + type;
    
    // 設定圖示
    if (type === 'success') {
        toastIcon.innerHTML = '✨';
    } else if (type === 'error') {
        toastIcon.innerHTML = '⚠️';
    } else {
        toastIcon.innerHTML = 'ℹ️';
    }
    
    toastTitle.innerText = title;
    toastMessage.innerText = message;
    
    // 3秒後消失
    setTimeout(() => {
        toast.classList.remove('show');
    }, 4000);
}

// 領取每日補給
function claimDailySupply() {
    const btn = document.getElementById('btn-daily-supply');
    btn.disabled = true;
    btn.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> 傳送中...`;
    
    fetch('/api/player/daily', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(res => {
        if (!res.ok) {
            return res.json().then(err => { throw new Error(err.message); });
        }
        return res.json();
    })
    .then(data => {
        showToast('補給成功！', data.data.message, 'success');
        
        // 更新 Navbar 資源
        document.getElementById('player-gold').innerText = data.data.gold.toLocaleString();
        document.getElementById('player-stones').innerText = data.data.soul_stones.toLocaleString();
        
        // 更新按鈕冷卻倒數 (60秒)
        startDailyCooldown(60);
    })
    .catch(err => {
        showToast('領取失敗', err.message || '連線錯誤，請稍後再試。', 'error');
        btn.disabled = false;
        btn.innerHTML = `<i class="bi bi-gift-fill text-warning me-1"></i> 每日補給`;
    });
}

// 補給按鈕倒數計時器
function startDailyCooldown(seconds) {
    const btn = document.getElementById('btn-daily-supply');
    let remaining = seconds;
    
    const interval = setInterval(() => {
        remaining--;
        if (remaining <= 0) {
            clearInterval(interval);
            btn.disabled = false;
            btn.innerHTML = `<i class="bi bi-gift-fill text-warning me-1"></i> 每日補給`;
        } else {
            btn.innerHTML = `<i class="bi bi-hourglass-split me-1"></i> 冷卻中 (${remaining}s)`;
        }
    }, 1000);
}

// 獲取並更新資源面板
function refreshPlayerStatus() {
    fetch('/api/player/status')
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            const goldEl = document.getElementById('player-gold');
            const stonesEl = document.getElementById('player-stones');
            if (goldEl) goldEl.innerText = data.gold.toLocaleString();
            if (stonesEl) stonesEl.innerText = data.soul_stones.toLocaleString();
        }
    });
}

// 餵食修煉守護靈
function feedGuardian(guardianId) {
    const card = document.getElementById(`guardian-card-${guardianId}`);
    
    fetch(`/api/guardians/${guardianId}/feed`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(res => {
        if (!res.ok) {
            return res.json().then(err => { throw new Error(err.message); });
        }
        return res.json();
    })
    .then(data => {
        const result = data.data;
        
        // 1. 播放卡牌閃爍特效 (閃光)
        card.classList.add('level-up-flash');
        setTimeout(() => card.classList.remove('level-up-flash'), 1000);
        
        // 2. 噴射升級粒子
        createParticles(card, result.is_level_up ? 30 : 10);
        
        // 3. 顯示通知
        if (result.is_level_up) {
            showToast('突破升級！', `${result.name} 突破至等級 Lv.${result.new_level}！基礎屬性大幅提升！`, 'success');
        } else {
            showToast('修煉提升', `${result.name} 獲得了 ${result.xp_gained} 點修煉經驗！`, 'info');
        }
        
        // 4. 更新前端 DOM 數值
        card.querySelector('.guardian-level').innerText = result.new_level;
        card.querySelector('.guardian-xp').innerText = result.new_xp;
        card.querySelector('.guardian-max-xp').innerText = result.max_xp;
        card.querySelector('.exp-progress-bar').style.width = `${(result.new_xp / result.max_xp) * 100}%`;
        
        card.querySelector('.guardian-hp').innerText = result.total_hp;
        card.querySelector('.guardian-hp-base').innerText = `(${result.base_hp})`;
        card.querySelector('.guardian-atk').innerText = result.total_atk;
        card.querySelector('.guardian-atk-base').innerText = `(${result.base_atk})`;
        card.querySelector('.guardian-def').innerText = result.total_def;
        card.querySelector('.guardian-def-base').innerText = `(${result.base_def})`;
        
        card.querySelector('.guardian-power').innerText = result.power;
        card.querySelector('.feed-cost').innerText = result.new_level * 150;
        
        // 5. 更新全域資源
        refreshPlayerStatus();
    })
    .catch(err => {
        showToast('修煉失敗', err.message, 'error');
    });
}

// 裝備插槽點擊分流處理
function handleSlotClick(guardianId, slotType, isFilled, equipmentId) {
    if (isFilled) {
        // 已有裝備，彈出卸下選項彈窗
        document.getElementById('unequip-guardian-id').value = guardianId;
        document.getElementById('unequip-equipment-id').value = equipmentId;
        
        const unequipModal = new bootstrap.Modal(document.getElementById('unequipModal'));
        unequipModal.show();
    } else {
        // 空白插槽，打開裝備選擇彈窗
        document.getElementById('modal-guardian-id').value = guardianId;
        document.getElementById('modal-slot-type').value = slotType;
        
        const container = document.getElementById('equip-options-container');
        container.innerHTML = ''; // 清空
        
        // 根據部位取得對應未裝備清單
        let options = [];
        if (slotType === 'weapon') {
            options = unequippedWeapons;
            document.getElementById('equipModalTitle').innerText = '裝備武器';
        } else if (slotType === 'armor') {
            options = unequippedArmors;
            document.getElementById('equipModalTitle').innerText = '裝備防具';
        } else if (slotType === 'accessory') {
            options = unequippedAccessories;
            document.getElementById('equipModalTitle').innerText = '裝備飾品';
        }
        
        if (options.length === 0) {
            container.innerHTML = `
                <div class="text-center py-4 text-secondary small">
                    <i class="bi bi-emoji-frown fs-2 d-block mb-2"></i>
                    背包中沒有多餘且適合此插槽的未裝備道具！
                </div>
            `;
        } else {
            options.forEach(eq => {
                const item = document.createElement('div');
                item.className = `glass-panel p-3 d-flex justify-content-between align-items-center cursor-pointer equipment-card rarity-${eq.rarity}`;
                item.style.borderLeftWidth = '4px';
                item.style.transition = 'all 0.2s';
                item.onclick = () => equipItem(guardianId, eq.id);
                
                item.onmouseenter = () => {
                    item.style.background = 'rgba(255, 255, 255, 0.08)';
                    item.style.transform = 'scale(1.02)';
                };
                item.onmouseleave = () => {
                    item.style.background = '';
                    item.style.transform = '';
                };
                
                item.innerHTML = `
                    <div>
                        <div class="d-flex align-items-center gap-2 mb-1">
                            <h6 class="mb-0 text-white fw-bold">${eq.name}</h6>
                            <span class="badge badge-rarity ${eq.rarity}">Lv.${eq.level}</span>
                        </div>
                        <div class="text-secondary small">
                            ${eq.hp > 0 ? `生命+${eq.hp} ` : ''}
                            ${eq.atk > 0 ? `攻擊+${eq.atk} ` : ''}
                            ${eq.def > 0 ? `防禦+${eq.def} ` : ''}
                        </div>
                    </div>
                    <button class="btn btn-sm btn-primary-glow py-1 px-3">裝備</button>
                `;
                container.appendChild(item);
            });
        }
        
        const equipSelectorModal = new bootstrap.Modal(document.getElementById('equipSelectorModal'));
        equipSelectorModal.show();
    }
}

// 執行裝備
function equipItem(guardianId, equipmentId) {
    fetch(`/api/guardians/${guardianId}/equip`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ equipment_id: equipmentId })
    })
    .then(res => {
        if (!res.ok) {
            return res.json().then(err => { throw new Error(err.message); });
        }
        return res.json();
    })
    .then(data => {
        showToast('裝備成功', data.data.message, 'success');
        
        // 關閉 Modal
        const modalEl = document.getElementById('equipSelectorModal');
        const modal = bootstrap.Modal.getInstance(modalEl);
        if (modal) modal.hide();
        
        // 1.2秒後重新整理頁面，載入最新狀態與背包
        setTimeout(() => {
            window.location.reload();
        }, 1200);
    })
    .catch(err => {
        showToast('裝備失敗', err.message, 'error');
    });
}

// 卸下裝備
function unequipItem() {
    const guardianId = document.getElementById('unequip-guardian-id').value;
    const equipmentId = document.getElementById('unequip-equipment-id').value;
    
    fetch(`/api/guardians/${guardianId}/unequip`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ equipment_id: equipmentId })
    })
    .then(res => {
        if (!res.ok) {
            return res.json().then(err => { throw new Error(err.message); });
        }
        return res.json();
    })
    .then(data => {
        showToast('已卸下裝備', data.data.message, 'success');
        
        // 關閉 Modal
        const modalEl = document.getElementById('unequipModal');
        const modal = bootstrap.Modal.getInstance(modalEl);
        if (modal) modal.hide();
        
        // 1.2秒後重新整理
        setTimeout(() => {
            window.location.reload();
        }, 1200);
    })
    .catch(err => {
        showToast('卸下失敗', err.message, 'error');
    });
}

// 強化裝備
function upgradeEquipment(equipmentId) {
    const card = document.getElementById(`equipment-card-${equipmentId}`);
    const btn = card.querySelector('.btn-upgrade-equip');
    btn.disabled = true;
    
    fetch(`/api/equipment/${equipmentId}/upgrade`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(res => {
        if (!res.ok) {
            return res.json().then(err => { throw new Error(err.message); });
        }
        return res.json();
    })
    .then(data => {
        const res = data.data;
        
        // 1. 播放閃爍特效與發光
        card.classList.add('level-up-flash');
        setTimeout(() => card.classList.remove('level-up-flash'), 1000);
        createParticles(card, 15);
        
        showToast('強化成功！', `${res.name} 已強化至 +${res.new_level}！`, 'success');
        
        // 2. 更新 DOM 數值
        card.querySelector('.equip-level').innerText = res.new_level;
        card.querySelector('.equip-hp .val').innerText = res.hp_bonus;
        card.querySelector('.equip-atk .val').innerText = res.atk_bonus;
        card.querySelector('.equip-def .val').innerText = res.def_bonus;
        
        // 計算並更新下一級強化花費
        // 稀有度對應倍率
        let mult = 1.0;
        if (card.classList.contains('rarity-Rare')) mult = 1.5;
        else if (card.classList.contains('rarity-Epic')) mult = 2.5;
        else if (card.classList.contains('rarity-Legendary')) mult = 4.0;
        
        const nextCost = Math.floor(res.new_level * 500 * mult);
        card.querySelector('.upgrade-cost').innerText = nextCost;
        btn.title = `消耗 ${nextCost} 金幣進行強化`;
        
        // 3. 更新全域資源
        refreshPlayerStatus();
        btn.disabled = false;
    })
    .catch(err => {
        showToast('強化失敗', err.message, 'error');
        btn.disabled = false;
    });
}

// 出售裝備
function sellEquipment(equipmentId, equipmentName) {
    if (!confirm(`您確定要以金幣出售「${equipmentName}」嗎？這項操作無法復原。`)) {
        return;
    }
    
    const card = document.getElementById(`equipment-card-${equipmentId}`);
    
    fetch(`/api/equipment/${equipmentId}/sell`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(res => {
        if (!res.ok) {
            return res.json().then(err => { throw new Error(err.message); });
        }
        return res.json();
    })
    .then(data => {
        showToast('已出售', data.data.message, 'success');
        
        // 1. 卡牌淡出並縮小移除
        card.style.transition = 'all 0.5s ease';
        card.style.opacity = '0';
        card.style.transform = 'scale(0.5)';
        
        setTimeout(() => {
            card.parentElement.remove();
            
            // 檢查是否還有任何裝備
            const items = document.querySelectorAll('.equipment-item-card');
            if (items.length === 0) {
                window.location.reload(); // 重新整理顯示空置狀態
            }
        }, 500);
        
        // 2. 更新 Navbar 金幣
        refreshPlayerStatus();
    })
    .catch(err => {
        showToast('出售失敗', err.message, 'error');
    });
}

// 遣散守護靈
function confirmReleaseGuardian(guardianId, guardianName) {
    if (!confirm(`警告：您確定要遣散「${guardianName}」，將它放歸虛空嗎？\n這將會自動卸下它身上的所有裝備。這項操作無法復原。`)) {
        return;
    }
    
    const card = document.getElementById(`guardian-card-${guardianId}`);
    
    fetch(`/api/guardians/${guardianId}/delete`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(res => {
        if (!res.ok) {
            return res.json().then(err => { throw new Error(err.message); });
        }
        return res.json();
    })
    .then(data => {
        showToast('契約解除', data.message, 'success');
        
        // 卡牌滑動消失
        card.style.transition = 'all 0.5s cubic-bezier(0.55, 0.085, 0.68, 0.53)';
        card.style.opacity = '0';
        card.style.transform = 'translateY(100px) scale(0.8)';
        
        setTimeout(() => {
            card.parentElement.remove();
            
            // 檢查是否還有守護靈
            const cards = document.querySelectorAll('[id^="guardian-card-"]');
            if (cards.length === 0) {
                window.location.reload();
            }
        }, 500);
        
        // 更新 Navbar 等狀態
        refreshPlayerStatus();
    })
    .catch(err => {
        showToast('遣散失敗', err.message, 'error');
    });
}

// 建立粒子發光爆炸效果
function createParticles(element, count = 20) {
    const rect = element.getBoundingClientRect();
    const overlay = document.body;
    
    for (let i = 0; i < count; i++) {
        const p = document.createElement('div');
        p.className = 'particle';
        
        // 隨機顏色 (金色、白色、紫光)
        const rand = Math.random();
        if (rand < 0.4) {
            p.style.background = '#ffe259';
            p.style.boxShadow = '0 0 10px #ffe259';
        } else if (rand < 0.8) {
            p.style.background = '#c300ff';
            p.style.boxShadow = '0 0 10px #c300ff';
        } else {
            p.style.background = '#00c6ff';
            p.style.boxShadow = '0 0 10px #00c6ff';
        }
        
        // 起始座標設在元素中心
        const startX = rect.left + rect.width / 2 + window.scrollX;
        const startY = rect.top + rect.height / 2 + window.scrollY;
        
        p.style.left = startX + 'px';
        p.style.top = startY + 'px';
        
        overlay.appendChild(p);
        
        // 隨機噴射方向與速度
        const angle = Math.random() * Math.PI * 2;
        const speed = 2 + Math.random() * 8;
        const vx = Math.cos(angle) * speed;
        const vy = Math.sin(angle) * speed;
        
        let x = startX;
        let y = startY;
        let opacity = 1;
        
        const animate = () => {
            x += vx;
            y += vy + 0.1; // 重力微落
            opacity -= 0.02;
            
            p.style.left = x + 'px';
            p.style.top = y + 'px';
            p.style.opacity = opacity;
            
            if (opacity > 0) {
                requestAnimationFrame(animate);
            } else {
                p.remove();
            }
        };
        
        requestAnimationFrame(animate);
    }
}

// 保單分析表單提交
function submitInsuranceAnalysis(event) {
    event.preventDefault();
    
    const guardianId = document.getElementById('ins-guardian-id').value;
    const life = parseInt(document.getElementById('ins-life').value);
    const medical = parseInt(document.getElementById('ins-medical').value);
    const accident = parseInt(document.getElementById('ins-accident').value);
    
    const btn = document.getElementById('btn-ins-submit');
    btn.disabled = true;
    btn.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> 正在開啟引導魔法陣...`;
    
    fetch('/api/insurance/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            guardian_id: guardianId,
            life_coverage: life,
            medical_coverage: medical,
            accident_coverage: accident
        })
    })
    .then(res => {
        if (!res.ok) {
            return res.json().then(err => { throw new Error(err.message); });
        }
        return res.json();
    })
    .then(data => {
        const res = data.data;
        showToast('保單護盾加持！', `成功為 ${res.guardian_name} 加持「${res.armor_name}」，防禦力增加 ${res.defense_increased} 點！`, 'success');
        
        // 關閉 Modal
        const modalEl = document.getElementById('insuranceAnalyzeModal');
        const modal = bootstrap.Modal.getInstance(modalEl);
        if (modal) modal.hide();
        
        // 執行酷炫前端升級動畫回饋
        playArmorUpgradeEffect(res);
        
        // 恢復按鈕
        btn.disabled = false;
        btn.innerHTML = `<i class="bi bi-shield-check me-1"></i> 啟動魔法陣·保單防禦引導`;
        
        // 1.5 秒後更新資源面板
        setTimeout(refreshPlayerStatus, 1500);
    })
    .catch(err => {
        showToast('分析失敗', err.message, 'error');
        btn.disabled = false;
        btn.innerHTML = `<i class="bi bi-shield-check me-1"></i> 啟動魔法陣·保單防禦引導`;
    });
}

// 實作保險護甲升級動態回饋
function playArmorUpgradeEffect(data) {
    const gid = data.guardian_id;
    const wrapper = document.getElementById(`insurance-wrapper-${gid}`);
    
    if (!wrapper) return;
    
    // 1. 卡牌震動發光
    wrapper.style.transform = 'scale(1.04)';
    wrapper.classList.add('level-up-flash');
    
    // 2. 金屬粒子爆炸 (多個粒子)
    createParticles(wrapper, 40);
    
    setTimeout(() => {
        wrapper.style.transform = '';
        wrapper.classList.remove('level-up-flash');
    }, 1200);
    
    // 3. 滾動數字動效
    animateNumberTicker(`stat-life-${gid}`, data.life_coverage, ' 萬元');
    animateNumberTicker(`stat-medical-${gid}`, data.medical_coverage, ' 元');
    animateNumberTicker(`stat-accident-${gid}`, data.accident_coverage, ' 萬元');
    animateNumberTicker(`stat-armor-level-${gid}`, data.armor_level, '');
    animateNumberTicker(`stat-def-val-${gid}`, data.defense_value, '', '+');
    
    // 4. 重新計算並充電進度條
    const bar = document.getElementById(`shield-bar-${gid}`);
    if (bar) {
        let pct = (data.defense_value / 500) * 100;
        if (pct > 100) pct = 100;
        bar.style.width = '0%'; // 先歸零
        setTimeout(() => {
            bar.style.width = `${pct}%`;
        }, 150);
    }
    
    // 5. 動態切換發光 Shield 圖示
    const shieldIcon = document.getElementById(`shield-icon-${gid}`);
    if (shieldIcon) {
        let emoji = '🪵';
        let color = '#8e9297';
        let shadow = '';
        
        if (data.armor_level >= 16) { emoji = '💎'; color = '#00f0ff'; shadow = 'drop-shadow(0 0 20px #00f0ff)'; }
        else if (data.armor_level >= 11) { emoji = '👑'; color = '#ffaa00'; shadow = 'drop-shadow(0 0 20px #ffaa00)'; }
        else if (data.armor_level >= 6) { emoji = '🛡️'; color = '#c300ff'; shadow = 'drop-shadow(0 0 15px #c300ff)'; }
        else if (data.armor_level >= 3) { emoji = '⛓️'; color = '#0099ff'; shadow = 'drop-shadow(0 0 10px #0099ff)'; }
        
        shieldIcon.innerHTML = `<span style="font-size: 5rem; color: ${color}; filter: ${shadow};" class="d-block">${emoji}</span>`;
    }
    
    // 6. 動態切換護甲稱號 Class 與名稱
    const title = document.getElementById(`armor-title-${gid}`);
    if (title) {
        title.innerText = data.armor_name;
        // 清理全部 class 再加上對應 class
        title.className = 'badge badge-rarity';
        if (data.armor_level >= 16) title.classList.add('Mythic');
        else if (data.armor_level >= 11) title.classList.add('Legendary');
        else if (data.armor_level >= 6) title.classList.add('Epic');
        else if (data.armor_level >= 3) title.classList.add('Rare');
        else title.classList.add('Common');
    }
}

// 數字跳動計時器
function animateNumberTicker(elementId, targetValue, suffix = '', prefix = '') {
    const el = document.getElementById(elementId);
    if (!el) return;
    
    // 取得舊數字，若非數字則從 0 開始
    const startVal = parseInt(el.innerText.replace(/[^0-9]/g, '')) || 0;
    const diff = targetValue - startVal;
    
    if (diff === 0) {
        el.innerText = prefix + targetValue.toLocaleString() + suffix;
        return;
    }
    
    const duration = 1000; // 1秒
    const startTime = performance.now();
    
    function tick(now) {
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function (easeOutQuad)
        const ease = progress * (2 - progress);
        const currentVal = Math.floor(startVal + diff * ease);
        
        el.innerText = prefix + currentVal.toLocaleString() + suffix;
        
        if (progress < 1) {
            requestAnimationFrame(tick);
        } else {
            el.innerText = prefix + targetValue.toLocaleString() + suffix;
        }
    }
    
    requestAnimationFrame(tick);
}

