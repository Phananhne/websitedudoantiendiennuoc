import datetime
import re
import os
import io

import numpy as np
from mysql.connector import cursor
from sklearn.neighbors import KNeighborsRegressor
import pandas as pd
import unicodedata
from fastapi import FastAPI, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, HTTPException, Form, Depends, Cookie, Response
from passlib.handlers.bcrypt import bcrypt
from pydantic import BaseModel, constr, EmailStr, ValidationError
from PIL import Image
from fastapi.security import OAuth2PasswordBearer
import mysql.connector
import boto3
from fastapi import Depends, HTTPException, status
from starlette.responses import FileResponse, JSONResponse, RedirectResponse, HTMLResponse, Response
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from transformers import GPT2LMHeadModel, GPT2Tokenizer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
app = FastAPI()
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (not recommended for production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'qlytiennuoc',
    'connection_timeout': 30,  # Adjust the timeout value as needed
}

# Mount static files directory
app.mount("/templates", StaticFiles(directory="templates"), name="templates")
templates = Jinja2Templates(directory="templates")
# Biến global để kiểm tra trạng thái đăng nhập
logged_in = False
current_user = None
# Định nghĩa các tuyến đường (endpoints) cho ứng dụng
@app.get("/")
async def read_root():
    return FileResponse("templates/main.html")

# Load GPT-2 model and tokenizer at the application level
model = GPT2LMHeadModel.from_pretrained("gpt2")
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

# Password validation function
def validate_password(password: str):
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")

    if not password[0].isupper():
        raise ValueError("Password must start with an uppercase letter")

    special_chars = set("!@#$%^&*()_-+=<>?/[]{}|")
    if not any(char in special_chars for char in password):
        raise ValueError("Password must contain at least one special character")

# Registration user model
class RegisterUser(BaseModel):
    username: str
    password: constr(min_length=8)
    email: EmailStr

# Hash password function
def hash_password(password: str) -> str:
    hashed_password = bcrypt.hash(password.encode('utf-8'))
    return hashed_password

# Save user to database function
def save_to_databasee(user):
    db = mysql.connector.connect(**DATABASE_CONFIG)
    query = "INSERT INTO `user` (`Name`, `Password`, `Email`) VALUES (%s, %s, %s);"

    try:
        validate_password(user['password'])
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    hashed_password = hash_password(user['password'])
    val = [(user['username'], hashed_password, user['email'])]
    mycursor = db.cursor()
    for item in val:
        mycursor.execute(query, item)
    db.commit()
    db.close()

# Registration endpoints
@app.get("/register")
async def register_page():
    return FileResponse("templates/Registerr.html")

@app.post("/register")
async def register_page(register_user: RegisterUser):
    save_to_databasee(register_user.dict())
    return JSONResponse(content={"message": "User registered successfully"}, status_code=201)
# Text generation endpoint
@app.post("/generate/")
async def generate_text(prompt: str):
    input_ids = tokenizer.encode(prompt, return_tensors="pt")
    output = model.generate(input_ids, max_length=50, num_return_sequences=1)
    generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
    return {"generated_text": generated_text}

# Save to database function for bill data
def save_to_database(data):
    db = mysql.connector.connect(**DATABASE_CONFIG)
    query = "INSERT INTO `bill` (`KH`, `DC`, `ID`, `chi_so_cu`, `chi_so_moi`, `KL_tieu_thu`, `tien_nuoc`, `tong_cong`, `ky_thang`,`nam`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,%s);"
    val = [(data['KH'], data['DC'], data['ID'], data['chi_so_cu'],
            data['chi_so_moi'], data['KL_tieu_thu'], data['tien_nuoc'],
            data['tong_cong'], data['ky_thang'], data['nam'])]
    mycursor = db.cursor()
    for item in val:
        mycursor.execute(query, item)
    db.commit()
    db.close()
@app.get("/index")
async def read_root():
    if not logged_in:
        # Nếu chưa đăng nhập, chuyển hướng đến trang đăng nhập
        return FileResponse("templates/Loginn.html")
    else:
        # Nếu đã đăng nhập, hiển thị trang index
        return FileResponse("templates/index.html")

# Image upload and text extraction endpoint
# Assuming you have a function to check whether the data already exists in the database
def check_existing_data(data):
    query = "SELECT * FROM `bill` WHERE `ID` = %s AND `chi_so_cu` = %s AND `chi_so_moi` = %s AND `KL_tieu_thu` = %s AND `tien_nuoc` = %s AND `tong_cong` = %s AND `ky_thang` = %s AND `nam` = %s"
    val = (
        data['ID'], data['chi_so_cu'], data['chi_so_moi'], data['KL_tieu_thu'],
        data['tien_nuoc'], data['tong_cong'], data['ky_thang'], data['nam']
    )
    mycursor = db.cursor()
    mycursor.execute(query, val)  # Execute with the entire tuple
    result = mycursor.fetchall()
    db.commit()
    return bool(result)
@app.post("/upload-bill/")
async def upload_bill(file: UploadFile = None):
    if not file:
        raise HTTPException(status_code=400, detail="File not provided")

    image_data = await file.read()
    image = Image.open(io.BytesIO(image_data))

    current_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    filename = f"{current_time}.jpg"
    upload_directory = 'upload'

    if not os.path.exists(upload_directory):
        os.makedirs(upload_directory)

    image_path = os.path.join(upload_directory, filename)
    image.save(image_path)

    text = extract_text_from_image(image_path)
    text = remove_accents(text)
    data = process_text(text)
    # save_to_database(data)
    if not check_existing_data(data):
        # If data does not exist, save to the database
        save_to_database(data)
    else:
        print("Data already exists in the database. Skipping save.")
    return {"text": data}


# Process text function for bill data
def process_text(text):
    # Using regular expressions to extract needed information
    data = {}

    # Extracting KH (might be empty in this sample)
    kh_match = re.search(r'KH:\s*(\S+)?', text)
    data['KH'] = kh_match.group(1) if kh_match and kh_match.group(1) else "N/A"

    # Extracting DC (address)
    dc_match = re.search(r'DC:\s*(.*?)(?=\n)', text)
    data['DC'] = dc_match.group(1).strip() if dc_match else "N/A"

    # Extracting ID
    id_match = re.search(r'ID:\s*(\d+)', text)
    data['ID'] = id_match.group(1) if id_match else "N/A"

    # Extracting chi so cu and chi so moi
    chi_so_cu_match = re.search(r'Chi so cu:\s*(\d+)', text)
    chi_so_moi_match = re.search(r'Chi so moi:\s*(\d+)', text)
    data['chi_so_cu'] = chi_so_cu_match.group(1) if chi_so_cu_match else "N/A"
    data['chi_so_moi'] = chi_so_moi_match.group(1) if chi_so_moi_match else "N/A"

    # Extracting KL tieu thu
    kl_match = re.search(r'KL tieu thu:\s*(\d+)', text)
    data['KL_tieu_thu'] = kl_match.group(1) if kl_match else "N/A"

    # Extracting tien nuoc
    tien_nuoc_match = re.search(r'Tien nuoc:\s*([\d,]+)', text)
    data['tien_nuoc'] = tien_nuoc_match.group(1).replace(',', '') if tien_nuoc_match else "N/A"

    # Extracting tong cong
    tong_cong_match = re.search(r'Tong cong\s*([\d,]+)', text)
    data['tong_cong'] = tong_cong_match.group(1).replace(',', '') if tong_cong_match else "N/A"

    # Extracting tu ngay and den ngay
    ky_thang_match = re.search(r'Ky thang:\s*(\d+)', text)
    data['ky_thang'] = ky_thang_match.group(1) if ky_thang_match else "N/A"

    nam_match = re.search(r'Nam:\s*(\d+)', text)
    data['nam'] = nam_match.group(1) if nam_match else "N/A"

    return data

# Remove accents from text function
def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

# Extract text from image using AWS Textract
def extract_text_from_image(image_path):
    client = boto3.client('textract', region_name='us-east-1')
    with open(image_path, 'rb') as file:
        img_data = file.read()
    response = client.detect_document_text(Document={'Bytes': img_data})
    detected_text = ''
    for item in response['Blocks']:
        if item['BlockType'] == 'LINE':
            detected_text += item['Text'] + '\n'
    return detected_text
#==========================================================================
db = mysql.connector.connect(user='root', password='123456', host='localhost', database='qlytiennuoc')
@app.get("/login")
async def login_page():
    return FileResponse("templates/Loginn.html")

@app.post("/login")
def login_user(name: str = Form(...), password: str = Form(...)):
    # Mở kết nối đến cơ sở dữ liệu

    # Tạo đối tượng cursor
    mycursor = db.cursor()

    # Nhập giá trị email và mật khẩu từ người dùng
    user_name = name
    user_password = password

    # Thực hiện truy vấn SELECT với giá trị email nhập từ người dùng
    code2 = "SELECT `password` FROM `user` WHERE `name` = %s"
    mycursor.execute(code2, (user_name,))

    # Lấy kết quả từ truy vấn
    result = mycursor.fetchone()

    # Kiểm tra xem email có tồn tại hay không và so sánh mật khẩu
    if result:
        db_password = result[0]
        # So sánh mật khẩu đã nhập với mật khẩu đã mã hóa từ cơ sở dữ liệu
        if bcrypt.verify(user_password.encode('utf-8'), db_password):
            # Nếu đăng nhập thành công, cập nhật biến logged_in
            global logged_in
            logged_in = True
            current_user = user_name
            return {"message": "Login successful"}
        else:
            return {"message": "login unsuccessful"}
    else:
        print("Name not found.")

    # Đóng kết nối đến cơ sở dữ liệu
    db.close()
#=================================================

# Assume you have functions to calculate total users, total orders, total data, and total for the current month.
def calculate_total_users():
    try:
        db = mysql.connector.connect(**DATABASE_CONFIG)
        query = "SELECT COUNT(DISTINCT ID) FROM `bill`"
        cursor = db.cursor()
        cursor.execute(query)
        result = cursor.fetchone()
        return str(result[0])
    finally:
        cursor.close()
        db.close()
def calculate_total_orders():
    try:
        db = mysql.connector.connect(**DATABASE_CONFIG)
        query = "SELECT COUNT(*) FROM `bill`"
        cursor = db.cursor()
        cursor.execute(query)
        result = cursor.fetchone()
        return str(result[0])
    finally:
        cursor.close()
        db.close()
def list_users():
    try:
        db = mysql.connector.connect(**DATABASE_CONFIG)
        query = "SELECT * FROM `user`"
        cursor = db.cursor(dictionary=True)  # Set dictionary=True to return results as dictionaries
        cursor.execute(query)
        users = cursor.fetchall()
        return users
    finally:
        cursor.close()
        db.close()
def list_bills():
    try:
        db = mysql.connector.connect(**DATABASE_CONFIG)
        query = "SELECT * FROM `bill`"
        cursor = db.cursor(dictionary=True)  # Set dictionary=True to return results as dictionaries
        cursor.execute(query)
        bills = cursor.fetchall()
        return bills
    finally:
        cursor.close()
        db.close()
#============================================================================
logged_ad = False
@app.get("/admin_login")
async def admin_login_page(request: Request):
    return FileResponse("Admin/Loginn.html")
@app.post("/admin_login")
async def admin_login(request: Request, name: str = Form(...), password: str = Form(...)):
    form_data = await request.form()
    name = form_data.get('name')
    password = form_data.get('password')
    print(name)
    print(password)
    # Kiểm tra xem username và password có trùng khớp với admin không
    if name == "admin" and password == "Anh@123456":
        # Nếu trùng khớp, cập nhật biến logged_in cho admin
        global logged_ad
        logged_ad = True
        return {"message": "Admin login successful"}
    else:
        return {"message": "Admin login unsuccessful"}
@app.get("/admin", response_class=HTMLResponse)
async def admin(request: Request):
    # Nếu đã đăng nhập, hiển thị trang admin
    total_user = calculate_total_users()
    total_order = calculate_total_orders()
    list_user = list_users()
    list_bill = list_bills()
    if not logged_ad:
        # Nếu chưa đăng nhập, chuyển hướng đến trang đăng nhập
        return templates.TemplateResponse("Admin/Loginn.html", {"request": request})
    else:
        return templates.TemplateResponse("Admin/index.html",
                                          {"request": request, "total_user": total_user, "total_order": total_order,
                                           "list_user": list_user, "list_bill": list_bill})
#=================================================
def execute_query(query):
    try:
        connection = mysql.connector.connect(**DATABASE_CONFIG)
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        connection.close()
from sklearn.model_selection import train_test_split
# Định nghĩa route để đọc dữ liệu từ bảng bill
# /read_data endpoint with authentication dependency
@app.get("/read_data", response_class=HTMLResponse)
async def table(request: Request):
    # Thực hiện truy vấn để lấy dữ liệu từ bảng bill
    query = "SELECT * FROM `bill`"
    data = execute_query(query)

    # Check if data is empty
    if not data:
        raise ValueError("No data retrieved from the database.")

    # Lấy các heading từ tên cột trong kết quả truy vấn
    headings = tuple(data[0].keys())

    # Assuming 'data' is a list of dictionaries
    data_df = pd.DataFrame(data)

    # Check if the DataFrame is empty
    if data_df.empty:
        raise ValueError("DataFrame is empty. Check your data loading and processing.")

    # Convert relevant columns to numeric types
    data_df['ky_thang'] = pd.to_numeric(data_df['ky_thang'], errors='coerce')
    data_df['nam'] = pd.to_numeric(data_df['nam'], errors='coerce')

    # Find the maximum year
    max_year = data_df['nam'].max()

    # Find the maximum month within the maximum year
    max_month = data_df.loc[data_df['nam'] == max_year, 'ky_thang'].max()

    # Filter the DataFrame for the maximum month and year
    max_month_data = data_df[(data_df['ky_thang'] == max_month) & (data_df['nam'] == max_year)]
    # Check if max_month_data is empty
    if max_month_data.empty:
        # Print information for debugging
        print(f"No data for the maximum month ({max_month}) and year ({max_year}).")
        print("Data for debugging:")
        print(data_df)
        raise ValueError("No data for the maximum month and year.")

    # Tạo DataFrame cho việc dự đoán
    data_to_predict = pd.DataFrame({
        'ID': max_month_data['ID'],
        'ky_thang': max_month_data['ky_thang'] + 1,  # Tháng tiếp theo
        'nam': max_month_data['nam'],
        'chi_so_cu': max_month_data['chi_so_moi']  # Chỉ số mới của tháng lớn nhất
    })
    X = data_df[['ID', 'ky_thang', 'nam', 'chi_so_cu']]
    y = data_df['tien_nuoc']

    # Check if there are samples in the training data
    if X.shape[0] == 0 or y.shape[0] == 0:
        raise ValueError("No samples found in the training data. Check your data processing.")

    # Specify the percentage for the test set (adjust as needed)
    test_size = 0.2

    # Ensure that there are enough samples for both training and testing
    if X.shape[0] < 2 or y.shape[0] < 2:
        raise ValueError("Not enough samples for training and testing. Check your data.")

    # Split the data into training and testing sets
    try:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
    except ValueError as e:
        print(f"Error during train-test split: {e}")
        raise

    # Xây dựng mô hình KNN với số lân cận K
    K = 12
    model = KNeighborsRegressor(n_neighbors=K)

    # Check if there are samples for training
    if X_train.shape[0] == 0 or y_train.shape[0] == 0:
        raise ValueError("No samples found for model training. Check your data.")

    model.fit(X_train, y_train)

    # Dự đoán mức sử dụng nước cho tháng 10/2023
    # Trong hàm Python
    # Trong hàm Python
    predicted_consume = model.predict(data_to_predict)
    return templates.TemplateResponse(
        "phantich.html",
        {"request": request, "headings": headings, "data": data, "predicted_consume": predicted_consume}
    )
@app.get("/get_user_details/{stt}")
async def get_user_details(stt: int):
    # Perform a database query or use any other method to fetch user details
    query = f"SELECT * FROM `user` WHERE ID = {stt}"
    user_details = execute_query(query)

    # Check if user details were found
    if not user_details:
        raise HTTPException(status_code=404, detail="User details not found")

    return user_details[0]
#==========================================================
@app.delete("/delete/{id}/{chi_so_cu}")
def delete_item(id: int, chi_so_cu: int):
    try:
        db = mysql.connector.connect(**DATABASE_CONFIG)
        query = "DELETE FROM `bill` WHERE ID = %s AND chi_so_cu = %s LIMIT 1;"
        val = (id, chi_so_cu)
        mycursor = db.cursor()
        mycursor.execute(query, val)
        db.commit()
        db.close()
        return {"id": id, "chi_so_cu": chi_so_cu, "message": "Item deleted successfully"}
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if db.is_connected():
            db.close()

# ====================================================================
@app.put("/update/{stt}/")
def update_item(stt: int, data: dict):
    try:
        db = mysql.connector.connect(**DATABASE_CONFIG)
        query = "UPDATE user SET Name = %s, Password = %s, Email = %s WHERE STT = %s"
        val = (data["name"], data["password"], data["email"], stt)
        mycursor = db.cursor()
        mycursor.execute(query, val)
        db.commit()
        db.close()
        return {"id": stt, **data, "message": "Item updated successfully"}
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))
#============================================================
# Simulate a user database (replace this with your actual user database)
user_database = {
    "phthi2611@gmail.com": {"password": "hashed_password"},
}

def send_reset_email(email: str):
    # Trong thực tế, bạn nên thực hiện việc gửi email reset mật khẩu ở đây
    print(f"Reset email sent to {email}")

def change_user_password(email: str, new_password: str):
    # Trong thực tế, bạn nên thực hiện việc thay đổi mật khẩu trong cơ sở dữ liệu ở đây
    user_database[email]["password"] = new_password
    print(f"Password changed for {email}")

@app.post("/forgot-password")
def forgot_password(email: str = Form(...)):
    # Kiểm tra xem email có tồn tại trong cơ sở dữ liệu không
    if email in user_database:
        # Gửi email reset mật khẩu (simulated)
        send_reset_email(email)
        # Trả về thông báo thành công (simulated)
        return {"message": "Reset email sent successfully"}
    else:
        # Nếu email không tồn tại, raise HTTPException với mã lỗi 404
        raise HTTPException(status_code=404, detail="Email not found")

@app.post("/change-password")
def change_password(email: str = Form(...), new_password: str = Form(...)):
    # Kiểm tra xem email có tồn tại trong cơ sở dữ liệu không
    if email in user_database:
        # Thay đổi mật khẩu (simulated)
        change_user_password(email, new_password)
        # Trả về thông báo thành công (simulated)
        return {"message": "Password changed successfully"}
    else:
        # Nếu email không tồn tại, raise HTTPException với mã lỗi 404
        raise HTTPException(status_code=404, detail="Email not found")
#====================================================================
@app.get("/chatbox")
async def chat_bot():
    return FileResponse("templates/chatbox.html")