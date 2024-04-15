function registerUser() {
    var username = document.getElementById("username").value;
    var password = document.getElementById("password").value;
    var email = document.getElementById("email").value;

    // Reset error messages
    document.getElementById('username-error').innerText = "";
    document.getElementById('password-error').innerText = "";
    document.getElementById('email-error').innerText = "";

    if (username.trim() === "") {
    document.getElementById('username-error').innerText = "Vui lòng nhập tên đăng nhập.";
    return;
    }

    // Kiểm tra mật khẩu
    var passwordPattern = /^(?=.*[A-Z])(?=.*[!@#$%^&*])(?=.{8,})/;
    if (!passwordPattern.test(password)) {
        document.getElementById('password-error').innerText = "Mật khẩu phải có ít nhất 8 ký tự, chữ cái đầu viết in hoa và có chứa ký tự đặc biệt.";
        // Adjust margin to move the form down

        return;
    }

    // Kiểm tra định dạng email
    var emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailPattern.test(email)) {
        document.getElementById('email-error').innerText = "Định dạng email không hợp lệ.";
        return;
    }


    const data = {
        username: username,
        password: password,
        email: email,
        // Thêm các trường dữ liệu khác nếu cần thiết
    };

    fetch('http://127.0.0.1:8000/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log('Success:', data);
            // Sau khi đăng ký thành công, chuyển hướng sang trang đăng nhập
            window.location.href = 'http://127.0.0.1:8000/login';
        })
        .catch(error => {
            console.error('Error:', error);

        });
}
function togglePasswordVisibility() {
    var passwordInput = document.getElementById("password");
    var eyeIcon = document.getElementById("eyeIcon");

    if (passwordInput.type === "password") {
        passwordInput.type = "text";
        eyeIcon.innerHTML = "&#128064;"; // Biểu tượng mắt đóng
    } else {
        passwordInput.type = "password";
        eyeIcon.innerHTML = "&#128065;"; // Biểu tượng mắt mở
    }
}

