document.addEventListener("DOMContentLoaded", () => {
  new Swiper(".testimonials-swiper", {
    loop: true,
    slidesPerView: 1,
    spaceBetween: 20,

    pagination: {
      el: ".swiper-pagination",
      clickable: true,
    },

    navigation: {
      nextEl: ".swiper-button-next",
      prevEl: ".swiper-button-prev",
    },
  });
});