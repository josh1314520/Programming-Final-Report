// 冒險者金庫 - 召喚祭壇 3D 卡牌與魔法陣互動特效

function triggerSummon(times) {
    const magicCircle = document.getElementById('magic-circle');
    const actions = document.getElementById('summon-actions');
    const statusTitle = document.getElementById('altar-status-title');
    const statusDesc = document.getElementById('altar-status-desc');
    
    // 1. 啟動魔法陣霓虹超載動畫與發光
    magicCircle.classList.add('active');
    actions.style.pointerEvents = 'none';
    actions.style.opacity = '0.3';
    statusTitle.innerText = '星門開啟！正在引導星辰通道...';
    statusDesc.innerText = '遠古英靈與神兵利器正在穿越虛空塵埃...';
    
    // 2. 向後端發送召喚請求
    fetch('/api/summon', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ times: times })
    })
    .then(res => {
        if (!res.ok) {
            return res.json().then(err => { throw new Error(err.message); });
        }
        return res.json();
    })
    .then(data => {
        // 更新 Navbar 資源
        document.getElementById('player-gold').innerText = data.gold_left.toLocaleString();
        document.getElementById('player-stones').innerText = data.soul_stones_left.toLocaleString();
        
        // Altar 存量也同步更新
        const altarStones = document.getElementById('altar-stones');
        if (altarStones) altarStones.innerText = data.soul_stones_left;
        
        // 3. 戲劇化延時展示卡牌，展現儀式感 (2秒動畫)
        setTimeout(() => {
            magicCircle.classList.remove('active');
            actions.style.pointerEvents = 'auto';
            actions.style.opacity = '1';
            
            // 切換平台展示
            document.getElementById('summon-altar-platform').style.display = 'none';
            document.getElementById('summon-reveal-platform').style.display = 'block';
            
            // 渲染抽卡成果
            renderRevealCards(data.results);
        }, 2200);
    })
    .catch(err => {
        showToast('召喚失敗', err.message || '引導星海之力失敗，請確認靈石是否足夠。', 'error');
        magicCircle.classList.remove('active');
        actions.style.pointerEvents = 'auto';
        actions.style.opacity = '1';
        statusTitle.innerText = '虛空星海召喚法陣';
        statusDesc.innerText = '凝聚星辰之力，開啟星門與遠古英靈及神兵契約';
    });
}

// 渲染抽中卡牌 (3D 翻轉效果)
function renderRevealCards(results) {
    const container = document.getElementById('reveal-cards-container');
    container.innerHTML = ''; // 清空
    
    results.forEach((item, index) => {
        const cardWrapper = document.createElement('div');
        cardWrapper.className = 'gacha-card-wrapper';
        
        // 翻轉邏輯與粒子爆炸
        const cardInner = document.createElement('div');
        cardInner.className = 'gacha-card-inner';
        
        // 動態飛入延遲
        cardWrapper.style.opacity = '0';
        cardWrapper.style.transform = 'translateY(50px) scale(0.9)';
        cardWrapper.style.transition = 'all 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
        
        setTimeout(() => {
            cardWrapper.style.opacity = '1';
            cardWrapper.style.transform = 'none';
        }, index * 150); // 卡牌依序飛入
        
        cardInner.onclick = () => {
            if (!cardInner.classList.contains('flipped')) {
                cardInner.classList.add('flipped');
                
                // 翻開時震動發光，如果是傳說級 (Legendary) 觸發金色噴射粒子
                if (item.rarity === 'Legendary') {
                    setTimeout(() => {
                        createAltarParticles(cardInner, 35, '#ffaa00');
                        showToast('⭐ 命定神契 ⭐', `恭喜召喚出傳說契約「${item.name}」！`, 'success');
                    }, 300);
                } else if (item.rarity === 'Epic') {
                    setTimeout(() => {
                        createAltarParticles(cardInner, 15, '#c300ff');
                    }, 300);
                } else {
                    setTimeout(() => {
                        createAltarParticles(cardInner, 6, '#0099ff');
                    }, 300);
                }
            }
        };
        
        // 卡牌背面 (未翻開)
        const cardBack = document.createElement('div');
        cardBack.className = 'gacha-card-back';
        
        // 卡牌正面 (翻開)
        const cardFront = document.createElement('div');
        cardFront.className = `gacha-card-front rarity-${item.rarity}`;
        
        let headerHtml = '';
        let bodyHtml = '';
        let typeLabel = '';
        
        if (item.type === 'guardian') {
            typeLabel = '守護靈';
            headerHtml = `
                <div class="d-flex justify-content-between align-items-center">
                    <span class="badge element-pill ${item.element}">${item.element}</span>
                    <span class="text-secondary small">契約</span>
                </div>
            `;
            
            // 守護靈對應 Emoji
            let emoji = '🔮';
            if (item.element === 'Fire') emoji = '🔥';
            else if (item.element === 'Water') emoji = '💧';
            else if (item.element === 'Wind') emoji = '🌪️';
            else if (item.element === 'Earth') emoji = '🛡️';
            else if (item.element === 'Light') emoji = '☀️';
            else if (item.element === 'Shadow') emoji = '😈';
            
            bodyHtml = `
                <div class="my-auto text-center">
                    <span style="font-size: 3rem; filter: drop-shadow(0 0 10px rgba(255,255,255,0.25));" class="d-block mb-2">${emoji}</span>
                    <h5 class="text-white fw-bold mb-2">${item.name}</h5>
                </div>
                <div class="bg-black-opacity p-2 rounded small text-start">
                    <div class="d-flex justify-content-between mb-1"><span class="text-secondary">生命</span><strong class="text-white">${item.base_hp}</strong></div>
                    <div class="d-flex justify-content-between mb-1"><span class="text-secondary">攻擊</span><strong class="text-white">${item.base_atk}</strong></div>
                    <div class="d-flex justify-content-between"><span class="text-secondary">防禦</span><strong class="text-white">${item.base_def}</strong></div>
                </div>
            `;
        } else {
            typeLabel = '裝備';
            let icon = '⚔️';
            if (item.equipment_type === 'armor') icon = '🛡️';
            else if (item.equipment_type === 'accessory') icon = '📿';
            
            headerHtml = `
                <div class="d-flex justify-content-between align-items-center">
                    <span class="badge badge-rarity ${item.rarity}">${item.rarity}</span>
                    <span class="text-secondary small">${icon}</span>
                </div>
            `;
            
            bodyHtml = `
                <div class="my-auto text-center">
                    <span style="font-size: 3rem; filter: drop-shadow(0 0 10px rgba(255,255,255,0.25));" class="d-block mb-2">${icon}</span>
                    <h5 class="text-white fw-bold mb-2 text-truncate">${item.name}</h5>
                </div>
                <div class="bg-black-opacity p-2 rounded small text-start">
                    ${item.hp_bonus > 0 ? `<div class="d-flex justify-content-between mb-1"><span class="text-secondary">生命</span><strong class="text-white">+${item.hp_bonus}</strong></div>` : ''}
                    ${item.atk_bonus > 0 ? `<div class="d-flex justify-content-between mb-1"><span class="text-secondary">攻擊</span><strong class="text-white">+${item.atk_bonus}</strong></div>` : ''}
                    ${item.def_bonus > 0 ? `<div class="d-flex justify-content-between"><span class="text-secondary">防禦</span><strong class="text-white">+${item.def_bonus}</strong></div>` : ''}
                </div>
            `;
        }
        
        cardFront.innerHTML = `
            ${headerHtml}
            ${bodyHtml}
            <div class="mt-2 text-center" style="font-size: 0.65rem; color: rgba(255,255,255,0.3); border-top: 1px solid rgba(255,255,255,0.05); padding-top: 6px;">
                ${typeLabel} · 虛空英靈契約書
            </div>
        `;
        
        cardInner.appendChild(cardBack);
        cardInner.appendChild(cardFront);
        cardWrapper.appendChild(cardInner);
        container.appendChild(cardWrapper);
    });
}

// 重回召喚主畫面
function resetSummonAltar() {
    document.getElementById('summon-reveal-platform').style.display = 'none';
    document.getElementById('summon-altar-platform').style.display = 'flex';
    
    const magicCircle = document.getElementById('magic-circle');
    const actions = document.getElementById('summon-actions');
    const statusTitle = document.getElementById('altar-status-title');
    const statusDesc = document.getElementById('altar-status-desc');
    
    magicCircle.classList.remove('active');
    actions.style.pointerEvents = 'auto';
    actions.style.opacity = '1';
    statusTitle.innerText = '虛空星海召喚法陣';
    statusDesc.innerText = '凝聚星辰之力，開啟星門與遠古英靈及神兵契約';
    
    // 重新載入未裝備數值
    refreshPlayerStatus();
}

// 召喚專用彩色發光粒子
function createAltarParticles(element, count = 20, color = '#ffaa00') {
    const rect = element.getBoundingClientRect();
    const overlay = document.body;
    
    for (let i = 0; i < count; i++) {
        const p = document.createElement('div');
        p.className = 'particle';
        
        p.style.background = color;
        p.style.boxShadow = `0 0 10px ${color}`;
        
        const startX = rect.left + rect.width / 2 + window.scrollX;
        const startY = rect.top + rect.height / 2 + window.scrollY;
        
        p.style.left = startX + 'px';
        p.style.top = startY + 'px';
        
        overlay.appendChild(p);
        
        const angle = Math.random() * Math.PI * 2;
        const speed = 3 + Math.random() * 9;
        const vx = Math.cos(angle) * speed;
        const vy = Math.sin(angle) * speed;
        
        let x = startX;
        let y = startY;
        let opacity = 1;
        
        const animate = () => {
            x += vx;
            y += vy + 0.15;
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
