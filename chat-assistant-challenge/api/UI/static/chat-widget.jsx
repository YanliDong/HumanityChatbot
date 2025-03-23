import * as React from 'react';
import * as ReactDOM from 'react-dom/client';
import {
    Button,
    Card,
    CardContent, CardHeader, Container,
    createTheme,
    CssBaseline, Divider,
    TextField,
    ThemeProvider
} from "@mui/material";
import SendIcon from '@mui/icons-material/Send';
import {getCookie} from "./utils.jsx";
import {Messages} from "./messages/messages.jsx";


window.addEventListener("DOMContentLoaded", function (e) {
    ReactDOM.createRoot(
        document.querySelector("#chat-widget")
    ).render(
        <React.StrictMode>
            <ChatWidget/>
        </React.StrictMode>
    );
});


const darkTheme = createTheme({
  palette: {
    mode: 'dark',
      primary: {
        main: '#0082ba'
      }
  },
});


function ChatWidget() {
    const [sessionId, setSessionId] = React.useState( null )
    const check_session_id = () => {
        let session_id = getCookie( 'session_id' )
        if ( session_id !== null ) {
            setSessionId( session_id );
        } else {
            setSessionId( null );
        }
    }

    React.useEffect( check_session_id, [] )

    let view = null;
    if ( sessionId !== null ) {
        view = <Conversation checkLogin={check_session_id}/>;
    } else {
        view = <Login onLogin={check_session_id}/>
    }

    return <>
        <ThemeProvider theme={darkTheme}>
            <CssBaseline />
            <Container
                sx={{
                    width: 650,
                    height: 800,
                    // margin: 4,
                }}
            >{view}</Container>
        </ThemeProvider>
    </>
}

function Login({
    onLogin
}) {
    const [username, setUsername] = React.useState( '' )
    const [password, setPassword] = React.useState( '' )

    let submit = async () => {
        try {
            const response = await fetch(
                "/log-in",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": 'application/json'
                    },
                    body: JSON.stringify({
                        username: username,
                        password: password
                    })
                }
            );
            const data = await response.json();
            onLogin();
        } catch (e) {

        }
    }

    return <Card>
        <CardHeader content="Login"/>
        <CardContent sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '10px'
        }}>
            <TextField
                label="Username" variant="outlined"
                id="username"
                value={username}
                onChange={ e => setUsername(e.target.value) }
            />
            <TextField
                label="Password" variant="outlined"
                id="password"
                type="password"
                value={password}
                onChange={ e => setPassword(e.target.value) }
            />
            <Button onClick={submit} variant="contained">Login</Button>
        </CardContent>
    </Card>
}

function Conversation({
    checkLogin
}) {
    const [apiVersion, setAPIVersion] = React.useState( 'v1' );
    const [ conversation, setConversation ] = React.useState( [] )
    const [loading, setLoading] = React.useState(false);

    React.useEffect( () => {
        let load_messages = async ( message )  => {
            try {
                const response = await fetch(
                    "/chat/load",
                    {
                        method: "POST",
                        headers: {
                            "Content-Type": 'application/json'
                        }
                    }
                );
                const data = await response.json();
                setConversation( data['conversation'] );
            } catch (e) {

            }
        }
        load_messages()
    }, [])

    let send_message = async ( message )  => {
        try {
            setConversation( (prevState ) => {
                let new_state = [...prevState];
                new_state.push( {
                    'role': 'user',
                    'content': message
                } )
                return new_state;
            })
            setLoading( true );
            const response = await fetch(
                `/chat/${apiVersion}/send`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": 'application/json'
                    },
                    body: JSON.stringify({
                        message: message
                    })
                }
            );
            const data = await response.json();
            setLoading( false );
            setConversation( data['conversation'] );
        } catch (e) {
            setLoading( false );
        }
    }

    let styles = {
        height: '100%',
        display: 'grid',
        gridTemplateRows: 'auto 1fr auto auto'
    }
    const change_version = () => setAPIVersion((prevState) => {
        if ( prevState === 'v1' ) {
            return 'v2'
        } else {
            return 'v1'
        }
    })

    const logout = async () => {
        try {
            const response = await fetch(
                `/log-out`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": 'application/json'
                    }
                }
            );
            checkLogin();
        } catch (e) {
            checkLogin();
        }
    }

    return <>
        <Card sx={styles}>
            <CardContent><span>Toggle Version</span><input type="checkbox" value={apiVersion === 'v2'} onChange={change_version}/><Button onClick={logout}>Log Out</Button></CardContent>
            <Messages messages={conversation} loading_response={loading} />
            <Divider/>
            <MessageBox send_message={send_message}/>
        </Card>
    </>
}

function MessageBox({
    send_message
}) {
    const [ message, setMessage ] = React.useState('');
    let on_send = () => {
        if ( message.trim().length === 0 ) {
            return;
        }
        setMessage( '' );
        send_message( message );
    }
    let on_key_up = (e) => {
        if (e.key === 'Enter' || e.keyCode === 13) {
            on_send()
        }
    }

    return <div style={{display: 'flex', padding: '8px'}}>
            <TextField
                multiline={true}
                sx={{width: '100%', padding: '4px'}}
                onKeyUp={on_key_up}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
            />
            <Button  sx={{flexAlign: 'top'}} onClick={on_send}><SendIcon/></Button>
    </div>;
}