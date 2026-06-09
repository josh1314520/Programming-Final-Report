document.addEventListener("DOMContentLoaded", () => {
    const readButtons = document.querySelectorAll('.read-news-btn');

    readButtons.forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const url = btn.dataset.url;
            
            // 開啟新分頁閱讀新聞
            window.open(url, '_blank');
            
            // 替換按鈕狀態避免重複點擊
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 處理中...';
            btn.disabled = true;

            try {
                const response = await fetch('/api/news/read', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ news_url: url })
                });

                const data = await response.json();

                if (data.success) {
                    showToast(data.message, 'success');
                    // 更新按鈕樣式
                    btn.className = 'btn btn-secondary disabled';
                    btn.innerHTML = '<i class="fas fa-check-circle"></i> 已閱讀 (已領取)';
                } else {
                    showToast(data.message, 'error');
                    // 恢復按鈕狀態
                    btn.className = 'btn btn-primary read-news-btn';
                    btn.disabled = false;
                    btn.innerHTML = '<i class="fas fa-book-reader"></i> 閱讀並領取獎勵';
                }
            } catch (err) {
                console.error(err);
                showToast('網路錯誤，請稍後再試。', 'error');
                btn.className = 'btn btn-primary read-news-btn';
                btn.disabled = false;
                btn.innerHTML = '<i class="fas fa-book-reader"></i> 閱讀並領取獎勵';
            }
        });
    });

    function showToast(message, type) {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        const icon = type === 'success' ? '<i class="fas fa-check-circle"></i>' : '<i class="fas fa-exclamation-circle"></i>';
        
        toast.innerHTML = `${icon} <span>${message}</span>`;
        container.appendChild(toast);

        // 動畫進入
        setTimeout(() => toast.classList.add('show'), 10);

        // 3秒後消失
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
});
