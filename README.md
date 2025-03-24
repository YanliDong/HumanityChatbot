# Humanity Chatbot

A conversational chatbot interface for interacting with the Humanity API to manage shifts, trades, and time off requests.

## Features

### Use Case 1: View Shifts
View your scheduled shifts for this week or next week.

**Example 1: View this week's shifts**
```
User: shift
Bot: You have the following shifts scheduled:
- Monday 9am-5pm
- Tuesday 9am-5pm
- Wednesday 9am-5pm
```

**Example 2: View next week's shifts**
```
User: next week shifts
Bot: You have the following shifts scheduled for next week:
- Monday 9am-5pm
- Tuesday 9am-5pm
- Wednesday 9am-5pm
```

### Use Case 2: Request Shift Trade
Request to trade a shift with another eligible employee.

**Example 1: Trade a shift**
```
User: Trade shifts
Bot: Here are your available shifts for trading:
- Monday 9am-5pm (ID: 1)
- Tuesday 9am-5pm (ID: 2)
- Wednesday 9am-5pm (ID: 3)
Please enter the ID of the shift you want to trade.

User: 1
Bot: Here are the eligible employees you can trade with:
- John Doe (ID: 101)
- Jane Smith (ID: 102)
- Alex Johnson (ID: 103)
Please enter the ID of the employee you want to trade with.

User: 101
Bot: Here are your shift trade request details:
Shift: Monday 9am-5pm
Trading with: John Doe
Would you like to submit this trade request? (yes/no)

User: yes
Bot: Your shift trade request has been submitted successfully!
```

### Use Case 3: Request Time Off
Request time off for future dates.

**Example 1: Request time off**
```
User: Request time off
Bot: You have 10 days of vacation time available.
Please enter the dates you would like to take off (format: YYYY-MM-DD to YYYY-MM-DD)

User: 2025-03-25 to 2025-03-30
Bot: Here are your time off request details:
Start Date: 2025-03-25
End Date: 2025-03-30
Duration: 6 days
Would you like to submit this time off request? (yes/no)

User: yes
Bot: Your time off request has been submitted successfully!
```

**Example 2: Request single day off**
```
User: Request time off
Bot: You have 10 days of vacation time available.
Please enter the dates you would like to take off (format: YYYY-MM-DD to YYYY-MM-DD)

User: 2025-03-25 to 2025-03-25
Bot: Here are your time off request details:
Start Date: 2025-03-25
End Date: 2025-03-25
Duration: 1 day
Would you like to submit this time off request? (yes/no)

User: yes
Bot: Your time off request has been submitted successfully!
```

### Use Case 4 (Bonus): Create Shift (Admin Only)
Create a new shift for an employee.

**Example 1: Create a shift**
```
User: Create shift
Bot: Here are the available employees:
- John Doe (ID: 101)
- Jane Smith (ID: 102)
- Alex Johnson (ID: 103)
Please enter the ID of the employee.

User: 101
Bot: Here are the available positions:
- Cashier (ID: 1)
- Manager (ID: 2)
- Stock Clerk (ID: 3)
Please enter the ID of the position.

User: 1
Bot: Here are your shift creation details:
Employee: John Doe
Position: Cashier
Start Time: 2025-03-25 09:00
End Time: 2025-03-25 17:00
Would you like to create this shift? (yes/no)

User: yes
Bot: Your shift has been created successfully!
```

## Setup and Installation

1. Clone the repository:
```bash
git clone https://github.com/YanliDong/HumanityChatbot.git
cd HumanityChatbot
```

2. Start the application using Docker Compose:
```bash
docker-compose -f development-docker-compose.yml up --build
```

3. Access the application at http://localhost:8080

## Environment Variables

Create a `.env` file in the root directory with the following variables:
```
PORT=8080
HUMANITY_API_URL=http://localhost:8001
LLM_SERVER_URL=http://localhost:8002
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
