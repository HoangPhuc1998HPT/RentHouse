-- ============================================
-- File: init_db.sql
-- Mục đích: Tạo schema (các bảng + trigger) cho ./rent_house_database.sqlite
-- ============================================

-- Tắt tạm khóa khóa ngoại để có thể DROP TABLE theo thứ tự bất kỳ
PRAGMA foreign_keys = OFF;

-----------------------------
-- Nếu đã có trigger / table tồn tại cũ, xóa hết đi
-- (đảm bảo lần chạy sau sẽ không báo lỗi "already exists")
-----------------------------

DROP TRIGGER IF EXISTS trg_after_insert_invoice;
DROP TRIGGER IF EXISTS trg_after_update_invoice;
DROP TRIGGER IF EXISTS trg_after_delete_invoice;
DROP TRIGGER IF EXISTS trg_update_room_electric_water;

DROP TABLE IF EXISTS LandlordAnalytics;
DROP TABLE IF EXISTS Invoices;
DROP TABLE IF EXISTS Rooms;
DROP TABLE IF EXISTS Tenants;
DROP TABLE IF EXISTS Landlords;
DROP TABLE IF EXISTS Users;
DROP TABLE IF EXISTS Admins;
DROP TABLE IF EXISTS advertisements;
DROP TABLE IF EXISTS maintenance_requests;
DROP TABLE IF EXISTS Notifications;
DROP TABLE IF EXISTS tenant_analytics;
DROP TABLE IF EXISTS RoomAnalytics;
DROP TABLE IF EXISTS InvoiceAnalytics;


-----------------------------
-- Bật lại PRAGMA foreign_keys
-----------------------------
PRAGMA foreign_keys = ON;


-- User's table
CREATE TABLE IF NOT EXISTS Users (
    UserID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    Username TEXT UNIQUE NOT NULL,
    Password TEXT NOT NULL,
    Role TEXT NOT NULL CHECK (Role IN ('admin', 'landlord', 'tenant')),
    IsActive INTEGER DEFAULT 0,
    CreatedAt TEXT DEFAULT CURRENT_TIMESTAMP
);



-- Admins table
CREATE TABLE IF NOT EXISTS Admins (
    AdminID INTEGER PRIMARY KEY AUTOINCREMENT,
    Fullname TEXT,
    UserID INTEGER,
    FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE
);

INSERT INTO Users (Username, Password, Role, IsActive) VALUES
('admin', 'admin', 'admin', 1);

-- Landlord table
CREATE TABLE Landlords (
    LandlordID    INTEGER PRIMARY KEY AUTOINCREMENT,
    Fullname      TEXT        NULL,
    Birth         TEXT        NULL,  -- 'YYYY-MM-DD'
    CCCD          TEXT        NULL,
    Gender        TEXT        NULL,
    JobTitle      TEXT        NULL,
    MaritalStatus TEXT CHECK (MaritalStatus IN ('Married','Single','Divorced','Other')) NULL,
    Email         TEXT        NULL,
    PhoneNumber   TEXT        NULL,
    HomeAddress   TEXT        NULL,
    UserID        INTEGER     NULL,
    CreatedAt     TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Tenants table
CREATE TABLE Tenants (
    TenantID       INTEGER PRIMARY KEY AUTOINCREMENT,
    Fullname       TEXT    NULL,
    Birth          TEXT    NULL,
    CCCD           TEXT    NULL,
    Gender         TEXT    NULL,
    JobTitle       TEXT    NULL,
    MaritalStatus  TEXT CHECK (MaritalStatus IN ('Married','Single','Divorced','Other')) NULL,
    Email          TEXT    NULL,
    PhoneNumber    TEXT    NULL,
    HomeAddress    TEXT    NULL,
    RentStartDate  TEXT    NULL,
    RentEndDate    TEXT    NULL,
    UserID         INTEGER NULL,
    CreatedAt      TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Rooms table
CREATE TABLE IF NOT EXISTS Rooms (
    RoomID INTEGER PRIMARY KEY AUTOINCREMENT,
    RoomName TEXT,
    Address TEXT,
    RoomType TEXT,              -- Loại phòng: ví dụ "Phòng trọ trong dãy trọ"
    Status TEXT,                -- Trạng thái: "Còn trống" hoặc "Đã thuê"
    Area REAL,                  -- Diện tích (m²)

    Floor INTEGER DEFAULT 0,              -- Tầng
    HasLoft INTEGER DEFAULT 0,            -- Gác lửng: 0 hoặc 1
    Bathroom INTEGER DEFAULT 0,              -- Phòng tắm: "Riêng", "Chung",...
    Kitchen INTEGER DEFAULT 0,              -- Nhà bếp: mô tả
    Furniture INTEGER DEFAULT 0,             -- Nội thất cơ bản
    Balcony INTEGER DEFAULT 0,          -- Ban công   -- Có ban công

    FreeWifi INTEGER DEFAULT 0,             -- Wifi miễn phí 1
    Parking INTEGER DEFAULT 0,              -- Chổ đậu xe  1
    AirConditioner INTEGER DEFAULT 0,       -- Máy điều hòa 1
    Fridge INTEGER DEFAULT 0,               -- Tủ lạnh 1
    WashingMachine INTEGER DEFAULT 0,       -- Máy giặt 1
    Security INTEGER DEFAULT 0,             -- Có bảo vệ 1
    Television INTEGER DEFAULT 0,           -- Có tivi 1

    PetAllowed INTEGER DEFAULT 0,           -- Thú cưng: " 0: không cho phép", "1: cho phép"
    -- giá cả
    RoomPrice REAL,            -- Giá thuê phòng
    ElectricityPrice REAL,      -- Giá điện
    WaterPrice REAL,           -- Giá nước
    InternetPrice REAL,        -- Giá internet
    OtherFees TEXT,            -- Phí khác: "Phí vệ sinh: 20000 VNĐ"
    GarbageServicePrice REAL,  -- Giá dịch vụ rác thải
    Deposit REAL,              -- Tiền cọc // load vào sau
    --  Chỉ số điện
    CurrentElectricityNum INTEGER, -- Số điện hiện tại, được cập nhật khi tạo phòng và tạo Invoice
    CurrentWaterNum INTEGER,       -- Số nước hiện tại, được cập nhật khi tạo phòng và tạo Invoice
    -- Thông tin thêm
    MaxTenants INTEGER,         -- Số người tối đa
    RentalDate Date,            -- Ngày cho thuê (dạng YYYY-MM-DD) được update khi có người thuê trọ
    Description TEXT,           -- Mô tả thêm

    TenantID INTEGER,          -- Người thuê hiện tại (nullable)
    LandlordID INTEGER NOT NULL ,        -- Chủ trọ
    CreatedAt TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (TenantID) REFERENCES Tenants(TenantID) ON DELETE SET NULL,
    FOREIGN KEY (LandlordID) REFERENCES Landlords(LandlordID) ON DELETE CASCADE
);
-- CurrentE or CUrrentW khi tạo phòng đã phải nhập, vậy khi hoạt động chỉ cần cập nhật cho nó ở Invoices
-- Lưu ý: PreElectricityNum là ở Invoices là số điện hiện tại tức là CurentElectricityNum ở Rooms
    -- Còn CurrentElectroniccityNum ở Invoices là số điện được nhập vào ở tháng hiện tại
-- Invoices table
CREATE TABLE IF NOT EXISTS Invoices (
    InvoiceID INTEGER PRIMARY KEY AUTOINCREMENT,
    RoomID INTEGER,
    TenantID INTEGER,
    LandlordID INTEGER,

    issue_date TEXT NOT NULL,  -- ISO format 'YYYY-MM-DD'              -- Ngày tạo hóa đơn

    CurrElectric INTEGER,   -- Số điện hiện tại được lấy từ form tạo hóa đơn
    CurrWater INTEGER,      -- Số nước hiện tại được lấy từ form tạo hóa đơn
    PreElectric  INTEGER, -- Số điện trước đó (CurrentElectricityNum ở Rooms)
    PreWater  INTEGER,    -- Số nước trước đó (CurrentWaterNum ở Rooms)

    -- Số điện đã sử dụng (CurrElectric - PreElectricityNum)
    --ElectricPrice REAL,   -- Lấy giá từ Rooms
    --WaterPrice REAL,      -- Lấy giá từ Rooms
    --RoomPrice REAL,       -- Lấy giá từ Rooms
    -- InternetFee REAL,     -- Lấy giá từ Rooms
    -- GarbageFee REAL,      -- Lấy giá từ Rooms

    TotalElectronicCost REAL,   -- Current - PreElectricityNum
    TotalWaterCost REAL,    -- Current - PreWaterNum
    TotalRoomPrice REAL,    -- Giá thuê phòng từ Rooms
    InternetFee REAL,       -- Giá internet từ Rooms
    TotalGarbageFee REAL,   -- Giá dịch vụ rác thải từ Rooms
    TotalAnotherFee REAL,   -- Phí khác từ Rooms

    Discount REAL DEFAULT 0,

    Status TEXT DEFAULT 'Chưa thanh toán'CHECK (Status IN ('Đã thanh toán', 'Chưa thanh toán')),

    FOREIGN KEY (RoomID) REFERENCES Rooms(RoomID),
    FOREIGN KEY (TenantID) REFERENCES Tenants(TenantID),
    FOREIGN KEY (LandlordID) REFERENCES Landlords(LandlordID)
);


-- QuangCao table
CREATE TABLE IF NOT EXISTS advertisements (
    ad_id INTEGER PRIMARY KEY AUTOINCREMENT,
    RoomID INTEGER NOT NULL,
    description TEXT,
    priority TEXT,
    image_path TEXT DEFAULT 'default_image.png',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (RoomID) REFERENCES rooms(RoomID) ON DELETE CASCADE
);


-- MaintenanceRequests table
CREATE TABLE IF NOT EXISTS maintenance_requests (
    request_id INTEGER PRIMARY KEY AUTOINCREMENT,
    TenantID INTEGER NOT NULL,
    RoomID INTEGER NOT NULL,

    issue_type TEXT NOT NULL,           -- VD: "Điện", "Nước", "Cấu trúc", v.v.
    urgency_level TEXT NOT NULL,        -- VD: "Bình thường", "Khẩn cấp"
    description TEXT NOT NULL,          -- Nội dung mô tả chi tiết

    contact_phone TEXT,    -- Số điện thoại liên hệ/ nếu không có sẽ tự load số điện thoại của người tạo
    available_time TEXT,   -- Thời gian thuận tiện liên hệ

    discovery_date TEXT,                -- Ngày phát hiện sự cố
    image_path TEXT,                    -- Đường dẫn ảnh minh họa (nếu có)

    status TEXT DEFAULT 'Pending' CHECK (status IN ('Pending', 'In Progress', 'Resolved', 'Đang xử lý', 'Đã hoàn thành')),
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (TenantID) REFERENCES tenants(TenantID),
    FOREIGN KEY (RoomID) REFERENCES rooms(RoomID)
);


-- Notifications table
CREATE TABLE IF NOT EXISTS Notifications (
    NotificationID INTEGER PRIMARY KEY AUTOINCREMENT,
    UserID INTEGER,
    Content TEXT,
    IsRead INTEGER DEFAULT 0,
    CreatedAt TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
);


-- AnalystLanlord table
CREATE TABLE IF NOT EXISTS LandlordAnalytics (
    AnalyticsID           INTEGER PRIMARY KEY AUTOINCREMENT,
    LandlordID            INTEGER NOT NULL,
    month                 TEXT    NOT NULL,
    year                  INTEGER NOT NULL,
    TotalIncome           REAL    DEFAULT 0.0,
    NumberOfRentedRooms   INTEGER DEFAULT 0,
    AveragePrice          REAL    DEFAULT 0.0,
    GrowthRate            REAL    DEFAULT 0.0,
    FOREIGN KEY (LandlordID) REFERENCES Landlords(LandlordID) ON DELETE CASCADE
  );



-- AnalystTenant table
CREATE TABLE IF NOT EXISTS tenant_analytics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    TenantID INTEGER NOT NULL,
    month INTEGER CHECK (month BETWEEN 1 AND 12),
    year INTEGER CHECK (year >= 2000),
    electricity_cost REAL DEFAULT 0,
    water_cost REAL DEFAULT 0,
    total_cost REAL GENERATED ALWAYS AS (electricity_cost + water_cost) VIRTUAL,
    due_date TEXT,
    FOREIGN KEY (TenantID) REFERENCES tenants(TenantID),
    UNIQUE (TenantID, month, year)
);


CREATE TABLE IF NOT EXISTS RoomAnalytics (
    idRoomAnalytics INTEGER PRIMARY KEY AUTOINCREMENT,
    RoomID INTEGER,
    Month INTEGER CHECK (Month BETWEEN 1 AND 12),
    Year INTEGER CHECK (Year >= 2000),
    ElectricityCost REAL DEFAULT 0,     -- Tổng tiền điện
    WaterCost REAL DEFAULT 0,           -- Tổng tiền nước
    TotalCost REAL GENERATED ALWAYS AS (ElectricityCost + WaterCost) VIRTUAL,
    FOREIGN KEY (RoomID) REFERENCES Rooms(RoomID) ON DELETE CASCADE,
    UNIQUE (RoomID, Month, Year)
);

-- InvoiceAnalytics table
CREATE TABLE IF NOT EXISTS InvoiceAnalytics (
    InvoiceID INTEGER PRIMARY KEY AUTOINCREMENT,
    LandlordID INTEGER,
    RoomID INTEGER,
    TenantID INTEGER,
    InvoiceDate TEXT,
    RoomPrice REAL,
    ElectricityUsed INTEGER,
    ElectricityCost REAL,
    WaterUsed INTEGER,
    WaterCost REAL,
    InternetFee REAL,
    GarbageFee REAL,
    OtherFee REAL,
    TotalCost REAL,
    PaymentStatus TEXT,
    FOREIGN KEY (InvoiceID) REFERENCES Invoices(InvoiceID)
);

-----Trigger---------
--------------------------------------------------------------------------------
-- 1. Trigger AFTER INSERT trên Invoices (khi tạo hóa đơn mới)
--------------------------------------------------------------------------------
CREATE TRIGGER IF NOT EXISTS trg_after_insert_invoice
AFTER INSERT ON Invoices
BEGIN
  -- (1) Tính giá trị "inc" (doanh thu) và "room_price" từ các cột có sẵn
  --     inc = total tiền tenant phải trả
  --     room_price = TotalRoomPrice (giá thuê phòng của bản ghi này)
  --
  --    Lưu ý: NEW.TotalRoomPrice, NEW.TotalElectronicCost, ... chính là cột đã có trong Invoices

  -- Nếu chưa có record tương ứng (LandlordID, tháng, năm) thì INSERT mới
  INSERT INTO LandlordAnalytics (
    LandlordID,
    month,
    year,
    TotalIncome,
    NumberOfRentedRooms,
    AveragePrice,
    GrowthRate
  )
  SELECT
    NEW.LandlordID,
    strftime('%m', NEW.issue_date) AS m,
    strftime('%Y', NEW.issue_date) AS y,
    -- inc: tổng doanh thu thực tế
    (NEW.TotalRoomPrice
     + COALESCE(NEW.TotalElectronicCost,   0)
     + COALESCE(NEW.TotalWaterCost,       0)
     + COALESCE(NEW.InternetFee,          0)
     + COALESCE(NEW.TotalGarbageFee,      0)
     + COALESCE(NEW.TotalAnotherFee,      0)
     - COALESCE(NEW.Discount,             0)
    ) AS inc,
    1 AS rented_rooms,
    -- Giá thuê phòng để tính trung bình: chính là TotalRoomPrice
    NEW.TotalRoomPrice AS avg_price,
    0.0 AS growth
  WHERE NOT EXISTS (
    SELECT 1
    FROM LandlordAnalytics
    WHERE LandlordID = NEW.LandlordID
      AND month = m
      AND year  = y
  );

  -- Nếu đã có dòng cho (LandlordID, tháng, năm), thì UPDATE (cộng dồn)
  UPDATE LandlordAnalytics
  SET
    TotalIncome = TotalIncome
                  + (NEW.TotalRoomPrice
                     + COALESCE(NEW.TotalElectronicCost, 0)
                     + COALESCE(NEW.TotalWaterCost,     0)
                     + COALESCE(NEW.InternetFee,        0)
                     + COALESCE(NEW.TotalGarbageFee,    0)
                     + COALESCE(NEW.TotalAnotherFee,    0)
                     - COALESCE(NEW.Discount,           0)
                    ),
    NumberOfRentedRooms = NumberOfRentedRooms + 1,
    AveragePrice =
      -- Tính trung bình mới: (giá trung bình cũ * số phòng cũ + giá phòng mới) / (số phòng cũ + 1)
      CASE
        WHEN NumberOfRentedRooms + 1 > 0 THEN
          ((AveragePrice * NumberOfRentedRooms)
           + NEW.TotalRoomPrice
          ) / (NumberOfRentedRooms + 1)
        ELSE
          0.0
      END
  WHERE LandlordID = NEW.LandlordID
    AND month = strftime('%m', NEW.issue_date)
    AND year  = strftime('%Y', NEW.issue_date);
END;

--------------------------------------------------------------------------------
-- 2. Trigger AFTER DELETE trên Invoices (khi xóa hóa đơn)
--------------------------------------------------------------------------------
CREATE TRIGGER IF NOT EXISTS trg_after_delete_invoice
AFTER DELETE ON Invoices
BEGIN
  -- Trừ ngược phần doanh thu = inc_old
  -- đếm lại số phòng và tính lại trung bình (nếu còn >0)
  UPDATE LandlordAnalytics
  SET
    TotalIncome = TotalIncome
                  - (OLD.TotalRoomPrice
                     + COALESCE(OLD.TotalElectronicCost, 0)
                     + COALESCE(OLD.TotalWaterCost,     0)
                     + COALESCE(OLD.InternetFee,        0)
                     + COALESCE(OLD.TotalGarbageFee,    0)
                     + COALESCE(OLD.TotalAnotherFee,    0)
                     - COALESCE(OLD.Discount,           0)
                    ),
    NumberOfRentedRooms = NumberOfRentedRooms - 1,
    AveragePrice = CASE
      WHEN NumberOfRentedRooms - 1 > 0 THEN
        -- Tính lại trung bình: ((avg_cũ * số_cũ) - giá_phòng_xóa) / (số_cũ - 1)
        ((AveragePrice * NumberOfRentedRooms) - OLD.TotalRoomPrice)
        / (NumberOfRentedRooms - 1)
      ELSE
        0.0
    END
  WHERE LandlordID = OLD.LandlordID
    AND month = strftime('%m', OLD.issue_date)
    AND year  = strftime('%Y', OLD.issue_date);

  -- Nếu đã không còn phòng nào trong tháng đó (NumberOfRentedRooms <= 0), xóa luôn dòng
  DELETE FROM LandlordAnalytics
  WHERE LandlordID = OLD.LandlordID
    AND month = strftime('%m', OLD.issue_date)
    AND year  = strftime('%Y', OLD.issue_date)
    AND NumberOfRentedRooms <= 0;
END;

CREATE TRIGGER IF NOT EXISTS trg_after_update_invoice
AFTER UPDATE ON Invoices
BEGIN
  -- Tính inc cũ và inc mới
  -- inc_old = OLD.TotalRoomPrice + OLD.TotalElectronicCost + … - OLD.Discount
  -- inc_new = NEW.TotalRoomPrice + NEW.TotalElectronicCost + … - NEW.Discount

  UPDATE LandlordAnalytics
  SET
    TotalIncome = TotalIncome
                  -- trừ inc cũ, cộng inc mới
                  - (OLD.TotalRoomPrice
                     + COALESCE(OLD.TotalElectronicCost, 0)
                     + COALESCE(OLD.TotalWaterCost,     0)
                     + COALESCE(OLD.InternetFee,        0)
                     + COALESCE(OLD.TotalGarbageFee,    0)
                     + COALESCE(OLD.TotalAnotherFee,    0)
                     - COALESCE(OLD.Discount,           0)
                    )
                  + (NEW.TotalRoomPrice
                     + COALESCE(NEW.TotalElectronicCost, 0)
                     + COALESCE(NEW.TotalWaterCost,     0)
                     + COALESCE(NEW.InternetFee,        0)
                     + COALESCE(NEW.TotalGarbageFee,    0)
                     + COALESCE(NEW.TotalAnotherFee,    0)
                     - COALESCE(NEW.Discount,           0)
                    ),
    AveragePrice = CASE
      WHEN NumberOfRentedRooms > 0 THEN
        -- Loại bỏ giá cũ, cộng giá mới vào trung bình
        ((AveragePrice * NumberOfRentedRooms)
         - OLD.TotalRoomPrice
         + NEW.TotalRoomPrice
        ) / NumberOfRentedRooms
      ELSE
        0.0
    END
  WHERE LandlordID = NEW.LandlordID
    AND month = strftime('%m', NEW.issue_date)
    AND year  = strftime('%Y', NEW.issue_date);
END;

-- --------------------------------------
-----------Data Sample-------------------
-- --------------------------------------

-------------------------------------------------------------------------------
--                           S E E D   D A T A
-------------------------------------------------------------------------------

-- Insert sample Users
--password123
INSERT INTO Users (Username, Password, Role, IsActive) VALUES
('landlord1', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'landlord', 1),
('landlord2', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'landlord', 1),
('tenant1', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'tenant', 1),
('tenant2', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'tenant', 1),
('tenant3', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'tenant', 1),
('tenant4', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'tenant', 1);


-- Insert sample Admins
INSERT INTO Admins (Fullname, UserID) VALUES
('Nguyễn Văn Admin', 1);

-- Insert sample Landlords
INSERT INTO Landlords (Fullname, Birth, CCCD, Gender, JobTitle, MaritalStatus, Email, PhoneNumber, HomeAddress, UserID) VALUES
('Trần Văn Chủ', '1980-05-15', '123456789012', 'Nam', 'Kinh doanh bất động sản', 'Married', 'tranvanchu@email.com', '0901234567', '123 Đường Nguyễn Văn Cừ, Q.5, TP.HCM', 2),
('Lê Thị Lan', '1975-08-20', '987654321098', 'Nữ', 'Đầu tư bất động sản', 'Single', 'lethilan@email.com', '0912345678', '456 Đường Lê Lợi, Q.1, TP.HCM', 3);

-- Insert sample Tenants
INSERT INTO Tenants (Fullname, Birth, CCCD, Gender, JobTitle, MaritalStatus, Email, PhoneNumber, HomeAddress, RentStartDate, RentEndDate, UserID) VALUES
('Nguyễn Thị Hoa', '1995-03-10', '111222333444', 'Nữ', 'Nhân viên văn phòng', 'Single', 'nguyenthihoa@email.com', '0987654321', '789 Đường Điện Biên Phủ, Q.3, TP.HCM', '2024-01-01', '2024-12-31', 4),
('Võ Minh Tuấn', '1992-07-25', '555666777888', 'Nam', 'Lập trình viên', 'Single', 'vominhtuan@email.com', '0976543210', '321 Đường Cách Mạng Tháng 8, Q.10, TP.HCM', '2024-02-01', '2025-01-31', 5),
('Phạm Thị Mai', '1990-12-05', '999888777666', 'Nữ', 'Kế toán', 'Married', 'phamthimai@email.com', '0965432109', '654 Đường Hoàng Văn Thụ, Q.Tân Bình, TP.HCM', '2024-03-01', '2025-02-28', 6),
('Hoàng Văn Nam', '1988-09-18', '444333222111', 'Nam', 'Giáo viên', 'Single', 'hoangvannam@email.com', '0954321098', '987 Đường Phan Xích Long, Q.Phú Nhuận, TP.HCM', NULL, NULL, 7);

-- Insert sample Rooms
INSERT INTO Rooms (
    RoomName, Address, RoomType, Status, Area, Floor, HasLoft, Bathroom, Kitchen, Furniture, Balcony,
    FreeWifi, Parking, AirConditioner, Fridge, WashingMachine, Security, Television, PetAllowed,
    RoomPrice, ElectricityPrice, WaterPrice, InternetPrice, GarbageServicePrice, Deposit,
    CurrentElectricityNum, CurrentWaterNum, MaxTenants, RentalDate, Description, TenantID, LandlordID
) VALUES
-- Phòng của chủ trọ 1
('Phòng 101', '123 Đường Nguyễn Văn Cừ, Q.5, TP.HCM', 'Phòng trọ trong dãy trọ', 'Đã thuê', 25.0, 1, 0, 1, 1, 1, 1,
 1, 1, 1, 1, 0, 1, 1, 0,
 3500000, 3500, 25000, 150000, 50000, 7000000,
 120, 15, 2, '2024-01-01', 'Phòng đầy đủ tiện nghi, gần trường đại học', 1, 1),

('Phòng 102', '123 Đường Nguyễn Văn Cừ, Q.5, TP.HCM', 'Phòng trọ trong dãy trọ', 'Đã thuê', 20.0, 1, 1, 1, 0, 1, 0,
 1, 1, 0, 1, 1, 1, 0, 0,
 2800000, 3500, 25000, 150000, 50000, 5600000,
 95, 12, 1, '2024-02-01', 'Phòng có gác lửng, thích hợp cho sinh viên', 2, 1),

('Phòng 201', '123 Đường Nguyễn Văn Cừ, Q.5, TP.HCM', 'Phòng trọ trong dãy trọ', 'Đã thuê', 30.0, 2, 0, 1, 1, 1, 1,
 1, 1, 1, 1, 1, 1, 1, 1,
 4200000, 3500, 25000, 150000, 50000, 8400000,
 140, 18, 2, '2024-03-01', 'Phòng rộng rãi, cho phép nuôi thú cưng', 3, 1),

('Phòng 202', '123 Đường Nguyễn Văn Cừ, Q.5, TP.HCM', 'Phòng trọ trong dãy trọ', 'Còn trống', 22.0, 2, 0, 1, 1, 1, 0,
 1, 1, 1, 1, 0, 1, 1, 0,
 3200000, 3500, 25000, 150000, 50000, 6400000,
 85, 10, 2, NULL, 'Phòng mới sửa chữa, sạch sẽ', NULL, 1),

-- Phòng của chủ trọ 2
('Phòng A1', '456 Đường Lê Lợi, Q.1, TP.HCM', 'Studio apartment', 'Còn trống', 35.0, 3, 0, 1, 1, 1, 1,
 1, 1, 1, 1, 1, 1, 1, 0,
 6000000, 4000, 30000, 200000, 80000, 12000000,
 200, 25, 2, NULL, 'Studio cao cấp, view đẹp, trung tâm thành phố', NULL, 2),

('Phòng A2', '456 Đường Lê Lợi, Q.1, TP.HCM', 'Studio apartment', 'Còn trống', 32.0, 3, 0, 1, 1, 1, 1,
 1, 1, 1, 1, 1, 1, 1, 1,
 5500000, 4000, 30000, 200000, 80000, 11000000,
 180, 22, 2, NULL, 'Studio hiện đại, đầy đủ tiện nghi, cho phép thú cưng', NULL, 2);

-- Insert sample Invoices
INSERT INTO Invoices (
    RoomID, TenantID, LandlordID, issue_date,
    CurrElectric, CurrWater, PreElectric, PreWater,
    TotalElectronicCost, TotalWaterCost, TotalRoomPrice, InternetFee, TotalGarbageFee, TotalAnotherFee,
    Discount, Status
) VALUES
-- Hóa đơn tháng 1/2024
(1, 1, 1, '2024-01-31', 150, 18, 120, 15, 105000, 75000, 3500000, 150000, 50000, 0, 0, 'Đã thanh toán'),
(2, 2, 1, '2024-01-31', 120, 14, 95, 12, 87500, 50000, 2800000, 150000, 50000, 0, 0, 'Đã thanh toán'),

-- Hóa đơn tháng 2/2024
(1, 1, 1, '2024-02-29', 180, 21, 150, 18, 105000, 75000, 3500000, 150000, 50000, 0, 100000, 'Đã thanh toán'),
(2, 2, 1, '2024-02-29', 145, 16, 120, 14, 87500, 50000, 2800000, 150000, 50000, 0, 0, 'Đã thanh toán'),
(3, 3, 1, '2024-02-29', 165, 20, 140, 18, 87500, 50000, 4200000, 150000, 50000, 0, 0, 'Đã thanh toán'),

-- Hóa đơn tháng 3/2024
(1, 1, 1, '2024-03-31', 210, 24, 180, 21, 105000, 75000, 3500000, 150000, 50000, 0, 0, 'Chưa thanh toán'),
(2, 2, 1, '2024-03-31', 170, 18, 145, 16, 87500, 50000, 2800000, 150000, 50000, 0, 0, 'Đã thanh toán'),
(3, 3, 1, '2024-03-31', 190, 23, 165, 20, 87500, 75000, 4200000, 150000, 50000, 0, 50000, 'Chưa thanh toán');

-- Update CurrentElectricityNum và CurrentWaterNum trong Rooms theo hóa đơn mới nhất
UPDATE Rooms SET CurrentElectricityNum = 210, CurrentWaterNum = 24 WHERE RoomID = 1;
UPDATE Rooms SET CurrentElectricityNum = 170, CurrentWaterNum = 18 WHERE RoomID = 2;
UPDATE Rooms SET CurrentElectricityNum = 190, CurrentWaterNum = 23 WHERE RoomID = 3;

-- Insert sample Advertisements
INSERT INTO advertisements (RoomID, description, priority, image_path, created_at) VALUES
(4, 'Phòng trọ giá rẻ, gần trường đại học, đầy đủ tiện nghi cơ bản. Liên hệ ngay!', 'Cao', 'room202_ad.jpg', '2024-03-15 10:00:00'),
(5, 'Studio cao cấp trung tâm Q.1, view đẹp, đầy đủ nội thất. Giá thuê hấp dẫn!', 'Rất cao', 'roomA1_ad.jpg', '2024-03-10 15:30:00'),
(6, 'Studio hiện đại, cho phép nuôi thú cưng, gần công viên và trung tâm mua sắm.', 'Trung bình', 'roomA2_ad.jpg', '2024-03-12 09:20:00');

-- Insert sample Maintenance Requests
INSERT INTO maintenance_requests (
    TenantID, RoomID, issue_type, urgency_level, description,
    contact_phone, available_time, discovery_date, image_path, status
) VALUES
(1, 1, 'Điện', 'Khẩn cấp', 'Ổ cắm điện trong phòng bị chập, có mùi khét. Cần sửa chữa gấp.',
 '0987654321', 'Sáng 8-12h, chiều 14-18h', '2024-03-20', 'electric_issue_room101.jpg', 'Pending'),

(2, 2, 'Nước', 'Bình thường', 'Vòi nước trong phòng tắm bị nhỏ giọt, cần thay gokét mới.',
 '0976543210', 'Chiều 13-17h', '2024-03-18', 'water_leak_room102.jpg', 'Đang xử lý'),

(3, 3, 'Cấu trúc', 'Bình thường', 'Cửa phòng bị kẹt, khó đóng mở. Có thể cần điều chỉnh bản lề.',
 '0965432109', 'Tối 18-20h', '2024-03-19', 'door_issue_room201.jpg', 'Đã hoàn thành');

-- Insert sample Notifications
INSERT INTO Notifications (UserID, Content, IsRead, CreatedAt) VALUES
(4, 'Hóa đơn tháng 3/2024 đã được tạo. Vui lòng kiểm tra và thanh toán trước ngày 5/4/2024.', 0, '2024-03-31 08:00:00'),
(5, 'Yêu cầu sửa chữa vòi nước của bạn đang được xử lý. Sẽ có thợ đến sửa trong ngày hôm nay.', 1, '2024-03-18 14:30:00'),
(6, 'Chúc mừng! Yêu cầu sửa chữa cửa phòng của bạn đã được hoàn thành.', 1, '2024-03-19 16:45:00'),
(2, 'Có 1 yêu cầu sửa chữa khẩn cấp từ phòng 101. Vui lòng kiểm tra và xử lý.', 0, '2024-03-20 09:15:00'),
(3, 'Có 2 phòng trống đang được quảng cáo. Kiểm tra hiệu quả quảng cáo trong tuần này.', 0, '2024-03-15 11:00:00');

-- Insert sample Tenant Analytics (sẽ được trigger tự động tính, nhưng có thể thêm dữ liệu mẫu)
INSERT INTO tenant_analytics (TenantID, month, year, electricity_cost, water_cost, due_date) VALUES
(1, 1, 2024, 105000, 75000, '2024-02-05'),
(1, 2, 2024, 105000, 75000, '2024-03-05'),
(1, 3, 2024, 105000, 75000, '2024-04-05'),
(2, 1, 2024, 87500, 50000, '2024-02-05'),
(2, 2, 2024, 87500, 50000, '2024-03-05'),
(2, 3, 2024, 87500, 50000, '2024-04-05'),
(3, 2, 2024, 87500, 50000, '2024-03-05'),
(3, 3, 2024, 87500, 75000, '2024-04-05');

-- Insert sample Room Analytics
INSERT INTO RoomAnalytics (RoomID, Month, Year, ElectricityCost, WaterCost) VALUES
(1, 1, 2024, 105000, 75000),
(1, 2, 2024, 105000, 75000),
(1, 3, 2024, 105000, 75000),
(2, 1, 2024, 87500, 50000),
(2, 2, 2024, 87500, 50000),
(2, 3, 2024, 87500, 50000),
(3, 2, 2024, 87500, 50000),
(3, 3, 2024, 87500, 75000);

-- Thêm một số dữ liệu để test các tháng khác nhau
INSERT INTO Invoices (
    RoomID, TenantID, LandlordID, issue_date,
    CurrElectric, CurrWater, PreElectric, PreWater,
    TotalElectronicCost, TotalWaterCost, TotalRoomPrice, InternetFee, TotalGarbageFee, TotalAnotherFee,
    Discount, Status
) VALUES
-- Hóa đơn tháng 4/2024
(1, 1, 1, '2024-04-30', 240, 27, 210, 24, 105000, 75000, 3500000, 150000, 50000, 0, 0, 'Chưa thanh toán'),
(2, 2, 1, '2024-04-30', 195, 20, 170, 18, 87500, 50000, 2800000, 150000, 50000, 0, 0, 'Chưa thanh toán');

-- Test data cho việc kiểm tra trigger analytics
-- Dữ liệu này sẽ tự động được tính toán thông qua trigger khi insert/update/delete Invoices

PRAGMA foreign_keys = ON;