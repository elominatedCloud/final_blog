const toggleBtn = document.querySelector(".navbar_toggleBtn");
const menu = document.querySelector(".head-menu");
const link = document.querySelector(".head-link");
const nav_category = document.querySelector(".nav-sidebar");

toggleBtn.addEventListener("click", () => {
  menu.classList.toggle("active");
  link.classList.toggle("active");
  nav_category.classList.toggle("active");
});
