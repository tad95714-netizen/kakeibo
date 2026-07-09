/**
 * レポート(月次集計)パネルの画面ロジック。
 * 選択した月の収入/支出/収支サマリーと、カテゴリ別内訳(バー表示)を描画する。
 */
const Reports = (() => {
    const monthInput = document.getElementById("report-month");
    const incomeEl = document.getElementById("report-income");
    const expenseEl = document.getElementById("report-expense");
    const balanceEl = document.getElementById("report-balance");
    const breakdownEl = document.getElementById("report-breakdown");

    function formatYen(amount) {
        return `¥${amount.toLocaleString("ja-JP")}`;
    }

    function currentYearMonth() {
        const now = new Date();
        return { year: now.getFullYear(), month: now.getMonth() + 1 };
    }

    function parseMonthInput() {
        const value = monthInput.value;
        if (!value) {
            return currentYearMonth();
        }
        const [year, month] = value.split("-").map(Number);
        return { year, month };
    }

    function renderBreakdown(items, maxAmount) {
        breakdownEl.innerHTML = "";

        if (items.length === 0) {
            const empty = document.createElement("li");
            empty.className = "ledger-list__empty";
            empty.textContent = "この月のデータはまだありません";
            breakdownEl.appendChild(empty);
            return;
        }

        for (const item of items) {
            const li = document.createElement("li");
            li.className = `report-breakdown__item report-breakdown__item--${item.type}`;

            const label = document.createElement("div");
            label.className = "report-breakdown__label";

            const name = document.createElement("span");
            name.className = "report-breakdown__name";
            name.textContent = item.category_name;

            const amount = document.createElement("span");
            amount.className = "report-breakdown__amount";
            amount.textContent = formatYen(item.amount);

            label.append(name, amount);

            const track = document.createElement("div");
            track.className = "report-breakdown__bar-track";

            const bar = document.createElement("div");
            bar.className = `report-breakdown__bar report-breakdown__bar--${item.type}`;
            const ratio = maxAmount > 0 ? (item.amount / maxAmount) * 100 : 0;
            bar.style.width = `${ratio}%`;

            track.appendChild(bar);
            li.append(label, track);
            breakdownEl.appendChild(li);
        }
    }

    async function load() {
        const { year, month } = parseMonthInput();
        let report;
        try {
            report = await Api.getMonthlyReport(year, month);
        } catch (e) {
            Toast.show(e.message);
            report = { total_income: 0, total_expense: 0, balance: 0, category_breakdown: [] };
        }

        incomeEl.textContent = formatYen(report.total_income);
        expenseEl.textContent = formatYen(report.total_expense);
        balanceEl.textContent = formatYen(report.balance);

        const maxAmount = report.category_breakdown.reduce((max, item) => Math.max(max, item.amount), 0);
        renderBreakdown(report.category_breakdown, maxAmount);
    }

    const { year, month } = currentYearMonth();
    monthInput.value = `${year}-${String(month).padStart(2, "0")}`;
    monthInput.addEventListener("change", load);

    return { load };
})();