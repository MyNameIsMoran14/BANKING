function openModal() {
    document.getElementById('loginModal').style.display = 'block';
}
function closeModal() {
    document.getElementById('loginModal').style.display = 'none';
}
// Закрытие при клике вне окна
window.onclick = function(event) {
    const modal = document.getElementById('loginModal');
    if (event.target == modal) {
        modal.style.display = "none";
    }
}
