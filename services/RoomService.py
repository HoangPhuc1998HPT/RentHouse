from typing import List, Dict

from RentalManagementApplication.Repository.InvoiceRepository import InvoiceRepository
from RentalManagementApplication.Repository.RoomRepository import RoomRepository
from RentalManagementApplication.Repository.TenantRepository import TenantRepository
from RentalManagementApplication.frontend.Component.ErrorDialog import ErrorDialog
from RentalManagementApplication.frontend.Component.SuccessDialog import SuccessDialog


class RoomService:

    @staticmethod
    def get_all_rooms():
        """
        Lấy danh sách phòng (dành cho Admin), đồng thời bổ sung trường 'STT'.
        Trả về list[dict] với các key:
          - STT
          - room_id
          - room_name
          - room_style
          - landlord_name
          - tenant_name
          - address
        """
        raw_rooms = RoomRepository.get_all_rooms()
        if not raw_rooms:
            print("[RoomService] Không có dữ liệu phòng từ DB, trả về danh sách rỗng.")
            return []

        # Thêm trường STT (số thứ tự) cho mỗi phòng
        result = []
        for idx, room in enumerate(raw_rooms, start=1):
            # Tạo một dict mới, giữ nguyên các key gốc và thêm 'STT'
            room_with_stt = {
                "STT": idx,
                "room_id": room.get("room_id", ""),
                "room_name": room.get("room_name", ""),
                "room_style": room.get("room_style", ""),
                "landlord_name": room.get("landlord_name", ""),
                "tenant_name": room.get("tenant_name") or "",  # nếu None thì để chuỗi rỗng
                "address": room.get("address", "")
            }
            result.append(room_with_stt)

        return result

    @staticmethod
    def get_room_by_id(room_id):
        """Lấy thông tin phòng theo id"""
        return RoomRepository.get_room_by_id(room_id)

    @staticmethod
    def update_room_tenant(room_id, tenant_id):
        """Cập nhật người thuê cho phòng"""
        return RoomRepository.update_room_tenant(room_id, tenant_id)

    '''Đã kiểm tra đồng bộ và chuẩn hóa'''
    @staticmethod
    def handle_data_for_room_list_page(landlord_id: int) -> List[Dict]:
        """
        Trả về list[dict] với mỗi dict có đầy đủ các key:
          - stt         : số thứ tự
          - id_room     : RoomID
          - ten_phong   : RoomName
          - nguoi_thue  : Fullname của tenant ('' nếu trống)
          - gia         : RoomPrice
          - so_dien     : CurrentElectricityNum
          - so_nuoc     : CurrentWaterNum
          - hoa_don     : trạng thái hóa đơn mới nhất ('Đã thanh toán' / 'Chưa thanh toán')
        """
        raw_rooms = RoomRepository.get_all_room_by_landlord(landlord_id)
        room_list: List[Dict] = []

        for idx, room in enumerate(raw_rooms, start=1):
            # Lấy tên người thuê
            tenant_name = ""
            if room.tenant_id:
                tenant = TenantRepository.get_tenant_by_id(room.tenant_id)
                tenant_name = tenant.fullname if tenant else ""

            # Lấy trạng thái hóa đơn gần nhất
            latest_invoice = InvoiceRepository.get_latest_invoice_by_room(room.room_id)
            invoice_status = latest_invoice.status if latest_invoice else "Chưa thanh toán"

            room_list.append({
                "stt": idx,
                "id_room": room.room_id,
                "ten_phong": room.room_name,
                "nguoi_thue": tenant_name,
                "gia": room.room_price,
                "so_dien": room.current_electricity_num,
                "so_nuoc": room.current_water_num,
                "hoa_don": invoice_status
            })

        return room_list

    '''Đã kiểm tra đồng bộ và chuẩn hóa'''
    @staticmethod
    def handle_data_for_create_new_room(id_landlord, room_create_data) -> bool:
        # (nếu cần) gắn lại id_landlord vào trong room_create_data
        room_create_data["id_landlord"] = id_landlord
        return RoomRepository.create_new_room(room_create_data)

    @staticmethod
    def collect_data_room(id_landlord: int, room_data: dict) -> dict:
        """
        room_data phải có thêm:
          free_wifi, parking, air_conditioner, fridge, washing_machine,
          security, television, kitchen, floor, has_loft,
          bathroom, balcony, furniture, pet_allowed
        """
        room_data["id_landlord"] = id_landlord
        return room_data

    @staticmethod
    def collect_data_create_room(id_landlord,room_name, number_people, address, type_room
    ,status,other_infor,area, price_rent,electric_price, water_price, num_electric, num_water):
        room_create_data = {
            'id_landlord': id_landlord,
            'room_name': room_name,
            'number_people': number_people,
            'address': address,
            'type_room': type_room,
            'status': status,
            'other_infor': other_infor,
            'area': area,
            'price_rent': price_rent,
            'electric_price': electric_price,
            'water_price': water_price,
            'num_electric': num_electric,
            'num_water': num_water
        }

        return room_create_data

    @staticmethod
    def handle_data_for_room_home(room_id):
        data_room_home = RoomRepository.get_data_for_handle_room_home(room_id)
        new_data = {}
        '''
            'current_electricity':356,
            'current_water':20,
            'electricity_price':3800,
            'water_price':100000,
            'old_electricity': 256,
            'old_water': 256,
            'old_electricity_price':3800,
            'old_water_price': 100000,
        '''
        percent_grow_num_electricity = RoomService.percent_two_num(data_room_home['current_electricity'], data_room_home['old_electricity'])
        percent_grow_num_water = RoomService.percent_two_num(data_room_home['current_water'],data_room_home['old_water'])
        percent_grow_electricity_price = RoomService.percent_two_num(data_room_home['electricity_price'],data_room_home['old_electricity'])
        percent_grow_water_price = RoomService.percent_two_num(data_room_home['water_price'],data_room_home['old_water_price'])

        new_data['current_electricity'] = str(data_room_home['current_electricity'])+" KWH"
        new_data['current_water'] = str(data_room_home['current_water']) + " m³"
        new_data['electricity_price'] = str(data_room_home['electricity_price']) + " VNĐ/KWH"
        new_data['water_price'] = str(data_room_home['water_price']) + " VNĐ/m³"

        new_data['percent_grow_num_electricity'] = str(percent_grow_num_electricity) + " %"
        new_data['percent_grow_num_water'] = str(percent_grow_num_water) + " %"
        new_data['percent_grow_electricity_price'] = str(percent_grow_electricity_price) + " %"
        new_data['percent_grow_water_price'] = str(percent_grow_water_price) + " %"

        return  new_data

    @staticmethod
    def percent_two_num(a,b):
        percent = (a - b)/a
        percent = percent*100
        return round(percent,2)

    @staticmethod
    def get_translated_room_info(room_id):
        """Chuyển đổi key tiếng Anh → tiếng Việt để dùng trong giao diện RoomsInfor"""
        row = RoomRepository.get_data_for_handle_room_infor(room_id)  # dữ liệu thô
        if not row:
            return {}

        def yes_no_meaning(value, content):
            return content if str(value) == "1" or value == 1 else "Không"

        # Xử lý các tiện ích riêng biệt
        row["HasLoft"] = yes_no_meaning(row.get("HasLoft"), "Có gác lửng")
        row["Bathroom"] = yes_no_meaning(row.get("Bathroom"), "Có phòng tắm riêng")
        row["Kitchen"] = yes_no_meaning(row.get("Kitchen"), "Có nhà bếp")
        row["Balcony"] = yes_no_meaning(row.get("Balcony"), "Có ban công")
        row["Furniture"] = yes_no_meaning(row.get("Furniture"), "Có nội thất")
        row["PetAllowed"] = yes_no_meaning(row.get("PetAllowed"), "Cho phép thú cưng")

        # Thiết bị điện
        appliances = {
            "Điều hòa": row.get("AirConditioner"),
            "Máy giặt": row.get("WashingMachine"),
            "Tủ lạnh": row.get("Fridge"),
            "Tivi": row.get("Television"),
            "Bảo vệ": row.get("Security"),
        }
        row["appliances"] = ", ".join([name for name, v in appliances.items() if str(v) == "1"])

        # Tiện ích
        utilities = {
            "Wifi miễn phí": row.get("FreeWifi"),
            "Chỗ để xe": row.get("Parking"),
        }
        row["utilities"] = ", ".join([name for name, v in utilities.items() if str(v) == "1"])

        # Mapping hiển thị
        mapping = {
            "RoomName": "Tên phòng",
            "Address": "Địa chỉ",
            "RoomType": "Loại phòng",
            "Status": "Trạng thái",
            "Area": "Diện tích",

            "Floor": "Tầng",
            "HasLoft": "Gác lửng",
            "Bathroom": "Phòng tắm",
            "Kitchen": "Nhà bếp",
            "Balcony": "Ban công",
            "Furniture": "Nội thất cơ bản",

            "CurrentElectricityNum": "Số điện",
            "CurrentWaterNum": "Số nước",
            "RoomPrice": "Giá thuê",
            "Deposit": "Tiền đặt cọc",
            "ElectricityPrice": "Giá điện",
            "WaterPrice": "Giá nước",
            "InternetPrice": "Internet",
            "GarbageServicePrice": "Phí rác",
            "OtherFees": "Phí khác",
            "PetAllowed": "Thú cưng",

            "MaxTenants": "Số người tối đa",
            "RentalDate": "Ngày có thể thuê",
            "Description": "Mô tả",

            "appliances": "Thiết bị điện",
            "utilities": "Tiện ích",

            "Fullname": "Chủ trọ",
            "PhoneNumber": "SĐT",
            "Email": "Địa chỉ mail"
        }

        translated = {}
        for en_key, vi_key in mapping.items():
            if en_key in row:
                value = row[en_key]

                # Nếu DB trả None, mặc định thành chuỗi rỗng

                if value is None:
                    value = ""

                if isinstance(value, float):
                    value = f"{value:.1f}"
                elif isinstance(value, int):
                    value = f"{value:,}"
                elif isinstance(value, str):
                    value = value.strip()

                # Thêm đơn vị hiển thị
                if en_key == "Area":
                    value += " m²"
                elif en_key == "CurrentWaterNum":
                    value += " m³"
                elif en_key == "CurrentElectricityNum":
                    value += " KWH"
                elif en_key in ["RoomPrice"]:
                    value += " VNĐ/tháng"
                elif en_key in ["Deposit"]:
                    value += " VNĐ"
                elif en_key in ["ElectricityPrice", "InternetPrice", "WaterPrice", "GarbageServicePrice","OtherFees"]:
                    value += " VNĐ"

                translated[vi_key] = value

        return translated

    @staticmethod
    def get_data_send_to_update_tenant_rent_room(room_id, tenant_id):
        is_update = RoomRepository.update_room_tenant(room_id, tenant_id)
        if is_update:
            SuccessDialog.show_success("Cập nhật người thuê thành công!", '')
            #print("[RoomService] Cập nhật thành công.")
            return True
        else:
            ErrorDialog.show_error("Cập nhật người thuê không thành công!", '')
            #print("[RoomService] Cập nhật không thành công.")
            return False

    @staticmethod
    def get_list_room_by_id_landlord(id_landlord):
        """Lấy danh sách phòng theo id chủ trọ"""
        return RoomRepository.get_list_room_by_id_landlord(id_landlord)

    @staticmethod
    def get_room_monthly_stats(room_id):
        return RoomRepository.get_room_monthly_stats(room_id)
