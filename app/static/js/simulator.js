/* ==========================================================================
   ADVENTURER'S VAULT - DYNAMIC JS SIMULATOR & INTERACTIVITY ENGINE
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function() {
    // 1. 初始化 DOM 元素參照
    const sliders = {
        gold: document.getElementById('slider-gold'),
        mana: document.getElementById('slider-mana'),
        bonds: document.getElementById('slider-bonds'),
        eggs: document.getElementById('slider-eggs'),
        supplies: document.getElementById('slider-supplies')
    };

    const badges = {
        gold: document.getElementById('badge-gold'),
        mana: document.getElementById('badge-mana'),
        bonds: document.getElementById('badge-bonds'),
        eggs: document.getElementById('badge-eggs'),
        supplies: document.getElementById('badge-supplies')
    };

    const bars = {
        gold: document.getElementById('bar-gold'),
        mana: document.getElementById('bar-mana'),
        bonds: document.getElementById('bar-bonds'),
        eggs: document.getElementById('bar-eggs'),
        supplies: document.getElementById('bar-supplies')
    };

    const totalText = document.getElementById('portfolio-total-text');
    const disasterSelect = document.getElementById('disaster-select');
    const descriptionBox = document.getElementById('disaster-description-box');
    const runSimBtn = document.getElementById('btn-run-simulation');
    const resetVaultBtn = document.getElementById('btn-reset-vault');
    const simTerminal = document.getElementById('sim-terminal');
    const terminalStatus = document.getElementById('terminal-status');
    const progressWidget = document.getElementById('progress-widget');
    const progressMonth = document.getElementById('progress-month');
    const progressValue = document.getElementById('progress-value');
    const progressBarInner = document.getElementById('progress-bar-inner');
    
    // 報告面板元素
    const reportPanel = document.getElementById('report-result-panel');
    const reportMddVal = document.getElementById('report-mdd-val');
    const reportMddDesc = document.getElementById('report-mdd-desc');
    const reportRecoveryVal = document.getElementById('report-recovery-val');
    const reportRecoveryDesc = document.getElementById('report-recovery-desc');
    const reportMinValText = document.getElementById('report-min-val');
    const reportFinalValText = document.getElementById('report-final-val');
    const reportNetDesc = document.getElementById('report-net-desc');
    const reportAdviceText = document.getElementById('report-advice-text');
    const chartSvgContainer = document.getElementById('chart-svg-container');
    const gaugeFillCircle = document.getElementById('gauge-fill-circle');

    // 災難情境描述對照表
    const disasterDescriptions = {
        "2008 年矮人銀行金融海嘯": "<strong>2008年全球次貸金融海嘯重現</strong>。公債違約風險飆高，魔力水晶與飛龍蛋等高風險板塊全面重挫，實體黃金發揮極佳避險防護。建議配置至少 25% 以上實體黃金，加購『公會存託保險』可保護公債損失。",
        "2020 年魔力瘟疫疫情大爆發": "<strong>COVID-19 疫情大爆發情境</strong>。初期發生全資產流動性恐慌崩盤，但隨後由於遠距魔法興盛，魔力水晶展開強勁 V 反彈。實體物資在疫情中狂飆 70%。建議加購『強化冷鏈糧倉』並提高物資配置以獲取暴利。",
        "2000 年魔導科技泡沫破裂": "<strong>2000年網路科技泡沫破裂</strong>。以『魔力水晶』為首的魔法科技板塊暴跌達 80%，泡沫破裂對其他實體與防守公債影響相對輕微。配置水晶時，強烈建議搭配『魔法護盾過載協議』以減免 50% 跌幅。",
        "1929 年精靈帝國大蕭條": "<strong>1929年全球大蕭條再現</strong>。長達 16 個月的毀滅性通縮蕭條。全資產暴跌，皇家公債違約，復原期極其漫長。唯有實體黃金能穩定持平並逆勢升值。建議將黃金配置比例提升至 35% 以上以求渡過寒冬。"
    };

    // 2. 初始化災難描述
    function updateDisasterDescription() {
        const selected = disasterSelect.value;
        descriptionBox.innerHTML = disasterDescriptions[selected] || "";
    }
    disasterSelect.addEventListener('change', updateDisasterDescription);
    updateDisasterDescription();

    // 3. 實作高精度等比例滑桿鎖定連動算法 (Proportional Slider Locking)
    let sliderKeys = ['gold', 'mana', 'bonds', 'eggs', 'supplies'];
    
    // 當前滑桿數值快照，用來計算差值
    let currentAllocations = {
        gold: 20,
        mana: 20,
        bonds: 20,
        eggs: 20,
        supplies: 20
    };

    function updateUI() {
        let sum = 0;
        sliderKeys.forEach(k => {
            const val = currentAllocations[k];
            sliders[k].value = val;
            badges[k].innerText = val + "%";
            bars[k].style.width = val + "%";
            sum += val;
        });

        // 確保精準為 100%
        if (Math.abs(sum - 100) < 0.1) {
            totalText.innerText = "100%";
            totalText.className = "valid-total";
            runSimBtn.disabled = false;
        } else {
            totalText.innerText = sum + "%";
            totalText.className = "invalid-total";
            runSimBtn.disabled = true;
        }
    }

    function handleSliderInput(changedKey, newValue) {
        newValue = Math.round(parseFloat(newValue));
        if (newValue < 0) newValue = 0;
        if (newValue > 100) newValue = 100;

        const oldValue = currentAllocations[changedKey];
        const diff = newValue - oldValue;

        if (diff === 0) return;

        // 設定變更滑桿的值
        currentAllocations[changedKey] = newValue;

        // 計算剩餘其他滑桿的總和
        let otherKeys = sliderKeys.filter(k => k !== changedKey);
        let sumOthers = 0;
        otherKeys.forEach(k => { sumOthers += currentAllocations[k]; });

        if (diff > 0) {
            // 向上調整：需要從其他滑桿扣除
            if (sumOthers > 0) {
                let remainingToDeduct = diff;
                // 按比例扣除
                otherKeys.forEach(k => {
                    const ratio = currentAllocations[k] / sumOthers;
                    const deduct = Math.min(currentAllocations[k], Math.round(diff * ratio));
                    currentAllocations[k] -= deduct;
                    remainingToDeduct -= deduct;
                });
                
                // 若因為四捨五入還有剩餘，隨機/順序微調扣除
                if (remainingToDeduct !== 0) {
                    for (let k of otherKeys) {
                        if (currentAllocations[k] >= remainingToDeduct && remainingToDeduct > 0) {
                            currentAllocations[k] -= remainingToDeduct;
                            remainingToDeduct = 0;
                            break;
                        } else if (remainingToDeduct < 0) {
                            // 扣過頭了，加回來
                            currentAllocations[k] -= remainingToDeduct;
                            remainingToDeduct = 0;
                            break;
                        }
                    }
                }
            } else {
                // 如果其他滑桿都是 0，則新值不能超過 100
                currentAllocations[changedKey] = 100;
            }
        } else {
            // 向下調整：需要按比例分配給其他滑桿
            let remainingToAdd = -diff;
            if (sumOthers > 0) {
                otherKeys.forEach(k => {
                    const ratio = currentAllocations[k] / sumOthers;
                    const add = Math.round((-diff) * ratio);
                    currentAllocations[k] += add;
                    remainingToAdd -= add;
                });
            } else {
                // 如果其他都是 0，平均分配
                const avg = Math.round(remainingToAdd / 4);
                otherKeys.forEach((k, idx) => {
                    if (idx === 3) {
                        currentAllocations[k] += remainingToAdd - (avg * 3);
                    } else {
                        currentAllocations[k] += avg;
                    }
                });
                remainingToAdd = 0;
            }
            
            // 四捨五入尾數修正
            if (remainingToAdd !== 0) {
                currentAllocations[otherKeys[0]] += remainingToAdd;
            }
        }

        // 雙重保險：校正總和必須恰為 100
        let total = 0;
        sliderKeys.forEach(k => { total += currentAllocations[k]; });
        if (total !== 100) {
            let error = 100 - total;
            // 加給值最大的那個 key 以保持穩定
            let maxKey = sliderKeys[0];
            sliderKeys.forEach(k => {
                if (currentAllocations[k] > currentAllocations[maxKey]) maxKey = k;
            });
            currentAllocations[maxKey] += error;
        }

        updateUI();
    }

    // 綁定 sliders 拖動事件
    sliderKeys.forEach(k => {
        sliders[k].addEventListener('input', function(e) {
            handleSliderInput(k, e.target.value);
        });
    });

    // 4. 配置範本一鍵設定 (Knight, Paladin, Mage)
    const presets = {
        knight: { gold: 40, mana: 8, bonds: 30, eggs: 2, supplies: 20 },
        paladin: { gold: 30, mana: 20, bonds: 20, eggs: 10, supplies: 20 },
        mage: { gold: 10, mana: 50, bonds: 10, eggs: 20, supplies: 10 }
    };

    document.querySelectorAll('.preset-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const presetName = this.getAttribute('data-preset');
            const data = presets[presetName];
            if (data) {
                currentAllocations = {
                    gold: data.gold,
                    mana: data.mana,
                    bonds: data.bonds,
                    eggs: data.eggs,
                    supplies: data.supplies
                };
                updateUI();
                
                // 加一個短暫的綠色發光特效提示已加載範本
                document.querySelector('.progress-track').style.boxShadow = '0 0 15px rgba(74, 222, 128, 0.4)';
                setTimeout(() => {
                    document.querySelector('.progress-track').style.boxShadow = '0 1px 3px rgba(0,0,0,0.5)';
                }, 600);
            }
        });
    });

    // 初始化 UI
    updateUI();

    // 5. 「重整公會金庫」API 一鍵重設物資
    resetVaultBtn.addEventListener('click', function() {
        if (!confirm("確定要將金庫實體物資恢復至全滿初始狀態嗎？(黃金5,000 / 水晶2,000 / 公債2,000...)")) return;
        
        resetVaultBtn.disabled = true;
        resetVaultBtn.innerHTML = '<i class="fa-solid fa-spinner-third fa-spin"></i> 恢復中...';

        fetch('/api/vault/reset', { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    // 更新看板
                    updateVaultDisplay(data.vault);
                    // 提示文字發光特效
                    triggerAssetsFlashGlow();
                    alert(data.message);
                } else {
                    alert("重置金庫失敗：" + data.message);
                }
            })
            .catch(err => {
                console.error("Error resetting vault:", err);
                alert("連線至伺服器失敗，無法重設金庫。");
            })
            .finally(() => {
                resetVaultBtn.disabled = false;
                resetVaultBtn.innerHTML = '<i class="fa-solid fa-arrows-rotate"></i> 重整公會金庫';
            });
    });

    function updateVaultDisplay(vault) {
        document.getElementById('val-gold').innerText = vault.gold.toLocaleString('en-US');
        document.getElementById('val-mana').innerText = vault.mana_crystals.toLocaleString('en-US');
        document.getElementById('val-bonds').innerText = vault.bonds.toLocaleString('en-US');
        document.getElementById('val-eggs').innerText = vault.dragon_eggs.toLocaleString('en-US');
        document.getElementById('val-supplies').innerText = vault.supplies.toLocaleString('en-US');
    }

    function triggerAssetsFlashGlow() {
        const cards = ['gold', 'mana', 'bonds', 'eggs', 'supplies'];
        cards.forEach(c => {
            const cardEl = document.getElementById(`vault-card-${c}`);
            cardEl.style.transform = 'scale(1.05)';
            cardEl.style.boxShadow = '0 0 20px rgba(212, 175, 55, 0.4)';
            setTimeout(() => {
                cardEl.style.transform = '';
                cardEl.style.boxShadow = '';
            }, 600);
        });
    }

    // 6. 「發動資產壓力測試」動態模擬引擎 (Ajax + Typewriter Logs)
    runSimBtn.addEventListener('click', function() {
        // 獲取加購升級項目
        const upgrades = [];
        document.querySelectorAll('.upgrade-cb:checked').forEach(cb => {
            upgrades.push(cb.value);
        });

        // 整理配置資料
        const payload = {
            disaster_type: disasterSelect.value,
            portfolio: {
                gold: currentAllocations.gold,
                mana_crystals: currentAllocations.mana,
                bonds: currentAllocations.bonds,
                dragon_eggs: currentAllocations.eggs,
                supplies: currentAllocations.supplies
            },
            upgrades: upgrades
        };

        // 鎖定 UI 按鈕
        runSimBtn.disabled = true;
        runSimBtn.innerHTML = '<i class="fa-solid fa-hourglass-clock fa-spin"></i> 時空法陣模擬中...';
        
        // 隱藏前一次的報告，展示全新動態日誌
        reportPanel.style.display = 'none';
        simTerminal.innerHTML = '';
        progressWidget.style.display = 'block';
        
        terminalStatus.innerHTML = '<span class="badge-dot dot-red"></span> 模擬觀測中';
        terminalStatus.className = 'status-badge text-red';

        // 滾動到水晶球監控面板
        simTerminal.scrollIntoView({ behavior: 'smooth', block: 'center' });

        // 印出初始行
        printTerminalLine(`🔮 [第 0 個月] 壓力測試時空法陣開啟！注入初始估值儲備：10,000.00 點能量。`, 'term-gold');
        printTerminalLine(`⚖️ 資產比例：黃金 ${payload.portfolio.gold}% | 水晶 ${payload.portfolio.mana_crystals}% | 公債 ${payload.portfolio.bonds}% | 飛龍蛋 ${payload.portfolio.dragon_eggs}% | 糧草 ${payload.portfolio.supplies}%`, 'term-gray');
        if (upgrades.length > 0) {
            printTerminalLine(`🛡️ 加購防禦合約：${upgrades.join(', ')}`, 'term-cyan');
        } else {
            printTerminalLine(`⚠️ 警告：未購買任何避險加購項目，金庫防護係數處於初始裸奔狀態。`, 'term-red');
        }

        // 發送異步請求
        fetch('/api/simulate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                // 成功獲取 24 個月模擬數據！執行「逐月時間軸動態回放動畫」
                runTimelineAnimation(data);
            } else {
                printTerminalLine(`❌ 模擬法陣崩塌：${data.message}`, 'term-red');
                resetSimButton();
            }
        })
        .catch(err => {
            console.error("Error simulation:", err);
            printTerminalLine(`❌ 模擬失敗：連線至公會法術伺服器中斷。`, 'term-red');
            resetSimButton();
        });
    });

    function printTerminalLine(text, className = '') {
        const line = document.createElement('div');
        line.className = `terminal-line ${className}`;
        line.innerText = text;
        simTerminal.appendChild(line);
        simTerminal.scrollTop = simTerminal.scrollHeight; // 自動滾動到底部
    }

    function resetSimButton() {
        runSimBtn.disabled = false;
        runSimBtn.innerHTML = '<i class="fa-solid fa-circle-play"></i> 發動資產風險壓力測試';
        terminalStatus.innerHTML = '<span class="badge-dot dot-green"></span> 靜止中';
        terminalStatus.className = 'status-badge';
    }

    // 7. 逐月時間流逝與事件日誌回放動畫 (RPG Typewriter log streamer)
    function runTimelineAnimation(data) {
        const chartData = data.chart_data;
        const disaster = disasterSelect.value;
        let m = 1;

        const interval = setInterval(() => {
            if (m > 24) {
                clearInterval(interval);
                // 模擬結束！
                finishSimulation(data);
                return;
            }

            const monthData = chartData[m];
            const prevMonthData = chartData[m - 1];
            const value = monthData.value;
            const change = ((value - prevMonthData.value) / prevMonthData.value) * 100.0;
            
            // 更新進度條
            progressMonth.innerText = m;
            progressValue.innerText = value.toFixed(2).toLocaleString('en-US');
            progressBarInner.style.width = (m / 24 * 100) + "%";

            // 根據月度漲跌決定日誌顏色
            let termColor = 'term-gray';
            let changePrefix = change >= 0 ? '+' : '';
            let trendText = `${changePrefix}${change.toFixed(1)}%`;
            
            if (change > 1.5) termColor = 'term-green';
            else if (change < -1.5) termColor = 'term-red';

            // 生成豐富幽默的時空背景事件日誌內容
            let logMsg = `第 ${m} 個月：大盤估值變更為 ${value.toFixed(2)} 點 (${trendText})。`;

            // 在某些關鍵時間節點插入 RPG 趣味敘事
            if (disaster === "2008 年矮人銀行金融海嘯") {
                if (m === 2) logMsg += ` [海嘯警訊] 矮人抵押雷曼銀行被傳流動性枯竭！公債價格搖晃。`;
                else if (m === 4) logMsg += ` [信貸黑洞] 矮人銀行宣布破產！皇家公債引發拋售潮。`;
                else if (m === 6) logMsg += ` [大衰退] 狂暴泡沫波及魔法水晶板塊，水晶資產重創 -5.5%！`;
                else if (m === 8) logMsg += ` [黃金閃耀] 實體黃金避險資金大量湧入，黃金暴漲！`;
                else if (m === 12) logMsg += ` [大盤觸底] 流動性危機最黑暗期已過，開始步入漫長復甦期。`;
            } 
            else if (disaster === "2020 年魔力瘟疫疫情大爆發") {
                if (m === 1) logMsg += ` [瘟疫爆發] 致命黑死魔力瘟疫肆虐！冒險隊伍隔離，大盤全線恐慌下挫！`;
                else if (m === 3) logMsg += ` [糧食短缺] 圍城物資告急！糧草大宗商品引發囤積狂熱，瘋狂暴漲！`;
                else if (m === 6) logMsg += ` [遠距通訊] 公會推出「水晶遠端傳送魔法」，魔力水晶爆發超預期 V 型反彈！`;
                else if (m === 12) logMsg += ` [冷鏈套利] 糧草儲備價格維持歷史新高，冷鏈糧倉合約帶來源源不絕的利潤。`;
                else if (m === 18) logMsg += ` [飛龍蛋劇震] 投機市場飛龍蛋遭游資爆炒，劇烈寬幅震盪！`;
            }
            else if (disaster === "2000 年魔導科技泡沫破裂") {
                if (m === 2) logMsg += ` [泡沫破滅] 水晶Dot-Com神話破滅！投機性法陣水晶板塊遭受連鎖銷毀！`;
                else if (m === 5) logMsg += ` [雪崩跌勢] 水晶大跌 -8.5%！未有護盾過載防禦的金庫面臨資產清零風險！`;
                else if (m === 10) logMsg += ` [黃金自保] 實體黃金與防守型公債在本次科技浪潮破滅中穩健如磐石。`;
                else if (m === 15) logMsg += ` [泡沫出清] 科技泡沫清算完畢，殘存的高端魔導水晶尋求低點估值整理。`;
            }
            else if (disaster === "1929 年精靈帝國大蕭條") {
                if (m === 1) logMsg += ` [黑色星期四] 精靈帝國證券交易所崩盤！通縮冰封時代降臨！`;
                else if (m === 5) logMsg += ` [物價雪崩] 商業萎縮，物資與水晶價格齊跌 -4%，皇家公債遭遇大面積破產違約！`;
                else if (m === 10) logMsg += ` [黃金稱霸] 唯有黃金在此通縮嚴寒中完美保值，持金者成為唯一的王者。`;
                else if (m === 16) logMsg += ` [冰封極限] 金庫資產回檔至極限冰點，尋求歷史大底。`;
                else if (m === 22) logMsg += ` [微弱曦光] 帝國啟動新政重建計畫，全板塊物資出現微弱的復甦跡象。`;
            }

            printTerminalLine(`⏳ ${logMsg}`, termColor);
            m++;
        }, 80); // 80ms 跨度一個月
    }

    // 8. 模擬結束！渲染指針式 MDD 儀表盤、恢復沙漏、SVG折線圖與避險卷軸
    function finishSimulation(data) {
        printTerminalLine(`🏆 [第 24 個月] 壓力測試順利完成！時空法陣平穩關閉。生成詳細風險報告...`, 'term-gold');
        
        // 解鎖按鈕
        resetSimButton();

        // 顯示報告面板
        reportPanel.style.display = 'block';

        // A. 渲染 Max Drawdown 圓形 CSS 儀表盤 (Circular Gauge)
        const mdd = data.max_drawdown;
        reportMddVal.innerText = mdd + "%";
        
        // 指針式 Dashoffset 計算 (總周長為 251.2px)
        const dashoffset = 251.2 - (251.2 * mdd / 100);
        gaugeFillCircle.style.strokeDashoffset = dashoffset;

        // 根據 MDD 自動判定評分與顏色
        let mddColor = 'var(--color-safe-emerald)';
        let mddText = '極度安全 (Low Risk)';
        if (mdd > 40.0) {
            mddColor = 'var(--color-danger-crimson)';
            mddText = '金庫崩毀 (Severe Hazard)';
            reportMddVal.style.color = 'var(--color-danger-crimson)';
        } else if (mdd > 20.0) {
            mddColor = 'var(--color-warning-yellow)';
            mddText = '中度風險 (Moderate Shock)';
            reportMddVal.style.color = 'var(--color-warning-yellow)';
        } else {
            reportMddVal.style.color = 'var(--color-safe-emerald)';
        }
        gaugeFillCircle.style.stroke = mddColor;
        reportMddDesc.innerText = mddText;
        reportMddDesc.style.color = mddColor;

        // B. 渲染恢復期沙漏 (Hourglass)
        const rp = data.recovery_period;
        const hourglassWrapper = document.getElementById('hourglass-wrapper');
        
        if (rp >= 25) {
            reportRecoveryVal.innerText = "24+ 個月";
            reportRecoveryVal.style.color = 'var(--color-danger-crimson)';
            reportRecoveryDesc.innerText = "漫長嚴冬 (Failed Recovery)";
            reportRecoveryDesc.style.color = 'var(--color-danger-crimson)';
            // 沙漏漏完停止動畫
            hourglassWrapper.innerHTML = '<i class="fa-solid fa-hourglass-empty text-red"></i>';
        } else {
            reportRecoveryVal.innerText = rp + " 個月";
            reportRecoveryVal.style.color = 'var(--color-safe-emerald)';
            // 根據恢復速度給予頭銜
            let rpText = '極速復甦 (V-Shape Rebound)';
            if (rp > 15) rpText = '緩慢爬坡 (Slow Crawl)';
            else if (rp > 8) rpText = '平穩修復 (Steady Return)';
            
            reportRecoveryDesc.innerText = rpText;
            reportRecoveryDesc.style.color = 'var(--color-safe-emerald)';
            hourglassWrapper.innerHTML = '<i class="fa-solid fa-hourglass-start animate-flip"></i>';
        }

        // C. 渲染金額演變
        reportMinValText.innerText = data.min_total_val.toLocaleString('en-US', {minimumFractionDigits: 2});
        reportFinalValText.innerText = data.final_total_val.toLocaleString('en-US', {minimumFractionDigits: 2});
        
        const netChange = ((data.final_total_val - data.initial_total_val) / data.initial_total_val) * 100.0;
        const changePrefix = netChange >= 0 ? '+' : '';
        reportNetDesc.innerText = `績效表現：${changePrefix}${netChange.toFixed(1)}%`;
        reportNetDesc.className = 'evolution-desc ' + (netChange >= 0 ? 'text-green' : 'text-red');

        // D. 渲染避險羊皮紙 HTML (markdown parse)
        let parsedAdvice = data.hedging_advice
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n\n/g, '<br><br>');
        reportAdviceText.innerHTML = parsedAdvice;

        // E. 繪製 SVG 曲線圖 (24個月走勢折線圖)
        drawSVGChart(data.chart_data);

        // F. 真實連動！更新上方金庫實體物資狀態，並發光暗示物資扣除/增加
        updateVaultDisplay(data.updated_vault);
        triggerAssetsFlashGlow();

        // 報告展開後平滑滾動到報告區域
        reportPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    // 9. 精美純 SVG 折線圖動態繪製邏輯
    function drawSVGChart(chartData) {
        chartSvgContainer.innerHTML = ''; // 清空

        if (!chartData || chartData.length === 0) return;

        const containerWidth = chartSvgContainer.clientWidth || 650;
        const containerHeight = 220;
        const padding = { top: 15, right: 35, bottom: 25, left: 45 };

        // 取得極值以利座標轉換
        const minVal = Math.min(...chartData.map(d => d.value));
        const maxVal = Math.max(...chartData.map(d => d.value));
        const valRange = maxVal - minVal;

        // 加 15% 上下邊界
        const yMin = Math.max(0, minVal - (valRange * 0.15 || 500));
        const yMax = maxVal + (valRange * 0.15 || 500);
        const yRange = yMax - yMin;

        let svg = `<svg width="100%" height="${containerHeight}" viewBox="0 0 ${containerWidth} ${containerHeight}" xmlns="http://www.w3.org/2000/svg" style="background: rgba(10, 10, 16, 0.4); border-radius: 8px;">`;

        // 轉換座標 helper
        function getX(month) {
            return padding.left + (month / 24) * (containerWidth - padding.left - padding.right);
        }
        function getY(val) {
            return padding.top + (1 - (val - yMin) / yRange) * (containerHeight - padding.top - padding.bottom);
        }

        // 1. 畫背景橫向虛線 (3條)
        const levels = [yMin + yRange * 0.25, yMin + yRange * 0.5, yMin + yRange * 0.75];
        levels.forEach(level => {
            const y = getY(level);
            svg += `<line x1="${padding.left}" y1="${y}" x2="${containerWidth - padding.right}" y2="${y}" stroke="rgba(255, 255, 255, 0.05)" stroke-dasharray="4 4" />`;
            svg += `<text x="${padding.left - 8}" y="${y + 4}" fill="rgba(255, 255, 255, 0.4)" font-size="9" text-anchor="end" font-family="'Outfit', sans-serif">${Math.round(level)}</text>`;
        });

        // 2. 畫 10,000 點金庫起跑參考線
        const y10k = getY(10000);
        if (y10k >= padding.top && y10k <= containerHeight - padding.bottom) {
            svg += `<line x1="${padding.left}" y1="${y10k}" x2="${containerWidth - padding.right}" y2="${y10k}" stroke="rgba(212, 175, 55, 0.2)" stroke-width="1.5" stroke-dasharray="5 3" />`;
            svg += `<text x="${containerWidth - padding.right - 5}" y="${y10k - 5}" fill="rgba(212, 175, 55, 0.5)" font-size="9" text-anchor="end" font-family="'Outfit', sans-serif">金庫基準點 (10,000)</text>`;
        }

        // 3. 畫漸層折線下落陰影
        let shadowPoints = `M ${getX(0)} ${getY(chartData[0].value)}`;
        chartData.forEach(d => {
            shadowPoints += ` L ${getX(d.month)} ${getY(d.value)}`;
        });
        shadowPoints += ` L ${getX(24)} ${containerHeight - padding.bottom} L ${getX(0)} ${containerHeight - padding.bottom} Z`;

        svg += `
            <defs>
                <linearGradient id="chart-shadow-grad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stop-color="rgba(212, 175, 55, 0.2)" />
                    <stop offset="100%" stop-color="rgba(212, 175, 55, 0.0)" />
                </linearGradient>
            </defs>
            <path d="${shadowPoints}" fill="url(#chart-shadow-grad)" />
        `;

        // 4. 畫主折線
        let linePath = `M ${getX(0)} ${getY(chartData[0].value)}`;
        chartData.forEach(d => {
            linePath += ` L ${getX(d.month)} ${getY(d.value)}`;
        });
        svg += `<path d="${linePath}" fill="none" stroke="rgba(212, 175, 55, 0.9)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" filter="drop-shadow(0px 0px 4px rgba(212, 175, 55, 0.4))" />`;

        // 5. 畫 X 軸時間刻度
        for (let m = 0; m <= 24; m += 4) {
            const x = getX(m);
            svg += `<line x1="${x}" y1="${containerHeight - padding.bottom}" x2="${x}" y2="${containerHeight - padding.bottom + 4}" stroke="rgba(255, 255, 255, 0.15)" />`;
            svg += `<text x="${x}" y="${containerHeight - padding.bottom + 16}" fill="rgba(255, 255, 255, 0.5)" font-size="9" text-anchor="middle" font-family="'Outfit', sans-serif">M${m}</text>`;
        }

        // 6. 標示折線月份端點 (小圓球)
        chartData.forEach(d => {
            const cx = getX(d.month);
            const cy = getY(d.value);
            
            // 是否為最低/最高點
            const isMin = d.value === minVal;
            const isMax = d.value === maxVal;
            let nodeColor = 'rgba(212, 175, 55, 1)';
            let nodeRadius = 3;
            
            if (isMin) {
                nodeColor = 'rgba(255, 75, 75, 1)';
                nodeRadius = 4.5;
            } else if (isMax) {
                nodeColor = 'rgba(75, 255, 75, 1)';
                nodeRadius = 4.5;
            }

            svg += `
                <circle cx="${cx}" cy="${cy}" r="${nodeRadius}" fill="${nodeColor}" stroke="rgba(10, 10, 16, 0.9)" stroke-width="1.2" class="chart-node-dot">
                    <title>第 ${d.month} 個月\n估值：${d.value.toFixed(2)}</title>
                </circle>
            `;
        });

        svg += '</svg>';
        chartSvgContainer.innerHTML = svg;
    }
});
