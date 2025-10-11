const provinsiSelect = document.getElementById("provinsiSelect");
const kabupatenSelect = document.getElementById("kabupatenSelect");
const loadDataBtn = document.getElementById("loadDataBtn");
const dataContainer = document.getElementById("dataContainer");
const debugInfo = document.getElementById("debugInfo");

let wilayahData = {};

function getTodayDateString() {
  const now = new Date();
  const wib = new Date(now.getTime() + (7 * 60 * 60 * 1000));
  const y = wib.getFullYear();
  const m = String(wib.getMonth() + 1).padStart(2, '0');
  const d = String(wib.getDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
}

async function loadWilayah() {
  try {
    const res = await fetch("wilayah.json");
    wilayahData = await res.json();
    for (const prov in wilayahData) {
      const opt = document.createElement("option");
      opt.value = prov;
      opt.textContent = prov;
      provinsiSelect.appendChild(opt);
    }
    restoreLastSelection();
  } catch (err) {
    dataContainer.innerHTML = `<div class="error">❌ Gagal memuat wilayah.json</div>`;
  }
}

provinsiSelect.addEventListener("change", () => {
  kabupatenSelect.innerHTML = '<option value="">-- Pilih Kabupaten/Kota --</option>';
  const prov = provinsiSelect.value;
  if (!prov) {
    kabupatenSelect.disabled = true;
    return;
  }
  wilayahData[prov].forEach(kab => {
    const opt = document.createElement("option");
    opt.value = kab;
    opt.textContent = kab;
    kabupatenSelect.appendChild(opt);
  });
  kabupatenSelect.disabled = false;
});

loadDataBtn.addEventListener("click", async () => {
  const prov = provinsiSelect.value;
  const kab = kabupatenSelect.value;
  if (!prov || !kab) {
    alert("Pilih provinsi dan kabupaten/kota terlebih dahulu!");
    return;
  }
  saveSelection(prov, kab);
  await loadData(prov, kab);
});

async function loadData(prov, kab) {
  const fileName = `${prov} ${kab} 10 2025.json`;
  const filePath = `data/${fileName}`;
  dataContainer.innerHTML = `<div class="loading">⏳ Memuat jadwal dari <b>${kab}</b>...</div>`;

  try {
    const res = await fetch(filePath);
    if (!res.ok) throw new Error("Gagal fetch file JSON");
    const json = await res.json();
    const today = getTodayDateString();
    const todayData = json.data[today];
    if (!todayData) {
      dataContainer.innerHTML = `<div class="error">⚠️ Data untuk tanggal ${today} tidak ditemukan.</div>`;
      return;
    }
    renderToday(todayData, json);
  } catch (err) {
    dataContainer.innerHTML = `<div class="error">❌ Gagal memuat file: ${fileName}</div>`;
  }
}

function renderToday(todayData, meta) {
  const keys = [
    ["Imsak", todayData.imsak],
    ["Subuh", todayData.subuh],
    ["Terbit", todayData.terbit],
    ["Dhuha", todayData.dhuha],
    ["Dzuhur", todayData.dzuhur],
    ["Ashar", todayData.ashar],
    ["Maghrib", todayData.maghrib],
    ["Isya", todayData.isya],
  ];

  dataContainer.innerHTML = `
    <div class="info fade">
      <h2>${meta.kabko} — ${meta.prov}</h2>
      <p>${todayData.tanggal}</p>
      <div class="data-display">
        ${keys.map(([k,v]) => `
          <div class="data-item">
            <div class="data-title">${k}</div>
            <div class="data-content">${v}</div>
          </div>`).join("")}
      </div>
    </div>
  `;
}

// 🔖 Simpan pilihan user
function saveSelection(prov, kab) {
  localStorage.setItem("lastProvinsi", prov);
  localStorage.setItem("lastKabupaten", kab);
}

// 🔁 Pulihkan pilihan terakhir
function restoreLastSelection() {
  const lastProv = localStorage.getItem("lastProvinsi");
  const lastKab = localStorage.getItem("lastKabupaten");

  if (lastProv && wilayahData[lastProv]) {
    provinsiSelect.value = lastProv;
    kabupatenSelect.innerHTML = '<option value="">-- Pilih Kabupaten/Kota --</option>';
    wilayahData[lastProv].forEach(kab => {
      const opt = document.createElement("option");
      opt.value = kab;
      opt.textContent = kab;
      kabupatenSelect.appendChild(opt);
    });
    kabupatenSelect.disabled = false;

    if (lastKab) {
      kabupatenSelect.value = lastKab;
      loadData(lastProv, lastKab);
    }
  }
}

window.addEventListener("DOMContentLoaded", loadWilayah);
