/**
 * バックエンドAPIとの通信を担う共通処理。
 * fetchのラッパーとして、エラーハンドリングとJSONへの変換をまとめて行う。
 * 他のJSファイルからは `Api.getCategories()` のように呼び出す。
 */
const Api = (() => {
  const BASE_URL = "/api";

  async function request(path, options = {}) {
    const response = await fetch(`${BASE_URL}${path}`, {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      let message = `通信エラーが発生しました (${response.status})`;
      try {
        const body = await response.json();
        if (body && body.detail) {
          message = body.detail;
        }
      } catch (_) {
        // JSONで返らないエラーの場合はデフォルトメッセージを使う
      }
      throw new Error(message);
    }

    if (response.status === 204) {
      return null;
    }

    return response.json();
  }

  function toQueryString(params) {
    const query = new URLSearchParams();
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== null && value !== "") {
        query.set(key, value);
      }
    }
    const str = query.toString();
    return str ? `?${str}` : "";
  }

  return {
    // カテゴリ
    getCategories: (filters = {}) => request(`/categories${toQueryString(filters)}`),
    createCategory: (data) => request("/categories", { method: "POST", body: JSON.stringify(data) }),
    updateCategory: (id, data) => request(`/categories/${id}`, { method: "PUT", body: JSON.stringify(data) }),
    deleteCategory: (id) => request(`/categories/${id}`, { method: "DELETE" }),

    // 収支データ
    getTransactions: (filters = {}) => request(`/transactions${toQueryString(filters)}`),
    createTransaction: (data) => request("/transactions", { method: "POST", body: JSON.stringify(data) }),
    updateTransaction: (id, data) => request(`/transactions/${id}`, { method: "PUT", body: JSON.stringify(data) }),
    deleteTransaction: (id) => request(`/transactions/${id}`, { method: "DELETE" }),

    // レポート(月次集計)
    getMonthlyReport: (year, month) => request(`/reports/monthly${toQueryString({ year, month })}`),
  };
})();