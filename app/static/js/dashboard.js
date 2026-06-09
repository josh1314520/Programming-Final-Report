document.addEventListener("DOMContentLoaded", () => {
    // 實作進度條動畫
    const progressBar = document.querySelector('.progress-bar');
    if (progressBar && progressBar.dataset.target) {
        // 設定一小段延遲讓動畫能被看見
        setTimeout(() => {
            progressBar.style.width = progressBar.dataset.target;
        }, 300);
    }
});
