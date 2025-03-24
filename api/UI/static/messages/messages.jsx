import {
    Accordion,
    AccordionDetails,
    AccordionSummary, Avatar,
    Button,
    Card,
    CardContent,
    Divider, List, ListItem, ListItemIcon, ListItemText, Paper, Skeleton, Tooltip, Typography
} from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import AssistantIcon from "@mui/icons-material/Assistant";
import * as React from "react";
import EventIcon from '@mui/icons-material/Event';
import SwapHorizIcon from '@mui/icons-material/SwapHoriz';
import TipsAndUpdatesIcon from '@mui/icons-material/TipsAndUpdates';
import ErrorIcon from '@mui/icons-material/Error';
import ClickAwayListener from '@mui/material/ClickAwayListener';
import EventBusyIcon from '@mui/icons-material/EventBusy';

const message_styles = {
    borderRadius: '8px',
    marginBottom: '8px',
}

const assistant_message_styles = {
    ...message_styles,
    marginRight: 'auto',
    textAlign: 'left',
    border: '1px solid #E1BE6A',
    borderLeft: '6px solid #E1BE6A',
}
const user_message_styles = {
    ...message_styles,
    marginLeft: 'auto',
    textAlign: 'right',
    border: '1px solid #40B0A6',
    borderRight: '6px solid #40B0A6'
}

export function Messages({
    messages,
    loading_response
}) {

    const bottom_of_chat = React.useRef(null);
    const scrollToBottom = () => {
      bottom_of_chat.current.scrollIntoView({ behavior: "smooth" });
    }

    React.useEffect(
        scrollToBottom
    )

    let message_html = [];
    messages.map( ( x, i ) =>  {
        if( x['content'] === null ) {
            console.log( 'skipping record' );
            console.log( x );
            return;
        }
        switch( x['role'] ) {

            case 'assistant':
                message_html.push(
                    <AssistantMessage x={x} key={i}/>
                )
                break;
            case 'tool':
                // message_html.push(
                //     <ToolMessage x={x} key={i}/>
                // )
                break;
            case 'user':
                message_html.push(
                    <UserMessage message={x} key={i}/>
                )
                break;
            case 'scratchpad':
                message_html.push(
                    <ScratchpadMessage message={x} key={i}/>
                )
                break;
        }
    })
    let loading_skeleton = null;
    if ( loading_response ) {
        loading_skeleton = <Skeleton animation="wave" />
    }

    return <CardContent sx={{ overflowY: 'scroll' }}>
        {message_html}
        {loading_skeleton}
        <span ref={bottom_of_chat}/>
    </CardContent>
}

function ScratchpadMessage({
    message
}) {
    let content = message['content'];
    let outputs = [];
    switch ( content['entry_type'] ) {
        case 'trade_requests':
            content['entry_data'].map( ( x, i ) =>  {
              outputs.push(
                  <TradeRequestCard entry={x} key={i}/>
              )
            })
            break;
        case 'shifts':
            content['entry_data'].map( ( x, i ) =>  {
              outputs.push(
                  <ShiftCard entry={x} key={i}/>
              )
            })
            break;
        case 'leave_request':
            outputs.push(
                <LeaveRequestCard entry={content['entry_data']}/>
            )
            break;
        case 'schedules':
            outputs.push(
                <SchedulesCard entry={content['entry_data']}/>
            )
            break;
        case 'employees':
            outputs.push(
                <EmployeesCard entry={content['entry_data']}/>
            )
    }

    return outputs
}

function TradeRequestCard({
    entry
}) {
    let event_name = '';
    if ( entry['title'].trim().length > 0 ) {
        event_name = <>{entry['title']}<br/></>;
    }
    return <Accordion sx={{
        ...assistant_message_styles
    }}>
        <AccordionSummary
          expandIcon={<ExpandMoreIcon />}
        >
            <div style={{
                    display: 'flex',
                    alignContent: 'center',
                    gap: '6px'
                }}>
                <SwapHorizIcon fontSize="small"/>{event_name}
                <TimeRange start_date={entry['start_date']} end_date={entry['end_date']}/>
            </div>
        </AccordionSummary>
        <Divider/>
        <AccordionDetails>
            Schedule: {entry['schedule_name']}<br/><br/>
            Trade Reason: <br/>
            {entry['reason']}
        </AccordionDetails>
        <Divider/>
        <AccordionDetails>
            Recipients:
            {
                entry['recipients'].map( (r, i) => {
                    return <div style={{
                        display: "flex",
                        alignItems: "center",
                        gap: '8px',
                        marginBottom: '8px'
                    }} key={i}>
                        <Avatar alt="employee" src={r['avatar']['small']} />
                        <div>{r['name']}</div>
                        <ConflictsBadge conflict_groups={r['conflict_groups']}/>
                    </div>
                })
            }
        </AccordionDetails>
        <Divider/>
        <AccordionDetails>
            <Button variant="outlined">Make Trade</Button>
        </AccordionDetails>
    </Accordion>

}

function LeaveRequestCard({
    entry
}) {
    return <Card sx={{
        ...assistant_message_styles
    }}>
        <Accordion>
            <AccordionSummary
              expandIcon={<ExpandMoreIcon />}
            >
                <div style={{
                        display: 'flex',
                        alignContent: 'center',
                        gap: '6px'
                    }}>
                    <EventBusyIcon fontSize="small"/>
                    <TimeRange start_date={entry['start_date']} end_date={entry['end_date']}/>
                </div>
            </AccordionSummary>
            <Divider/>
            <AccordionDetails>
                Leave Type: {entry['leave_type_name']}<br/><br/>
            </AccordionDetails>
            <Divider/>
            <AccordionDetails>
                <Button variant="outlined">Make Leave Request</Button>
            </AccordionDetails>
        </Accordion>
    </Card>
}


function ConflictsBadge({
    conflict_groups
}) {
    const [ModalOpen, setModalOpen ] = React.useState( false );
    let conflicts = []
    conflict_groups.map( (c, i) => {
      if (c[1].trim() === '' ) {
          return;
      }
      conflicts.push(
          <ListItemText>- {c[1]}</ListItemText>
      )
    } )
    if (conflicts.length === 0 ) {
        return null;
    }

    return <>
    <ClickAwayListener onClickAway={()=>setModalOpen(false)}>
        <Tooltip
          open={ModalOpen}
          onClose={()=>setModalOpen(false)}
          disableFocusListener
          disableHoverListener
          disableTouchListener
          sx={{
              maxWidth: 500,
              opacity: 1
          }}
          PopperProps={{
              disablePortal: true,
            }}
          title={
            <div style={{opacity:1}}>
                <Typography id="modal-modal-title" variant="h6" component="h2">
                  Trade Conflicts
                </Typography>
                <Typography id="modal-modal-description" sx={{ mt: 2 }}>
                  <List>
                      {conflicts}
                  </List>
                </Typography>
              </div>
            }
          aria-labelledby="modal-modal-title"
          aria-describedby="modal-modal-description"
        >
            <Button onClick={()=> setModalOpen(true)}><ErrorIcon color="error"/></Button>
        </Tooltip>
    </ClickAwayListener>
    </>
}

function ShiftCard({
    entry
}) {
    let event_name = '';
    if ( entry['title'].trim().length > 0 ) {
        event_name = <>{entry['title']}<br/></>;
    }

    return <Accordion sx={{
        ...assistant_message_styles,
    }}>
        <AccordionSummary
          expandIcon={<ExpandMoreIcon />}
        >
            <div style={{
                display: 'flex',
                alignContent: 'center',
                gap: '6px'
            }}>
                <EventIcon fontSize="small"/><TimeRange start_date={entry['start_date']} end_date={entry['end_date']}/><br/>
                {event_name}
            </div>
        </AccordionSummary>
        <Divider/>
        <AccordionDetails>
            Schedule:  {entry['schedule_name']}
            <EmployeesCard entry={entry['employees']}/>
        </AccordionDetails>
        <Divider/>
        <AccordionDetails>
            <Button variant="outlined">Trade</Button>
        </AccordionDetails>
    </Accordion>

}

function SchedulesCard({
    entry
}) {
    let list_items = entry.map( ( x, i ) =>  {
        return <ListItem>
            <ListItemText>{x['schedule_name']}</ListItemText>
        </ListItem>
    })

    return <Paper sx={{
        ...assistant_message_styles,
        maxHeight: 300,
        overflowY: 'auto'
    }}>
        <List dense>
            {list_items}
        </List>
    </Paper>
}

function EmployeesCard({
    entry
}) {
    let list_items = entry.map( ( x, i ) =>  {
        return <ListItem>
            <ListItemIcon><Avatar alt="employee" src={x['avatar']['small']} /></ListItemIcon>
            <ListItemText> {x['name']}</ListItemText>
        </ListItem>
    })

    return <Paper sx={{
        ...assistant_message_styles,
        maxHeight: 300,
        overflowY: 'auto'
    }}>
        <List dense>
            {list_items}
        </List>
    </Paper>
}

function UserMessage({
    message
}) {
    return <Message
        icon={null}
        text={message['content']}
        userMessage={true}
    />;
}


function ToolMessage({
    x
}) {
    return <Message
        icon={<TipsAndUpdatesIcon fontSize="small" />}
        text={x['content']}/>;
}


function AssistantMessage({
    x
}) {
    return <Message
        icon={<AssistantIcon fontSize="small" />}
        text={x['content']}/>;
}

function Message({
    styles = {},
    icon,
    text,
    userMessage = false
}) {
    text = text.trim()
    let text_with_breaks = text.split('\n').map((text, index) => (
        <React.Fragment key={index}>
          {text}
          <br/>
        </React.Fragment>
      ));

    let border = assistant_message_styles;
    if ( userMessage ) {
        border = user_message_styles;
    }

    let final_styles = {
        display: 'flex',
        alignContent: 'center',
        gap: '6px',
        padding: '16px !important',
        maxWidth: 'fit-content',
        width: 'max-content',
        ...border,
        ...styles
    }
    return <CardContent sx={final_styles}>
        {icon}  {text_with_breaks}
    </CardContent>
}

function TimeRange({
    start_date,
    end_date
}) {
    if (start_date['formatted'] === end_date['formatted'] ) {
        return <>{start_date['formatted']} {start_date['time']} - {end_date['time']}</>
    } else {
        return <>{start_date['formatted']} {start_date['time']} - {end_date['formatted']} {end_date['time']}</>
    }
}