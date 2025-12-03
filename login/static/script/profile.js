const uploadForm = document.getElementById("uploadForm");
const previewFrame = document.getElementById("preview");
const sidebar = document.getElementById("sidebar");
const menuToggle = document.getElementById("menuToggle");
const menuOverlay = document.getElementById("menuOverlay");

function showPreview(fileUrl) {
  previewFrame.src = fileUrl;
  previewFrame.style.display = "block";
  localStorage.setItem("lastUploadedFile", fileUrl);
}

if (previewFrame) {
  const lastFile = localStorage.getItem("lastUploadedFile");
  if (lastFile) {
    showPreview(lastFile);
  }
}

if (uploadForm && previewFrame) {
  uploadForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const fileInput = uploadForm.querySelector("input[name=document]");
    if (!fileInput.files.length) {
      alert("Будь ласка, оберіть файл перед завантаженням.");
      return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append("document", file);

    try {
      const res = await fetch("http://127.0.0.1:8000/upload", {
        method: "POST",
        body: formData
      });

      if (!res.ok) {
        throw new Error("Upload failed");
      }

      const data = await res.json();
      const fileUrl = `http://127.0.0.1:8000/uploads/${data.filename}`;

      showPreview(fileUrl);
    } catch (error) {
      console.error(error);
      alert("Сталася помилка при завантаженні. Спробуйте ще раз.");
    }
  });
}

const toggleMenu = () => {
  if (!sidebar || !menuOverlay) return;
  sidebar.classList.toggle("sidebar--open");
  menuOverlay.classList.toggle("menu-overlay--visible");
  document.body.classList.toggle("menu-open");
};

menuToggle?.addEventListener("click", toggleMenu);
menuOverlay?.addEventListener("click", () => {
  if (sidebar?.classList.contains("sidebar--open")) {
    toggleMenu();
  }
});

window.addEventListener("resize", () => {
  if (window.innerWidth > 768 && sidebar) {
    sidebar.classList.remove("sidebar--open");
    menuOverlay?.classList.remove("menu-overlay--visible");
    document.body.classList.remove("menu-open");
  }
});