const shownMessageIds = new Set();

document.addEventListener("DOMContentLoaded", function () {
  const fileInput = document.getElementById("fileInput");
  const fakeButton = document.getElementById("selectImageBtn");
  const fileNameDisplay = document.getElementById("fileNameDisplay");

  if (fakeButton && fileInput) {
    fakeButton.addEventListener("click", () => {
      console.log("✅ 選擇圖片按鈕被點了");
      fileInput.click();
    });

    fileInput.addEventListener("change", () => {
      const file = fileInput.files[0];
      if (file) {
        fileNameDisplay.textContent = file.name;
      } else {
        fileNameDisplay.textContent = "";
      }
    });
  } else {
    console.log("⚠️ 沒有找到按鈕或 file input");
  }

  // 初次載入留言
  loadMessages();
});

document.getElementById("uploadForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    const form = e.target;
    const content = form.content.value;
    const imageFile = form.file.files[0];

    console.log("🧪 content value:", content);

    if (!content || !imageFile) {
      alert("請輸入留言與選擇圖片");
      return;
    }

    // 1. 上傳圖片
    const imageForm = new FormData();
    imageForm.append("file", imageFile);
    const imageRes = await fetch("/api/upload", {
      method: "POST",
      body: imageForm,
    });
    const imageData = await imageRes.json();
    const imageUrl = imageData.url;

    // 2. 送出留言資料
    const res = await fetch("/api/messages", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        content,
        img_url: imageUrl,
      }),
    });

    const data = await res.json();
    if (!res.ok) {
      alert("❌ 送出失敗：" + data.error);
      return;
    }

    alert("✅ 留言成功");
    form.reset();
    document.getElementById("fileNameDisplay").textContent = "";

    // 3. 即時將留言加到最上面
    const container = document.getElementById("messageList");
    const box = document.createElement("div");
    box.className = "message-box";
    box.innerHTML = `
      <p>${content}</p>
      <img src="${imageUrl}" style="max-width: 300px;" />
      <p style="color: gray; font-size: 12px;">剛剛</p>
      <hr />
    `;
    container.prepend(box);
  } catch (err) {
    console.error("❌ 發生錯誤", err);
    alert("❌ 系統錯誤，請稍後再試");
  }
});

async function loadMessages() {
  const res = await fetch("/api/messages");
  const data = await res.json();
  const container = document.getElementById("messageList");

  if (!data.success || !data.data.length) return;

  data.data.forEach((msg) => {
    if (shownMessageIds.has(msg.id)) return;

    const box = document.createElement("div");
    box.className = "message-box";
    box.innerHTML = `
      <p>${msg.content}</p>
      <img src="${msg.img_url}" style="max-width: 300px;" />
      <p style="color: gray; font-size: 12px;">${msg.created_at}</p>
      <hr />
    `;
    container.appendChild(box); // 舊留言照時間順序疊下去
    shownMessageIds.add(msg.id);
  });
}
