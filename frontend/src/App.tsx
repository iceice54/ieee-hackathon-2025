import React, { useEffect, useRef, useState } from "react";
import {
  Box,
  Button,
  TextField,
  Typography,
  Container,
  InputAdornment,
  AppBar,
  Toolbar,
} from "@mui/material";
import { FaPaperPlane } from "react-icons/fa";

interface Message {
  text: string;
  sender: "user" | "bot";
}

const App: React.FC = () => {
  const [input, setInput] = useState<string>("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [isMessageSent, setIsMessageSent] = useState<boolean>(false);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  const handleMessageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setInput(event.target.value);
  };

  const handleSendClick = () => {
    if (input.trim()) {
      setIsMessageSent(true);
      console.log(input);
      setInput(""); // Clear input after sending.
    }
  };

  const sendMessage = (text: string, sender: "user" | "bot") => {
    if (!text.trim()) return;
    setMessages((prev) => [...prev, { text, sender }]);
    setInput(""); // Clear input after sending
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <Container
      maxWidth={false}
      disableGutters
      sx={{
        height: "100vh",
        margin: "0px",
        justifyContent: "center",
      }}
    >
      <AppBar
        position="sticky"
        sx={{ backgroundColor: "#29867c", alignSelf: "baseline" }}
      >
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1, textAlign: "center" }}>
            Changentic AI
          </Typography>
        </Toolbar>
      </AppBar>
      <Box
        display="flex"
        flexDirection="column"
        alignItems="center"
        justifyContent="center"
        height="600px"
        width="100vw"
        bgcolor="#f5f5f5"
        marginTop="10px"
      >
        {/* Chatbot Title */}
        {isMessageSent && (
          <Box
            sx={{
              flex: 1, // Take up remaining space
              width: "70%",
              maxWidth: "1200px",
              margin: "0",
              overflowY: "auto", // Enable scrolling for long conversations
              mb: 2,
            }}
          >
            {messages.map((msg, index) => (
              <Box
                key={index}
                sx={{
                  display: "flex",
                  justifyContent:
                    msg.sender === "user" ? "flex-end" : "flex-start",
                  mb: 1,
                }}
              >
                <Typography
                  sx={{
                    bgcolor: msg.sender === "user" ? "#1976d2" : "#e0e0e0",
                    color: msg.sender === "user" ? "white" : "black",
                    p: 1.5,
                    borderRadius: "10px",
                    maxWidth: "70%",
                  }}
                >
                  {msg.text}
                </Typography>
              </Box>
            ))}
          </Box>
        )}
        {!isMessageSent && (
          <Typography variant="h3" color="#29867c" gutterBottom>
            Changentic AI
          </Typography>
        )}

        {/* Message Input and Send Button */}
        <Box
          display="flex"
          alignItems="center"
          justifyContent="center"
          width="100%"
          margin="0px"
          mt={4}
        >
          <TextField
            variant="outlined"
            label="Ask a question"
            value={input}
            onChange={handleMessageChange}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                e.preventDefault();
                handleSendClick();
                sendMessage(input, "user");
              }
            }}
            multiline
            maxRows={6} // Maximum number of rows before scroll appear
            sx={{
              margin: 0,
              marginBottom: 3,
              width: "70%", // Adjust width here (e.g., 70% of the parent container)
            }}
            slotProps={{
              input: {
                endAdornment: (
                  <InputAdornment position="end">
                    <Button
                      onClick={handleSendClick}
                      sx={{
                        width: "30px",
                        height: "40px",
                        backgroundColor: "#29867c",
                        color: "white",
                        "&:hover": {
                          backgroundColor: "#20665e ",
                        },
                      }}
                    >
                      <FaPaperPlane />
                    </Button>
                  </InputAdornment>
                ),
              },
            }}
          />
        </Box>
      </Box>
    </Container>
  );
};

export default App;
