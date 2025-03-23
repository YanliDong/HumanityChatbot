import json
from typing import List, Dict, Optional

from pydantic import BaseModel, ConfigDict, TypeAdapter

from humanity_client.client import Client


class ScratchpadEntry(BaseModel):
    entry_type: str
    entry_data: dict | list


class Employee(BaseModel):
    id: str
    name: str
    avatar: Optional[None | Dict | str ] = None

    def model_post_init(self, __context):
        if isinstance( self.avatar, str ):
            self.avatar = json.loads( self.avatar )
            for avatar_size in self.avatar.keys():
                if self.avatar[avatar_size].startswith( 'https://www.humanity.com/'):
                    continue
                else:
                    self.avatar[ avatar_size ] = f'https://www.humanity.com/{self.avatar[ avatar_size ]}'


class Time(BaseModel):
    date: str
    time: str
    formatted: str


class Shift(BaseModel):
    model_config = ConfigDict( extra = 'ignore' )

    id: int
    title: str
    schedule: int
    schedule_name: str
    employees: List[ Employee ]
    start_date: Time
    end_date: Time


class ToolResponse(BaseModel):
    """
    user_message: message to display directly to the user.
    tool_response: data to present to the language model, usually json.
    scratchpad: A scratchpad entry that can be rendered for the user
    """
    user_message: str = ''
    tool_response: str = ''
    scratchpad: ScratchpadEntry | None = None
    return_to_client: bool = False


CLIENT_TYPE = Client
SCRATCHPAD_TYPE = List[ScratchpadEntry]


async def load_shifts(
    start_date: str,
    stop_date: str,
    client: CLIENT_TYPE,
    scratchpad: SCRATCHPAD_TYPE
) -> ToolResponse:
    status, shifts_response = await client.Shifts.list(start_date=start_date, end_date=stop_date)
    
    if status != 200 or 'data' not in shifts_response:
        return ToolResponse(
            user_message=f"Sorry, I couldn't retrieve your shifts for the period {start_date} to {stop_date}.",
            tool_response=json.dumps({"error": "Failed to load shifts", "status": status})
        )
    
    shifts = shifts_response['data']
    
    # Create a formatted response for the user
    if not shifts:
        user_message = f"You don't have any shifts scheduled between {start_date} and {stop_date}."
    else:
        shift_details = []
        for shift in shifts:
            start_time = shift['start_date']['formatted']
            end_time = shift['end_date']['formatted']
            shift_details.append(f"• {shift['title']}: {start_time} to {end_time}")
        
        user_message = f"Here are your shifts between {start_date} and {stop_date}:\n" + "\n".join(shift_details)
    
    # Add to scratchpad for visualization
    scratchpad_entry = ScratchpadEntry(
        entry_type="shifts",
        entry_data=shifts
    )
    
    return ToolResponse(
        user_message=user_message,
        tool_response=json.dumps(shifts),
        scratchpad=scratchpad_entry
    )

async def request_time_off(
    start_date: str,
    end_date: str,
    leave_type_id: str,
    reason: str,
    client: CLIENT_TYPE,
    scratchpad: SCRATCHPAD_TYPE
) -> ToolResponse:
    # First get the available leave types to validate
    status, leave_types_response = await client.LeaveTypes.list()
    
    if status != 200 or 'data' not in leave_types_response:
        return ToolResponse(
            user_message="Sorry, I couldn't retrieve the available leave types.",
            tool_response=json.dumps({"error": "Failed to load leave types", "status": status})
        )
    
    # Verify leave type is valid
    leave_type_valid = False
    leave_type_name = ""
    for leave_type in leave_types_response['data']:
        if str(leave_type['id']) == leave_type_id:
            leave_type_valid = True
            leave_type_name = leave_type['name']
            break
    
    if not leave_type_valid:
        return ToolResponse(
            user_message="Sorry, the selected leave type is not valid.",
            tool_response=json.dumps({"error": "Invalid leave type"})
        )
    
    # Submit the time off request
    status, response = await client.Leaves.create(
        start_date=start_date,
        end_date=end_date,
        leave_type_id=leave_type_id,
        reason=reason
    )
    
    if status != 200 or 'data' not in response:
        return ToolResponse(
            user_message=f"Sorry, I couldn't submit your time off request for {start_date} to {end_date}.",
            tool_response=json.dumps({"error": "Failed to create leave request", "status": status})
        )
    
    leave_data = response['data']
    
    # Create scratchpad entry
    scratchpad_entry = ScratchpadEntry(
        entry_type="time_off_request",
        entry_data=leave_data
    )
    
    user_message = f"Your time off request has been submitted successfully!\n\nType: {leave_type_name}\nDates: {start_date} to {end_date}\nReason: {reason}\nStatus: {leave_data.get('status', 'Pending')}"
    
    return ToolResponse(
        user_message=user_message,
        tool_response=json.dumps(leave_data),
        scratchpad=scratchpad_entry
    )

async def get_available_leave_types(
    client: CLIENT_TYPE,
    scratchpad: SCRATCHPAD_TYPE
) -> ToolResponse:
    status, response = await client.LeaveTypes.list()
    
    if status != 200 or 'data' not in response:
        return ToolResponse(
            user_message="Sorry, I couldn't retrieve the available leave types.",
            tool_response=json.dumps({"error": "Failed to load leave types", "status": status})
        )
    
    leave_types = response['data']
    
    # Format leave types for user
    leave_type_list = []
    for leave_type in leave_types:
        leave_type_list.append(f"• {leave_type['name']} (ID: {leave_type['id']})")
    
    user_message = "Here are the available leave types:\n" + "\n".join(leave_type_list)
    
    # Create scratchpad entry
    scratchpad_entry = ScratchpadEntry(
        entry_type="leave_types",
        entry_data=leave_types
    )
    
    return ToolResponse(
        user_message=user_message,
        tool_response=json.dumps(leave_types),
        scratchpad=scratchpad_entry
    )

async def request_shift_trade(
    shift_id: str,
    trade_with_employee_id: str,
    client: CLIENT_TYPE,
    scratchpad: SCRATCHPAD_TYPE
) -> ToolResponse:
    # First verify the shift exists
    status, shift_response = await client.Shifts.get(shift_id)
    
    if status != 200 or 'data' not in shift_response:
        return ToolResponse(
            user_message=f"Sorry, I couldn't find the shift with ID {shift_id}.",
            tool_response=json.dumps({"error": "Failed to find shift", "status": status})
        )
    
    # Get eligible employees for the trade
    status, eligible_response = await client.Shifts.get_trade_list(shift_id)
    
    if status != 200 or 'data' not in eligible_response:
        return ToolResponse(
            user_message=f"Sorry, I couldn't retrieve employees eligible for trading shift {shift_id}.",
            tool_response=json.dumps({"error": "Failed to get eligible employees", "status": status})
        )
    
    # Verify employee is eligible for trade
    eligible_employees = eligible_response['data']
    employee_valid = False
    employee_name = ""
    
    for employee in eligible_employees:
        if employee['id'] == trade_with_employee_id:
            employee_valid = True
            employee_name = employee['name']
            break
    
    if not employee_valid:
        return ToolResponse(
            user_message="Sorry, the selected employee is not eligible for this shift trade.",
            tool_response=json.dumps({"error": "Invalid employee for trade"})
        )
    
    # Submit the trade request
    status, trade_response = await client.Trades.create(
        shift_id=shift_id,
        trade_with=trade_with_employee_id
    )
    
    if status != 200 or 'data' not in trade_response:
        return ToolResponse(
            user_message=f"Sorry, I couldn't submit your shift trade request for shift {shift_id}.",
            tool_response=json.dumps({"error": "Failed to create trade request", "status": status})
        )
    
    trade_data = trade_response['data']
    
    # Create scratchpad entry
    scratchpad_entry = ScratchpadEntry(
        entry_type="shift_trade",
        entry_data=trade_data
    )
    
    shift_info = shift_response['data']
    start_time = shift_info['start_date']['formatted']
    end_time = shift_info['end_date']['formatted']
    
    user_message = f"Your shift trade request has been submitted successfully!\n\nShift: {shift_info['title']} ({start_time} to {end_time})\nTrading with: {employee_name}\nStatus: {trade_data.get('status', 'Pending')}"
    
    return ToolResponse(
        user_message=user_message,
        tool_response=json.dumps(trade_data),
        scratchpad=scratchpad_entry
    )

async def get_eligible_trade_employees(
    shift_id: str,
    client: CLIENT_TYPE,
    scratchpad: SCRATCHPAD_TYPE
) -> ToolResponse:
    # First verify the shift exists
    status, shift_response = await client.Shifts.get(shift_id)
    
    if status != 200 or 'data' not in shift_response:
        return ToolResponse(
            user_message=f"Sorry, I couldn't find the shift with ID {shift_id}.",
            tool_response=json.dumps({"error": "Failed to find shift", "status": status})
        )
    
    # Get eligible employees for the trade
    status, eligible_response = await client.Shifts.get_trade_list(shift_id)
    
    if status != 200 or 'data' not in eligible_response:
        return ToolResponse(
            user_message=f"Sorry, I couldn't retrieve employees eligible for trading shift {shift_id}.",
            tool_response=json.dumps({"error": "Failed to get eligible employees", "status": status})
        )
    
    eligible_employees = eligible_response['data']
    
    if not eligible_employees:
        user_message = f"There are no employees eligible to trade for shift {shift_id}."
    else:
        employee_list = []
        for employee in eligible_employees:
            employee_list.append(f"• {employee['name']} (ID: {employee['id']})")
        
        user_message = f"Here are the employees eligible for trading shift {shift_id}:\n" + "\n".join(employee_list)
    
    # Create scratchpad entry
    scratchpad_entry = ScratchpadEntry(
        entry_type="eligible_employees",
        entry_data=eligible_employees
    )
    
    return ToolResponse(
        user_message=user_message,
        tool_response=json.dumps(eligible_employees),
        scratchpad=scratchpad_entry
    )