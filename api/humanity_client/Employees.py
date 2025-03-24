

class Employees:
    def __init__(self, parent):
        self.parent: "Client" = parent

    async def get_me(
        self
    ):
        return await self.parent.get(
            '/me',
            {}
        )

    async def get_employees(
        self,
        schedule: int = None,
        disabled: bool = False,
        inactive: bool = False
    ):
        params = {}
        if schedule is not None:
            params['schedule'] = int( schedule )
        return await self.parent.get(
            '/employees',
            params
        )
