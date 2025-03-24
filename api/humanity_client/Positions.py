
class Positions:
    def __init__(self, parent):
        self.parent: "Client" = parent

    async def get_positions(
        self
    ):
        return await self.parent.get(
            '/positions'
        )
