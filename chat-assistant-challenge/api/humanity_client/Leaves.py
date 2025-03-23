

class Leaves:
    def __init__(self, parent):
        self.parent: "Client" = parent

    async def post_leave_request(
        self,
        employee_id: int|str,
        leave_type_id: int|str,
        start_date: str,
        end_date: str
    ):
        post_data = {
            'employee': int(employee_id),
            'leavetype': int(leave_type_id),
            'start_date': start_date,
            'end_date': end_date
        }
        return await self.parent.post(
            f'/leaves',
            post_data
        )
