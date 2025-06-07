from QLNHATRO.RentalManagementApplication.Repository.AdvertisementRepository import AdvertisementRepository

from QLNHATRO.RentalManagementApplication.Repository.RoomRepository import RoomRepository
from QLNHATRO.RentalManagementApplication.backend.model.Advertisement import Advertisement


class AdvertisementService:

    @staticmethod
    def create_advertisement(room_id: int, description: str, image_path: str, preferences: str):
        # Tạo dict data đúng với khóa mà Advertisement __init__ mong đợi
        data = {
            "RoomID": room_id,
            "description": description,
            "priority": preferences,
            "image_path": image_path
            # Nếu cần ad_id (update) hoặc created_at, có thể thêm ở đây
        }
        ad = Advertisement(data)
        AdvertisementRepository.save_advertisement(ad)
        return ad

    @staticmethod
    def get_all_advertised_rooms_for_view():
        rooms = RoomRepository.get_all_rooms()
        ads = AdvertisementRepository.get_all_advertisements()
        data = []

        for idx, ad in enumerate(ads, 1):
            matched_room = next((r for r in rooms if r["id"] == ad.room_id), None)
            if matched_room:
                landlord_id = matched_room.get("id_chutro")
                from QLNHATRO.RentalManagementApplication.Repository.LandlordRepository import LanlordRepository
                landlord_name = LanlordRepository.get_landlord_name_by_id(landlord_id)
                data.append({
                    "STT": idx,
                    "Tên chủ trọ": landlord_name,
                    "Tên phòng": matched_room["ten_phong"],
                    "Diện tích phòng": f"{matched_room['dien_tich']} m²",
                    "Giá phòng": f"{matched_room['gia_phong']:,} VNĐ",
                    "Mô tả": ad.description,
                    "Ưu tiên": ad.priority,
                    "id_room": matched_room["id"]
                })
        return data
