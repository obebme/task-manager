const state = {
  tasks: [],
  filter: "all",
  query: "",
  editingId: null,
};

const els = {
  taskList: document.getElementById("taskList"),
  emptyState: document.getElementById("emptyState"),
  emptyTitle: document.getElementById("emptyTitle"),
  emptyText: document.getElementById("emptyText"),
  totalCount: document.getElementById("totalCount"),
  doneCount: document.getElementById("doneCount"),
  activeCount: document.getElementById("activeCount"),
  progressPercent: document.getElementById("progressPercent"),
  progressBar: document.getElementById("progressBar"),
  resultCount: document.getElementById("resultCount"),
  searchInput: document.getElementById("searchInput"),
  modalBackdrop: document.getElementById("modalBackdrop"),
  modalTitle: document.getElementById("modalTitle"),
  titleInput: document.getElementById("titleInput"),
  descriptionInput: document.getElementById("descriptionInput"),
  taskForm: document.getElementById("taskForm"),
  saveBtn: document.getElementById("saveBtn"),
  apiStatusDot: document.getElementById("apiStatusDot"),
  apiStatusText: document.getElementById("apiStatusText"),
  toast: document.getElementById("toast"),
};

function showToast(message) {
  els.toast.textContent = message;
  els.toast.classList.remove("hidden");
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => els.toast.classList.add("hidden"), 2400);
}

function setApiStatus(online) {
  els.apiStatusDot.classList.toggle("online", online);
  els.apiStatusDot.classList.toggle("offline", !online);
  els.apiStatusText.textContent = online ? "API онлайн" : "API недоступен";
}

async function apiRequest(path, options = {}) {
  const response = await fetch(path, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    let detail = `HTTP ${response.status}`;
    try {
      const body = await response.json();
      if (body.detail) detail = body.detail;
    } catch {
      // Ignore non-JSON error bodies.
    }
    throw new Error(detail);
  }

  if (response.status === 204) return null;
  return response.json();
}

async function loadTasks() {
  try {
    const tasks = await apiRequest("/tasks");
    state.tasks = Array.isArray(tasks) ? tasks : [];
    setApiStatus(true);
    render();
  } catch (error) {
    setApiStatus(false);
    showToast(`Ошибка: ${error.message}`);
    render();
  }
}

function getVisibleTasks() {
  const query = state.query.trim().toLowerCase();

  return state.tasks.filter((task) => {
    const matchesFilter =
      state.filter === "all" ||
      (state.filter === "active" && !task.completed) ||
      (state.filter === "done" && task.completed);

    const matchesQuery =
      !query ||
      task.title.toLowerCase().includes(query) ||
      task.description.toLowerCase().includes(query);

    return matchesFilter && matchesQuery;
  });
}

function renderStats() {
  const total = state.tasks.length;
  const done = state.tasks.filter((task) => task.completed).length;
  const active = total - done;
  const progress = total ? Math.round((done / total) * 100) : 0;

  els.totalCount.textContent = total;
  els.doneCount.textContent = done;
  els.activeCount.textContent = active;
  els.progressPercent.textContent = `${progress}%`;
  els.progressBar.style.width = `${progress}%`;
}

function renderTasks() {
  const visible = getVisibleTasks();
  els.taskList.innerHTML = "";
  els.resultCount.textContent = `${visible.length} ${pluralize(visible.length, "задача", "задачи", "задач")}`;

  if (!visible.length) {
    els.emptyState.classList.remove("hidden");
    els.emptyTitle.textContent = state.tasks.length ? "Ничего не найдено" : "Задач пока нет";
    els.emptyText.textContent = state.tasks.length
      ? "Попробуй другой поиск или фильтр."
      : "Создай первую задачу — она сразу появится здесь.";
    return;
  }

  els.emptyState.classList.add("hidden");

  for (const task of visible) {
    const card = document.createElement("article");
    card.className = `task-card${task.completed ? " done" : ""}`;
    card.innerHTML = `
      <div class="task-top">
        <span class="task-id">#${task.id}</span>
        <span class="badge ${task.completed ? "done" : ""}">
          ${task.completed ? "✓ Выполнена" : "○ В работе"}
        </span>
      </div>
      <h3 class="task-title">${escapeHtml(task.title)}</h3>
      <p class="task-description">${escapeHtml(task.description || "Без описания")}</p>
      <div class="card-actions">
        <button class="small-btn" data-action="toggle" data-id="${task.id}">
          ${task.completed ? "↩ Вернуть" : "✓ Выполнить"}
        </button>
        <button class="small-btn" data-action="edit" data-id="${task.id}">Изменить</button>
        <button class="small-btn danger" data-action="delete" data-id="${task.id}">Удалить</button>
      </div>
    `;
    els.taskList.appendChild(card);
  }
}

function render() {
  renderStats();
  renderTasks();
}

function openModal(task = null) {
  state.editingId = task ? task.id : null;
  els.modalTitle.textContent = task ? "Изменить задачу" : "Новая задача";
  els.saveBtn.textContent = task ? "Сохранить" : "Создать";
  els.titleInput.value = task?.title || "";
  els.descriptionInput.value = task?.description || "";
  els.modalBackdrop.classList.remove("hidden");
  setTimeout(() => els.titleInput.focus(), 0);
}

function closeModal() {
  els.modalBackdrop.classList.add("hidden");
  state.editingId = null;
  els.taskForm.reset();
}

async function createTask(title, description) {
  const created = await apiRequest("/tasks", {
    method: "POST",
    body: JSON.stringify({ title, description }),
  });
  state.tasks.push(created);
  showToast("Задача создана");
}

async function updateTask(taskId, payload) {
  const updated = await apiRequest(`/tasks/${taskId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
  state.tasks = state.tasks.map((task) => task.id === taskId ? updated : task);
  showToast("Задача обновлена");
}

async function deleteTask(taskId) {
  const task = state.tasks.find((item) => item.id === taskId);
  if (!task) return;
  if (!window.confirm(`Удалить задачу «${task.title}»?`)) return;

  await apiRequest(`/tasks/${taskId}`, { method: "DELETE" });
  state.tasks = state.tasks.filter((item) => item.id !== taskId);
  showToast("Задача удалена");
}

function pluralize(n, one, few, many) {
  const mod10 = n % 10;
  const mod100 = n % 100;
  if (mod10 === 1 && mod100 !== 11) return one;
  if (mod10 >= 2 && mod10 <= 4 && !(mod100 >= 12 && mod100 <= 14)) return few;
  return many;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

document.getElementById("openCreateBtn").addEventListener("click", () => openModal());
document.getElementById("emptyCreateBtn").addEventListener("click", () => openModal());
document.getElementById("closeModalBtn").addEventListener("click", closeModal);
document.getElementById("cancelBtn").addEventListener("click", closeModal);
document.getElementById("refreshBtn").addEventListener("click", loadTasks);

els.searchInput.addEventListener("input", (event) => {
  state.query = event.target.value;
  renderTasks();
});

document.querySelectorAll(".filter-btn").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".filter-btn").forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    state.filter = button.dataset.filter;
    renderTasks();
  });
});

els.taskList.addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button) return;

  const taskId = Number(button.dataset.id);
  const task = state.tasks.find((item) => item.id === taskId);
  if (!task) return;

  try {
    if (button.dataset.action === "toggle") {
      await updateTask(taskId, { completed: !task.completed });
      render();
    }

    if (button.dataset.action === "edit") {
      openModal(task);
    }

    if (button.dataset.action === "delete") {
      await deleteTask(taskId);
      render();
    }
  } catch (error) {
    showToast(`Ошибка: ${error.message}`);
  }
});

els.taskForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const title = els.titleInput.value.trim();
  const description = els.descriptionInput.value.trim();
  if (!title) return;

  els.saveBtn.disabled = true;

  try {
    if (state.editingId === null) {
      await createTask(title, description);
    } else {
      await updateTask(state.editingId, { title, description });
    }

    closeModal();
    render();
  } catch (error) {
    showToast(`Ошибка: ${error.message}`);
  } finally {
    els.saveBtn.disabled = false;
  }
});

els.modalBackdrop.addEventListener("click", (event) => {
  if (event.target === els.modalBackdrop) closeModal();
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && !els.modalBackdrop.classList.contains("hidden")) {
    closeModal();
  }
});

loadTasks();
