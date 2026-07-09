/**
 * 収支入力・一覧パネルの画面ロジック。
 * 入力フォームでは種別(収入/支出)に応じてカテゴリの選択肢を絞り込み、
 * 一覧パネルでは月ごとの取引とサマリー(収入/支出/収支)を表示する。
 */
const Transactions = (() => {
    // --- 入力フォーム関連 ---
    const formEl = document.getElementById("tx-form");
    const dateInput = document.getElementById("tx-date");
    const amountInput = document.getElementById("tx-amount");
    const categorySelect = document.getElementById("tx-category");
    const memoInput = document.getElementById("tx-memo");
    const formErrorEl = document.getElementById("tx-form-error");

    // --- 一覧パネル関連 ---
    const monthInput = document.getElementById("list-month");
    const summaryIncomeEl = document.getElementById("summary-income");
    const summaryExpenseEl = document.getElementById("summary-expense");
    const summaryBalanceEl = document.getElementById("summary-balance");
    const listEl = document.getElementById("transaction-list");

    function formatYen(amount) {
        return `¥${amount.toLocaleString("ja-JP")}`;
    }

    // "2026-07-01" -> "7/1" (文字列のまま扱い、Dateへの変換によるタイムゾーンずれを避ける)
    function formatDateShort(dateStr) {
        const [, month, day] = dateStr.split("-");
        return `${Number(month)}/${Number(day)}`;
    }

    function currentYearMonth() {
        const now = new Date();
        const month = String(now.getMonth() + 1).padStart(2, "0");
        return `${now.getFullYear()}-${month}`;
    }

    function monthToDateRange(yearMonth) {
        const [year, month] = yearMonth.split("-").map(Number);
        const lastDay = new Date(year, month, 0).getDate();
        return {
            dateFrom: `${yearMonth}-01`,
            dateTo: `${yearMonth}-${String(lastDay).padStart(2, "0")}`,
        };
    }

    /* ------------------------- 入力フォーム ------------------------- */

    function selectedTxType() {
        return formEl.querySelector('input[name="tx-type"]:checked').value;
    }

    function populateCategoryOptions() {
        const type = selectedTxType();
        const categories = Categories.getByType(type);
        const currentValue = categorySelect.value;

        categorySelect.innerHTML = "";
        const placeholder = document.createElement("option");
        placeholder.value = "";
        placeholder.disabled = true;
        placeholder.textContent = "選択してください";
        categorySelect.appendChild(placeholder);

        for (const category of categories) {
            const option = document.createElement("option");
            option.value = String(category.id);
            option.textContent = category.name;
            categorySelect.appendChild(option);
        }

        // 直前に選んでいたカテゴリが引き続き選択肢にあれば維持する
        if (categories.some((c) => String(c.id) === currentValue)) {
            categorySelect.value = currentValue;
        } else {
            placeholder.selected = true;
        }
    }

    function showFormError(message) {
        formErrorEl.textContent = message;
        formErrorEl.hidden = false;
    }

    function clearFormError() {
        formErrorEl.hidden = true;
        formErrorEl.textContent = "";
    }

    async function handleSubmit(event) {
        event.preventDefault();
        clearFormError();

        const type = selectedTxType();
        const date = dateInput.value;
        const amount = Number(amountInput.value);
        const categoryId = categorySelect.value;
        const memo = memoInput.value.trim();

        if (!date) {
            showFormError("日付を入力してください");
            return;
        }
        if (!Number.isFinite(amount) || amount <= 0 || !Number.isInteger(amount)) {
            showFormError("金額は1円以上の整数で入力してください");
            return;
        }
        if (!categoryId) {
            showFormError("カテゴリを選択してください");
            return;
        }

        try {
            await Api.createTransaction({
                date,
                amount,
                type,
                category_id: Number(categoryId),
                memo: memo || null,
            });
            formEl.reset();
            populateCategoryOptions();
            Toast.show("記帳しました");
            await loadList();
        } catch (e) {
            showFormError(e.message);
        }
    }

    /* ------------------------- 一覧パネル ------------------------- */

    function renderSummary(transactions) {
        let income = 0;
        let expense = 0;
        for (const t of transactions) {
            if (t.type === "income") {
                income += t.amount;
            } else {
                expense += t.amount;
            }
        }
        summaryIncomeEl.textContent = formatYen(income);
        summaryExpenseEl.textContent = formatYen(expense);
        summaryBalanceEl.textContent = formatYen(income - expense);
    }

    function renderList(transactions) {
        listEl.innerHTML = "";

        if (transactions.length === 0) {
            const empty = document.createElement("li");
            empty.className = "ledger-list__empty";
            empty.textContent = "この月の記録はまだありません";
            listEl.appendChild(empty);
            return;
        }

        for (const t of transactions) {
            const item = document.createElement("li");
            item.className = "ledger-list__item";

            const dateEl = document.createElement("span");
            dateEl.className = "ledger-list__date";
            dateEl.textContent = formatDateShort(t.date);

            const detail = document.createElement("div");
            detail.className = "ledger-list__detail";

            const categoryEl = document.createElement("div");
            categoryEl.className = "ledger-list__category";
            categoryEl.textContent = t.category ? t.category.name : "";
            detail.appendChild(categoryEl);

            if (t.memo) {
                const memoEl = document.createElement("div");
                memoEl.className = "ledger-list__memo";
                memoEl.textContent = t.memo;
                detail.appendChild(memoEl);
            }

            const amountEl = document.createElement("span");
            amountEl.className = `ledger-list__amount ledger-list__amount--${t.type}`;
            const sign = t.type === "expense" ? "-" : "+";
            amountEl.textContent = `${sign}${formatYen(t.amount)}`;

            const deleteBtn = document.createElement("button");
            deleteBtn.type = "button";
            deleteBtn.className = "ledger-list__delete";
            deleteBtn.textContent = "削除";
            deleteBtn.setAttribute("aria-label", "この記録を削除");
            deleteBtn.addEventListener("click", () => handleDeleteTransaction(t.id));

            item.append(dateEl, detail, amountEl, deleteBtn);
            listEl.appendChild(item);
        }
    }

    async function loadList() {
        const { dateFrom, dateTo } = monthToDateRange(monthInput.value || currentYearMonth());
        let transactions;
        try {
            transactions = await Api.getTransactions({ date_from: dateFrom, date_to: dateTo });
        } catch (e) {
            Toast.show(e.message);
            transactions = [];
        }
        renderList(transactions);
        renderSummary(transactions);
    }

    async function handleDeleteTransaction(id) {
        if (!confirm("この記録を削除しますか?")) {
            return;
        }
        try {
            await Api.deleteTransaction(id);
            Toast.show("削除しました");
            await loadList();
        } catch (e) {
            Toast.show(e.message);
        }
    }

    /* ------------------------- 初期化 ------------------------- */

    monthInput.value = currentYearMonth();
    populateCategoryOptions();

    formEl.querySelectorAll('input[name="tx-type"]').forEach((radio) => {
        radio.addEventListener("change", populateCategoryOptions);
    });
    formEl.addEventListener("submit", handleSubmit);
    monthInput.addEventListener("change", loadList);
    document.addEventListener("categories:changed", populateCategoryOptions);

    return { loadList };
})();