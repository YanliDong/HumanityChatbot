from typing import List, Literal


class Shifts:
    def __init__(self, parent):
        self.parent: "Client" = parent

    async def get_shift_trade_list(
        self,
        shift_id: int
    ):
        return await self.parent.get(
            f'/shifts/{shift_id}/tradelist_v2'
        )

    async def post_shift(
        self,
        schedule_id: int,
        employee_ids: List[ str ],
        start_date: str,
        stop_date: str,
        start_time: str,
        stop_time: str,
    ):
        return await self.parent.post(
            '/shifts',
            {
                "start_time": start_time,
                "end_time": stop_time,
                "start_date": start_date,
                "end_date": stop_date,
                "schedule": schedule_id,
                "employee_id": ','.join( employee_ids )
            }
        )

    async def get_shift(
        self,
        shift_id: int|str
    ):
        return await self.parent.get(
            f'/shifts/{shift_id}'
        )

    async def get_shifts(
        self,
        start_date: str,
        end_date: str,
        mode: Literal[
            'overview',
            'location',
            'schedule',
            'incomplete',
            'employees',
            'employee',
            'open',
            'openapproval',
            'confirm',
            'onnow',
            'late',
            'upcoming',
            'recent',
            'multiple'
        ] = 'employee',
        employees: List[int] = None
    ):
        if mode not in ['confirm', 'employees']:
            assert employees is None, 'employees filter only works with mode = confirm,employees'

        params = {
            'start_date': start_date,
            'end_date': end_date,
            'mode': mode
        }

        if employees is not None and len( employees ) > 0:
            params['employees'] = ','.join( [ str(e) for e in employees ] )

        return await self.parent.get(
            '/shifts',
            params
        )
