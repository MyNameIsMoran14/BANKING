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

document.addEventListener("DOMContentLoaded", () => {
    const userMenu = document.querySelector('.user-menu');
    const dropdown = document.querySelector('.dropdown-content');
    
    if (userMenu && dropdown) {
        let menuTimeout;
        
        userMenu.addEventListener('mouseenter', () => {
            clearTimeout(menuTimeout);
            dropdown.style.display = 'block';
        });
        
        userMenu.addEventListener('mouseleave', () => {
            // Задержка перед закрытием
            menuTimeout = setTimeout(() => {
                dropdown.style.display = 'none';
            }, 300); // 300ms задержка
        });
        
        dropdown.addEventListener('mouseenter', () => {
            clearTimeout(menuTimeout);
        });
        
        dropdown.addEventListener('mouseleave', () => {
            dropdown.style.display = 'none';
        });
    }
});

// Автоматическое скрытие flash-сообщений через 2 секунды
document.addEventListener("DOMContentLoaded", () => {
    const flashes = document.querySelectorAll(".flash");
    
    if (flashes.length > 0) {
        flashes.forEach(flash => {
            // Через 2 секунды добавляем класс для анимации исчезновения
            setTimeout(() => {
                flash.classList.add("hide");
                
                // Через 0.5 секунды удаляем элемент из DOM
                setTimeout(() => {
                    if (flash.parentElement) {
                        flash.remove();
                    }
                }, 500);
                
            }, 2000); // 2 секунды
        });
    }
});

let activeRoleMenu = null;

function toggleRoleMenu(button) {
    const dropdown = button.parentElement.querySelector('.role-dropdown-content');
    const menuId = dropdown.id;
    
    // Закрываем предыдущее открытое меню
    if (activeRoleMenu && activeRoleMenu !== dropdown) {
        activeRoleMenu.style.display = 'none';
    }
    
    // Переключаем текущее меню
    if (dropdown.style.display === 'block') {
        dropdown.style.display = 'none';
        activeRoleMenu = null;
    } else {
        dropdown.style.display = 'block';
        activeRoleMenu = dropdown;
    }
}

// Закрываем меню при клике вне его
document.addEventListener('click', function(event) {
    if (activeRoleMenu && !event.target.closest('.role-dropdown')) {
        activeRoleMenu.style.display = 'none';
        activeRoleMenu = null;
    }
});

// Закрываем меню при выборе опции
document.addEventListener('submit', function(event) {
    if (event.target.closest('.role-dropdown-content form')) {
        if (activeRoleMenu) {
            activeRoleMenu.style.display = 'none';
            activeRoleMenu = null;
        }
    }
});
document.addEventListener("DOMContentLoaded", () => {
    const hoverItems = document.querySelectorAll('.hover-modal');

    hoverItems.forEach(item => {
        const popup = item.querySelector('.hover-popup');
        let popupTimeout;

        const showPopup = () => {
            clearTimeout(popupTimeout);
            item.classList.add('active');
        };

        const hidePopup = () => {
            popupTimeout = setTimeout(() => {
                item.classList.remove('active');
            }, 300);
        };

        item.addEventListener('mouseenter', showPopup);
        item.addEventListener('mouseleave', hidePopup);

        popup.addEventListener('mouseenter', showPopup);
        popup.addEventListener('mouseleave', hidePopup);
    });
});