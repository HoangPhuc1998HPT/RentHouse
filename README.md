This is a school project about Rental Management Application

Project Structure:
- UI Design: PyQt5/PyQt6
- Database: SQLite
- Code Structure: MVC Model
- Naming Convetion:
  - File name: UpperCaseEachLetter
  - Functions: lower_case_each_letter 
- dev-only folder (development branch): This folder is only for creating testing data in development



-----------------------

Hiệu chỉnh truy vấn CSDL từ các truy xuất
ấu trúc MVC (Model-View-Controller):

Model:
  Quản lý dữ liệu.
  Đại diện cấu trúc dữ liệu của đối tượng và logic nghiệp vụ.
View:
  Hiển thị giao diện người dùng.
  Không chứa logic nghiệp vụ hoặc dữ liệu trực tiếp.
Controller:
  Nhận đầu vào từ View, xử lý thông qua Model, và trả kết quả về lại View.
  Không chứa logic phức tạp, thường chỉ gọi hàm từ Service.

Vậy theo cấu trúc thưc mục MVC như thế nào?
 ----------------------------------
Quy tắc KẾT NỐI giữa các lớp
UI chỉ biết Controller. Controller chỉ biết Service. Service chỉ biết Repository. Repository chỉ biết Database.
Data chỉ truyền xuống theo một chiều. Nếu muốn callback/result, luôn dùng giá trị trả về (không callback ngược dòng).
Không bao giờ để UI hoặc Controller truy cập trực tiếp DB hoặc model data thô.
Tách biệt clear mapping giữa field của UI và DB (service chịu trách nhiệm).
--------------------------
API tối ưu, hạn chế lỗi và hiệu suất
Tất cả method CRUD nên return rõ ràng: thành công/trả về object, thất bại trả None/raise lỗi custom.
Hàm update chỉ cho phép update field hợp lệ, reject các field không đúng (an toàn cho DB).
Validate đầu vào ở UI (format), Service (logic), Repository (integrity).
Transaction rollback nếu có lỗi ở Repository, đảm bảo không gây leak connection.
Sử dụng connection pooling hoặc context manager cho DB để tránh leak resource, tối ưu hiệu suất.
Luôn log lỗi đầy đủ ở từng tầng, trả về lỗi rõ ràng cho UI xử lý.
Chỉ SELECT field thực sự cần cho màn hình đó (không dùng SELECT * cho mọi query), giúp tối ưu IO.
Nếu cần join nhiều bảng, để ở tầng Service hoặc Repository, không làm ở UI.

Model:
Chỉ lưu logic dữ liệu, không chứa logic xử lý.
Đặt thuộc tính trùng DB.
Repository:
Chỉ truy cập DB, không xử lý logic nghiệp vụ hoặc mapping phức tạp.
Tách biệt hoàn toàn khỏi tầng View, chỉ trả về object Model hoặc dict chuẩn hóa.
Nếu cần validate, trả về lỗi rõ ràng.
Service:
Chỉ xử lý nghiệp vụ, validate, mapping field, tổng hợp nhiều nguồn dữ liệu.
Không truy cập trực tiếp DB hay nhận input/raw từ UI.
Trả về object/model/dict đã xử lý sạch sẽ.
Controller:
Chỉ nhận dữ liệu đã validate, mapping giữa View và Service.
Không xử lý business logic hay truy cập DB.
View/UI:
Chỉ quản lý giao diện, không truy cập DB.
Không trực tiếp validate business logic (chỉ validate UI).
Gọi Controller khi cần thực thi tác vụ.
Database Layer:
Đóng gói kết nối, rollback, transaction, cursor/ORM (nếu có).
Không được dùng trực tiếp ngoài Repository.
-----------------------
Quy tắc KẾT NỐI giữa các lớp:
UI chỉ biết Controller. Controller chỉ biết Service. Service chỉ biết Repository. Repository chỉ biết Database.
Data chỉ truyền xuống theo một chiều. Nếu muốn callback/result, luôn dùng giá trị trả về (không callback ngược dòng).
Không bao giờ để UI hoặc Controller truy cập trực tiếp DB hoặc model data thô.
Tách biệt clear mapping giữa field của UI và DB (service chịu trách nhiệm)
API tối ưu, hạn chế lỗi và hiệu suất:
Tất cả method CRUD nên return rõ ràng: thành công/trả về object, thất bại trả None/raise lỗi custom.
Hàm update chỉ cho phép update field hợp lệ, reject các field không đúng (an toàn cho DB).
Validate đầu vào ở UI (format), Service (logic), Repository (integrity).
Transaction rollback nếu có lỗi ở Repository, đảm bảo không gây leak connection.
Sử dụng connection pooling hoặc context manager cho DB để tránh leak resource, tối ưu hiệu suất.
Luôn log lỗi đầy đủ ở từng tầng, trả về lỗi rõ ràng cho UI xử lý.
Chỉ SELECT field thực sự cần cho màn hình đó (không dùng SELECT * cho mọi query), giúp tối ưu IO.
Nếu cần join nhiều bảng, để ở tầng Service hoặc Repository, không làm ở UI.