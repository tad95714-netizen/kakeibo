/**
 * トースト通知の共通処理。
 * 画面下部に短いメッセージを一時的に表示する。
 * (読み込み順の都合上このファイルに置いているが、他のJSファイルからも利用する)
 */
const Toast = (() => {
    const el = document.getElementById("toast");
    let timerId = null;

    function show(message, duration = 3000) {
        el.textContent = message;
        el.hidden = false;
        clearTimeout(timerId);
        timerId = setTimeout(() => {
            el.hidden = true;
        }, duration);
    }

    return { show };
})();

/**
 * カテゴリ管理パネルの画面ロジック。
 * カテゴリの一覧表示・追加・削除を担当する。
 * 他のファイル(transactions.js)からは Categories.getAll() / getByType() で
 * 現在のカテゴリ一覧を参照できる。カテゴリが変化した際は
 * "categories:changed" イベントを発火するので、必要なファイルはそれを購読できる。
 */
const Categories = (() => {
    let cache = [];

    const listEl = document.getElementById("category-list");
    const formEl = document.getElementById("category-form");
    const nameInput = document.getElementById("category-name");
    const errorEl = document.getElementById("category-form-error");

    function typeLabel(type) {
        return type === "income" ? "収入用" : "支出用";
    }

    function render() {
        listEl.innerHTML = "";

        if (cache.length === 0) {
            const empty = document.createElement("li");
            empty.className = "ledger-list__empty";
            empty.textContent = "まだカテゴリがありません";
            listEl.appendChild(empty);
            return;
        }

        for (const category of cache) {
            const item = document.createElement("li");
            item.className = "category-list__item";

            const name = document.createElement("span");
            name.className = "category-list__name";
            name.textContent = category.name;

            const badge = document.createElement("span");
            badge.className = `category-list__badge category-list__badge--${category.type}`;
            badge.textContent = typeLabel(category.type);

            const deleteBtn = document.createElement("button");
            deleteBtn.type = "button";
            deleteBtn.className = "category-list__delete";
            deleteBtn.textContent = "削除";
            deleteBtn.setAttribute("aria-label", `${category.name}を削除`);
            deleteBtn.addEventListener("click", () => handleDelete(category.id));

            item.append(name, badge, deleteBtn);
            listEl.appendChild(item);
        }
    }

    function notifyChanged() {
        document.dispatchEvent(new CustomEvent("categories:changed"));
    }

    async function load() {
        try {
            cache = await Api.getCategories();
        } catch (e) {
            cache = [];
            Toast.show(e.message);
        }
        render();
        notifyChanged();
    }

    function showError(message) {
        errorEl.textContent = message;
        errorEl.hidden = false;
    }

    function clearError() {
        errorEl.hidden = true;
        errorEl.textContent = "";
    }

    async function handleSubmit(event) {
        event.preventDefault();
        clearError();

        const name = nameInput.value.trim();
        const type = formEl.querySelector('input[name="category-type"]:checked').value;

        if (!name) {
            showError("カテゴリ名を入力してください");
            return;
        }

        try {
            await Api.createCategory({ name, type });
            formEl.reset();
            Toast.show("カテゴリを追加しました");
            await load();
        } catch (e) {
            showError(e.message);
        }
    }

    async function handleDelete(id) {
        if (!confirm("このカテゴリを削除しますか?")) {
            return;
        }
        try {
            await Api.deleteCategory(id);
            Toast.show("カテゴリを削除しました");
            await load();
        } catch (e) {
            Toast.show(e.message);
        }
    }

    formEl.addEventListener("submit", handleSubmit);

    return {
        load,
        getAll: () => cache,
        getByType: (type) => cache.filter((c) => c.type === type),
    };
})();