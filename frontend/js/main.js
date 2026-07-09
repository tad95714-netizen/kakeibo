/**
 * 画面全体の初期化を行うエントリーポイント。
 * タブ(入力/一覧/カテゴリ)の切り替えと、起動時のデータ読み込みをまとめる。
 */
(() => {
    function initTabs() {
        const tabs = document.querySelectorAll(".tab-bar__tab");
        const panels = document.querySelectorAll(".panel");

        tabs.forEach((tab) => {
            tab.addEventListener("click", () => {
                const targetId = tab.dataset.panel;

                tabs.forEach((t) => t.classList.toggle("is-active", t === tab));
                panels.forEach((panel) => {
                    const isTarget = panel.id === targetId;
                    panel.hidden = !isTarget;
                    panel.classList.toggle("is-active", isTarget);
                });

                // 一覧タブを開いたときは最新のデータに更新する
                if (targetId === "panel-list") {
                    Transactions.loadList();
                }
            });
        });
    }

    async function init() {
        initTabs();
        try {
            await Promise.all([Categories.load(), Transactions.loadList()]);
        } catch (e) {
            Toast.show("初期データの読み込みに失敗しました");
        }
    }

    init();
})();