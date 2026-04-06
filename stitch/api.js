/**
 * CSU Date 前端 API 工具
 * Token：优先 csudate_token（与 login 一致），兼容旧键 csudate_access_token。
 * API 根：默认 http://127.0.0.1:8888，可 localStorage.setItem('csudate_api_base', url) 覆盖。
 */
(function () {
  var KEY_TOKEN = 'csudate_token';
  var KEY_TOKEN_LEGACY = 'csudate_access_token';
  var KEY_API = 'csudate_api_base';

  window.csudateGetToken = function () {
    return localStorage.getItem(KEY_TOKEN) || localStorage.getItem(KEY_TOKEN_LEGACY);
  };

  // 本地开发用 127.0.0.1:8888，线上 Nginx 反代同域名用空串
  var DEFAULT_API = location.hostname === '127.0.0.1' || location.hostname === 'localhost'
    ? 'http://127.0.0.1:8888'
    : '';

  window.CSU_DATE_API_BASE = function () {
    return (localStorage.getItem(KEY_API) || DEFAULT_API).replace(/\/$/, '');
  };

  window.csudateSetApiBase = function (url) {
    if (url) localStorage.setItem(KEY_API, String(url).replace(/\/$/, ''));
    else localStorage.removeItem(KEY_API);
  };

  window.csudateAuthHeaders = function (jsonBody) {
    var h = {};
    if (jsonBody !== false) h['Content-Type'] = 'application/json';
    var t = window.csudateGetToken();
    if (t) h['Authorization'] = 'Bearer ' + t;
    return h;
  };

  window.csudateFetch = function (path, options) {
    options = options || {};
    var url = CSU_DATE_API_BASE() + path;
    var headers = Object.assign({}, csudateAuthHeaders(true), options.headers || {});
    if (options.body instanceof FormData) delete headers['Content-Type'];
    return fetch(url, Object.assign({}, options, { headers: headers })).then(function (res) {
      if (res.status === 401) {
        localStorage.removeItem(KEY_TOKEN);
        localStorage.removeItem(KEY_TOKEN_LEGACY);
        localStorage.removeItem('csudate_user');
      }
      return res;
    });
  };

  window.csudateLogout = function () {
    localStorage.removeItem(KEY_TOKEN);
    localStorage.removeItem(KEY_TOKEN_LEGACY);
    localStorage.removeItem('csudate_user');
  };

  window.csudateApiErrorMessage = function (data) {
    if (!data || data.detail == null) return '请求失败';
    if (typeof data.detail === 'string') return data.detail;
    if (Array.isArray(data.detail))
      return data.detail
        .map(function (d) {
          return d.msg || d.message || JSON.stringify(d);
        })
        .join('；');
    return String(data.detail);
  };

  window.csudateRefreshMe = async function () {
    if (!window.csudateGetToken()) return null;
    var res = await csudateFetch('/api/user/me', { method: 'GET' });
    if (res.status === 401) {
      window.location.href = 'login.html';
      return null;
    }
    if (!res.ok) return null;
    var user = await res.json();
    localStorage.setItem('csudate_user', JSON.stringify(user));
    return user;
  };
})();
