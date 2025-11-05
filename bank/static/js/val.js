document.getElementById("creditForm").addEventListener("submit", function(e) {
    const amount = document.getElementById("amount").value;
    const phone = document.getElementById("phone").value;
    const name = document.getElementById("name").value;
    const phonePattern = /^\+7\s?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}$/;

    if (!phonePattern.test(phone)) {
        alert("Введите корректный номер телефона, например +7 (999) 123-45-67");
        e.preventDefault();
        return;
    }

    if (!name.trim()) {
        alert("Введите ваше имя");
        e.preventDefault();
        return;
    }

    if (parseFloat(amount) < 1) {
        alert("Сумма кредита должна быть больше нуля");
        e.preventDefault();
        return;
    }
});