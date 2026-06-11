/* ==========================================================================
   主線任務系統 前端 JavaScript 控制器
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    // 全域變數
    let currentAdventurer = null;
    let questsData = [];

    // Canvas 粒子特效引擎變數
    const canvas = document.getElementById('confetti-canvas');
    const ctx = canvas.getContext('2d');
    let confettiActive = false;
    let particles = [];
    const colors = ['#d4af37', '#ffdf7a', '#aa7c11', '#fff', '#e2e8f0'];

    // DOM 元素快取
    const lvNum = document.getElementById('lv-number');
    const titleTag = document.getElementById('title-tag');
    const expText = document.getElementById('exp-text');
    const expFill = document.getElementById('exp-fill');
    const walletGold = document.getElementById('wallet-gold');
    const activeQuestsGrid = document.getElementById('active-quests-grid');
    const lockedQuestsGrid = document.getElementById('locked-quests-grid');

    // 視窗遮罩快取
    const questModal = document.getElementById('quest-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalFormContainer = document.getElementById('modal-form-container');
    const modalErrorAlert = document.getElementById('modal-error-alert');
    const questSubmitForm = document.getElementById('quest-submit-form');
    
    // 升級遮罩快取
    const levelupOverlay = document.getElementById('levelup-overlay');
    const levelupOldLv = document.getElementById('levelup-old-lv');
    const levelupNewLv = document.getElementById('levelup-new-lv');
    const levelupNewTitle = document.getElementById('levelup-new-title');
    const levelupCloseBtn = document.getElementById('levelup-close-btn');

    // Toast 提示
    const toast = document.getElementById('toast');

    /* ==========================================================================
       初始化 Canvas 粒子物理引擎
       ========================================================================== */
    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();

    class ConfettiParticle {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height - canvas.height;
            this.size = Math.random() * 8 + 6;
            this.speedX = Math.random() * 4 - 2;
            this.speedY = Math.random() * 5 + 3;
            this.rotation = Math.random() * 360;
            this.rotationSpeed = Math.random() * 4 - 2;
            this.color = colors[Math.floor(Math.random() * colors.length)];
        }
        update() {
            this.x += this.speedX;
            this.y += this.speedY;
            this.rotation += this.rotationSpeed;
            if (this.y > canvas.height) {
                this.y = -20;
                this.x = Math.random() * canvas.width;
            }
        }
        draw() {
            ctx.save();
            ctx.translate(this.x, this.y);
            ctx.rotate((this.rotation * Math.PI) / 180);
            ctx.fillStyle = this.color;
            ctx.shadowBlur = 8;
            ctx.shadowColor = '#d4af37';
            // 畫金箔碎片
            ctx.fillRect(-this.size / 2, -this.size / 2, this.size, this.size);
            ctx.restore();
        }
    }

    function initConfetti() {
        particles = [];
        for (let i = 0; i < 150; i++) {
            particles.push(new ConfettiParticle());
        }
    }

    function animateConfetti() {
        if (!confettiActive) {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            return;
        }
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        particles.forEach(p => {
            p.update();
            p.draw();
        });
        requestAnimationFrame(animateConfetti);
    }

    function triggerEpicConfetti() {
        confettiActive = true;
        initConfetti();
        animateConfetti();
        // 噴灑 6 秒後漸漸停止
        setTimeout(() => {
            confettiActive = false;
        }, 6000);
    }

    /* ==========================================================================
       資料 API 獲取與 UI 渲染
       ========================================================================== */
    
    // 1. 獲取冒險者屬性並渲染
    async function fetchAdventurerStatus(animateWallet = false) {
        try {
            const response = await fetch('/api/adventurer');
            const data = await response.json();
            if (data.success) {
                const adv = data.adventurer;
                currentAdventurer = adv;
                
                // 渲染等級與稱號
                lvNum.innerText = `Lv.${adv.level}`;
                titleTag.innerText = adv.title;

                // 經驗值比例計算
                const nextLevelExp = adv.level * 100;
                const percent = Math.min((adv.exp / nextLevelExp) * 100, 100);
                expFill.style.width = `${percent}%`;
                expText.innerText = `EXP: ${adv.exp} / ${nextLevelExp} (${percent.toFixed(0)}%)`;

                // 金幣滾動動畫
                if (animateWallet) {
                    animateNumber(walletGold, parseInt(walletGold.innerText) || 0, adv.gold, 1500);
                } else {
                    walletGold.innerText = adv.gold;
                }
            }
        } catch (error) {
            console.error("Error fetching adventurer status:", error);
        }
    }

    // 數字漸變滾動動畫
    function animateNumber(element, start, end, duration) {
        let startTime = null;
        function update(currentTime) {
            if (!startTime) startTime = currentTime;
            const progress = Math.min((currentTime - startTime) / duration, 1);
            const value = Math.floor(progress * (end - start) + start);
            element.innerText = value;
            if (progress < 1) {
                requestAnimationFrame(update);
            } else {
                element.innerText = end;
            }
        }
        requestAnimationFrame(update);
    }

    // 2. 獲取任務列表並動態渲染
    async function fetchQuests() {
        try {
            const response = await fetch('/api/quests');
            const data = await response.json();
            if (data.success) {
                questsData = data.quests;
                renderQuests(questsData);
            }
        } catch (error) {
            console.error("Error fetching quests:", error);
        }
    }

    function renderQuests(quests) {
        activeQuestsGrid.innerHTML = '';
        lockedQuestsGrid.innerHTML = '';

        quests.forEach(quest => {
            const card = document.createElement('div');
            card.className = `quest-card ${quest.status}-quest`;
            
            // 決定狀態標籤文字與樣式
            let badgeText = '鎖定中';
            let badgeClass = 'badge-locked';
            if (quest.status === 'available') {
                badgeText = '可接取';
                badgeClass = 'badge-available';
            } else if (quest.status === 'active') {
                badgeText = '進行中';
                badgeClass = 'badge-active';
            } else if (quest.status === 'completed') {
                badgeText = '已完成';
                badgeClass = 'badge-completed';
            }

            // 建立子目標預覽 HTML
            let objectivesPreviewHTML = '';
            if (quest.objectives && quest.objectives.length > 0) {
                const checkedCount = (quest.status === 'completed') ? quest.objectives.length : 0;
                objectivesPreviewHTML = `
                    <div class="quest-objectives-preview">
                        <div class="preview-title">
                            <span>主線目標進度</span>
                            <span>${checkedCount}/${quest.objectives.length}</span>
                        </div>
                        <ul class="preview-list">
                            ${quest.objectives.map(obj => {
                                const isDone = quest.status === 'completed';
                                return `
                                    <li class="preview-item ${isDone ? 'obj-done' : 'obj-todo'}">
                                        <i class="fa ${isDone ? 'fa-check-circle' : 'fa-circle-o'}"></i>
                                        <span>${obj.description}</span>
                                    </li>
                                `;
                            }).join('')}
                        </ul>
                    </div>
                `;
            }

            // 按鈕行為設計
            let btnHTML = '';
            if (quest.status === 'locked') {
                btnHTML = `<button class="btn" disabled><i class="fa fa-lock"></i> 前置任務鎖定中</button>`;
            } else if (quest.status === 'available') {
                btnHTML = `<button class="btn btn-primary btn-accept" data-id="${quest.id}"><i class="fa fa-handshake-o"></i> 簽訂契約 (接取)</button>`;
            } else if (quest.status === 'active') {
                btnHTML = `<button class="btn btn-primary btn-submit" data-id="${quest.id}"><i class="fa fa-pencil-square-o"></i> 執行劇情並提交</button>`;
            } else if (quest.status === 'completed') {
                btnHTML = `<button class="btn btn-secondary" disabled><i class="fa fa-check"></i> 主線任務已提交</button>`;
            }

            card.innerHTML = `
                <div>
                    <div class="quest-header">
                        <span class="quest-badge ${badgeClass}">${badgeText}</span>
                        <span style="font-size: 0.8rem; color: var(--text-muted)">Display Order: ${quest.display_order}</span>
                    </div>
                    <h3 class="quest-title">${quest.title}</h3>
                    <p class="quest-desc">${quest.description}</p>
                    
                    ${objectivesPreviewHTML}
                </div>
                
                <div>
                    <div class="quest-rewards">
                        <span class="reward-item reward-exp"><i class="fa fa-star"></i> +${quest.reward_exp} EXP</span>
                        <span class="reward-item reward-gold"><i class="fa fa-database"></i> +${quest.reward_gold} GOLD</span>
                    </div>
                    ${btnHTML}
                </div>
            `;

            // 進行中或可接取或已完成的放上面，鎖定的放下面
            if (quest.status === 'locked') {
                lockedQuestsGrid.appendChild(card);
            } else {
                activeQuestsGrid.appendChild(card);
            }
        });

        // 綁定按鈕事件
        document.querySelectorAll('.btn-accept').forEach(btn => {
            btn.addEventListener('click', e => {
                const questId = e.currentTarget.getAttribute('data-id');
                acceptQuest(questId);
            });
        });

        document.querySelectorAll('.btn-submit').forEach(btn => {
            btn.addEventListener('click', e => {
                const questId = e.currentTarget.getAttribute('data-id');
                openQuestSubmitForm(questId);
            });
        });
    }

    /* ==========================================================================
       任務接取與表單視窗互動
       ========================================================================== */

    // 1. 接取任務
    async function acceptQuest(questId) {
        try {
            const response = await fetch(`/api/quests/${questId}/accept`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await response.json();
            if (data.success) {
                showToast(data.message);
                fetchAdventurerStatus();
                fetchQuests();
            } else {
                alert(data.error);
            }
        } catch (error) {
            console.error("Error accepting quest:", error);
        }
    }

    // 2. 開啟對應任務的表單
    function openQuestSubmitForm(questId) {
        const quest = questsData.find(q => q.id == questId);
        if (!quest) return;

        modalTitle.innerText = `主線表單：${quest.title}`;
        modalErrorAlert.style.display = 'none';
        questSubmitForm.setAttribute('data-quest-id', questId);

        // 渲染故事引導 HTML
        let formFieldsHTML = `
            <div class="story-intro-panel">
                “ ${quest.story_intro} ”
            </div>
        `;

        // 根據任務 ID 動態載入專屬表單欄位
        if (questId === 1) {
            // 開戶任務
            formFieldsHTML += `
                <div class="form-group">
                    <label for="real_name">冒險者真實姓名</label>
                    <input type="text" id="real_name" name="real_name" class="form-control" placeholder="輸入您的稱呼" required minlength="2">
                </div>
                <div class="form-group">
                    <label for="character_class">選定之冒險職業</label>
                    <select id="character_class" name="character_class" class="form-control" required>
                        <option value="Warrior">戰士 (Warrior) - 精通體格與物理防禦</option>
                        <option value="Mage">法師 (Mage) - 掌管元素與奧術秘寶</option>
                        <option value="Rogue">盜賊 (Rogue) - 靈活暗步與開鎖大師</option>
                        <option value="Cleric">牧師 (Cleric) - 神聖信仰與庇護治癒</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="vault_password">安全金庫保險箱密碼</label>
                    <input type="password" id="vault_password" name="vault_password" class="form-control" placeholder="至少六位數安全防護" required minlength="6">
                </div>
                <div class="form-group">
                    <label for="license_number">您的冒險執照編號</label>
                    <input type="text" id="license_number" name="license_number" class="form-control" placeholder="格式如: ADV-12345" required pattern="^ADV-\\d{5}$">
                </div>
            `;
        } else if (questId === 2) {
            // 保單分析任務
            formFieldsHTML += `
                <div class="form-group">
                    <label>當前探險風險評級</label>
                    <div class="radio-group">
                        <label class="radio-label">
                            <input type="radio" name="risk_level" value="low" checked>
                            <span>低風險地區 (如: 新手草原、地鼠洞窟)</span>
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="risk_level" value="medium">
                            <span>中風險地區 (如: 骷髏廢墟、蜘蛛巢穴)</span>
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="risk_level" value="high">
                            <span>高風險地區 (如: 熔岩深淵、巨龍巢穴)</span>
                        </label>
                    </div>
                </div>
                <div class="form-group">
                    <label for="coverage_amount">期望之保險保障額度 (金幣)</label>
                    <input type="number" id="coverage_amount" name="coverage_amount" class="form-control" placeholder="輸入範圍: 10,000 ~ 1,000,000" min="10000" max="1000000" required>
                </div>
                <div class="form-group">
                    <label>加購主要保險項目 (可複選)</label>
                    <div class="checkbox-group">
                        <label class="checkbox-label">
                            <input type="checkbox" name="insurance_types" value="casualty" checked>
                            <span>人身意外亡故險 (保障靈魂重塑金費)</span>
                        </label>
                        <label class="checkbox-label">
                            <input type="checkbox" name="insurance_types" value="property">
                            <span>史詩裝備損毀折舊險 (防範巨龍吐息熔解)</span>
                        </label>
                        <label class="checkbox-label">
                            <input type="checkbox" name="insurance_types" value="theft">
                            <span>財寶盜竊丟失險 (防範地精或同行盜賊偷竊)</span>
                        </label>
                    </div>
                </div>
            `;
        } else {
            // 自訂任務：動態渲染其 objectives 當成文字輸入框
            quest.objectives.forEach(obj => {
                formFieldsHTML += `
                    <div class="form-group">
                        <label for="${obj.code_identifier}">${obj.description}</label>
                        <input type="text" id="${obj.code_identifier}" name="${obj.code_identifier}" class="form-control" required placeholder="請填寫此目標進度">
                    </div>
                `;
            });
        }

        formFieldsHTML += `
            <button type="submit" class="btn btn-primary" style="margin-top: 15px">
                <i class="fa fa-paper-plane-o"></i> 簽訂契約並交付任務
            </button>
        `;

        modalFormContainer.innerHTML = formFieldsHTML;
        questModal.classList.add('active');
    }

    // 關閉 Modal
    document.querySelectorAll('.modal-close-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            questModal.classList.remove('active');
        });
    });

    // 3. 提交任務表單後端處理
    questSubmitForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        modalErrorAlert.style.display = 'none';

        const questId = questSubmitForm.getAttribute('data-quest-id');
        const formData = new FormData(questSubmitForm);
        const payload = {};

        // 解析表單資料為 JSON
        if (questId == 1) {
            payload.real_name = formData.get('real_name');
            payload.character_class = formData.get('character_class');
            payload.vault_password = formData.get('vault_password');
            payload.license_number = formData.get('license_number');
        } else if (questId == 2) {
            payload.risk_level = formData.get('risk_level');
            payload.coverage_amount = formData.get('coverage_amount');
            
            // 解析複選框
            const checkboxes = questSubmitForm.querySelectorAll('input[name="insurance_types"]:checked');
            payload.insurance_types = Array.from(checkboxes).map(cb => cb.value);
        } else {
            // 自訂任務
            const quest = questsData.find(q => q.id == questId);
            quest.objectives.forEach(obj => {
                payload[obj.code_identifier] = formData.get(obj.code_identifier);
            });
        }

        try {
            const response = await fetch(`/api/quests/${questId}/submit`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await response.json();
            
            if (data.success) {
                // 關閉 Modal
                questModal.classList.remove('active');
                
                // 觸發金箔粒子煙火
                triggerEpicConfetti();

                // 處理升級
                if (data.new_stats.is_level_up) {
                    showLevelUpScreen(data.new_stats);
                } else {
                    showToast(data.message);
                }

                // 刷新資料
                fetchAdventurerStatus(true);
                fetchQuests();
            } else {
                modalErrorAlert.innerText = data.error;
                modalErrorAlert.style.display = 'flex';
            }
        } catch (error) {
            console.error("Error submitting quest form:", error);
            modalErrorAlert.innerText = "通訊失敗，後端魔法矩陣斷開連線！";
            modalErrorAlert.style.display = 'flex';
        }
    });

    /* ==========================================================================
       升級特效面板處理
       ========================================================================= */
    function showLevelUpScreen(stats) {
        // 設定升級數值
        levelupOldLv.innerText = `Lv.${stats.level - stats.level_ups_count}`;
        levelupNewLv.innerText = `Lv.${stats.level}`;
        levelupNewTitle.innerText = stats.title;
        
        levelupOverlay.classList.add('active');
    }

    levelupCloseBtn.addEventListener('click', () => {
        levelupOverlay.classList.remove('active');
    });

    /* ==========================================================================
       管理控制台：自訂主線任務建立
       ========================================================================== */
    const addObjectiveBtn = document.getElementById('add-objective-btn');
    const customObjectivesContainer = document.getElementById('custom-objectives-container');
    const customQuestForm = document.getElementById('custom-quest-form');
    
    // 動態新增子目標輸入欄位
    addObjectiveBtn.addEventListener('click', () => {
        const row = document.createElement('div');
        row.className = 'objective-input-row';
        row.innerHTML = `
            <input type="text" class="form-control obj-desc" placeholder="目標描述 (例: 完成第二次投資保險)" required>
            <input type="text" class="form-control obj-id" placeholder="程式代碼 (例: invest_task)" required pattern="^[a-zA-Z0-9_]+$">
            <button type="button" class="objective-remove-btn"><i class="fa fa-trash"></i></button>
        `;
        
        row.querySelector('.objective-remove-btn').addEventListener('click', () => {
            row.remove();
        });
        
        customObjectivesContainer.appendChild(row);
    });

    // 提交建立自訂任務
    customQuestForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const title = document.getElementById('custom-title').value;
        const description = document.getElementById('custom-desc').value;
        const storyIntro = document.getElementById('custom-story').value;
        const rewardGold = document.getElementById('custom-reward-gold').value;
        const rewardExp = document.getElementById('custom-reward-exp').value;
        
        // 抓取子目標
        const objectives = [];
        const rows = customObjectivesContainer.querySelectorAll('.objective-input-row');
        rows.forEach(row => {
            objectives.push({
                description: row.querySelector('.obj-desc').value,
                code_identifier: row.querySelector('.obj-id').value
            });
        });

        // 預設將新任務的前置任務設為 2 (保單分析)，形成一條完整的解鎖任務鏈
        const payload = {
            title,
            description,
            story_intro: storyIntro,
            reward_gold: rewardGold,
            reward_exp: rewardExp,
            prerequisite_quest_id: 2, 
            objectives
        };

        try {
            const response = await fetch('/api/quests/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await response.json();
            if (data.success) {
                showToast(data.message);
                customQuestForm.reset();
                // 留下一個預設的子目標欄位，清空其他的
                customObjectivesContainer.innerHTML = `
                    <div class="objective-input-row">
                        <input type="text" class="form-control obj-desc" placeholder="目標描述 (例: 完成第二次投資保險)" required>
                        <input type="text" class="form-control obj-id" placeholder="程式代碼 (例: invest_task)" required pattern="^[a-zA-Z0-9_]+$">
                    </div>
                `;
                fetchQuests();
            } else {
                alert(data.error);
            }
        } catch (error) {
            console.error("Error creating custom quest:", error);
            alert("後端接口無法建立任務！");
        }
    });

    /* ==========================================================================
       Toast 提示工具
       ========================================================================== */
    function showToast(message) {
        toast.innerText = message;
        toast.classList.add('active');
        setTimeout(() => {
            toast.classList.remove('active');
        }, 5000);
    }

    // 啟動載入
    fetchAdventurerStatus();
    fetchQuests();
});
