
class Locations:
    def __init__(self, parent):
        self.parent: "Client" = parent

    async def get_locations(
        self
    ):
        return await self.parent.get(
            '/locations'
        )
