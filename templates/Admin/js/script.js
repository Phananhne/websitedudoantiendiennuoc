$("#menu-btn").click(function () {
  $("#menu").toggleClass("password");
});

var maker = document.querySelector("#maker");
var item = document.querySelectorAll(".items li");

function indicator(e) {
  maker.style.top = e.offsetTop + "px";
  maker.style.height = e.offsetHeight + "px";
}

item.forEach((link) => {
  link.addEventListener("click", (e) => {
    indicator(e.target);
  });
});

document.addEventListener("DOMContentLoaded", function () {
  const usersTable = document.getElementById("users");
  const billsTable = document.getElementById("bills");
  const blanksTable = document.getElementById("blanks");

  // Ẩn bảng hóa đơn ban đầu
  billsTable.classList.add("hidden");
  blanksTable.classList.add("hidden");
  // Lấy danh sách các liên kết và thêm sự kiện click cho mỗi liên kết
  const menuLinks = document.querySelectorAll("#menu .items li");
  menuLinks.forEach((link) => {
    link.addEventListener("click", function () {
      // Lấy id của bảng từ thuộc tính data-target
      const targetTableId = this.querySelector("a").getAttribute("data-target");
      // Ẩn tất cả các bảng
      usersTable.classList.add("hidden");
      billsTable.classList.add("hidden");
      blanksTable.classList.add("hidden");
      // Hiển thị bảng tương ứng
      document.getElementById(targetTableId).classList.remove("hidden");
    });
  });
});
$(document).ready(function() {
    // Gửi yêu cầu GET đến endpoint /admin để lấy thông tin total_user
    $.get("/admin", function(data) {
        // Cập nhật giá trị của total_user khi nhận được dữ liệu từ server
        $("#totalUsers").text(data.total_user);
        // Cập nhật giá trị của total_orders khi nhận được dữ liệu từ server
        $("#totalOrder").text(data.total_orders);
        $("#totaldatas").text(data.total_orders);
    });
});
var currentDate = new Date();

// Lấy tháng từ thời gian hiện tại
var currentMonth = currentDate.toLocaleString('default', { month: 'long' });

// Hiển thị tháng trong thẻ h3
document.getElementById('currentMonth').innerHTML = currentMonth;
// JavaScript để sắp xếp bảng
function sortTable(columnIndex) {
    var table, rows, switching, i, x, y, shouldSwitch;
    table = document.getElementById("users");
    switching = true;
    while (switching) {
        switching = false;
        rows = table.getElementsByTagName("tr");
        for (i = 1; i < (rows.length - 1); i++) {
            shouldSwitch = false;
            x = rows[i].getElementsByTagName("td")[columnIndex];
            y = rows[i + 1].getElementsByTagName("td")[columnIndex];
            if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
                shouldSwitch = true;
                break;
            }
        }
        if (shouldSwitch) {
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            switching = true;
        }
    }
}
function sortTable(columnIndex) {
    var table, rows, switching, i, x, y, shouldSwitch;
    table = document.getElementById("bills");
    switching = true;
    while (switching) {
        switching = false;
        rows = table.getElementsByTagName("tr");
        for (i = 1; i < (rows.length - 1); i++) {
            shouldSwitch = false;
            x = rows[i].getElementsByTagName("td")[columnIndex];
            y = rows[i + 1].getElementsByTagName("td")[columnIndex];
            if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
                shouldSwitch = true;
                break;
            }
        }
        if (shouldSwitch) {
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            switching = true;
        }
    }
}
function getUserDetails(userId) {
    if (userId !== undefined) {
        fetch(`/get_user_details/${userId}`)
            .then(response => response.json())
            .then(data => {
                displayUserDetails(data);
            })
            .catch(error => console.error('Error fetching user details:', error));
    }
}
function displayUserDetails(userDetails) {
    // Modify this function to update the UI with the user details as needed
    console.log('User Details:', userDetails);
    // Example: Update a modal, show a popup, etc.
}
document.addEventListener('DOMContentLoaded', function () {
    var deleteButtons = document.querySelectorAll('.delete-btn');
    deleteButtons.forEach(function (button) {
        button.addEventListener('click', function (event) {
            event.preventDefault();

            var rowIndex = this.parentNode.parentNode.getAttribute('data-index');
            var chiSoCu = this.parentNode.parentNode.getAttribute('data-chi-so-cu');

            // Gửi yêu cầu xóa đến endpoint Flask với cả ID và chi_so_cu
            fetch('/delete/' + rowIndex + '/' + chiSoCu, {
                method: 'DELETE',
            })
            .then(response => response.json())
            .then(data => {
                // Xử lý phản hồi từ server, ví dụ: thông báo thành công hoặc hiển thị lỗi
                alert(data.message || data.error);
                // Nếu xóa thành công, cập nhật giao diện người dùng
                if (!data.error) {
                    var deletedIndex = data.id;
                    var deletedRow = document.querySelector('[data-index="' + deletedIndex + '"]');
                    if (deletedRow) {
                        deletedRow.remove();
                    }
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });
});
$(document).ready(function() {
    var originalRowHtml;

    $("#userDetails").on("click", "#updateButton", function() {
        var stt = $(this).closest("tr").data("user-stt");
        var name = $(this).closest("tr").find(".name p").text();
        var email = $(this).closest("tr").find(".email p").text();
        var password = $(this).closest("tr").find(".password p").text();

        var updateForm = `
            <form id="updateForm">
                <input type="hidden" name="stt" value="${stt}">
                Name: <input type="text" name="name" value="${name}"><br>
                Email: <input type="text" name="email" value="${email}"><br>
                Password: <input type="text" name="password" value="${password}"><br>
                <input type="button" value="Update" id="updateSubmitButton">
            </form>
        `;

        originalRowHtml = $(this).closest("tr").html();
        $(this).closest("tr").html(updateForm);
    });

    $("#userDetails").on("click", "#updateSubmitButton", function() {
        var stt = $("input[name='stt']").val();
        var name = $("input[name='name']").val();
        var email = $("input[name='email']").val();
        var password = $("input[name='password']").val();

        $.ajax({
            type: "PUT",
            url: `/update/${stt}/`,
            contentType: "application/json",
            data: JSON.stringify({ name: name, email: email, password: password }),
            success: function(response) {
                alert(response.message);
                var row = $("#userDetails").find(`tr[data-user-stt='${stt}']`);
                row.html(originalRowHtml);
            },
            error: function(error) {
                alert("Error updating item: " + error.responseJSON.detail);
            }
        });
    });
});
