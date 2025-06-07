from _datetime import datetime
from typing import List, Dict, Optional, Any

from RentalManagementApplication.Repository.MaintenanceRepository import MaintenanceRepository



class MaintenanceService:


    @staticmethod
    def create_maintenance_request(room_id: int, tenant_id: int, request_data: Dict) -> Dict:
        """
        Tạo yêu cầu bảo trì mới (DB) và trả về kết quả dưới dạng dict:
        {
            'success': bool,
            'message': str,
            'request_id': int (nếu thành công)
        }
        """
        try:
            # 1. Validate tenant_id, room_id
            if not isinstance(room_id, int) or room_id <= 0:
                return {'success': False, 'message': 'Room ID không hợp lệ'}
            if not isinstance(tenant_id, int) or tenant_id <= 0:
                return {'success': False, 'message': 'Tenant ID không hợp lệ'}

            # 2. Kiểm tra các trường bắt buộc trong request_data
            required_fields = ['issue_type', 'urgency_level', 'description']
            for field in required_fields:
                if not request_data.get(field):
                    return {
                        'success': False,
                        'message': f'Thiếu thông tin bắt buộc: {field}'
                    }

            # 3. Kiểm tra giá trị hợp lệ
            valid_issue_types = ['Điện', 'Nước', 'Cấu trúc', 'Điều hòa', 'Khác']
            valid_urgency_levels = ['Khẩn cấp', 'Bình thường', 'Thấp']
            if request_data['issue_type'] not in valid_issue_types:
                return {
                    'success': False,
                    'message': f'Loại sự cố không hợp lệ. Chọn một trong: {", ".join(valid_issue_types)}'
                }
            if request_data['urgency_level'] not in valid_urgency_levels:
                return {
                    'success': False,
                    'message': f'Mức độ khẩn cấp không hợp lệ. Chọn một trong: {", ".join(valid_urgency_levels)}'
                }

            # 4. Gọi Repository để chèn
            new_id = MaintenanceRepository.create_maintenance_request(
                tenant_id=tenant_id,
                room_id=room_id,
                issue_type=request_data['issue_type'],
                urgency_level=request_data['urgency_level'],
                description=request_data['description'],
                contact_phone=request_data.get('contact_phone'),
                available_time=request_data.get('available_time'),
                discovery_date=request_data.get('discovery_date'),
                image_path=request_data.get('image_path')
            )
            if new_id is None:
                return {'success': False, 'message': 'Không thể tạo yêu cầu bảo trì. Vui lòng thử lại.'}

            return {
                'success': True,
                'message': 'Đã tạo yêu cầu bảo trì thành công',
                'request_id': new_id
            }

        except Exception as e:
            print(f"❌ [Service] Lỗi create_maintenance_request: {e}")
            return {'success': False, 'message': f'Lỗi hệ thống: {e}'}

    @staticmethod
    def get_requests_by_room_id(room_id: int) -> List[Dict]:
        """
        Lấy yêu cầu bảo trì (format) theo room_id.
        """
        try:
            if not isinstance(room_id, int) or room_id <= 0:
                print("❌ [Service] Room ID không hợp lệ")
                return []

            raw = MaintenanceRepository.get_requests_by_room_id(room_id)
            return [MaintenanceService._format_maintenance_request(r) for r in raw]

        except Exception as e:
            print(f"❌ [Service] Lỗi get_requests_by_room_id: {e}")
            return []

    @staticmethod
    def get_maintenance_list(landlord_id: int) -> List[Dict[str, Any]]:
        # 1. Validate
        if not isinstance(landlord_id, int) or landlord_id <= 0:
            print("[Service] Landlord ID không hợp lệ")
            return []

        # 2. Lấy object
        raw_objs = MaintenanceRepository.get_maintenance_requests_by_landlord(landlord_id)
        print(f"[DEBUG] raw_objs count = {len(raw_objs)}")
        if raw_objs:
            # In thử object đầu tiên để kiểm tra mapping
            print("[DEBUG] sample raw_obj.__dict__ =", raw_objs[0].__dict__)

        # 3. Convert → dict và inject stt
        formatted = []
        for idx, obj in enumerate(raw_objs, start=1):
            data: Dict[str, Any] = obj.__dict__.copy()
            data['stt'] = idx

            # 4. Gọi formatter
            formatted.append(MaintenanceService._format_maintenance_request(data))

        print(f"✅ [Service] Lấy được {len(formatted)} yêu cầu bảo trì cho landlord {landlord_id}")
        return formatted

    @staticmethod
    def get_requests_by_tenant_id(tenant_id: int) -> List[Dict]:
        """
        Lấy yêu cầu bảo trì (format) theo tenant_id.
        """
        try:
            if not isinstance(tenant_id, int) or tenant_id <= 0:
                print("❌ [Service] Tenant ID không hợp lệ")
                return []

            raw = MaintenanceRepository.get_requests_by_tenant_id(tenant_id)
            return [MaintenanceService._format_maintenance_request(r) for r in raw]

        except Exception as e:
            print(f"❌ [Service] Lỗi get_requests_by_tenant_id: {e}")
            return []

    @staticmethod
    def _format_maintenance_request(request: Dict) -> Dict:
        """
        Format một maintenance request để hiển thị:
        - format created_at thành "DD/MM/YYYY"
        - ánh xạ status, urgency, issue_type sang tiếng Việt có icon
        """
        try:
            # 1. Format created_at (nếu có chữ "T", dùng fromisoformat; nếu vẫn còn khoảng trắng, thay bằng 'T')
            created_at = request.get('created_at', '')
            formatted_date = 'N/A'
            if created_at:
                try:
                    # Nếu dạng "YYYY-MM-DD HH:MM:SS", chuyển space->T
                    if ' ' in created_at:
                        created_at = created_at.replace(' ', 'T')
                    dt = datetime.fromisoformat(created_at)
                    formatted_date = dt.strftime('%d/%m/%Y')
                except Exception:
                    # Fallback lấy 10 ký tự đầu
                    formatted_date = created_at[:10]

            # 2. Format status
            status = request.get('status', '')
            status_mapping = {
                'Pending': '⏳ Chờ xử lý',
                'In Progress': '🔄 Đang xử lý',
                'Resolved': '✅ Đã hoàn thành',
                'Đang xử lý': '🔄 Đang xử lý',
                'Đã hoàn thành': '✅ Đã hoàn thành'
            }
            formatted_status = status_mapping.get(status, status or 'Unknown')

            # 3. Format urgency
            urgency = request.get('urgency_level', '')
            urgency_mapping = {
                'Khẩn cấp': '🚨 Khẩn cấp',
                'Bình thường': '📝 Bình thường',
                'Thấp': '🔻 Thấp'
            }
            formatted_urgency = urgency_mapping.get(urgency, urgency or '')

            # 4. Format issue_type
            issue_type = request.get('issue_type', '')
            issue_type_mapping = {
                'Điện': '⚡ Điện',
                'Nước': '💧 Nước',
                'Cấu trúc': '🏗️ Cấu trúc',
                'Điều hòa': '❄️ Điều hòa',
                'Khác': '🔧 Khác'
            }
            formatted_issue_type = issue_type_mapping.get(issue_type, f"🔧 {issue_type}")

            # 5. Trả về dict mới đã format
            return {
                'stt': request.get('stt', 0),
                'request_id': request.get('request_id'),
                'room_id': request.get('room_id'),
                'room_name': request.get('room_name', 'N/A'),
                'tenant_id': request.get('tenant_id'),
                'tenant_name': request.get('tenant_name', 'N/A'),
                'tenant_phone': request.get('tenant_phone', ''),
                'issue_type': formatted_issue_type,
                'urgency_level': formatted_urgency,
                'description': request.get('description', ''),
                'contact_phone': request.get('contact_phone', request.get('tenant_phone', '')),
                'available_time': request.get('available_time', ''),
                'discovery_date': request.get('discovery_date', ''),
                'image_path': request.get('image_path', ''),
                'status': formatted_status,
                'created_at': formatted_date,
                # Raw values để nếu cần xử lý thêm ở UI/Controller
                'raw_status': request.get('status', ''),
                'raw_urgency': request.get('urgency_level', ''),
                'raw_issue_type': request.get('issue_type', '')
            }

        except Exception as e:
            print(f"❌ [Service] Lỗi format maintenance request: {e}")
            return request

    @staticmethod
    def get_maintenance_detail(request_id: int) -> Optional[Dict]:
        """
        Lấy chi tiết một yêu cầu bảo trì đã format sẵn.
        """
        try:
            if not isinstance(request_id, int) or request_id <= 0:
                print("❌ [Service] Request ID không hợp lệ")
                return None

            raw = MaintenanceRepository.get_maintenance_request_by_id(request_id)
            if not raw:
                return None

            return MaintenanceService._format_maintenance_request(raw)

        except Exception as e:
            print(f"❌ [Service] Lỗi get_maintenance_detail: {e}")
            return None

    @staticmethod
    def update_maintenance_status(request_id: int, new_status: str) -> Dict:
        """
        Cập nhật trạng thái của một yêu cầu.
        Trả về dict: {'success': bool, 'message': str}
        """
        try:
            # 1. Validate input
            if not isinstance(request_id, int) or request_id <= 0:
                return {'success': False, 'message': 'ID yêu cầu không hợp lệ'}
            if not new_status:
                return {'success': False, 'message': 'Trạng thái không được để trống'}

            valid_statuses = ['Pending', 'In Progress', 'Resolved', 'Đang xử lý', 'Đã hoàn thành']
            if new_status not in valid_statuses:
                return {'success': False,
                        'message': f'Trạng thái không hợp lệ. Chọn một trong: {", ".join(valid_statuses)}'}

            # 2. Thực hiện update qua Repository
            success = MaintenanceRepository.update_maintenance_status(request_id, new_status)
            if success:
                return {'success': True, 'message': f'Đã cập nhật trạng thái thành "{new_status}"'}
            else:
                return {'success': False, 'message': 'Không tìm thấy yêu cầu hoặc không thể cập nhật'}

        except Exception as e:
            print(f"❌ [Service] Lỗi update_maintenance_status: {e}")
            return {'success': False, 'message': f'Lỗi hệ thống: {e}'}

    @staticmethod
    def get_maintenance_statistics(landlord_id: int) -> Dict:
        """
        Lấy thống kê cho landlord (nếu không tồn tại, trả về 0 cho mỗi field).
        """
        try:
            if not isinstance(landlord_id, int) or landlord_id <= 0:
                print("❌ [Service] Landlord ID không hợp lệ")
                return {
                    'total_requests': 0,
                    'pending_count': 0,
                    'in_progress_count': 0,
                    'resolved_count': 0,
                    'urgent_count': 0
                }

            stats = MaintenanceRepository.get_maintenance_statistics(landlord_id)
            if not stats:
                return {
                    'total_requests': 0,
                    'pending_count': 0,
                    'in_progress_count': 0,
                    'resolved_count': 0,
                    'urgent_count': 0
                }
            return stats

        except Exception as e:
            print(f"❌ [Service] Lỗi get_maintenance_statistics: {e}")
            return {
                'total_requests': 0,
                'pending_count': 0,
                'in_progress_count': 0,
                'resolved_count': 0,
                'urgent_count': 0
            }

    @staticmethod
    def delete_maintenance_request(request_id: int) -> Dict:
        """
        Xóa một yêu cầu bảo trì. Trả về dict {'success': bool, 'message': str}.
        """
        try:
            if not isinstance(request_id, int) or request_id <= 0:
                return {'success': False, 'message': 'ID yêu cầu không hợp lệ'}

            success = MaintenanceRepository.delete_maintenance_request(request_id)
            if success:
                return {'success': True, 'message': 'Đã xóa yêu cầu bảo trì thành công'}
            else:
                return {'success': False, 'message': 'Không tìm thấy yêu cầu hoặc xóa không thành công'}

        except Exception as e:
            print(f"❌ [Service] Lỗi delete_maintenance_request: {e}")
            return {'success': False, 'message': f'Lỗi hệ thống: {e}'}

    @staticmethod
    def filter_by_status(landlord_id: int, status: str) -> List[Dict]:
        """
        Lọc yêu cầu bảo trì theo trạng thái (hoặc trả cả list nếu status='all').
        """
        try:
            if not isinstance(landlord_id, int) or landlord_id <= 0:
                print("❌ [Service] Landlord ID không hợp lệ")
                return []

            if status == "all":
                return MaintenanceService.get_maintenance_list(landlord_id)

            raw = MaintenanceRepository.get_maintenance_requests_by_landlord(landlord_id)
            # Lọc ở chính Service (cũng có thể gọi trực tiếp repository.get_by_status nếu có)
            filtered = [r for r in raw if r.get('status') == status]
            return [MaintenanceService._format_maintenance_request(r) for r in filtered]

        except Exception as e:
            print(f"❌ [Service] Lỗi filter_by_status: {e}")
            return []

    @staticmethod
    def filter_by_urgency(landlord_id: int, urgency: str) -> List[Dict]:
        """
        Lọc yêu cầu bảo trì theo mức độ khẩn cấp (hoặc trả cả list nếu urgency='all').
        """
        try:
            if not isinstance(landlord_id, int) or landlord_id <= 0:
                print("❌ [Service] Landlord ID không hợp lệ")
                return []

            if urgency == "all":
                return MaintenanceService.get_maintenance_list(landlord_id)

            valid_urgencies = ['Khẩn cấp', 'Bình thường', 'Thấp']
            if urgency not in valid_urgencies:
                print(f"❌ [Service] Mức độ khẩn cấp không hợp lệ: {urgency}")
                return []

            raw = MaintenanceRepository.get_maintenance_requests_by_landlord(landlord_id)
            filtered = [r for r in raw if r.get('urgency_level') == urgency]
            formatted = [MaintenanceService._format_maintenance_request(r) for r in filtered]
            print(f"✅ [Service] Lọc được {len(formatted)} yêu cầu với mức độ '{urgency}' cho landlord {landlord_id}")
            return formatted

        except Exception as e:
            print(f"❌ [Service] Lỗi filter_by_urgency: {e}")
            return []
