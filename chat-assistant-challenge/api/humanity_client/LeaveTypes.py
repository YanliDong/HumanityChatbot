

class LeaveTypes:
    def __init__(self, parent):
        self.parent: "Client" = parent

    async def get_employee_leave_types(
        self,
        employee_id: int|str
    ):
        return await self.parent.get(
            f'/employees/{int(employee_id)}/leave-types'
        )

    async def get_leave_types(
        self
    ):
        params = {}
        return await self.parent.get(
            '/leave-types',
            params
        )
