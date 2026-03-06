function byId(id) {
  return document.getElementById(id);
}

function linesToArray(text) {
  return text.split(/\r?\n/).map(s => s.trim()).filter(Boolean);
}

function safePretty(value) {
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value);
  }
}

function appendLog(text, type = "info") {
  const log = byId("log");
  if (!log) return;

  const now = new Date().toLocaleString();
  const prefix =
    type === "error"
      ? "[ERROR]"
      : type === "ok"
      ? "[OK]"
      : "[INFO]";

  const line = document.createElement("div");
  line.className = `log-line ${type}`;
  line.textContent = `[${now}] ${prefix} ${text}`;

  log.prepend(line);
  log.scrollTop = 0;
}

function setBackendStatus(text, ok = false, error = false) {
  const el = byId("backendStatus");
  if (!el) return;
  el.textContent = text;
  el.className = "status" + (ok ? " ok" : error ? " error" : "");
}

async function ensureDefaultState() {
  const data = await chrome.storage.local.get(["settings", "activeEnv"]);
  let settings = data.settings;
  let activeEnv = data.activeEnv;

  if (!settings || !settings.envs || Object.keys(settings.envs).length === 0) {
    settings = {
      envs: {
        dev: {
          apiBase: "http://127.0.0.1:8642",
          sourceRedis: {
            host: "127.0.0.1",
            port: 6379,
            password: null,
            db: 0
          },
          targetRedis: {
            host: "127.0.0.1",
            port: 6379,
            password: null,
            db: 1
          },
          serverConfig: {
            platform: "1",
            group: "1",
            server: "S1",
            pre_login: "local_"
          },
          defaultHashName: "Account",
          defaultTables: ["Account"],
          defaultDeleteKeys: []
        }
      }
    };
    activeEnv = "dev";
    await chrome.storage.local.set({ settings, activeEnv });
  } else if (!activeEnv || !settings.envs[activeEnv]) {
    activeEnv = Object.keys(settings.envs)[0];
    await chrome.storage.local.set({ settings, activeEnv });
  }

  return { settings, activeEnv };
}

async function getState() {
  return await ensureDefaultState();
}

async function getEnvSettings() {
  const { settings, activeEnv } = await getState();
  const env = settings.envs[activeEnv];
  if (!env) {
    throw new Error("当前环境配置不存在，请先到 options 页面保存配置");
  }
  return { env, activeEnv, settings };
}

async function refreshEnvSelect() {
  const { settings, activeEnv } = await getState();
  const select = byId("envName");
  if (!select) return;

  select.innerHTML = "";

  Object.keys(settings.envs).forEach(name => {
    const opt = document.createElement("option");
    opt.value = name;
    opt.textContent = name;
    if (name === activeEnv) opt.selected = true;
    select.appendChild(opt);
  });
}

async function switchEnv() {
  try {
    const envName = byId("envName").value;
    const { settings } = await getState();
    await chrome.storage.local.set({ settings, activeEnv: envName });
    appendLog(`已切换环境 ${envName}`, "ok");
    await fillDefaults();
    await refreshBackendStatus();
  } catch (err) {
    appendLog(`切换环境失败: ${err.message}`, "error");
  }
}

async function apiFetch(path, method = "GET", body = null) {
  const { env } = await getEnvSettings();
  const url = `${env.apiBase}${path}`;

  const init = {
    method,
    headers: {
      "Content-Type": "application/json"
    }
  };

  if (body !== null) {
    init.body = JSON.stringify(body);
  }

  const resp = await fetch(url, init);
  const text = await resp.text();

  let json;
  try {
    json = JSON.parse(text);
  } catch {
    json = { raw: text };
  }

  if (!resp.ok) {
    throw new Error(json.message || `HTTP ${resp.status}: ${text}`);
  }

  return json;
}

async function refreshBackendStatus() {
  setBackendStatus("后端状态：检查中...");

  try {
    const { env } = await getEnvSettings();
    const resp = await fetch(`${env.apiBase}/api/health`);
    const text = await resp.text();
    setBackendStatus(`后端状态：正常 (${resp.status}) ${text}`, true, false);
  } catch (err) {
    setBackendStatus(`后端状态：异常 - ${err.message}`, false, true);
  }
}

async function fillDefaults() {
  const { env } = await getEnvSettings();

  if (byId("hashName")) {
    byId("hashName").value = env.defaultHashName || "Account";
  }
  if (byId("batchHashName")) {
    byId("batchHashName").value = env.defaultHashName || "Account";;
  }
  if (byId("viewHashName")) {
    byId("viewHashName").value = env.defaultHashName || "Account";
  }
  if (byId("deleteTables")) {
    byId("deleteTables").value = (env.defaultTables || []).join("\n");
  }
  if (byId("deleteKeys")) {
    byId("deleteKeys").value = (env.defaultDeleteKeys || []).join("\n");
  }
}

function getSelectedRedis(env, selectId) {
  const value = byId(selectId)?.value || "target";
  return value === "source" ? env.sourceRedis : env.targetRedis;
}

async function testRedisConnection() {
  try {
    const { env } = await getEnvSettings();
    const targetName = byId("testTarget").value;
    const cfg = targetName === "source" ? env.sourceRedis : env.targetRedis;
    appendLog(`开始测试 ${targetName} Redis 连接`);
    const result = await apiFetch("/api/redis/test", "POST", cfg);
    appendLog(result.message || safePretty(result), "ok");
  } catch (err) {
    appendLog(`Redis 测试失败: ${err.message}`, "error");
  }
}

async function backupDb() {
  try {
    const { env } = await getEnvSettings();
    appendLog("开始执行数据库备份：source -> target");
    const result = await apiFetch("/api/redis/backup", "POST", {
      source: env.sourceRedis,
      target: env.targetRedis
    });
    appendLog(result.message || safePretty(result), "ok");
  } catch (err) {
    appendLog(`备份失败: ${err.message}`, "error");
  }
}

async function localizeAccount() {
  try {
    const { env } = await getEnvSettings();
    const hashName = byId("hashName").value.trim() || env.defaultHashName || "Account";
    const sourceField = byId("sourceField").value.trim();
    const targetFieldRaw = byId("targetField").value.trim();

    if (!sourceField) {
      throw new Error("sourceField 不能为空");
    }

    const result = await apiFetch("/api/process/localize-account", "POST", {
      source: env.sourceRedis,
      target: env.targetRedis,
      hash_name: hashName,
      source_field: sourceField,
      target_field: targetFieldRaw === "" ? null : targetFieldRaw,
      server: env.serverConfig
    });

    appendLog((result.message || "本地化成功") + ` -> ${safePretty(result.data)}`, "ok");
  } catch (err) {
    appendLog(`本地化失败: ${err.message}`, "error");
  }
}

async function batchLocalize() {
  try {
    const { env } = await getEnvSettings();
    const hashName = byId("batchHashName").value.trim() || "acc";

    appendLog(`开始对全表执行本地化: ${hashName}`);

    const result = await apiFetch("/api/process/localize-all-acc", "POST", {
      source: env.sourceRedis,
      target: env.targetRedis,
      hash_name: hashName,
      source_fields: [],
      server: env.serverConfig
    });

    const targets = Array.isArray(result.data) ? result.data : [];
    appendLog(result.message || `全表本地化成功，共 ${targets.length} 个字段`, "ok");

    if (targets.length) {
      appendLog(`已生成 ${targets.length} 个目标字段，前 20 个：${targets.slice(0, 20).join(", ")}`);
    }
  } catch (err) {
    appendLog(`全表本地化失败: ${err.message}`, "error");
  }
}

async function deleteKeys() {
  try {
    const { env } = await getEnvSettings();
    const keys = linesToArray(byId("deleteKeys").value);

    if (!keys.length) {
      throw new Error("请填写要删除的 keys");
    }

    const expected = `DELETE ${keys.length} db=${env.targetRedis.db}`;
    const confirmText = window.prompt(
      `危险操作：删除 ${keys.length} 个 keys\n请输入确认词：\n${expected}`,
      ""
    );

    if (confirmText === null) {
      appendLog("已取消删除 keys");
      return;
    }

    const result = await apiFetch("/api/redis/delete-keys", "POST", {
      target: env.targetRedis,
      keys,
      confirm_text: confirmText
    });

    appendLog(result.message || "删除 keys 成功", "ok");
  } catch (err) {
    appendLog(`删除 keys 失败: ${err.message}`, "error");
  }
}

async function deleteTables() {
  try {
    const { env } = await getEnvSettings();
    const tables = linesToArray(byId("deleteTables").value);

    if (!tables.length) {
      throw new Error("请填写要删除的 tables");
    }

    const expected = `DELETE_TABLES ${tables.length} db=${env.targetRedis.db}`;
    const confirmText = window.prompt(
      `危险操作：删除 ${tables.length} 个 tables\n请输入确认词：\n${expected}`,
      ""
    );

    if (confirmText === null) {
      appendLog("已取消删除 tables");
      return;
    }

    const result = await apiFetch("/api/redis/delete-tables", "POST", {
      target: env.targetRedis,
      tables,
      confirm_text: confirmText
    });

    appendLog(result.message || "删除 tables 成功", "ok");
  } catch (err) {
    appendLog(`删除 tables 失败: ${err.message}`, "error");
  }
}

let fieldListVisible = false;

async function listFields() {
  const listEl = byId("fieldList");
  const btn = byId("listFieldsBtn");

  if (fieldListVisible) {
    listEl.textContent = "";
    listEl.style.display = "none";
    btn.textContent = "列出字段";
    fieldListVisible = false;
    appendLog("字段列表已收起");
    return;
  }

  try {
    const { env } = await getEnvSettings();
    const hashName = byId("viewHashName").value.trim() || env.defaultHashName || "Account";
    const redisTarget = getSelectedRedis(env, "viewRedisTarget");

    appendLog(`开始列出字段: ${hashName} from ${byId("viewRedisTarget").value}`);

    const result = await apiFetch("/api/redis/hash/list", "POST", {
      target: redisTarget,
      hash_name: hashName
    });

    const fields = result.data || [];
    listEl.textContent = fields.join("\n");
    listEl.style.display = "block";
    btn.textContent = "收起字段";
    fieldListVisible = true;

    appendLog(`成功加载 ${fields.length} 个字段`, "ok");
  } catch (err) {
    appendLog(`列出字段失败: ${err.message}`, "error");
  }
}

async function viewField() {
  try {
    const { env } = await getEnvSettings();
    const hashName = byId("viewHashName").value.trim() || env.defaultHashName || "Account";
    const field = byId("viewField").value.trim();
    const redisTarget = getSelectedRedis(env, "viewRedisTarget");

    if (!field) {
      throw new Error("请输入要查看的 field");
    }

    appendLog(`开始读取字段: ${hashName}/${field} from ${byId("viewRedisTarget").value}`);

    const result = await apiFetch("/api/redis/hash/get", "POST", {
      target: redisTarget,
      hash_name: hashName,
      field
    });

    byId("fieldViewer").textContent = safePretty(result.data);
    appendLog(result.message || "读取字段成功", "ok");
  } catch (err) {
    appendLog(`读取字段失败: ${err.message}`, "error");
  }
}

async function flushDb() {
  try {
    const { env } = await getEnvSettings();
    const expected = `FLUSHDB db=${env.targetRedis.db} host=${env.targetRedis.host}`;
    const confirmText = window.prompt(
      `危险操作：清空目标 DB\n请输入确认词：\n${expected}`,
      ""
    );

    if (confirmText === null) {
      appendLog("已取消 flushdb");
      return;
    }

    const result = await apiFetch("/api/redis/flushdb", "POST", {
      target: env.targetRedis,
      confirm_text: confirmText
    });

    appendLog(result.message || "flushdb 成功", "ok");
  } catch (err) {
    appendLog(`flushdb 失败: ${err.message}`, "error");
  }
}

function clearLog() {
  const log = byId("log");
  if (!log) return;
  log.innerHTML = "";
  appendLog("日志已清空", "ok");
}

function toggleViewerSection() {
  const body = byId("viewerSectionBody");
  const btn = byId("toggleViewerSectionBtn");
  const section = byId("viewerSection");

  if (!body || !btn || !section) return;

  const isCollapsed = body.classList.contains("collapsed");

  if (isCollapsed) {
    body.classList.remove("collapsed");
    btn.textContent = "收起";
    appendLog("已展开可视化面板");

    window.setTimeout(() => {
      section.scrollIntoView({
        behavior: "smooth",
        block: "start"
      });
    }, 40);
  } else {
    body.classList.add("collapsed");
    btn.textContent = "展开";
    appendLog("已收起可视化面板");
  }
}

function bindEvents() {
  byId("envName")?.addEventListener("change", switchEnv);
  byId("testRedisBtn")?.addEventListener("click", testRedisConnection);
  byId("backupBtn")?.addEventListener("click", backupDb);
  byId("localizeBtn")?.addEventListener("click", localizeAccount);
  byId("batchLocalizeBtn")?.addEventListener("click", batchLocalize);
  byId("deleteKeysBtn")?.addEventListener("click", deleteKeys);
  byId("deleteTablesBtn")?.addEventListener("click", deleteTables);
  byId("listFieldsBtn")?.addEventListener("click", listFields);
  byId("viewFieldBtn")?.addEventListener("click", viewField);
  byId("flushBtn")?.addEventListener("click", flushDb);
  byId("clearLogBtn")?.addEventListener("click", clearLog);
  byId("toggleViewerSectionBtn")?.addEventListener("click", toggleViewerSection);
}

document.addEventListener("DOMContentLoaded", async () => {
  bindEvents();

  try {
    await ensureDefaultState();
    await refreshEnvSelect();
    await fillDefaults();
    await refreshBackendStatus();
    appendLog("插件初始化完成", "ok");
  } catch (err) {
    appendLog(`插件初始化失败: ${err.message}`, "error");
    setBackendStatus(`初始化失败：${err.message}`, false, true);
  }
});