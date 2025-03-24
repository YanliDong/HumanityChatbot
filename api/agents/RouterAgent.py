from datetime import datetime, timedelta
import re
import json

import dspy
from dspy import InputField, OutputField

from agents.BaseAgent import BaseAgent
from functions import (
    load_shifts, 
    request_time_off, 
    get_available_leave_types,
    request_shift_trade, 
    get_eligible_trade_employees
)


class ShiftIntent(dspy.Signature):
    """Determine if the user wants to view their shifts."""
    query = InputField()
    is_shift_intent = OutputField(desc="True if the user wants to view shifts, False otherwise")
    timeframe = OutputField(desc="The timeframe mentioned (this week, next week, specific date, etc.)")


class TimeOffIntent(dspy.Signature):
    """Determine if the user wants to request time off."""
    query = InputField()
    is_timeoff_intent = OutputField(desc="True if the user wants to request time off, False otherwise")
    start_date = OutputField(desc="Start date for time off request (if mentioned)")
    end_date = OutputField(desc="End date for time off request (if mentioned)")
    reason = OutputField(desc="Reason for time off request (if mentioned)")


class ShiftTradeIntent(dspy.Signature):
    """Determine if the user wants to trade shifts."""
    query = InputField()
    is_trade_intent = OutputField(desc="True if the user wants to trade shifts, False otherwise")
    shift_id = OutputField(desc="The shift ID the user wants to trade (if mentioned)")
    trade_with = OutputField(desc="The employee ID to trade with (if mentioned)")


class RootRouterAgent(BaseAgent):
    def __init__(self, *args):
        super().__init__(*args)
        self.shift_predictor = dspy.Predict(ShiftIntent)
        self.timeoff_predictor = dspy.Predict(TimeOffIntent)
        self.trade_predictor = dspy.Predict(ShiftTradeIntent)
    
    def format_date(self, date_str):
        """Format date string to YYYY-MM-DD for API calls."""
        today = datetime.now()
        
        if date_str.lower() == "today":
            return today.strftime("%Y-%m-%d")
        elif date_str.lower() == "tomorrow":
            return (today + timedelta(days=1)).strftime("%Y-%m-%d")
        elif "this week" in date_str.lower():
            # Start of current week (Monday)
            start_of_week = today - timedelta(days=today.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            return start_of_week.strftime("%Y-%m-%d"), end_of_week.strftime("%Y-%m-%d")
        elif "next week" in date_str.lower():
            # Start of next week (Monday)
            start_of_week = today + timedelta(days=7-today.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            return start_of_week.strftime("%Y-%m-%d"), end_of_week.strftime("%Y-%m-%d")
        elif "month" in date_str.lower():
            # Start of current month
            start_of_month = today.replace(day=1)
            # End of current month
            if today.month == 12:
                end_of_month = today.replace(year=today.year+1, month=1, day=1) - timedelta(days=1)
            else:
                end_of_month = today.replace(month=today.month+1, day=1) - timedelta(days=1)
            return start_of_month.strftime("%Y-%m-%d"), end_of_month.strftime("%Y-%m-%d")
        
        # Try to parse date from string using regex
        date_pattern = r"(\d{4}-\d{2}-\d{2})"
        matches = re.findall(date_pattern, date_str)
        if matches:
            return matches[0]
        
        return None

    async def handle_shift_request(self, timeframe, today_str):
        """Handle request to view shifts."""
        start_date = today_str
        end_date = today_str
        
        if isinstance(timeframe, tuple):
            start_date, end_date = timeframe
        elif timeframe and self.format_date(timeframe):
            date_result = self.format_date(timeframe)
            if isinstance(date_result, tuple):
                start_date, end_date = date_result
            else:
                start_date = date_result
                end_date = date_result
        
        return await load_shifts(start_date, end_date, self.client, self.scratchpad)

    async def handle_timeoff_request(self, start_date, end_date, reason):
        """Handle request for time off."""
        # If dates are not provided, ask user for input
        if not start_date or not end_date:
            # First get available leave types to show user
            leave_types_response = await get_available_leave_types(self.client, self.scratchpad)
            return leave_types_response
        
        # User needs to select a leave type and provide dates
        return ToolResponse(
            user_message="To request time off, I need a start date, end date, leave type, and reason. Could you please provide these details?",
            tool_response=json.dumps({"action": "request_time_off_details"})
        )

    async def handle_trade_request(self, shift_id, trade_with):
        """Handle request to trade shifts."""
        # If shift ID not provided, get user's shifts first
        if not shift_id:
            today = datetime.now()
            end_date = (today + timedelta(days=30)).strftime("%Y-%m-%d")
            shifts_response = await load_shifts(today.strftime("%Y-%m-%d"), end_date, self.client, self.scratchpad)
            return ToolResponse(
                user_message="To trade shifts, please let me know which shift you'd like to trade by providing its ID from the list above.",
                tool_response=shifts_response.tool_response
            )
        
        # If shift ID provided but no trade_with, get eligible employees
        if shift_id and not trade_with:
            return await get_eligible_trade_employees(shift_id, self.client, self.scratchpad)
        
        # If both shift ID and trade_with provided, initiate trade
        if shift_id and trade_with:
            return await request_shift_trade(shift_id, trade_with, self.client, self.scratchpad)
        
        return ToolResponse(
            user_message="I need more information to process your shift trade request.",
            tool_response=json.dumps({"error": "Insufficient information"})
        )

    async def forward(self, history, request, today=None):
        if today is None:
            today = datetime.now().strftime("%Y-%m-%d")
        
        # Check user intent from request
        shift_intent = self.shift_predictor(query=request)
        timeoff_intent = self.timeoff_predictor(query=request)
        trade_intent = self.trade_predictor(query=request)
        
        # Handle based on identified intent
        if shift_intent.is_shift_intent:
            return await self.handle_shift_request(shift_intent.timeframe, today)
        
        elif timeoff_intent.is_timeoff_intent:
            return await self.handle_timeoff_request(
                timeoff_intent.start_date, 
                timeoff_intent.end_date, 
                timeoff_intent.reason
            )
        
        elif trade_intent.is_trade_intent:
            return await self.handle_trade_request(
                trade_intent.shift_id,
                trade_intent.trade_with
            )
        
        # Default response if no intent is matched
        return {
            "response": "I'm not sure how to help with that request. You can ask me to view your shifts, request time off, or trade shifts."
        }
