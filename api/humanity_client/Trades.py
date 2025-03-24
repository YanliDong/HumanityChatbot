from typing import List, Literal


class Trades:
    def __init__(self, parent):
        self.parent: "Client" = parent

    async def get_trades(
        self,
        mode: Literal['manage', 'requested', 'available']
    ):
        return await self.parent.get(
            '/trade',
            {
                'mode': mode
            }
        )

    async def post_trade(
        self,
        trade_with: List[str],
        reason: str,
        shift: int
    ):
        return await self.parent.post(
            '/trades',
            {
                'tradewith': ','.join(trade_with),
                'reason': reason,
                'shift': shift
            }
        )
